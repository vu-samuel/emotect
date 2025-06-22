import streamlit as st
import tempfile

def offer_html_download(html_out: str, filename: str = "report.html"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmpfile:
        tmpfile.write(html_out)
        tmpfile_path = tmpfile.name

    with open(tmpfile_path, "r", encoding="utf-8") as f:
        html_bytes = f.read().encode("utf-8")

    st.download_button(
        label="📄 Download HTML Report",
        data=html_bytes,
        file_name=filename,
        mime="text/html"
    )

    st.info("Tipp: Nach dem Öffnen im Browser einfach **Strg + P** drücken und als PDF speichern.")
