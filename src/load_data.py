import pandas as pd
from pathlib import Path

def get_data_paths(raw_dir: str) -> dict:
    raw_dir = Path(raw_dir)
    return{
        'raw_data': raw_dir / 'data_raw_immo_welt_de.csv',
        'population': raw_dir / 'plz_gebiete.xlsx',
        'bundesland': raw_dir / 'bundesland.xlsx',
        'cities': raw_dir / 'postleitzahlen.csv'
    }

def load_data(path: Path | str) -> pd.DataFrame:
    return pd.read_csv(path, sep=';', decimal=',')

def load_auxiliary_data(raw_dir):
    paths = get_data_paths(raw_dir)
    
    df_population = pd.read_excel(
        paths['population'],
        usecols=['plz', 'note', 'population', 'area_qkm']
    )
    df_bundesland = pd.read_excel(
        paths['bundesland'],
        usecols=['short_name', 'long_name', 'population_land', 'cadaster_area']
    )
    
    df_cities = pd.read_csv(
        paths['cities'], sep=';', decimal=','
    )
    
    return df_population, df_bundesland, df_cities