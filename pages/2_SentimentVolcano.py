import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

# === Layout & Seite ===
st.set_page_config(layout="wide", page_title="🌋 EMOTECT | Crisis Pressure Tracker", page_icon="🌋")

st.markdown("""
<style>
    html, body, [class*="css"] { margin: 0; padding: 0; }
    .main .block-container { padding: 0rem; max-width: 100%; }
    .stPlotlyChart { padding: 0 !important; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# === Imports aus Projektstruktur ===
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DUMMY_FULL_SENTIMENT_FILE, COMPANY_INFO
from utils.negative_pressure_report_generator import generate_negative_pressure_pdf

# === Schlüsselwörter
RISK_KEYWORDS = [
    "fraud", "scandal", "layoffs", "corruption", "bribery",
    "leak", "hack", "fine", "lawsuit", "whistleblower",
    "investigation", "collapse", "resignation", "probe", "recession", "bad", "loss"
]

def count_keywords(text, keywords):
    if pd.isna(text):
        return 0
    return sum(bool(re.search(rf"{re.escape(k)}", str(text).lower())) for k in keywords)

def classify_volcano_level(pressure):
    if pressure < 3: return "calm"
    elif pressure < 6: return "smoking"
    elif pressure < 9: return "red_hot"
    return "eruption"

def classify_alert(pressure):
    if pressure >= 8: return "⚠️ ERUPTION ALERT"
    elif pressure >= 5: return "🔶 Volcano Warning"
    return None

# === Daten einlesen
if not DUMMY_FULL_SENTIMENT_FILE.exists():
    st.error("❌ Dummy-Sentiment Data missing.")
    st.stop()

df = pd.read_csv(DUMMY_FULL_SENTIMENT_FILE, parse_dates=["date"])

# 🔄 Sicherstellen, dass Ticker konsistent groß sind
df["ticker"] = df["ticker"].str.upper()

# === Filter last 7 days ===
today = pd.to_datetime(datetime.now().date())
one_week_ago = today - timedelta(days=7)

df = df[df["date"].between(one_week_ago, today)]

# === Auswahlbereich: Dropdown oder Slider
st.sidebar.markdown("### 🗓️ Time Interval")
day_options = {"Past 1 Day": 1, "Past 7 Days": 7, "Past 14 Days": 14, "Past 30 Days": 30}
selected_range = st.sidebar.selectbox("(aggregated) Time Interval", list(day_options.keys()))
day_span = day_options[selected_range]

use_slider = st.sidebar.checkbox("🔧 Time-Slider instead of Dropdown", value=False)

if use_slider:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    start_date, end_date = st.sidebar.slider(
        "Date Interval",
        min_value=min_date,
        max_value=max_date,
        value=(max_date - timedelta(days=day_span), max_date),
        format="YYYY-MM-DD"
    )
    
    # Konvertiere Slider-Werte in Timestamps
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

else:
    today = pd.to_datetime(datetime.now().date())
    end_date = today
    start_date = today - timedelta(days=day_span)

# ✅ Gültiger Vergleich mit datetime64-Spalte
df = df[df["date"].between(start_date, end_date)]
date_range_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"


# === Risk-Zählung (nur über Keywords – Sentimentfilter entfernt)
df["risk_hits_title"] = df["title"].apply(lambda x: count_keywords(x, RISK_KEYWORDS))
df["risk_hits_desc"] = df["description"].apply(lambda x: count_keywords(x, RISK_KEYWORDS))
df["risk_hits_total"] = df["risk_hits_title"] + df["risk_hits_desc"]
df_risky = df[df["risk_hits_total"] > 0].copy()

# === Volcano-Level aggregieren
volcano_df = df_risky.groupby("ticker")["risk_hits_total"].sum().reset_index()
volcano_df.columns = ["ticker", "pressure"]
volcano_df["level"] = volcano_df["pressure"].apply(classify_volcano_level)
volcano_df["alert"] = volcano_df["pressure"].apply(classify_alert)

# === Standortdaten extrahieren
location_df = pd.DataFrame([
    {**info, "ticker": ticker} for ticker, info in COMPANY_INFO.items() if "lat" in info and "lon" in info
])

# === Zusammenführen
merged_df = pd.merge(volcano_df, location_df, on="ticker", how="inner")

# === Letzter Snapshot
latest_date = df["date"].max()
title_str = latest_date.strftime("%Y-%m-%d") if isinstance(latest_date, pd.Timestamp) else "Unknown"

# === Farben und Labels
LEVEL_COLOR_MAP = {
    "calm": "#2ecc71",
    "smoking": "#f1c40f",
    "red_hot": "#e67e22",
    "eruption": "#e74c3c"
}
LEVEL_LABEL_MAP = {
    "calm": "🟢 Calm",
    "smoking": "🌫 Smoking",
    "red_hot": "🔥 Red Hot",
    "eruption": "💥 Eruption"
}

# === Logo und Header
logo_path = Path(__file__).resolve().parent.parent / "assets" / "emotect_logo.png"
col1, col2 = st.columns([0.1, 0.9])
with col1:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.warning("Logo fehlt.")
with col2:
    st.markdown("""
    <h1 style='margin-bottom: 0; color: #0F4C81; font-size: 32px;'>EMOTECT – Sentiment Volcano</h1>
    <p style='color: #666; font-size: 14px; margin-top: 4px;'>Emotional Risk Detection for Corporate Decision-Makers</p>
    """, unsafe_allow_html=True)

# === Intro-Kasten

st.markdown(f"""
<div style="padding: 1.5rem 2rem; background-color: #f9f9f9; border-radius: 12px;">
    <h2 style="margin-bottom: 0.5rem;">🔥 Crisis Pressure Tracker</h2>
    <p style="color: #333; font-size: 16px;">📅 Aggregated pressure from <code>{date_range_str}</code></p>
</div>
""", unsafe_allow_html=True)

# === Volcano Map
fig = go.Figure()
for _, row in merged_df.iterrows():
    fig.add_trace(go.Scattergeo(
        lon=[row["lon"]],
        lat=[row["lat"]],
        text=f"{row['name']}<br>{LEVEL_LABEL_MAP[row['level']]}<br>Pressure: {row['pressure']}<br>{row['alert'] or ''}",
        mode="markers+text",
        textposition="top center",
        marker=dict(
            size=18,
            symbol="triangle-up",
            color=LEVEL_COLOR_MAP.get(row["level"], "gray"),
            line=dict(width=0.5, color="black")
        ),
        hoverinfo="text"
    ))

fig.update_layout(
    autosize=True,
    height=880,
    margin=dict(l=0, r=0, t=20, b=0),
    geo=dict(
        scope='europe',
        projection_type='mercator',
        center=dict(lat=51.0, lon=10.0),
        lataxis_range=[47, 55],
        lonaxis_range=[5, 16],
        showland=True,
        landcolor="rgb(229, 229, 229)",
        countrycolor="white"
    )
)

st.plotly_chart(fig, use_container_width=True)


# === Sidebar-Legende
if st.sidebar.checkbox("📘 Show Legend", value=True):
    st.sidebar.markdown("## Volcano Levels")
    st.sidebar.markdown("""
    <ul style="font-size: 15px;">
        <li><span style="color:#2ecc71;">🟢 Calm</span> – 0–2</li>
        <li><span style="color:#f1c40f;">🌫 Smoking</span> – 3–5</li>
        <li><span style="color:#e67e22;">🔥 Red Hot</span> – 6–8</li>
        <li><span style="color:#e74c3c;">💥 Eruption</span> – 9+</li>
    </ul>
    """, unsafe_allow_html=True)

# Zählung nach Woche + Ticker
df_risky["week"] = df_risky["date"].dt.to_period("W").apply(lambda r: r.start_time)
weekly_df = df_risky.groupby(["week", "ticker"])["risk_hits_total"].sum().reset_index()

# === Alerts anzeigen
st.subheader("🚨 Active Volcano Alerts")
active_alerts = volcano_df[volcano_df["alert"].notnull()]
if active_alerts.empty:
    st.success("No active crisis alerts at the moment. 🌤️")
else:
    # === PDF Batch Download für alle Alerts
    if st.button("📁 Download All Reports as ZIP"):
        import zipfile, tempfile
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as zip_temp:
            with zipfile.ZipFile(zip_temp.name, 'w') as zf:
                for _, row in active_alerts.iterrows():
                    ticker = row["ticker"]
                    path = generate_negative_pressure_pdf(row["ticker"], volcano_df, weekly_df, date_range_str)
                    zf.write(path, arcname=path.name)
            st.success("ZIP file created.")
            st.download_button("📥 Download ZIP", open(zip_temp.name, "rb"), file_name="emotect_alert_reports.zip")

    for _, row in active_alerts.iterrows():
        name = COMPANY_INFO[row["ticker"]]["name"]
        alert_msg = row["alert"]
        st.error(f"{alert_msg} – {name} ({row['ticker']}) | Level: {row['level'].capitalize()}, Pressure: {row['pressure']}")
        if st.button(f"📄 PDF for {name} ({row['ticker']})", key=row["ticker"]):
            path = generate_negative_pressure_pdf(
                row["ticker"],
                volcano_df,
                weekly_df,
                date_range_str)
            st.success(f"Report created: {path.name}")
            with open(path, "rb") as file:
                st.download_button("📥 Download File", file, file_name=path.name, mime="application/pdf")

# === Tabelle anzeigen
st.subheader("📋 Overview: Pressure-Level per Company")
st.dataframe(volcano_df.sort_values("pressure", ascending=False), use_container_width=True)


# === Zeitreihe: Druckentwicklung pro Unternehmen ===
st.subheader("📊 Weekly Pressure Trend per Company")

# === Top 5 Ticker nach Gesamtdruck im Zeitraum
top_tickers = (
    weekly_df.groupby("ticker")["risk_hits_total"]
    .sum().sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# === Sidebar: Zeitreihenoptionen
st.sidebar.markdown("### 📊 Time Series Options")
show_all = st.sidebar.checkbox("🔘 Show all companies", value=False)
only_with_data = st.sidebar.checkbox("🔍 Only Companies with reported Pressure", value=True)
show_area_chart = st.sidebar.checkbox("📈 Show Stacked Area Chart", value=True)

if show_all:
    user_selected = sorted(weekly_df["ticker"].unique())
else:
    user_selected = st.sidebar.multiselect(
        "🔎 Choose companies for the Time Series (empty = Top 5)", 
        options=sorted(weekly_df["ticker"].unique()),
        default=top_tickers
    )

if only_with_data:
    active_tickers = weekly_df["ticker"].unique()
    user_selected = [t for t in user_selected if t in active_tickers]

# === Gefilterte Daten vorbereiten
filtered_weekly_df = weekly_df[weekly_df["ticker"].isin(user_selected)]
# === Optional: Logarithmische Skalierung
use_log = st.sidebar.checkbox("🔁 Log Y-Axis", value=False, key="log_scale_toggle")
if not filtered_weekly_df.empty:
    fig_weekly = px.line(
        filtered_weekly_df,
        x="week", y="risk_hits_total", color="ticker",
        labels={"risk_hits_total": "Pressure", "week": "Week"},
        title="📊 Weekly Crisis Pressure per Company"
    )
    fig_weekly.update_layout(
    height=500,
    yaxis_type="log" if use_log else "linear"
)
    st.plotly_chart(fig_weekly, use_container_width=True)
else:
    st.info("No data available for the selected companies in the specified time range.")

# === Optional: Stacked Area Chart für Gesamtdruck
if show_area_chart:
    st.subheader("📈 Total Pressure Development (Stacked Area Chart)")

    if not weekly_df.empty:
        fig_area = px.area(
            weekly_df,
            x="week",
            y="risk_hits_total",
            color="ticker",
            labels={"risk_hits_total": "Pressure", "week": "Week"},
            title="📈 Aggregated Weekly Risk Pressure (Stacked)"
        )
        fig_area.update_layout(height=500, legend_title="Company")
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("No aggregated data for chosen time interval.")
