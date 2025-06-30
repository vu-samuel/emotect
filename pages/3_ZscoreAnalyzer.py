import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import DUMMY_FULL_SENTIMENT_FILE, DUMMY_Z_SCORE_FILE, COMPANY_INFO, EMOTECT_LOGO
from utils.zscore_report_generator import generate_zscore_report_html
from pathlib import Path

# === Page Configuration ===
st.set_page_config(layout="wide", page_title="🌋 EMOTECT | Crisis Pressure Tracker", page_icon="🌋")
st.markdown("""
<style>
    html, body, [class*="css"] { margin: 0; padding: 0; }
    .main .block-container { padding: 0rem; max-width: 100%; }
    .stPlotlyChart { padding: 0 !important; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# === Logo und Header ===
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

st.title("Emoquake – Detect Emotional Extremes")

# === Company Selection ===
company_options = {info["name"]: ticker for ticker, info in COMPANY_INFO.items()}
selected_name = st.selectbox("Select Company:", sorted(company_options.keys()))
ticker = company_options[selected_name]

# === Load Data ===
if not DUMMY_FULL_SENTIMENT_FILE.exists():
    st.error("❌ Sentiment data file not found.")
    st.stop()

df = pd.read_csv(DUMMY_FULL_SENTIMENT_FILE, parse_dates=["date"])
df = df[df["ticker"] == ticker]

# === Date Filter ===
st.sidebar.markdown("### Time Interval")
interval_options = {
    "Past 1 Day": 1,
    "Past 7 Days": 7,
    "Past 14 Days": 14,
    "Past 30 Days": 30
}
selected_days = interval_options[st.sidebar.selectbox("Aggregate data over:", list(interval_options.keys()))]

today = pd.to_datetime("today").normalize()
start_date = today - pd.Timedelta(days=selected_days)
df = df[df["date"].between(start_date, today)]

if df.empty:
    st.warning("No articles found for this company.")
    st.stop()

# === Daily Aggregation & Z-Score ===
df["date"] = pd.to_datetime(df["date"]).dt.date
df_daily = df.groupby("date").agg({"sentiment_score": "mean"}).reset_index()
df_daily["date"] = pd.to_datetime(df_daily["date"])

window = st.slider("Rolling Window Size", min_value=3, max_value=30, value=max(5, min(14, len(df_daily) // 2)))
df_daily["mean"] = df_daily["sentiment_score"].rolling(window, min_periods=3).mean()
df_daily["std"] = df_daily["sentiment_score"].rolling(window, min_periods=3).std()
df_daily["z_score"] = (df_daily["sentiment_score"] - df_daily["mean"]) / df_daily["std"]
df_daily["z_score_smooth"] = df_daily["z_score"].ewm(span=3).mean()

latest_z = df_daily["z_score"].iloc[-1]
latest_date = df_daily["date"].iloc[-1]
st.markdown(f"## Latest Z-Score: {latest_z:+.2f}")

# === Interpretation ===
if abs(latest_z) >= 2:
    st.error("Severe sentiment shock detected.")
elif abs(latest_z) >= 1:
    st.warning("Mild sentiment anomaly observed.")
else:
    st.success("Sentiment trend stable.")

# === Visual Layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Z-Score Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily["date"],
        y=df_daily["z_score_smooth"],
        name="Z-Score (Smoothed)",
        line=dict(color="crimson")
    ))
    fig.add_hline(y=2, line_dash="dot", line_color="green", annotation_text="+2 Threshold")
    fig.add_hline(y=-2, line_dash="dot", line_color="red", annotation_text="-2 Threshold")
    fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Z-Score", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(f"Z-Score for {selected_name} ({latest_date.date()})")

    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_z,
        gauge={
            'axis': {'range': [-3, 3]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [-3, -2], 'color': "red"},
                {'range': [-2, -1], 'color': "yellow"},
                {'range': [-1, 1], 'color': "green"},
                {'range': [1, 2], 'color': "yellow"},
                {'range': [2, 3], 'color': "red"},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': latest_z
            }
        }
    ))
    st.plotly_chart(gauge_fig, use_container_width=True)

# === Standortkarte ===
if "lat" in COMPANY_INFO[ticker] and "lon" in COMPANY_INFO[ticker]:
    st.subheader("Company Headquarters")
    st.map(pd.DataFrame({
        "lat": [COMPANY_INFO[ticker]["lat"]],
        "lon": [COMPANY_INFO[ticker]["lon"]]
    }))

# === Zeitraum-Box ===
date_range_str = f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
st.markdown(f"""
<div style="padding: 1.5rem 2rem; background-color: #f9f9f9; border-radius: 12px;">
    <h4 style="margin-bottom: 0.5rem;">Emotional Volatility Tracker</h4>
    <p style="color: #333; font-size: 16px;">Data range: <code>{date_range_str}</code></p>
</div>
""", unsafe_allow_html=True)

# === Extreme Sentiment Days ===
st.subheader("Extreme Sentiment Days")
threshold = st.slider("Z-Score Threshold", -5.0, 5.0, 2.0, step=0.1)
extremes = df_daily[abs(df_daily["z_score"] >= threshold)]
st.dataframe(extremes[["date", "sentiment_score", "z_score"]].sort_values("z_score", ascending=False))

'''# === Export HTML Report ===
st.markdown("---")
st.markdown("### Export Z-Score Report")
generate_zscore_report_html(ticker=ticker, df_daily=df_daily, company_name=selected_name)

# === Save Z-Score File
df_daily["ticker"] = ticker
DUMMY_Z_SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
df_daily.to_csv(DUMMY_Z_SCORE_FILE, index=False)


# 🔁 dummy update to trigger streamlit refresh'''
