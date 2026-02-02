from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import re

from app.ai_client import get_ai_reply

# ---------------------------
# Load env
# ---------------------------
load_dotenv()

app = FastAPI(title="Agentic Honeypot API")

API_KEY = os.getenv("API_KEY")

# ---------------------------
# Memory Store
# ---------------------------
memory_store = {}

# ---------------------------
# Request Model
# ---------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str

# ---------------------------
# Extraction Functions
# ---------------------------
def extract_upi(text):
    return re.findall(r'\b[\w.-]+@[\w.-]+\b', text)

def extract_links(text):
    return re.findall(r'https?://[^\s]+', text)

def extract_phone_numbers(text):
    return re.findall(r'\b\d{10}\b', text)

# ---------------------------
# Risk Scoring
# ---------------------------
def calculate_risk(msg, upi, links, phones):
    score = 0

    keywords = [
        "urgent","otp","prize",
        "lottery","bank","transfer","reward"
    ]

    for k in keywords:
        if k in msg.lower():
            score += 15

    score += len(upi) * 20
    score += len(links) * 20
    score += len(phones) * 15

    return min(score, 100)

# ---------------------------
# Health
# ---------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------
# Honeypot Chat
# ---------------------------
@app.post("/honeypot/chat")
def honeypot_chat(req: ChatRequest, x_api_key: str = Header(None, alias="x-api-key")):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    history = memory_store.get(req.session_id, [])

    history.append({"role": "user", "content": req.message})

    # Scam detection
    msg_lower = req.message.lower()
    scam_keywords = ["money","otp","bank","urgent","transfer","lottery","upi"]
    is_scam = any(word in msg_lower for word in scam_keywords)

    # ---------------------------
    # AI Reply (via ai_client)
    # ---------------------------
    reply = get_ai_reply(history)

    history.append({"role": "assistant", "content": reply})
    memory_store[req.session_id] = history

    # ---------------------------
    # Extraction
    # ---------------------------
    upi_ids = extract_upi(req.message)
    links = extract_links(req.message)
    phones = extract_phone_numbers(req.message)

    # ---------------------------
    # Risk Score
    # ---------------------------
    risk_score = calculate_risk(req.message, upi_ids, links, phones)

    # ---------------------------
    # Response
    # ---------------------------
    return {
        "status": "success",
        "is_scam": is_scam,
        "risk_score": risk_score,
        "reply": reply,
        "conversation_memory": history[-6:],
        "extracted_info": {
            "upi_id": upi_ids,
            "links": links,
            "phone_numbers": phones
        }
    }
