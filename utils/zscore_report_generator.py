import tempfile
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import pandas as pd
import sys
from datetime import datetime
import streamlit as st

# === Projekt-Config laden ===
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import COMPANY_INFO

# === Jinja2 Template Directory ===
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_FILE = TEMPLATE_DIR / "zscore_report.html"

def offer_html_download(html_out: str, filename: str = "report.html"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmpfile:
        tmpfile.write(html_out)
        tmpfile_path = tmpfile.name

    with open(tmpfile_path, "r", encoding="utf-8") as f:
        html_bytes = f.read().encode("utf-8")

    st.download_button(
        label="📄 Download HTML Report",
        data=html_bytes,
        file_name=filename,
        mime="text/html"
    )

    st.info("Tipp: Nach dem Öffnen im Browser einfach **Strg + P** drücken und als PDF speichern.")

def generate_zscore_report_html(ticker, df_daily, company_name=None):
    company_name = company_name or COMPANY_INFO.get(ticker, {}).get("name", ticker)
    date_range = f"{df_daily['date'].min().date()} to {df_daily['date'].max().date()}"
    window = df_daily["mean"].first_valid_index() or "N/A" if "mean" in df_daily.columns else "N/A"

    latest_row = df_daily.dropna(subset=["z_score"]).iloc[-1]
    latest_z = round(latest_row["z_score"], 2)

    if abs(latest_z) >= 2:
        zscore_status = "Severe emotional shock"
    elif abs(latest_z) >= 1:
        zscore_status = "Mild anomaly"
    else:
        zscore_status = "Stable sentiment"

    # === Extreme Days Table ===
    extreme_df = df_daily[abs(df_daily["z_score"]) >= 2]
    extreme_table = extreme_df[["date", "sentiment_score", "z_score"]] \
        .sort_values("z_score", ascending=False).to_dict(orient="records")

    # === Render HTML without Plotly PNGs (Streamlit Cloud safe) ===
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_FILE.name)
    html_out = template.render(
        company_name=company_name,
        ticker=ticker,
        date_range=date_range,
        window=window,
        latest_z=latest_z,
        zscore_status=zscore_status,
        zscore_plot_path=None,  # Placeholder or omit from template
        gauge_path=None,
        extreme_table=extreme_table,
        now=datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    offer_html_download(html_out, filename=f"Zscore_Report_{ticker}_{datetime.now().date()}.html")
