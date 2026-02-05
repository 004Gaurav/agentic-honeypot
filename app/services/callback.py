import httpx
from app.core.config import GUVI_CALLBACK_URL
from app.core.logging import logger

async def send_callback(
    session_id: str,
    session_data: dict,
    agent_notes: str,
    scam_detected: bool = True
):
    """
    Sends final intelligence to GUVI
    """

    intelligence_dict = {
        "bankAccounts": list(session_data.get("bankAccounts", [])),
        "upiIds": list(session_data.get("upiIds", [])),
        "phishingLinks": list(session_data.get("phishingLinks", [])),
        "phoneNumbers": list(session_data.get("phoneNumbers", [])),
        "suspiciousKeywords": list(session_data.get("suspiciousKeywords", []))
    }
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": session_data.get("message_count", 0),
        "extractedIntelligence": intelligence_dict,
        "agentNotes": agent_notes or "Scammer used urgency and financial manipulation."
    }

    logger.info(f"[{session_id}] Sending callback payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
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
    
