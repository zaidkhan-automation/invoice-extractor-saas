"""
app.py
Streamlit front-end for Invoice Extractor Pro v1.

Run with:
    streamlit run src/app.py
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from extractor import extract_invoice_data
import os

st.set_page_config(page_title="Invoice Extractor Pro v1", layout="centered")
st.title("📑 Invoice Extractor — Pro v1")
st.write("Upload a PDF invoice (digital PDF preferred). The app extracts basic invoice fields and lets you download results as Excel.")

uploaded = st.file_uploader("Upload invoice (PDF)", type=["pdf"])

if uploaded is not None:
    # Save uploaded file to a temporary path so pdfplumber can open it
    tmp_dir = "data"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, "tmp_invoice.pdf")
    with open(tmp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    with st.spinner("Extracting data..."):
        try:
            df = extract_invoice_data(tmp_path)
        except Exception as e:
            st.error(f"Extraction failed: {e}")
            st.stop()

    st.subheader("Extracted Data")
    st.dataframe(df)

    # Show basic stats
    st.write(f"Rows extracted: {len(df)}")

    # Download as Excel
    towrite = BytesIO()
    df.to_excel(towrite, index=False, engine="openpyxl")
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="invoice_data.xlsx">Download extracted data (Excel)</a>'
    st.markdown(href, unsafe_allow_html=True)

    # Also offer CSV
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    b64csv = base64.b64encode(csv_bytes).decode()
    href_csv = f'<a href="data:text/csv;base64,{b64csv}" download="invoice_data.csv">Download extracted data (CSV)</a>'
    st.markdown(href_csv, unsafe_allow_html=True)

    # Clean up temp file (optional)
    try:
        os.remove(tmp_path)
    except Exception:
        pass