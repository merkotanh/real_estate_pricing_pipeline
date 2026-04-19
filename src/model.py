import pandas as pd
import numpy as np
import logging
import os
import joblib

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold

logger = logging.getLogger(__name__)

def kfold_target_encoding(df, col, target, n_splits=5):
    df = df[(df['is_valid'])].copy()
    global_mean = df[target].mean()

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    te_col = f"{col}_te"
    df[te_col] = np.nan

    for train_idx, val_idx in kf.split(df):
        train_fold = df.iloc[train_idx]
        val_fold = df.iloc[val_idx]

        mapping = train_fold.groupby(col)[target].mean()

        df.iloc[val_idx, df.columns.get_loc(te_col)] = (
            val_fold[col].map(mapping)
        )
    df[te_col] = df[te_col].fillna(global_mean)
    full_mapping = df.groupby(col)[target].mean()

    return df, full_mapping, global_mean


def prepare_features(df: pd.DataFrame, marketing_type: str):
    df_model = df[(df['is_valid']) & (df['marketing_type'] == marketing_type)].copy()

    if df_model.empty:
        logger.warning(f"No data for training model for {marketing_type}")
        return None, None, None

    ##------target encoding-------
    df_model, city_map, city_global = kfold_target_encoding(
        df_model, 'city', 'price_per_sqm'
    )
    df_model, obj_map, obj_global = kfold_target_encoding(
        df_model, 'object_type', 'price_per_sqm'
    )

    ##------features-------
    features = ['size_sqm', 'density_city', 'listings_per_1k_bundesland', 'listings_per_1k_city', 'city_te', 'object_type_te']
    
    X = df_model[features]
    y = df_model['price_per_sqm']

    encoders = {
        'city': (city_map, city_global),
        'object_type': (obj_map, obj_global)
    }

    logger.info(f"{marketing_type}: training on {len(X)} rows")

    return X, y, df_model.index, encoders

def train_model(X, y):
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)

    model = LinearRegression()
    model.fit(X_imputed, y)

    return model, imputer

def apply_te(series, mapping, global_mean):
    return series.map(mapping).fillna(global_mean)

def predict_price(marketing_type, model, imputer, df, features, encoders):
    df = df[(df['is_valid']) & (df['marketing_type'] == marketing_type)].copy()

    city_map, city_global = encoders['city']
    obj_map, obj_global = encoders['object_type']

    df['city_te'] = apply_te(df['city'], city_map, city_global)
    df['object_type_te'] = apply_te(df['object_type'], obj_map, obj_global)

    X = df[features]

    X_imputed = imputer.transform(X)

    return model.predict(X_imputed)

def run_modeling(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['is_valid'] & df['price_per_sqm'].notna()].copy()

    df['predicted_price_per_sqm'] = np.nan
    df['predicted_price'] = np.nan

    model_artifacts = {}

    for mt, key in [('zur Miete','rent'), ('zum Kauf', 'buy')]:
        X, y, idx, encoders = prepare_features(df, mt)
        
        if X is None:
            continue

        model, imputer = train_model(X, y)
        features = X.columns.tolist()

        preds = predict_price(
            mt,
            model,
            imputer,
            df.loc[idx],
            features,
            encoders
        )

        df.loc[idx, 'predicted_price_per_sqm'] = preds
        df.loc[idx, 'predicted_price'] = preds * df.loc[idx, 'size_sqm']

        model_artifacts[key] = {
            'model': model,
            'imputer': imputer,
            'features': features,
            'target': 'price_per_sqm',
            'segment': mt
        }
        
        logger.info(f"{mt}: prediction done")

    return df, model_artifacts

def save_artifacts(obj, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(obj, path)


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['is_valid'] & df['price_per_sqm'].notna()].copy()

    df['gap'] = df['predicted_price_per_sqm'] - df['price_per_sqm']
    df['ratio'] = df['gap'] / df['price_per_sqm']#.replace(0, pd.NA)

    metrics = (
        df.groupby('marketing_type')
        .agg(
            MAE=('gap', lambda x: x.abs().mean()),
            RMSE=('gap', lambda x: np.sqrt((x**2).mean())),
            bias=('gap', 'mean'),
        )
    )

    df = df.merge(metrics, on='marketing_type', how='left')

    return df

def classify_prices(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['is_valid'] & df['price_per_sqm'].notna()].copy()
    
    df['price_category'] = pd.cut(
        df['ratio'],
        bins=[-float('inf'), -0.2, 0.2, float('inf')],
        labels=['Overpriced', 'Fair Price', 'Underpriced']
    )

    df['price_category'] = df['price_category'].cat.add_categories(['Invalid data'])
    
    df['price_category'] = df['price_category'].where(
        df['is_valid'],
        'Invalid data'
    )

    return df
