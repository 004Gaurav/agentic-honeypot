import os
from dotenv import load_dotenv

load_dotenv()

# -------- SECURITY --------
API_KEY = os.getenv("API_KEY", "")

if not API_KEY:
    print("WARNING: API_KEY not set")


# -------- OPENROUTER CONFIG --------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set")

MODEL = os.getenv(
    "MODEL",
    "arcee-ai/trinity-large-preview:free"
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# -------- GUVI CALLBACK --------
GUVI_CALLBACK_URL = os.getenv(
    "GUVI_CALLBACK_URL",
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
)
