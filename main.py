import os
import logging

from pathlib import Path
from datetime import datetime

from src.pipeline import process_data
from src.model import run_modeling, classify_prices, add_metrics, save_artifacts
from src.validation import create_data_quality_report


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data/processed'
MODEL_DIR = PROJECT_ROOT / 'model'
LOGS_DIR =  PROJECT_ROOT / 'logs'
REPORTS_DIR = PROJECT_ROOT / 'reports'


os.makedirs('logs', exist_ok=True)
os.makedirs('reports', exist_ok=True)

report_excel_path = REPORTS_DIR / 'quality_report.xlsx'
report_html_path = REPORTS_DIR / 'quality_report.html'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
    handlers = [
        logging.FileHandler('logs/processing.log', encoding='utf-8'),
        logging.StreamHandler()
    ], 
    force=True
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    df = process_data(RAW_DIR)

    report = create_data_quality_report(df, output_excel=report_excel_path, output_html=report_html_path)
   
    df, model_artifacts = run_modeling(df)
    logger.info('Modeling completed')

    if 'rent' in model_artifacts:
         save_artifacts(model_artifacts['rent'], MODEL_DIR / 'rent_model.pkl')
    if 'buy' in model_artifacts:
         save_artifacts(model_artifacts['buy'], MODEL_DIR / 'buy_model.pkl')

    df = add_metrics(df)
    logger.info('Metrics added')
    
    df = classify_prices(df)
    logger.info('Prices classified')

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    df.to_csv(
        PROCESSED_DIR / 'immowelt_cleaned.csv',
        index=False,
        sep=';',
        decimal=',',
        encoding='utf-8-sig'
    )

    logger.info('Data saved!')