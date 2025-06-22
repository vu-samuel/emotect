import os
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import FULL_SENTIMENT_FILE, PROCESSED_DIR

# === Parameter ===
ROLLING_WINDOW = 30
Z_SCORE_FILE = PROCESSED_DIR / "z_scores.csv"

# === Lade Sentimentdaten ===
if not FULL_SENTIMENT_FILE.exists():
    raise FileNotFoundError(f"{FULL_SENTIMENT_FILE} not found. Run sentiment_engine.py first.")

df = pd.read_csv(FULL_SENTIMENT_FILE, parse_dates=["date"])

# === Tagesdurchschnitt pro Unternehmen ===
daily = (
    df.groupby(["ticker", "date"])
    .agg(mean_sentiment=("sentiment_score", "mean"), count=("sentiment_score", "count"))
    .reset_index()
)

# === Sortieren für Rolling-Operationen
daily = daily.sort_values(by=["ticker", "date"])

# === Rolling-Mittelwert & -Stdabweichung (3 Tage)
daily["rolling_mean"] = (
    daily.groupby("ticker")["mean_sentiment"]
    .transform(lambda x: x.rolling(window=ROLLING_WINDOW, min_periods=3).mean())
)
daily["rolling_std"] = (
    daily.groupby("ticker")["mean_sentiment"]
    .transform(lambda x: x.rolling(window=ROLLING_WINDOW, min_periods=3).std())
)

# === Z-Score berechnen
daily["z_score"] = (daily["mean_sentiment"] - daily["rolling_mean"]) / daily["rolling_std"]

# === Ungültige Zeilen entfernen
daily = daily.dropna(subset=["z_score"])

# === Speichern
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
daily.to_csv(Z_SCORE_FILE, index=False)

print(f"✅ 3-Tage-Z-Scores gespeichert nach: {Z_SCORE_FILE}")
