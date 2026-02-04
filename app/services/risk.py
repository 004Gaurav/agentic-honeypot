from app.utils.constants import SCAM_KEYWORDS


def calculate_risk(text: str) -> str:
    if not text:
        return "LOW"

    t = text.lower()
    score = 0

    for word in SCAM_KEYWORDS:
        if word in t:
            score += 10

    if score >= 40:
        return "HIGH"
    elif score >= 20:
        return "MEDIUM"
    return "LOW"
