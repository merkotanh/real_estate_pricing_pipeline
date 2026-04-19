import numpy as np
import pandas as pd

def extract_object_type(df: pd.DataFrame) -> pd.DataFrame:
    df[['object_type', 'marketing_type']] = df['title'].str.extract(r'(\w+)\s+(zur Miete|zum Kauf)')
    return df

def calculate_price_per_sqm(df: pd.DataFrame) -> pd.DataFrame:
    df['price_per_sqm'] = df['price_euro'] / df['size_sqm']
    df.loc[df['size_sqm'] == 0, 'price_per_sqm'] = None
    return df

def add_isvalid(df: pd.DataFrame) -> pd.DataFrame:
    df['is_valid'] = (
        (
            (df['marketing_type'] == 'zur Miete') &
            df['price_per_sqm'].between(3,85) &
            (df['size_sqm'] > 9)
        )
        |
        (
            (df['marketing_type'] == 'zum Kauf') &
            (df['price_per_sqm'].notna())
        )
    )
    return df

def categorized_size(df: pd.DataFrame) -> pd.DataFrame:
    df['size_category'] = pd.cut(
        df['size_sqm'],
        bins=[0,50,100,200,1000],
        labels=['small', 'medium', 'large', 'luxury']
    )
    return df
#df_population['density_city'] = df_population['population'] / df_population['area_qkm']
#df_land['density_land'] = (df_land['population_land'] / df_land['cadaster_area'])

#df_cities = postleitzahlen.csv
#df_population = plz_gebiete.xlsx,  usecols=['plz', 'note', 'population','area_qkm'])
#df_land = bundesland.xls   usecols=['short_name', 'long_name', 'population_land', 'cadaster_area'])

def calculate_density_land(df_bundesland: pd.DataFrame) -> pd.DataFrame:
    df_bundesland['density_land'] = df_bundesland['population_land'] / df_bundesland['cadaster_area']
    df_bundesland.loc[df_bundesland['cadaster_area'] == 0, 'density_land'] = None
    return df_bundesland

def calculate_density_city(df_population: pd.DataFrame) -> pd.DataFrame:
    df_population['density_city'] = df_population['population'] / df_population['area_qkm']
    df_population.loc[df_population['area_qkm'] == 0, 'density_city'] = None
    return df_population
    
def add_bundesland_features(df: pd.DataFrame) -> pd.DataFrame:
    df['list_by_bundesland'] = (
        df.groupby('bundesland')['bundesland']
        .transform('count')
    )

    df['listings_per_1k_bundesland'] = np.where(
        df['density_land'] > 0,
        (df['list_by_bundesland'] / df['density_land']) * 1000,
        np.nan
    )

    return df

def add_city_features(df: pd.DataFrame) -> pd.DataFrame:
    df['list_by_city'] = (
        df.groupby('city')['city']
        .transform('count')
    )

    df['listings_per_1k_city'] = np.where(
        df['density_city'] > 1000,
        (df['list_by_city'] / df['density_city']) * 1000,
        np.nan
    )

    return df

def add_listing_density_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_bundesland_features(df)
    df = add_city_features(df)
    return df
    