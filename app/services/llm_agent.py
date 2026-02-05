import httpx
import os
from pathlib import Path

from app.core.logging import logger
from app.core.config import  MODEL

HF_API_KEY = os.getenv("HF_API_KEY")
HF_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

# Load system prompt
try:
    SYSTEM_PROMPT = Path("app/prompts/system.txt").read_text(encoding="utf-8")
except:
    SYSTEM_PROMPT = "You are a polite, slightly confused human."


async def generate_reply(text: str, history=None, metadata=None):

    history = history or []
    metadata = metadata or {}

    # -------- BUILD CONTEXT --------
    history_text = ""

    for h in history[-5:]:
        history_text += f"{h.get('sender')}: {h.get('text')}\n"

    prompt = f"""
{SYSTEM_PROMPT}

Conversation so far:
{history_text}

Stranger: {text}
You:
"""

    try:
        async with httpx.AsyncClient(timeout=60) as client:

            response = await client.post(
                HF_URL,
                headers={
                    "Authorization": f"Bearer {HF_API_KEY}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "temperature": 0.7,
                        "max_new_tokens": 60,
                        "return_full_text": False
                    }
                }
            )

        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            reply = data[0].get("generated_text", "").strip()

        logger.info(f"LLM reply: {reply}")

        if reply:
            return reply

    except Exception as e:
        logger.error(f"LLM error: {e}")

    return "I am not sure I understand. Can you explain?"

async def generate_agent_notes(history: list) -> str:
    """
    Generate summary notes about scammer behavior
    """

    convo = ""

    for h in history[-10:]:
        convo += f"{h.get('sender')}: {h.get('text')}\n"

    prompt = f"""
Analyze the scam conversation below.

Write 1 short sentence summarizing:
- scammer tactics
- intent
- style

Conversation:
{convo}

Summary:
"""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                HF_URL,
                headers={
                    "Authorization": f"Bearer {HF_API_KEY}"
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "temperature": 0.5,
                        "max_new_tokens": 40,
                        "return_full_text": False
                        }
                }
            )

        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            notes = data[0].get("generated_text", "").strip()

        if notes:
            return notes

    except Exception as e:
        logger.error(f"AgentNotes error: {e}")

    return "Scammer used urgency and financial manipulation."
