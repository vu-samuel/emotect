from jinja2 import Environment, FileSystemLoader
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime
from utils.html_export_utils import offer_html_download


def generate_emomood_html(export_df, date_range_str):
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("mood_report.html")

    html_out = template.render(
        date_range=date_range_str,
        avg_sentiment=round(export_df["sentiment"].mean(), 3) if not export_df.empty else 0.0,
        delta_sentiment=round(export_df["sentiment_delta"].mean(), 3) if "sentiment_delta" in export_df.columns else 0.0,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        logo_path=f"file://{Path('assets/emotect_logo.png').resolve()}",
        data=[
            {
                "ticker": row["ticker"],
                "name": row["name"],
                "sentiment": round(row["sentiment"], 3),
            }
            for _, row in export_df.iterrows()
        ]
    )

    offer_html_download(html_out, filename=f"Emomood_Report_{datetime.now().date()}.html")
