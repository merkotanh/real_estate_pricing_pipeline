import pandas as pd

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()

def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    df['price_euro'] = (
        df['price_raw']
        .astype(str)
        .str.replace(r'[^\d,\.]', '', regex=True)
        .str.replace('.', '', regex=False)  
      #  .str.replace(',', '.', regex=False)
        .pipe(pd.to_numeric, errors='coerce')
    )
    return df

def clean_size(df: pd.DataFrame) -> pd.DataFrame:
    df['size_sqm'] = (
        df['size_raw']
        .astype(str)
        .str.replace('m²', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.extract(r'(\d+[.,]?\d+)')[0]
        .pipe(pd.to_numeric, errors='coerce')
    )
    return df

def extract_city(df: pd.DataFrame) -> pd.DataFrame:
    df['city'] = (
        df['location_full']
        .str.extract(r'([A-Za-zßäöüÄÖÜ\s\-]+)\s*\(\d+\)')[0]
        .str.strip()
    )
    return df

def extract_zipcode(df: pd.DataFrame) -> pd.DataFrame:
    df['zip'] = (
        df['location_full']
        .astype(str)
        .str.extract(r'\(([^()]*)\)\s*$')[0]
        .str.extract(r'(\d+)')
        .astype('Int64')
    )
    return df

def extract_rooms(df: pd.DataFrame) -> pd.DataFrame:
    df['rooms'] = (
        df['rooms_raw']
        .astype(str)
        .str.extract(r'(\d+(?:,\d+)?|WG)')[0]
    )
    return df

def extract_floor(df: pd.DataFrame) -> pd.DataFrame:
    df['floor'] = (
        df['floor_raw']
        .astype(str)
        .str.extract(r'(\d+(?:,\d+)?|EG|UG)')[0]
    )
    return df

def extract_free(df: pd.DataFrame) -> pd.DataFrame:
    df['free'] = (
        df['free_raw']
        .astype(str)
        .str.extract(r'(\d{2}\.\d{2}\.\d{4}|sofort)')[0]
    )
    return df
    