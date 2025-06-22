from jinja2 import Environment, FileSystemLoader
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime
from weasyprint import HTML

def generate_emomood_pdf(export_df, date_range_str):
    # === Template-Verzeichnis festlegen ===
    template_dir = Path("templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("mood_report.html")

    # === HTML rendern ===
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

    # === Temporäre PDF-Datei erstellen und HTML dort reinschreiben ===
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf_path = Path(tmpfile.name)
        HTML(string=html_out, base_url=str(template_dir.resolve())).write_pdf(str(pdf_path))
        return pdf_path
