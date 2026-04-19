from pathlib import Path
import logging

from src.load_data import get_data_paths, load_data, load_auxiliary_data
from src.clean_data import (
    remove_duplicates,
    clean_price,
    clean_size,
    extract_city,
    extract_zipcode,
    extract_rooms,
    extract_floor,
    extract_free
)
from src.feature_engineering import (
    extract_object_type,
    calculate_price_per_sqm,
    categorized_size,
    add_isvalid,
    calculate_density_land,
    calculate_density_city,
    add_listing_density_features
)

from src.enrichment import (
    merge_with_bundesland,
    merge_with_population,
    merge_with_all
)

from src.postprocessing import finalize_dataset

logger = logging.getLogger(__name__)

def process_data(raw_dir: Path | str): 
    raw_dir = Path(raw_dir)
    paths = get_data_paths(raw_dir)

    logger.info('Pipeline started')
    df = load_data(paths['raw_data'])
    logger.info(f"Loaded data: {df.shape}")

    logger.info('Cleaning and calculating price per sqm')
    df = (
        df
        .pipe(remove_duplicates)
        .pipe(clean_price)
        .pipe(clean_size)
        .pipe(extract_city)
        .pipe(extract_zipcode)
        .pipe(extract_rooms)
        .pipe(extract_floor)
        .pipe(extract_free)
        .pipe(extract_object_type)
        .pipe(calculate_price_per_sqm)
    )
    logger.info('Cleaning and calculating completed')

    logger.info('Checking price per sqm validation, add listings categories')
    df = (
        df
        .pipe(add_isvalid)
        .pipe(categorized_size)
    )
    logger.info(f"Valid rows: {df['is_valid'].mean():.2%}")
    
    logger.info('Loading external data')
    df_population, df_bundesland, df_cities = load_auxiliary_data(raw_dir)
    logger.info(f"Loaded external data, sizes: {df_population.shape}, {df_bundesland.shape}, {df_cities.shape}")

    logger.info('Calculatings dencity')
    df_bundesland = (
        df_bundesland
        .pipe(calculate_density_land)
    )

    df_population = (
        df_population
        .pipe(calculate_density_city)
    )
    logger.info('Calculatings dencity completed')

    logger.info('Merging external data')
    df_cities = (
        df_cities
        .pipe(merge_with_bundesland, df_bundesland)
        .pipe(merge_with_population, df_population)
    )

    df = (df.pipe(merge_with_all, df_cities))
    logger.info(f"Merging comleted, dataset size: {df.shape}")
    
    df = (df.pipe(add_listing_density_features))

    df = finalize_dataset(df)
    logger.info(f"Final dataset size: {df.shape}")
    
    return df