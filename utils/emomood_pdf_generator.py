from jinja2 import Environment, FileSystemLoader
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime
import pdfkit

# PDFKit-Konfiguration für Streamlit Cloud (wichtig!)
config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")  # oder lokaler Pfad wie '/usr/local/bin/wkhtmltopdf'

def generate_emomood_pdf(export_df, date_range_str):
    # === Jinja2 HTML-Template laden ===
    env = Environment(loader=FileSystemLoader("templates"))
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

    # === PDF generieren ===
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdfkit.from_string(html_out, tmpfile.name, configuration=config)
        return Path(tmpfile.name)
