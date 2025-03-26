# === network_agent.py ===
import requests
import fitz  # PyMuPDF
import re
from .context import TransactionContext
from src.config import CONFIG

OFAC_PDF_URL = CONFIG["network_agent"]["ofac_pdf_url"]
ofac_names = set()

def fetch_and_parse_ofac_pdf():
    global ofac_names
    response = requests.get(OFAC_PDF_URL, timeout=20)
    response.raise_for_status()

    with fitz.open(stream=response.content, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    names = set(re.findall(r"\n([A-Z][A-Z\s\.,\-]+)\n", text))
    ofac_names = {name.strip().lower() for name in names if len(name.strip()) > 2}

fetch_and_parse_ofac_pdf()

def analyze(context: TransactionContext) -> TransactionContext:
    sender = context.data['sender'].lower()
    receiver = context.data['receiver'].lower()

    sender_flag = any(name in sender for name in ofac_names)
    receiver_flag = any(name in receiver for name in ofac_names)

    context.update("linked_to_high_risk", sender_flag or receiver_flag)
    context.log.append(f"[OFAC Check] sender '{sender}' risk: {sender_flag}, receiver '{receiver}' risk: {receiver_flag}")
    return context
