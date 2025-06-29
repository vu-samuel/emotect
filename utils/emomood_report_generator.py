from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
import base64
from utils.html_export_utils import offer_html_download

# === Helper: Base64 encode images ===
def encode_image_to_base64(path):
    with open(path, "rb") as img_file:
        return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"

# === Mood label from score
def score_to_mood(score):
    if score >= 0.6: return "☀️ Sunny"
    elif score >= 0.2: return "🌤️ Mostly Positive"
    elif score >= -0.2: return "☁️ Neutral"
    elif score >= -0.6: return "🌧️ Negative"
    else: return "⛈️ Very Negative"

# === Main function for EmotiForecast report
def generate_emomood_html(
    export_df,
    company,
    start_date,
    end_date,
    weather_map_path
):
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("mood_report.html")

    logo_path = encode_image_to_base64("assets/emotect_logo.png")
    weather_map_b64 = encode_image_to_base64(weather_map_path)

    summary_table = [
        {
            "date": end_date,
            "company": row["name"],
            "mood": score_to_mood(row["sentiment"]),
            "avg_sentiment": f"{row['sentiment']:.2f}"
        }
        for row in export_df.to_dict(orient="records")
    ]

    html_out = template.render(
        company=company,
        start_date=start_date,
        end_date=end_date,
        logo_path=logo_path,
        weather_map_path=weather_map_b64,
        summary_table=summary_table,
        generated_on=datetime.now().strftime("%Y-%m-%d")
    )

    offer_html_download(html_out, filename=f"Emomood_Report_{datetime.now().date()}.html")
