import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from utils.emomood_report_generator import generate_emomood_html
from config import DUMMY_FULL_SENTIMENT_FILE, COMPANY_INFO, EMOTECT_LOGO

# === Init ===
os.makedirs("temp", exist_ok=True)

# === Farben definieren ===
PRIMARY_BLUE = "#0F4C81"
SOFT_GRAY = "#f9f9f9"

# === Streamlit Page Config ===
st.set_page_config(layout="wide", page_title="☀️ EMOTECT | Emotion Weather Map", page_icon="☀️")

st.markdown("""
<style>
    html, body, [class*="css"] { margin: 0; padding: 0; }
    .main .block-container { padding: 0rem; max-width: 100%; }
    .stPlotlyChart { padding: 0 !important; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# === Load Data ===
df = pd.read_csv(DUMMY_FULL_SENTIMENT_FILE, parse_dates=["date"])
df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")

# === Sidebar: Date Filter ===
st.sidebar.markdown("### 🗓️ Time Range")
range_options = {"Past 1 Day": 1, "Past 7 Days": 7, "Past 14 Days": 14, "Past 30 Days": 30}
selected_range = st.sidebar.selectbox("Aggregate sentiment over:", list(range_options.keys()))

use_slider = st.sidebar.checkbox("🔧 Use manual date range", value=False)

if use_slider:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    start_date, end_date = st.sidebar.slider("Date Range", min_value=min_date, max_value=max_date,
        value=(max_date - timedelta(days=range_options[selected_range]), max_date))
else:
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=range_options[selected_range])

df = df[df["date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))]
date_range_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

# === Aggregation ===
current_df = df[df["date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))]
current_avg = current_df.groupby("ticker")["sentiment_score"].mean().reset_index()
current_avg.columns = ["ticker", "sentiment"]

prev_start = pd.to_datetime(start_date) - timedelta(days=range_options[selected_range])
prev_end = pd.to_datetime(start_date) - timedelta(days=1)
prev_df = df[df["date"].between(prev_start, prev_end)]
prev_avg = prev_df.groupby("ticker")["sentiment_score"].mean().reset_index()
prev_avg.columns = ["ticker", "prev_sentiment"]

avg_sentiment = pd.merge(current_avg, prev_avg, on="ticker", how="left")
avg_sentiment["sentiment_delta"] = avg_sentiment["sentiment"] - avg_sentiment["prev_sentiment"]

location_df = pd.DataFrame([
    {"ticker": ticker, "name": info["name"], "lat": info["lat"], "lon": info["lon"]}
    for ticker, info in COMPANY_INFO.items()
    if "lat" in info and "lon" in info and "name" in info
])

map_df = pd.merge(avg_sentiment, location_df, on="ticker", how="inner")

# === Selection ===
all_tickers = sorted(map_df["ticker"].unique())
selected_tickers = st.sidebar.multiselect(
    "🏢 Select companies to highlight and report",
    options=all_tickers,
    default=[]
)

# === Mapping Logic ===
def sentiment_to_icon(score):
    if score >= 0.6: return "☀️"
    elif score >= 0.2: return "🌤️"
    elif score >= -0.2: return "☁️"
    elif score >= -0.6: return "🌧️"
    else: return "⛈️"

def sentiment_to_color(score):
    if score >= 0.6: return "#FFD700"
    elif score >= 0.2: return "#ADD8E6"
    elif score >= -0.2: return "#C0C0C0"
    elif score >= -0.6: return "#6495ED"
    else: return "#DC143C"

map_df["icon"] = map_df["sentiment"].apply(sentiment_to_icon)
map_df["color"] = map_df["sentiment"].apply(sentiment_to_color)

highlight_df = map_df[map_df["ticker"].isin(selected_tickers)] if selected_tickers else map_df

# === Header ===
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(EMOTECT_LOGO, use_container_width=True)
with col2:
    st.markdown("""
    <h1 style='margin-bottom: 0; color: #0F4C81; font-size: 32px;'>EMOTECT – Emotion Weather Forecast</h1>
    <p style='color: #666; font-size: 14px; margin-top: 4px;'>Emotional Risk Detection for Corporate Decision-Makers</p>
    """, unsafe_allow_html=True)

# === Info Box ===
avg_score = avg_sentiment["sentiment"].mean()
delta_score = avg_sentiment.get("sentiment_delta", pd.Series([0]*len(avg_sentiment))).mean()
delta_arrow = "▲" if delta_score > 0 else "▼"
delta_color = "green" if delta_score > 0 else "crimson"

st.markdown(f"""
<div style="padding: 1.5rem 2rem; background-color: #f9f9f9; border-radius: 12px;">
    <h2 style="margin-bottom: 0.5rem;">☀️ Emotion Weather Forecast</h2>
    <p style="color: #333; font-size: 16px;">🗓️ Aggregated from <code>{date_range_str}</code></p>
    <p style="color: #333; font-size: 16px;">📈 Average Sentiment: <b>{avg_score:.2f}</b>
        <span style="color: {delta_color}; font-weight: bold;">{delta_arrow} {delta_score:+.2f}</span>
    </p>
</div>
""", unsafe_allow_html=True)

# === Plot Map ===
fig = go.Figure()
fig.add_trace(go.Scattergeo(
    lon=highlight_df["lon"],
    lat=highlight_df["lat"],
    text=[f"{row['name']}<br>Sentiment: {row['sentiment']:.2f} {row['icon']}" for _, row in highlight_df.iterrows()],
    mode="markers+text",
    textposition="top center",
    marker=dict(size=18, color=highlight_df["color"], line=dict(width=0.5, color="white")),
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
    ),
    transition=dict(duration=500, easing="cubic-in-out")
)
st.plotly_chart(fig, use_container_width=True)

# === Details ===
if selected_tickers:
    st.subheader("📌 Details for Selected Companies")
    selected_data = highlight_df[["ticker", "name", "sentiment", "sentiment_delta"]].copy()
    selected_data.columns = ["Ticker", "Company", "Avg Sentiment", "Δ Sentiment"]
    selected_data["Δ Sentiment"] = selected_data["Δ Sentiment"].apply(lambda x: f"{x:+.2f}")
    selected_data["Avg Sentiment"] = selected_data["Avg Sentiment"].apply(lambda x: f"{x:.2f}")
    st.dataframe(selected_data, use_container_width=True)

# === Export ===
#st.markdown("---")
#st.markdown("### Export EmotectForecast Report")

#weather_map_path = "temp/weather_map.png"
#fig.write_image(weather_map_path, width=1000, height=800)

#if st.button("📄 Generate Report as HTML"):
#    generate_emomood_html(
#        export_df=highlight_df,
#        company="Selected Companies",
#        start_date=start_date.strftime("%Y-%m-%d"),
#        end_date=end_date.strftime("%Y-%m-%d"),
#        weather_map_path=weather_map_path)

