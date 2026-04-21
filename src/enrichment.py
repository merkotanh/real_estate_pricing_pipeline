import pandas as pd

#    df_population -> plz_gebiete.xlsx  ['plz', 'note', 'population', 'area_qkm']
#    df_bundesland -> bundesland.xlsx ['short_name', 'long_name', 'population_land', 'cadaster_area']
#    df_cities -> postleitzahlen.csv  plz

def merge_with_bundesland(df_cities, df_bundesland):
    return df_cities.merge(
        df_bundesland,
        how='left',
        left_on='bundesland',
        right_on='long_name'
    )

def merge_with_population(df_cities, df_population):
    return df_cities.merge(
        df_population,
        how='left',
        left_on='plz', 
        right_on='plz'
    )
    
def merge_with_all(df, df_cities):
    return df.merge(
        df_cities,
        how='left',
        left_on=['zip', 'city'],
        right_on=['plz', 'ort']
    )
