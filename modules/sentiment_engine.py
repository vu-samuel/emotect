import os
import json
import pandas as pd
from pathlib import Path
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))  # Füge das Projektverzeichnis zum Pfad hinzu
from config import (
    COMPANY_INFO,
    get_news_filename,
    FULL_SENTIMENT_FILE
)

# === VADER vorbereiten ===
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# === Artikel sammeln ===
all_articles = []

for ticker, info in COMPANY_INFO.items():
    file_path = get_news_filename(ticker)
    if not os.path.exists(file_path):
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    for article in articles:
        if article.get("sentiment_score") is not None:
            continue  # Überspringe bereits analysierte Artikel

        text = f"{article.get('title', '')}. {article.get('description', '')}".strip()
        score = sia.polarity_scores(text)["compound"]
        article["sentiment_score"] = round(score, 4)
        article["sentiment_label"] = (
            "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
        )

    # === JSON-Datei aktualisieren ===
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    all_articles.extend(articles)

# === Full Sentiment File (CSV) erstellen ===
if all_articles:
    df = pd.DataFrame(all_articles)
    df = df[df["sentiment_score"].notnull()].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df.drop_duplicates(subset=["url"], inplace=True)

    # Sortierung & finale Speicherung
    df.sort_values(by=["ticker", "date"], inplace=True)
    FULL_SENTIMENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FULL_SENTIMENT_FILE, index=False)
    print(f"✅ {len(df)} Artikel mit Sentiment gespeichert → {FULL_SENTIMENT_FILE.name}")
else:
    print("🔁 Keine neuen Artikel zum Analysieren.")
