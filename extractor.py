"""
extractor.py
Invoice text + table extraction for Invoice Extractor Pro v1
"""

import pandas as pd
import pdfplumber
import re

def extract_invoice_data(pdf_file):
    """
    Extracts invoice details from PDF (basic fields).
    Works best on digital PDFs (not scanned images).
    """

    data = {
        "Invoice Number": None,
        "Date": None,
        "Total Amount": None,
        "Vendor": None
    }

    # Open PDF and grab text from all pages
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Regex patterns (basic, customizable)
    invoice_no = re.search(r"Invoice\s*No[:\s]*([\w-]+)", text, re.I)
    date = re.search(r"Date[:\s]*([\d/-]+)", text, re.I)
    total = re.search(r"Total\s*[:\s$]*([\d,\.]+)", text, re.I)
    vendor = re.search(r"Vendor[:\s](.)", text, re.I)

    if invoice_no: data["Invoice Number"] = invoice_no.group(1)
    if date: data["Date"] = date.group(1)
    if total: data["Total Amount"] = total.group(1)
    if vendor: data["Vendor"] = vendor.group(1)

    return pd.DataFrame([data])