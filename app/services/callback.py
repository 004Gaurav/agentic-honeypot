import httpx
from app.core.config import GUVI_CALLBACK_URL
from app.core.logging import logger


async def send_callback(
    session_id: str,
    session_data: dict,
    scam_detected: bool = True
):
    """
    Sends final intelligence to GUVI
    """

    payload = {
        "sessionId": session_id,

        # dynamic flag
        "scamDetected": scam_detected,

        "totalMessagesExchanged": session_data.get("message_count", 0),

        "extractedIntelligence": {
            "bankAccounts": list(session_data.get("bankAccounts", [])),
            "upiIds": list(session_data.get("upiIds", [])),
            "phishingLinks": list(session_data.get("phishingLinks", [])),
            "phoneNumbers": list(session_data.get("phoneNumbers", [])),
            "suspiciousKeywords": list(session_data.get("suspiciousKeywords", []))
        },

        "agentNotes": (
            "Scammer used social engineering tactics, urgency language, "
            "and attempted financial redirection."
        )
    }

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(
                GUVI_CALLBACK_URL,
                json=payload
            )

        logger.info(f"[{session_id}] Callback status: {r.status_code}")

        return 200 <= r.status_code < 300

    except httpx.TimeoutException:
        logger.error(f"[{session_id}] Callback timeout")
        return False

    except Exception as e:
        logger.error(f"[{session_id}] Callback failed: {e}")
        return False
