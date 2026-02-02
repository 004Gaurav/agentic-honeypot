from fastapi import FastAPI, Header, HTTPException, Request
from typing import Optional
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
    message: str
    session_id: Optional[str] = "default"

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
@app.post("/honeypot/chat")
async def honeypot_chat(request: Request, x_api_key: str = Header(None, alias="x-api-key")):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # READ RAW BODY SAFELY
    try:
        raw_body = await request.body()
        if raw_body:
            import json
            body = json.loads(raw_body)
        else:
            body = {}
    except:
        body = {}

    message = body.get("message") or body.get("text") or "Hello"
    session_id = body.get("session_id", "default")

    history = memory_store.get(session_id, [])
    history.append({"role": "user", "content": message})

    # SAFE AI reply
    try:
        reply = get_ai_reply(history)
    except:
        reply = "I am not very good with banking... can you explain?"

    history.append({"role": "assistant", "content": reply})
    memory_store[session_id] = history

    # Extraction
    upi_ids = extract_upi(message)
    links = extract_links(message)
    phones = extract_phone_numbers(message)

    # Risk
    risk_score = calculate_risk(message, upi_ids, links, phones)

    return {
        "status": "success",
        "reply": reply,
        "risk_score": risk_score,
        "extracted_info": {
            "upi_id": upi_ids,
            "links": links,
            "phone_numbers": phones
        }
    }
