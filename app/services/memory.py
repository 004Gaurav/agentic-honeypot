import time

sessions = {}

MAX_SESSIONS = 1000
SESSION_TTL = 3600  # 1 hour


def get_session(session_id: str):

    # Cleanup if too many sessions
    if len(sessions) > MAX_SESSIONS:
        cleanup_sessions()

    if session_id not in sessions:
        sessions[session_id] = {
            "created": time.time(),
            "last_updated": time.time(),

            # engagement
            "message_count": 0,

            # intelligence storage
            "upiIds": set(),
            "phoneNumbers": set(),
            "phishingLinks": set(),
            "bankAccounts": set(),
            "suspiciousKeywords": set(),
            "history": [],
            "callback_sent": False
        }

    return sessions[session_id]


def update_session(session_id: str, extracted: dict):

    session = get_session(session_id)

    session["message_count"] += 1
    session["last_updated"] = time.time()

    # Merge intelligence
    session["upiIds"].update(extracted.get("upiIds", []))
    session["phoneNumbers"].update(extracted.get("phoneNumbers", []))
    session["phishingLinks"].update(extracted.get("phishingLinks", []))
    session["bankAccounts"].update(extracted.get("bankAccounts", []))

    return session


def mark_callback_sent(session_id: str):
    if session_id in sessions:
        sessions[session_id]["callback_sent"] = True


def cleanup_sessions():

    now = time.time()

    expired = [
        sid for sid, s in sessions.items()
        if now - s.get("last_updated", s["created"]) > SESSION_TTL
    ]

    for sid in expired:
        del sessions[sid]
