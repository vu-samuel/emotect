import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# === Projektstruktur einbinden ===
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import NEWS_DIR, FULL_SENTIMENT_FILE

# === Logging Setup ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "batch_sentiment_engine.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Sentiment Setup ===
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# === Trusted News laden ===
json_files = [f for f in os.listdir(NEWS_DIR) if f.endswith('_trusted.json')]
all_articles = []

for file_name in json_files:
    file_path = os.path.join(NEWS_DIR, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
        for article in articles:
            all_articles.append({
                'company_name': article.get('company_name'),
                'title': article.get('title'),
                'description': article.get('description'),
                'publishedAt': article.get('publishedAt'),
                'url': article.get('url'),
                'source': article.get('source')
            })

df_new = pd.DataFrame(all_articles)
df_new['publishedAt'] = pd.to_datetime(df_new['publishedAt'], errors='coerce')
df_new.dropna(subset=['publishedAt'], inplace=True)
df_new['date'] = df_new['publishedAt'].dt.normalize()
df_new['text'] = df_new['title'].fillna('') + '. ' + df_new['description'].fillna('')

# === Bestehende Daten laden ===
if FULL_SENTIMENT_FILE.exists():
    df_old = pd.read_csv(FULL_SENTIMENT_FILE, parse_dates=['publishedAt'])
    known_urls = set(df_old['url'])
    df_new = df_new[~df_new['url'].isin(known_urls)]
else:
    df_old = pd.DataFrame()

# === VADER Sentiment Analyse ===
if not df_new.empty:
    logger.info("⚙️ Starte VADER Sentiment-Analyse...")

    def get_sentiment(text):
        scores = sia.polarity_scores(str(text))
        compound = scores["compound"]
        if compound > 0.1:
            label = "positive"
        elif compound < -0.1:
            label = "negative"
        else:
            label = "neutral"
        return pd.Series([compound, label])

    df_new[['sentiment_score', 'sentiment_label']] = df_new['text'].apply(get_sentiment)
    df_new['analyzed_at'] = pd.Timestamp.now()

    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    df_combined.drop_duplicates(subset=["url"], inplace=True)

    FULL_SENTIMENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_combined.to_csv(FULL_SENTIMENT_FILE, index=False)

    logger.info(f"✅ {len(df_new)} neue Artikel analysiert und gespeichert in '{FULL_SENTIMENT_FILE.name}'")
else:
    logger.info("🔁 Keine neuen Artikel zur Analyse gefunden.")
