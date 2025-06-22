import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime
import matplotlib
matplotlib.use("Agg")

# === Local Imports ===
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DUMMY_FULL_SENTIMENT_FILE
from utils.reputation_report_generator import generate_reputation_html

# === ESG Keyword Definitions ===
ESG_KEYWORDS = {
    "E": ["sustainability", "emissions", "climate", "pollution", "greenwashing", "carbon"],
    "S": ["diversity", "inclusion", "human rights", "labor", "health", "equality"],
    "G": ["corruption", "bribery", "whistleblower", "audit", "compliance", "governance"]
}

# === Streamlit Page Setup ===
st.set_page_config(page_title="🧠 EMOTECT | Reputation Radar", layout="wide")
st.markdown("""
<style>
    html, body, [class*="css"] { margin: 0; padding: 0; }
    .main .block-container { padding: 0rem; max-width: 100%; }
    .stPlotlyChart { padding: 0 !important; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

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


st.markdown("## 🧠 Reputation Radar")
st.markdown("### 🔎 ESG Filter · Wordcloud · Source Analysis")

# === Sidebar ESG Filter ===
st.sidebar.markdown("### 🌿 ESG Topic Filter")
selected_esg = st.sidebar.multiselect(
    "Show only articles containing keywords from the following categories:",
    options=["E", "S", "G"],
    default=["E", "S", "G"]
)

# === Load Sentiment Data ===
df = pd.read_csv(DUMMY_FULL_SENTIMENT_FILE, parse_dates=["date"])

# === Zeitraumfilter über Sidebar ===
st.sidebar.markdown("### ⏳ Date Range Filter")
min_date = df["date"].min().date()
max_date = df["date"].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select date range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# === Select Company ===
selected_ticker = st.selectbox("Select Company", sorted(df["ticker"].unique()))

# === Anzeige der aktuell gewählten Zeitspanne ===
st.markdown(f"🗓️ **Selected Time Period:** `{start_date}` → `{end_date}`")

df_selected = df[df["ticker"] == selected_ticker].copy()

df_selected = df_selected[
    (df_selected["date"].dt.date >= start_date) & 
    (df_selected["date"].dt.date <= end_date)
]
df_selected["combined_text"] = df_selected["title"].fillna("") + " " + df_selected["description"].fillna("")

# === ESG Match Function ===
def matches_esg(text, categories):
    text = text.lower()
    for cat in categories:
        if any(keyword in text for keyword in ESG_KEYWORDS[cat]):
            return True
    return False

# === ESG Category Count Function ===
def count_esg_categories(text):
    text = text.lower()
    counts = {"E": 0, "S": 0, "G": 0}
    for cat, keywords in ESG_KEYWORDS.items():
        counts[cat] = sum(1 for k in keywords if k in text)
    return counts

# === Apply ESG Filter and Breakdown ===
df_esg_filtered = df_selected[df_selected["combined_text"].apply(lambda text: matches_esg(text, selected_esg))].copy()
df_esg_filtered[["E_count", "S_count", "G_count"]] = df_esg_filtered["combined_text"].apply(
    lambda text: pd.Series(count_esg_categories(text))
)

# === Display ESG Article Count ===
st.metric("📄 ESG-relevant Articles", len(df_esg_filtered))

# === Wordcloud ===
st.markdown("#### 🧩 Wordcloud from ESG-filtered Articles")
if not df_esg_filtered.empty:
    combined_text = " ".join(df_esg_filtered["combined_text"].astype(str))
    wordcloud = WordCloud(width=800, height=300, background_color='white').generate(combined_text)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
else:
    st.info("No ESG-relevant articles found for this company.")

# === Source Diversity ===
st.markdown("#### 📡 Source Diversity (ESG-filtered)")
if not df_esg_filtered.empty:
    source_counts = df_esg_filtered["source"].value_counts().reset_index()
    source_counts.columns = ["Source", "Count"]
    fig_sources = px.bar(source_counts, x="Source", y="Count", title="Sources of ESG-Filtered Articles")
    st.plotly_chart(fig_sources, use_container_width=True)
else:
    st.warning("No sources available for ESG-filtered articles.")

# === ESG Breakdown Bar Chart ===
st.markdown("#### 🧮 ESG Category Breakdown per Article")
if not df_esg_filtered.empty:
    breakdown_data = df_esg_filtered[["title", "E_count", "S_count", "G_count"]].copy()
    breakdown_data = breakdown_data.melt(id_vars="title", var_name="Category", value_name="Mentions")
    fig_breakdown = px.bar(
        breakdown_data,
        x="Mentions", y="title", color="Category",
        orientation="h",
        title="ESG Keyword Distribution by Article",
        labels={"title": "Article Title", "Mentions": "Keyword Hits"}
    )
    fig_breakdown.update_layout(height=600)
    st.plotly_chart(fig_breakdown, use_container_width=True)
else:
    st.info("No breakdown data to display.")

# === PDF Export ===
if st.button("📄 Export Reputation PDF"):
    with st.spinner("Generating PDF report..."):
        path = generate_reputation_html(selected_ticker, df_esg_filtered, start_date=start_date, end_date=end_date)

        st.success("PDF ready.")
        st.download_button("📥 Download PDF", open(path, "rb"), file_name=f"{selected_ticker}_reputation_report.pdf")
