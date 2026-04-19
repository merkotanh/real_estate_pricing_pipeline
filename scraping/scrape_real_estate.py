import requests
from bs4 import BeautifulSoup
import re
import time
import random
import logging
import os
import json

from dotenv import load_dotenv

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

REQUEST_DELAY_MIN = float(os.getenv("REQUEST_DELAY_MIN", 2))
REQUEST_DELAY_MAX = float(os.getenv("REQUEST_DELAY_MAX", 5))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
RETRY_TOTAL = int(os.getenv("RETRY_TOTAL", 3))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", 1.5))

LOCATIONS = {
    "Deutschland": os.getenv("LOCATION_DEUTSCHLAND"),
    "München": os.getenv("LOCATION_MUENCHEN"),
    "München Kreis": os.getenv("LOCATION_MUENCHEN_KREIS"),
    "Berlin": os.getenv("LOCATION_BERLIN"),
    "Köln": os.getenv("LOCATION_KOELN"),
}

# -------------------- LOGGING --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("../logs/scraper_info.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# -------------------- USER AGENTS --------------------
user_agents = json.loads(os.getenv("USER_AGENTS"))

BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

def get_headers():
    return {
        **BASE_HEADERS,
        "User-Agent": random.choice(user_agents)
    }

# -------------------- SESSION --------------------
def create_session():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update(get_headers())
    
    return session

session = create_session()

def get_params(location_name, deal_type="Rent"):
    return {
        "locations": LOCATIONS[location_name],
        "estateTypes": "House,Apartment",
        "page": 1
    }

# -------------------- REQUEST --------------------
def get_page(page_num, location_name):
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    for attempt in range(3):
        try:
            params = get_params(location_name)
            params["page"] = page_num
            
            response = session.get(
                BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            if "captcha" in response.text.lower():
                logger.warning("Access challenge detected. Stopping requests.")
                return None

            return response.text
            
        except requests.RequestException as ex:
            logger.warning(f"Attempt {attempt+1} failed {ex}")
            time.sleep(5 * (attempt + 1))
    return None
    
# -------------------- CADRS --------------------
def parse_immo_card(card):
    values_raw = [
        d.get_text(";", strip=True).split(";")
        for d in card.find_all("div", recursive=False)
    ]

    title = values_raw[1][0]
    size_raw = next((v for v in values_raw[1] if "m²" in v), None)
    rooms = next((v for v in values_raw[1] if "Zimmer" in v), None)
    free = next((v for v in values_raw[1] if "frei ab" in v), None)
    floor = next((v for v in values_raw[1] if any(x in v for x in ["UG", "EG", "Geschoss"])), None) 
   
    price_raw = values_raw[0][0].replace("\xa0", " ")
    details_set = set(values_raw[1][1:]) - {title, size_raw, rooms, free, floor, '·'}
    additional_details = next(iter(details_set), '')
    
    location_full = values_raw[-1][0]
    location_num = re.search(r"\((.*?)\)", location_full)
    location_str = re.search(r"^(.*?)\s*\(", location_full)
    
    return {
        "title": title,
        "price_raw": price_raw,
        "size_raw": size_raw,
        "rooms_raw": rooms,
        "floor_raw": floor,
        "free_raw": free,
        "location_full": location_full,
        "location": location_str.group(1) if location_str else None,
        "post": location_num.group(1) if location_num else None,
        "cold_hot_rent": values_raw[0][1] if len(values_raw[0]) > 1 else '',
        "additional_details": additional_details
    }

# -------------------- SCRAPER --------------------
def scrape_pages(page_start=1, num_pages=1, location_name='München Kreis', deal_type='Rent'):
    data = []
    
    for page in range(page_start, page_start + num_pages):
        html = get_page(page, location_name)
        if not html:
            logger.error(f"Failed to load page {page}")
            continue
        
        soup = BeautifulSoup(html, "html.parser")
        
        list_container = soup.select_one("[data-testid='serp-core-scrollablelistview-testid']")
        
        if not list_container:
            logger.warning(f"NO container on page {page}")
            continue
            
        listings = list_container.select("[data-testid='cardmfe-description-box-text-test-id']")
        print(f"Page {page}: found {len(listings)} announcements")
        logger.info(f"Page {page}: found {len(listings)} announcements")

        for listing in listings:
            data.append(parse_immo_card(listing))
    return data

# -------------------- MAIN --------------------

if __name__ == "__main__": 
    import pandas as pd
    import sqlite3
    conn = sqlite3.connect("../data/raw/real_estate.db")
    
    #parametry CLI 
    #python scrape_real_estate.py --location Berlin --page_start 1 --pages 2
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--location", type=str, default='München')
    parser.add_argument("--page_start", type=int, default=1)
    parser.add_argument("--pages", type=int, default=19)
    args = parser.parse_args()

    file_name = "../data/raw/data_raw_real_estates.csv"
    write_header = not os.path.exists(file_name) or os.stat(file_name).st_size == 0
    
    data = scrape_pages(page_start=args.page_start, num_pages=args.pages, location_name=args.location)
    
    df = pd.DataFrame(data)
    df.to_csv(file_name, mode='a', header=write_header, index=False,  sep=";", encoding="utf-8-sig")
    
    df.to_sql("../data/raw/real_estates", conn, if_exists="append", index=False)
    conn.close()
    
    print("Saved raw data")
    logger.info("Saved raw data")
