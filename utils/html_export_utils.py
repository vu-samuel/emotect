import streamlit as st
import tempfile
import uuid
from pathlib import Path

def offer_html_download(html_out: str, filename: str = "report.html"):
    # Generate a unique temporary file name to avoid cross-page interference
    unique_suffix = uuid.uuid4().hex[:6]  # short random ID
    tmp_filename = f"{Path(filename).stem}_{unique_suffix}.html"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmpfile:
        tmpfile.write(html_out)
        tmpfile_path = tmpfile.name

    with open(tmpfile_path, "r", encoding="utf-8") as f:
        html_bytes = f.read().encode("utf-8")

    # Display download button with original filename (not the temp one)
    st.download_button(
        label="📄 Download HTML Report",
        data=html_bytes,
        file_name=filename,
        mime="text/html"
    )

    st.info("Tip: After opening in the browser, simply press **Ctrl + P** to save as a PDF.")
