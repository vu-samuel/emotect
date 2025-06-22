from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import tempfile
import plotly.express as px
import pandas as pd
import pdfkit

# === Setup ===
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_FILE = "pressure_report.html"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
template = env.get_template(TEMPLATE_FILE)

# === Optional: pdfkit configuration (streamlit cloud: no absolute path)
config = pdfkit.configuration()  # If wkhtmltopdf is in PATH

# === Chart Helper ===
def save_pressure_chart(weekly_df, ticker, title, filename):
    company_data = weekly_df[weekly_df["ticker"] == ticker].copy()

    # Format x-axis
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

    # === Table Data ===
    trend_table = weekly_df[weekly_df["ticker"] == ticker][["week", "risk_hits_total"]]
    trend_table = trend_table.sort_values("week", ascending=False)
    trend_rows = trend_table.to_dict(orient="records")

    # === Template Context ===
    context = {
        "company_name": company_name,
        "ticker": ticker,
        "date_range": date_range_str,
        "pressure": pressure,
        "level": level,
        "alert": alert,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "logo_path": Path("assets/emotect_logo.png").resolve().as_uri(),
        "line_chart_path": line_chart_path.resolve().as_uri(),
        "trend_table": trend_rows
    }

    html_out = template.render(**context)

    # === PDF Export ===
    filename = f"EMOTECT_PressureReport_{ticker}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = Path(tempfile.gettempdir()) / filename

    pdfkit.from_string(html_out, str(filepath), configuration=config)
    return filepath
