import os
import sys
import time
import json
import random
import datetime
import pandas as pd
import logging
from tqdm import tqdm
from pathlib import Path

# === Projektstruktur einbinden ===
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    COMPANY_INFO,
    RAW_NEWS_DIR,
    NEWSAPI_KEY,
    get_news_filename
)


# === Logging Setup ===
LOG_DIR = Path("logs")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RAW_NEWS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "newsapi_fetch.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === NewsAPI Setup ===
from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

# === Date Range Setup ===
today = datetime.datetime.now(datetime.timezone.utc)
thirty_days_ago = today - datetime.timedelta(days=30)
today_str = today.strftime("%Y-%m-%d")
thirty_days_ago_str = thirty_days_ago.strftime("%Y-%m-%d")

# === Sources and Domains to Filter ===
SOURCES = 'cnbc,reuters,bloomberg,the-wall-street-journal,yahoo-finance,business-insider,fortune'
DOMAINS = 'cnbc.com,reuters.com,bloomberg.com,wsj.com,finance.yahoo.com,businessinsider.com,fortune.com'


# === Fetch Articles per Company ===
for ticker, info in tqdm(COMPANY_INFO.items(), desc="🔍 Fetching news"):
    try:
        company_name = info["name"]

        all_articles = newsapi.get_everything(
            q=company_name,
            sources=SOURCES,
            domains=DOMAINS,
            from_param=thirty_days_ago_str,
            to=today_str,
            sort_by='relevancy',
            language='en'
        )

        articles = all_articles.get('articles', [])
        filtered_articles = []

        for article in articles:
            published_at = article.get('publishedAt')
            if not published_at:
                continue

            filtered_articles.append({
                "date": published_at[:10],
                "ticker": ticker,
                "company_name": company_name,
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "source": article.get("source", {}).get("name"),
                "sentiment_score": None  # Platzhalter für spätere Analyse
            })

        file_path = get_news_filename(ticker)

        # === Load Existing Articles ===
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
        else:
            existing_articles = []

        # === Combine and Deduplicate by URL ===
        all_combined = existing_articles + filtered_articles
        df_all = pd.DataFrame(all_combined)
        df_all.drop_duplicates(subset=["url"], inplace=True)
        deduped_articles = df_all.to_dict(orient="records")

        # === Save to JSON ===
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(deduped_articles, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 {ticker}: {len(filtered_articles)} new | {len(deduped_articles)} total in {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fetching news for {company_name}: {e}")

    time.sleep(random.uniform(2.5, 3.5))  # Rate limit safety
