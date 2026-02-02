from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import os
import ollama

from app.persona import SYSTEM_PROMPT
from app.extractor import (
    extract_upi, extract_links, extract_phone_numbers
)
from app.risk import calculate_risk
from app.memory import get_history, save_history

router = APIRouter()

API_KEY = os.getenv("API_KEY")

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/honeypot/chat")
def honeypot_chat(req: ChatRequest, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    history = get_history(req.session_id)
    history.append({"role":"user","content":req.message})

    # AI reply
    messages = [{"role":"system","content":SYSTEM_PROMPT}] + history

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=messages
    )

    reply = response["message"]["content"]

    history.append({"role":"assistant","content":reply})
    save_history(req.session_id, history)

    # Extraction
    upi = extract_upi(req.message)
    links = extract_links(req.message)
    phones = extract_phone_numbers(req.message)

    # Risk
    risk = calculate_risk(req.message, upi, links, phones)

    return {
        "status":"success",
        "reply":reply,
        "risk_score":risk,
        "conversation_memory":history[-6:],
        "extracted_info":{
            "upi_id":upi,
            "links":links,
            "phone_numbers":phones
        }
    }
