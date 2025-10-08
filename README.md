# Invoice Extractor — Pro v1

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://invoice-extractor-pro-v1-xxxxx.streamlit.app)

A streamlined tool to extract key fields from PDF invoices using *Python + pdfplumber + Streamlit*.  
Uploads messy invoices → extracts structured data (Invoice No, Date, Vendor, Total) → download as Excel/CSV.

---

## ✨ Features
- Extracts Invoice Number, Date, Total Amount, and Vendor  
- Works with digital PDF invoices (OCR add-on planned for scans)  
- Preview extracted data in-browser  
- Download as Excel or CSV instantly  

---

## 📸 Demo

*Before (sample invoice PDF)*  
![Before](assets/before.png)

*After (extracted structured data)*  
![After](assets/after.png)

🎥 [Watch demo video](assets/demo.mp4)

---

## 🚀 Live App
👉 [Try it here]https://invoice-extractor-pro-v1-n6bcpfasuqrgpslc3wxhqb.streamlit.app/
---

## 🛠 How to Run Locally

```bash
git clone https://github.com/zaidkhan-automation/invoice-extractor-pro-v1.git
cd invoice-extractor-pro-v1

python -m venv venv
# Windows
.\venv\Scripts\Activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
streamlit run src/app.py