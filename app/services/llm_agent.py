import httpx
from app.core.logging import logger

OLLAMA_URL = "http://localhost:11434/api/generate"

# Load persona prompt from file
SYSTEM_PROMPT = open("app/prompts/system.txt").read()


async def generate_reply(
    text: str,
    history=None,
    metadata=None
) -> str:
    """
    Generate LLM reply using conversation context
    """

    history = history or []
    metadata = metadata or {}

    # -------- BUILD HISTORY CONTEXT --------
    history_text = ""

    for h in history[-5:]:  # last 5 messages only
        sender = h.get("sender", "user")
        msg = h.get("text", "")
        history_text += f"{sender}: {msg}\n"

    # -------- METADATA CONTEXT --------
    meta_text = ""
    if metadata:
        meta_text = (
            f"Channel: {metadata.get('channel','')}, "
            f"Language: {metadata.get('language','')}, "
            f"Locale: {metadata.get('locale','')}\n"
        )

    # -------- FINAL PROMPT --------
    prompt = f"""
{SYSTEM_PROMPT}

Conversation so far:
{history_text}

Context:
{meta_text}

Stranger: {text}
You:
"""

    # -------- LLM CALL --------
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": "qwen2.5:3b",
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

        logger.info(f"Qwen reply: {reply}")

        # Safety fallback
        if reply:
            return reply

    except Exception as e:
        logger.error(f"Ollama error: {e}")

    # -------- FALLBACK --------
    return "I am a bit confused. Can you explain more?"
