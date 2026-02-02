from fastapi import FastAPI, Header, HTTPException, Request, Body
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
async def honeypot_chat(
    body: dict = Body(default={}),
    x_api_key: str = Header(None, alias="x-api-key")
):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {
        "status": "success",
        "message": "Honeypot active",
        "reply": "Hello, can you explain more?",
        "risk_score": 10,
        "extracted_info": {
            "upi_id": [],
            "links": [],
            "phone_numbers": []
        }
    }
