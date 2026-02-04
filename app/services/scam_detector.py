from app.core.logging import logger
from app.utils.constants import SCAM_KEYWORDS

def detect_scam(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower()

    for word in SCAM_KEYWORDS:
        if word in text_lower:
            logger.info(f"Scam keyword detected: {word}")
            return True

    return False
