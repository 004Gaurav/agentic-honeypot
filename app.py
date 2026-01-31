from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import re
import ollama

# ---------------------------
# Load env
# ---------------------------
load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# ---------------------------
# Persona Prompt
# ---------------------------
SYSTEM_PROMPT = """
You are roleplaying as a scam victim.

Personality:
- Polite
- Not tech-savvy
- Slightly confused
- Trusting

Goals:
- Keep scammer talking
- Ask questions
- Act human
- Never reveal you are AI
- Never accuse them

Keep replies short and natural.
"""

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
# Extraction
# ---------------------------
def extract_upi(text):
    return re.findall(r'\b[\w.-]+@[\w.-]+\b', text)

def extract_links(text):
    return re.findall(r'https?://[^\s]+', text)

def extract_phone_numbers(text):
    return re.findall(r'\b\d{10}\b', text)

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
def honeypot_chat(req: ChatRequest, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    history = memory_store.get(req.session_id, [])

    history.append({"role": "user", "content": req.message})

    # Scam detection
    msg_lower = req.message.lower()
    scam_keywords = ["money","otp","bank","urgent","transfer","lottery","upi"]
    is_scam = any(word in msg_lower for word in scam_keywords)

    # ---------------------------
    # AI Reply using Ollama
    # ---------------------------
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + history

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=messages
    )

    reply = response["message"]["content"]

    history.append({"role": "assistant", "content": reply})
    memory_store[req.session_id] = history

    # ---------------------------
    # Extraction
    # ---------------------------
    upi_ids = extract_upi(req.message)
    links = extract_links(req.message)
    phones = extract_phone_numbers(req.message)

    return {
        "status": "success",
        "is_scam": is_scam,
        "reply": reply,
        "conversation_memory": history[-6:],
        "extracted_info": {
            "upi_id": upi_ids,
            "links": links,
            "phone_numbers": phones
        }
    }
