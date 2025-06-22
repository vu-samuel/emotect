import os
import json
import datetime
import requests
import time
import logging
from tqdm import tqdm
from config import (
    NEWSDATA_API_KEY,
    RAW_NEWS_DIR,
    COMPANY_INFO,
    get_news_filename
)

# === Logging Setup ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "fetch_news_newsdata.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_news_for_company(company_name, from_date, to_date):
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": company_name,
        "language": "de",
        "from_date": from_date,
        "to_date": to_date
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            logger.warning(f"{company_name}: HTTP {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"{company_name}: Fehler beim Abruf – {e}")
        return []

def save_articles(ticker, company_name, articles_raw):
    file_path = get_news_filename(ticker)

    # Standardisieren & Filtern
    new_articles = []
    for a in articles_raw:
        if not a.get("link"):
            continue
        new_articles.append({
            "date": a.get("pubDate", "")[:10],
            "ticker": ticker,
            "company_name": company_name,
            "title": a.get("title", "").strip(),
            "description": a.get("description", "").strip(),
            "url": a.get("link", "").strip(),
            "source": a.get("source_id", ""),
            "sentiment_score": None
        })

    # Existierende laden
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    # Dedup nach URL
    all_combined = existing + new_articles
    deduped = {a["url"]: a for a in all_combined if a["url"]}
    final_articles = list(deduped.values())

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_articles, f, ensure_ascii=False, indent=2)

    return len(new_articles), len(final_articles)

def main(from_days_ago=1):
    today = datetime.date.today()
    from_date = (today - datetime.timedelta(days=from_days_ago)).isoformat()
    to_date = today.isoformat()

    logger.info(f"🔎 Starte Abruf von News ({from_date} bis {to_date})")

    for ticker, info in tqdm(COMPANY_INFO.items(), desc="🔍 Unternehmen"):
        company_name = info["name"]
        articles = fetch_news_for_company(company_name, from_date, to_date)
        if articles:
            new_count, total_count = save_articles(ticker, company_name, articles)
            logger.info(f"✅ {ticker}: +{new_count} neue Artikel (insg. {total_count})")
        else:
            logger.info(f"➖ {ticker}: keine neuen Artikel")
        time.sleep(1.5)  # API-Schonung

if __name__ == "__main__":
    main()
