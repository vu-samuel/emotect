from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import tempfile
import plotly.express as px
import pandas as pd
from utils.html_export_utils import offer_html_download
import plotly.io as pio

# === Template Setup ===
template_dir = Path(__file__).resolve().parent.parent / "templates"
template_file = "pressure_report.html"
env = Environment(loader=FileSystemLoader(str(template_dir)))
template = env.get_template(template_file)

def generate_pressure_html(ticker, volcano_df, weekly_df, date_range_str):
    company_row = volcano_df[volcano_df["ticker"] == ticker].iloc[0]
    company_name = company_row.get("name", ticker)
    pressure = int(company_row["pressure"])
    level = company_row["level"].capitalize()
    alert = company_row["alert"] or "No Alert"

    company_data = weekly_df[weekly_df["ticker"] == ticker].copy()

    if pd.api.types.is_datetime64_any_dtype(company_data["week"]):
        company_data["week"] = company_data["week"].dt.strftime("%Y-%m-%d")
    elif pd.api.types.is_period_dtype(company_data["week"]):
        company_data["week"] = company_data["week"].astype(str)

    fig = px.line(
        company_data,
        x="week",
        y="risk_hits_total",
        title="Weekly Pressure Trend",
        labels={"risk_hits_total": "Pressure", "week": "Week"},
        template="simple_white"
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))

    # Generate HTML chart instead of image
    chart_html = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)

    trend_table = company_data[["week", "risk_hits_total"]].sort_values("week", ascending=False)
    trend_rows = trend_table.to_dict(orient="records")

    context = {
        "company_name": company_name,
        "ticker": ticker,
        "date_range": date_range_str,
        "pressure": pressure,
        "level": level,
        "alert": alert,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "logo_path": Path("assets/emotect_logo.png").resolve().as_uri(),
        "chart_html": chart_html,
        "trend_table": trend_rows
    }

    html_out = template.render(**context)

    # 🔁 Use HTML Export Function
    filename = f"EMOTECT_PressureReport_{ticker}_{datetime.now().strftime('%Y%m%d')}.html"
    offer_html_download(html_out, filename=filename)

    return Path(filename)  # for ZIP or PDF fallback (optional)
