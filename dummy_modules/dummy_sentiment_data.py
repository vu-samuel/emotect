import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Liste von 40 DAX-Tickers (Platzhalter – ggf. anpassen)
dax_tickers = [
    "ADS", "BAS", "BMW", "ALV", "BAYN", "BEI", "BNR", "CON", "1COV", "DAI",
    "DHER", "DBK", "DTE", "EOAN", "FRE", "HEI", "HEN3", "IFX", "LIN", "MRK",
    "MTX", "MUV2", "PAH3", "PUM", "QIA", "RWE", "SAP", "SIE", "SHL", "SY1",
    "VOW3", "VNA", "WDI", "ZAL", "DWNI", "ENR", "HNR1", "RHM", "SRT3", "SDF"
]

# Zeitraum: 1 Jahr ab heute rückwärts
end_date = datetime.today()
start_date = end_date - timedelta(days=364)
date_range = pd.date_range(start=start_date, end=end_date)

# Dummy-Daten generieren
records = []
for date in date_range:
    for ticker in dax_tickers:
        sentiment = np.round(np.random.uniform(-1, 1), 4)
        records.append({
            "date": date,
            "ticker": ticker,
            "sentiment_score": sentiment
        })

# DataFrame bauen
df = pd.DataFrame(records)

# Rolling-Kennzahlen pro Ticker
df["rolling_mean"] = df.groupby("ticker")["sentiment_score"].transform(lambda x: x.rolling(window=3, min_periods=1).mean())
df["rolling_std"] = df.groupby("ticker")["sentiment_score"].transform(lambda x: x.rolling(window=3, min_periods=1).std())
df["z_score"] = (df["sentiment_score"] - df["rolling_mean"]) / df["rolling_std"]
df.sort_values(by=["ticker", "date"], inplace=True)

# Datei speichern
df.to_csv("dummy_sentiment.csv", index=False)
print("✅ Datei dummy_sentiment.csv erfolgreich erstellt.")
