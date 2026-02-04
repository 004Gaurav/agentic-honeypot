from fastapi import APIRouter, Request, Depends
from app.api.deps import verify_api_key
from app.core.logging import logger

from app.services.scam_detector import detect_scam
from app.services.extractor import extract_all
from app.services.memory import (
    cleanup_sessions,
    update_session,
    mark_callback_sent
)
from app.services.llm_agent import generate_reply
from app.services.callback import send_callback

router = APIRouter()


@router.post("/honeypot/chat")
async def honeypot_chat(
    request: Request,
    _: None = Depends(verify_api_key)
):

    # ---------------- SAFE JSON PARSE ----------------
    import json
    data = {}

    try:
        raw = await request.body()
        if raw:
            try:
                data = json.loads(raw.decode("utf-8", errors="ignore"))
            except:
                logger.warning("Invalid JSON received")
    except:
        logger.warning("Failed reading request body")

    if not isinstance(data, dict):
        data = {}

    # ---------------- INPUT PARSE ----------------
    session_id = str(data.get("sessionId", "default"))

    msg = data.get("message") or {}
    text = msg.get("text", "")

    history = data.get("conversationHistory", []) or []
    metadata = data.get("metadata", {}) or {}

    logger.info(f"[{session_id}] Incoming: {text}")

    # ---------------- SCAM DETECTION ----------------
    scam_detected = detect_scam(text)

    # ---------------- EXTRACTION ----------------
    extracted = extract_all(text)

    # ---------------- MEMORY UPDATE ----------------
    session = update_session(session_id, extracted)

    # Track suspicious keywords (spec requirement)
    KEYWORDS = ["urgent", "verify", "blocked", "suspend"]
    for k in KEYWORDS:
        if k in text.lower():
            session["suspiciousKeywords"].add(k)

    # ---------------- AI REPLY ----------------
    reply = await generate_reply(
        text=text,
        history=history,
        metadata=metadata
    )

    if not reply:
        reply = "Can you explain more?"

    # ---------------- CALLBACK LOGIC ----------------
    # Spec-perfect: send only if intelligence extracted
    if (
        scam_detected
        and session["message_count"] >= 5
        and (
            session["upiIds"]
            or session["phishingLinks"]
            or session["bankAccounts"]
        )
        and not session["callback_sent"]
    ):
        success = await send_callback(
    session_id,
    session,
    scam_detected=scam_detected
)

        if success:
            mark_callback_sent(session_id)
            logger.info(f"[{session_id}] Callback sent")

    # ---------------- CLEANUP ----------------
    cleanup_sessions()

    # ---------------- RESPONSE ----------------
    return {
        "status": "success",
        "reply": reply,

        "scamDetected": scam_detected,

        "engagementMetrics": {
            "messageCount": session["message_count"]
        },

        "extractedIntelligence": {
            "bankAccounts": list(session["bankAccounts"]),
            "upiIds": list(session["upiIds"]),
            "phoneNumbers": list(session["phoneNumbers"]),
            "phishingLinks": list(session["phishingLinks"]),
            "suspiciousKeywords": list(session["suspiciousKeywords"])
        }
    }
