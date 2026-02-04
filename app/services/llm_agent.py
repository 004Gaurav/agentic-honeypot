import httpx
from pathlib import Path

from app.core.logging import logger
from app.core.config import OLLAMA_URL, MODEL

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
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 60
                    }
                }
            )

        data = response.json()

        reply = data.get("response", "").strip()

        logger.info(f"LLM reply: {reply}")

        if reply:
            return reply

    except Exception as e:
        logger.error(f"Ollama error: {e}")

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
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )

        data = response.json()
        notes = data.get("response", "").strip()

        if notes:
            return notes

    except Exception as e:
        logger.error(f"AgentNotes error: {e}")

    return "Scammer used urgency and financial manipulation."
