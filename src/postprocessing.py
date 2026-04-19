import pandas as pd

def finalize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df['country'] = 'Germany'
    df.insert(0, 'id', range(1, len(df)+1))

    columns = [
        'id',
        'object_type',
        'marketing_type',
        'is_valid',
        'price_euro',
        'size_sqm',
        'size_category',
        'price_per_sqm', 
        'pred_price_sqm',
        'listings_per_1k_bundesland',
        'listings_per_1k_city',
        'density_city',
        'density_land', 
        'population_land',
        'location_full',
        'zip',
        'city',
        'bundesland',
        'short_name',
        'country',
        'rooms', 
        'floor', 
        'free',
        'cold_hot_rent'
    ]

    columns = [col for col in columns if col in df.columns]

    df = df[columns]

    return df
    