import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from pathlib import Path
import tempfile
from datetime import datetime

# === ESG Schlüsselwörter ===
ESG_KEYWORDS = {
    "E": ["sustainability", "emissions", "climate", "pollution", "greenwashing", "carbon"],
    "S": ["diversity", "inclusion", "human rights", "labor", "health", "equality"],
    "G": ["corruption", "bribery", "whistleblower", "audit", "compliance", "governance"]
}

def matches_esg_category(text):
    matches = []
    lower = text.lower()
    for cat, words in ESG_KEYWORDS.items():
        if any(word in lower for word in words):
            matches.append(cat)
    return matches

def generate_reputation_pdf(ticker, df_filtered, start_date, end_date):
    df_filtered["esg_tags"] = df_filtered["combined_text"].apply(matches_esg_category)

    # === Wordcloud ===
    wc_text = " ".join(df_filtered["combined_text"])
    wc = WordCloud(width=800, height=300, background_color="white").generate(wc_text)
    wordcloud_path = Path(tempfile.NamedTemporaryFile(suffix=".png", delete=False).name)
    wc.to_file(wordcloud_path)

    # === ESG Breakdown Chart ===
    esg_counts = {"E": 0, "S": 0, "G": 0}
    for tags in df_filtered["esg_tags"]:
        for tag in tags:
            esg_counts[tag] += 1

    esg_chart_path = Path(tempfile.NamedTemporaryFile(suffix=".png", delete=False).name)
    plt.figure(figsize=(5, 3))
    plt.bar(esg_counts.keys(), esg_counts.values(), color=["green", "blue", "orange"])
    plt.title("ESG Breakdown")
    plt.ylabel("Mentions")
    plt.tight_layout()
    plt.savefig(esg_chart_path)
    plt.close()

    # === Source Table ===
    sources = []
    if "source" in df_filtered.columns:
        sources_df = df_filtered["source"].dropna().value_counts().reset_index()
        sources_df.columns = ["Source", "Count"]
        sources = sources_df.to_dict(orient="records")

    # === Jinja2 Template Rendering ===
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("reputation_report_template.html")

    html_out = template.render(
        company=ticker,
        wordcloud_path=wordcloud_path.resolve().as_uri(),
        esg_chart_path=esg_chart_path.resolve().as_uri(),
        sources=sources,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        generated_on=datetime.now().strftime("%Y-%m-%d %H:%M"),
        logo_path=Path("assets/emotect_logo.png").resolve().as_uri()
    )

    # === PDF File Name with Dates ===
    pdf_filename = f"{ticker}_Reputation_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    pdf_path = Path(tempfile.gettempdir()) / pdf_filename

    # === Export via WeasyPrint ===
    HTML(string=html_out, base_url=str(template_dir.resolve())).write_pdf(str(pdf_path))

    return pdf_path
