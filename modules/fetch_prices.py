import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    get_stock_price_filename,
    STOCK_PRICE_DIR,
    START_DATE,
    END_DATE,
    get_all_tickers,
    COMPANY_INFO
)

import logging

# === Logging Setup ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "price_update.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# === Zielverzeichnis sicherstellen ===
os.makedirs(STOCK_PRICE_DIR, exist_ok=True)

# === Ticker mit ".DE" verwenden ===
tickers = get_all_tickers(with_suffix=True)

for ticker in tickers:
    ticker_short = ticker.replace(".DE", "")
    company_name = COMPANY_INFO.get(ticker_short, {}).get("name", ticker_short)
    try:
        file_path = get_stock_price_filename(ticker)

        # 1. Prüfen, ob Datei existiert → Startdatum setzen
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path, parse_dates=["Date"])
            last_date = existing_df["Date"].max()
            fetch_start = (pd.to_datetime(last_date) + timedelta(days=1)).date()
            logging.info(f"📂 {ticker}: Daten vorhanden. Letzter Tag: {last_date.date()}. Abruf ab {fetch_start}")
        else:
            existing_df = pd.DataFrame()
            fetch_start = START_DATE.date()
            logging.info(f"🆕 {ticker}: Keine Datei vorhanden. Abruf ab {fetch_start}")

        fetch_end = END_DATE.date()
        if fetch_start >= fetch_end:
            logging.info(f"✅ {ticker}: Keine neuen Daten nötig.")
            continue

        # 2. Abruf
        df_new = yf.download(ticker, start=fetch_start, end=fetch_end, group_by="column", auto_adjust=False)
        if isinstance(df_new.columns, pd.MultiIndex):
            df_new.columns = df_new.columns.get_level_values(0)
        df_new = df_new.reset_index()

        if df_new.empty:
            logging.warning(f"⚠️ {ticker}: Keine neuen Daten.")
            continue

        df_new["Company"] = company_name
        df_new["Ticker"] = ticker

        # 3. Kombinieren & Speichern
        combined_df = pd.concat([existing_df, df_new], ignore_index=True)
        combined_df.drop_duplicates(subset=["Date"], inplace=True)
        combined_df.sort_values("Date", inplace=True)
        combined_df.to_csv(file_path, index=False)

        logging.info(f"💾 {ticker}: +{len(df_new)} Zeilen. Gesamt: {len(combined_df)}")

    except Exception as e:
        logging.error(f"❌ Fehler bei {ticker}: {e}")
