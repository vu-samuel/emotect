import os
import tempfile
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import pandas as pd
import sys
from datetime import datetime
from weasyprint import HTML

# === Projekt-Config laden ===
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import COMPANY_INFO

# === Jinja2 Template Directory ===
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_FILE = TEMPLATE_DIR / "zscore_report.html"

def generate_zscore_pdf(ticker, df_daily, company_name=None, article_snippets=None):
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

    with tempfile.TemporaryDirectory() as tmpdir:
        zscore_plot_path = os.path.join(tmpdir, "zscore_chart.png")
        gauge_path = os.path.join(tmpdir, "gauge_chart.png")

        # === Z-Score Plot ===
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_daily["date"],
            y=df_daily["z_score"].ewm(span=3).mean(),
            mode='lines',
            name='Smoothed Z-Score',
            line=dict(color="crimson")
        ))
        fig1.add_hline(y=2, line_dash="dot", line_color="green")
        fig1.add_hline(y=-2, line_dash="dot", line_color="red")
        fig1.update_layout(title="Z-Score Over Time", xaxis_title="Date", yaxis_title="Z-Score")
        fig1.write_image(zscore_plot_path)

        # === Gauge Chart ===
        fig2 = go.Figure(go.Indicator(
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
        fig2.update_layout(height=300, title="Z-Score Gauge")
        fig2.write_image(gauge_path)

        # === Extreme Days Table ===
        extreme_df = df_daily[abs(df_daily["z_score"]) >= 2]
        extreme_table = extreme_df[["date", "sentiment_score", "z_score"]] \
            .sort_values("z_score", ascending=False).to_dict(orient="records")

        # === Render HTML ===
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        template = env.get_template(TEMPLATE_FILE.name)
        html_out = template.render(
            company_name=company_name,
            ticker=ticker,
            date_range=date_range,
            window=window,
            latest_z=latest_z,
            zscore_status=zscore_status,
            zscore_plot_path=Path(zscore_plot_path).resolve().as_uri(),
            gauge_path=Path(gauge_path).resolve().as_uri(),
            extreme_table=extreme_table,
            now=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        # === Save PDF with WeasyPrint ===
        pdf_path = os.path.join("exports", f"Zscore_Report_{ticker}_{datetime.now().date()}.pdf")
        os.makedirs("exports", exist_ok=True)

        HTML(string=html_out, base_url=str(TEMPLATE_DIR.resolve())).write_pdf(pdf_path)

        return Path(pdf_path)
