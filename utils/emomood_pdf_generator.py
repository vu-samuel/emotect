from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_emomood_pdf(export_df, date_range_str):
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("mood_report.html")

    # Render HTML content
    html_out = template.render(
        date_range=date_range_str,
        avg_sentiment=export_df["sentiment"].mean() if not export_df.empty else 0.0,
        delta_sentiment=export_df["sentiment_delta"].mean() if "sentiment_delta" in export_df.columns else 0.0,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        logo_path=f"file://{Path('assets/emotect_logo.png').resolve()}",
        data=[
            {
                "ticker": row["ticker"],
                "name": row["name"],
                "sentiment": row["sentiment"],
            }
            for _, row in export_df.iterrows()
    ]
)
    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        HTML(string=html_out).write_pdf(tmpfile.name)
        return Path(tmpfile.name)
