import re
from app.core.logging import logger

# ---------- REGEX ----------
UPI_REGEX = r'\b[\w.-]+@[\w.-]+\b'
PHONE_REGEX = r'\+?\d{10,12}\b'
LINK_REGEX = r'https?://[^\s]+'
BANK_REGEX = r'\b\d{9,18}\b'


# ---------- EXTRACTORS ----------
def extract_upi(text: str):
    return re.findall(UPI_REGEX, text or "")


def extract_phone_numbers(text: str):
    return re.findall(PHONE_REGEX, text or "")


def extract_links(text: str):
    return re.findall(LINK_REGEX, text or "")


def extract_bank_accounts(text: str):
    return re.findall(BANK_REGEX, text or "")


# ---------- MAIN ----------
def extract_all(text: str):

    upi = extract_upi(text)
    phones = extract_phone_numbers(text)
    links = extract_links(text)
    banks = extract_bank_accounts(text)

    logger.info(
        f"Extracted → UPI:{upi}, Phones:{phones}, Links:{links}, Banks:{banks}"
    )

    return {
        "upiIds": upi,
        "phoneNumbers": phones,
        "phishingLinks": links,
        "bankAccounts": banks
    }
