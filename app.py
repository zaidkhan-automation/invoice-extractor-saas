# streamlit_app.py — Invoice Extractor SaaS (demo + unlock CTA)
# -------------------------------------------------------------
# Features:
# - Daily free limit (session-based) + banner
# - Editable-amount Razorpay unlock CTA
# - PDF size guard
# - Optional OCR flag
# - Calls FastAPI backend: POST {API_BASE}{INVOICE_ENDPOINT}
# - Smart response handling (JSON pretty + download, or file bytes download)

import os
import io
import json
import datetime as dt
import requests
import streamlit as st

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Invoice Extractor SaaS", page_icon="📄", layout="centered")

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
INVOICE_ENDPOINT = os.getenv("INVOICE_ENDPOINT", "/extract")  # e.g. "/extract" or "/invoices/extract"
FREE_LIMIT_PER_DAY = int(os.getenv("FREE_LIMIT_PER_DAY", "3"))
RAZORPAY_LINK = os.getenv("RAZORPAY_LINK", "https://razorpay.me/@taskmindai")  # editable amount
CONTACT_MAILTO = os.getenv(
    "CONTACT_MAILTO",
    "mailto:contact@taskmindai.net?subject=TaskMindAI%20Invoice%20Extractor%20Access"
)
MAX_MB = float(os.getenv("DEMO_MAX_MB", "8"))  # demo PDF cap (MB)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))

# ------------------- DEMO LIMIT (BANNER) -------------------
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "last_reset" not in st.session_state:
    st.session_state.last_reset = dt.date.today()

# daily reset
if st.session_state.last_reset != dt.date.today():
    st.session_state.usage_count = 0
    st.session_state.last_reset = dt.date.today()

st.markdown(
    f"""
    <div style="background:#111a3a;border:1px solid #223060;padding:10px 12px;border-radius:10px;margin-bottom:12px;">
      ⚙ <b>Daily usage:</b> {st.session_state['usage_count']} / {FREE_LIMIT_PER_DAY} free runs.<br>
      🔓 <span style="color:#9fb7ff">Need full unlimited access?</span><br>
      <a href="{RAZORPAY_LINK}" target="_blank" style="color:#9cf;font-weight:700;">Pay to Unlock (amount editable)</a> ·
      <a href="{CONTACT_MAILTO}" style="color:#9cf;">Contact us</a>
    </div>
    """,
    unsafe_allow_html=True,
)

def check_limit_or_stop():
    """Stop processing if today's free quota is over."""
    if st.session_state.usage_count >= FREE_LIMIT_PER_DAY:
        st.error("Demo limit reached for today. Unlock full access below.")
        st.link_button("💳 Pay to Unlock (Editable Amount)", RAZORPAY_LINK, use_container_width=True)
        st.link_button("📧 Contact for custom pricing", CONTACT_MAILTO, use_container_width=True)
        st.stop()

# Optional sidebar meter
with st.sidebar:
    st.subheader("Usage")
    st.progress(min(st.session_state.usage_count / FREE_LIMIT_PER_DAY, 1.0))
    st.caption(f"{st.session_state.usage_count} of {FREE_LIMIT_PER_DAY} free runs today")
    st.caption(f"Demo PDF size cap: {MAX_MB:.0f} MB")
    st.markdown("---")
    st.caption(f"API: {API_BASE}{INVOICE_ENDPOINT}")

# ------------------- UI -------------------
st.title("📄 Invoice Extractor SaaS")
st.write("Upload a PDF invoice and get structured data instantly (JSON/CSV).")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Choose a PDF invoice", type=["pdf"], accept_multiple_files=False)
with col2:
    use_ocr = st.checkbox("Enable OCR (for scanned PDFs)", value=False,
                          help="Slightly slower. If PDF is scanned or text is not selectable, turn this on.")

# ------------------- PROCESS -------------------
if uploaded_file:
    st.success(f"File {uploaded_file.name} uploaded successfully!")
    if st.button("🔎 Extract Invoice Data", type="primary", use_container_width=True):

        # 1) check demo limit
        check_limit_or_stop()

        # 2) size guard
        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_MB:
            st.error(f"⚠ Demo limit: file must be under {MAX_MB:.0f} MB. Your file is {size_mb:.2f} MB.")
            st.stop()

        # 3) call backend
        with st.spinner("Extracting data... please wait"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"ocr": "true" if use_ocr else "false"}
                resp = requests.post(
                    f"{API_BASE}{INVOICE_ENDPOINT}",
                    files=files,
                    data=data,
                    timeout=REQUEST_TIMEOUT
                )
            except Exception as e:
                st.error(f"Backend unreachable. Check API_BASE/endpoint. Error: {e}")
                st.stop()

        # 4) handle response
        ctype = resp.headers.get("content-type", "")

        if resp.status_code == 200:
            # JSON path
            if "application/json" in ctype or resp.text.strip().startswith("{"):
                try:
                    payload = resp.json()
                except Exception:
                    # fallback: best effort parse
                    payload = json.loads(resp.text)

                st.success("✅ Extraction successful!")
                # Pretty show top-level fields (common invoice stuff if present)
                basic_keys = [
                    "invoice_number", "invoice_no", "date", "invoice_date",
                    "supplier", "vendor", "buyer", "customer",
                    "subtotal", "tax", "total", "currency"
                ]
                pretty = {k: v for k, v in payload.items() if k in basic_keys and payload.get(k) is not None}
                if pretty:
                    st.subheader("Summary")
                    st.json(pretty)

                # Line items table if present
                items = payload.get("items") or payload.get("line_items")
                if items and isinstance(items, list):
                    st.subheader("Line Items")
                    st.dataframe(items, use_container_width=True)

                # Full JSON download
                st.download_button(
                    "📥 Download JSON",
                    data=json.dumps(payload, indent=2).encode("utf-8"),
                    file_name=f"invoice_{uploaded_file.name.rsplit('.',1)[0]}.json",
                    mime="application/json",
                    use_container_width=True,
                )

                st.caption("Generated via TaskMindAI · taskmindai.net")
                st.session_state.usage_count += 1

            else:
                # assume file bytes (CSV/XLSX/ZIP)
                st.success("✅ Extraction successful! Download the structured data.")
                fname = resp.headers.get("x-filename") or f"invoice_{uploaded_file.name.rsplit('.',1)[0]}"
                # infer extension by mime
                ext = ".csv"
                if "spreadsheetml" in ctype:
                    ext = ".xlsx"
                elif "zip" in ctype:
                    ext = ".zip"
                elif "csv" in ctype:
                    ext = ".csv"

                st.download_button(
                    "📥 Download Result",
                    data=resp.content,
                    file_name=fname + ext,
                    mime=ctype or "application/octet-stream",
                    use_container_width=True,
                )
                st.caption("Generated via TaskMindAI · taskmindai.net")
                st.session_state.usage_count += 1

        else:
            # try to extract error
            msg = ""
            try:
                msg = resp.json().get("detail", "")
            except Exception:
                msg = resp.text[:500]
            st.error(f"Extraction failed (status {resp.status_code}). {msg or 'Please try another file.'}")

else:
    st.info("Please upload a PDF invoice to begin.")