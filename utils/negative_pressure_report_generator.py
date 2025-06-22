from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import plotly.express as px
import pandas as pd
import shutil

# === Load Jinja Template ===
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_FILE = "pressure_report.html"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
template = env.get_template(TEMPLATE_FILE)

# === Chart Helper ===
def save_pressure_chart(weekly_df, ticker, title, filename):
    company_data = weekly_df[weekly_df["ticker"] == ticker]
    # 🔧 Fix x-axis formatting
    if pd.api.types.is_datetime64_any_dtype(company_data["week"]):
        company_data["week"] = company_data["week"].dt.strftime("%Y-%m-%d")
    elif pd.api.types.is_period_dtype(company_data["week"]):
        company_data["week"] = company_data["week"].astype(str)

    fig = px.line(
        company_data,
        x="week",
        y="risk_hits_total",
        title=title,
        labels={"risk_hits_total": "Pressure", "week": "Week"},
        template="simple_white"
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    tmp_img = Path(tempfile.gettempdir()) / filename
    fig.write_image(str(tmp_img), scale=2)
    return tmp_img

# === Main Function ===
def generate_negative_pressure_pdf(ticker, volcano_df, weekly_df, date_range_str):
    """
    Generate a PDF pressure report for a given company.
    """
    # === Extract Info ===
    company_row = volcano_df[volcano_df["ticker"] == ticker].iloc[0]
    company_name = company_row.get("name", ticker)
    pressure = int(company_row["pressure"])
    level = company_row["level"].capitalize()
    alert = company_row["alert"] or "No Alert"

    # === Charts ===
    line_chart_path = save_pressure_chart(
        weekly_df, ticker,
        title="Weekly Pressure Trend",
        filename=f"{ticker}_weekly_chart.png"
    )

    # === Table Data (latest weekly breakdown)
    trend_table = weekly_df[weekly_df["ticker"] == ticker][["week", "risk_hits_total"]]
    trend_table = trend_table.sort_values("week", ascending=False)
    trend_rows = trend_table.to_dict(orient="records")

    # === Render Context
    context = {
        "company_name": company_name,
        "ticker": ticker,
        "date_range": date_range_str,
        "pressure": pressure,
        "level": level,
        "alert": alert,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "logo_path": f"file://{Path('assets/emotect_logo.png').resolve()}",
        "line_chart_path": f"file://{line_chart_path.resolve()}",
        "trend_table": trend_rows
    }

    html_out = template.render(**context)

    # === Create PDF
    # Erstelle benutzerdefinierten Dateinamen
    filename = f"EMOTECT_PressureReport_{ticker}_{date_range_str.replace(' ', '').replace(':', '-')}.pdf"
    filepath = Path(tempfile.gettempdir()) / filename

    # PDF erzeugen
    HTML(string=html_out, base_url=str(TEMPLATE_DIR)).write_pdf(str(filepath))
    return filepath
