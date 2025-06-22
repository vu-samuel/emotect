import streamlit as st
from PIL import Image

# === Konfiguration ===
st.set_page_config(
    page_title="EMOTECT – Emotional Risk Detection",
    layout="wide"
)

# === Farben definieren ===
PRIMARY_BLUE = "#0F4C81"
SOFT_GRAY = "#f9f9f9"

# === Logo (optional) ===
col1, col2 = st.columns([1, 12])
with col1:
    try:
        logo = Image.open("assets/emotect_logo.png")
        st.image(logo, use_container_width=True)
    except:
        st.write("")

with col2:
    st.markdown(f"<h1 style='color:{PRIMARY_BLUE}; margin-bottom:0;'>EMOTECT</h1>", unsafe_allow_html=True)
    st.caption("Emotional Risk Detection for Corporate Decision-Makers")

# === Hero Section ===
st.markdown("---")
st.markdown(f"""
<div style='background-color:{SOFT_GRAY}; padding: 20px; border-radius: 8px;'>
    <h3>🌋 From Emotion to Early Action</h3>
    <p>
        EMOTECT is an AI-powered dashboard that transforms public sentiment into actionable insights.
        Detect brewing reputational crises across DAX-listed companies before they erupt.
    </p>
</div>
""", unsafe_allow_html=True)

# === Module Übersicht ===
st.markdown("### 🔍 Core Modules")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌦️ EmoMood")
    st.markdown("""
    - Daily sentiment weather
    - Interactive visualization of sentiment data  
    - Timing insights for communication
    """)

with col2:
    st.subheader("🌋 Sentiment Volcano")
    st.markdown("""
    - Crisis pressure tracker  
    - Risk keyword monitoring  
    - Alert levels: calm → eruption
    """)

with col3:
    st.subheader("📉 EmoQuake")
    st.markdown("""
    - Emotional shock detector  
    - Z-score spike visualization  
    - Stability vs. volatility
    """)

# === Optional Module Übersicht ===
st.markdown("### 🔧 Optional Modules (coming soon)")
cols = st.columns(2)

with cols[0]:
    st.markdown("""
    - 🌿 **ESG Explorer**  
    - 📊 **Peer Comparison**  
    - 🧭 **Reputation Radar**  
    """)

with cols[1]:
    st.markdown("""
    - 📺 **Live Ticker**  
    - 📄 **Crisis Report Generator**  
    - 💡 **Sentiment Playbook**
    """)

# === Call to Action ===
st.markdown("---")
st.markdown(f"""
<div style='padding:20px; background-color:{PRIMARY_BLUE}; color:white; border-radius:6px'>
    <h3>🚀 Ready to explore EMOTECT?</h3>
    <p>Use the sidebar to navigate through modules like EmotiForecast, Volcano & EmoQuake.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("© 2025 EMOTECT. All rights reserved.")
