import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------- SECURITY --------
API_KEY = os.getenv("API_KEY", "")

if not API_KEY:
    print("WARNING: API_KEY not set")


# -------- OLLAMA CONFIG --------
MODEL = os.getenv(
    "MODEL",
    "qwen2.5:1.5b"  # default safe model
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)


# -------- GUVI CALLBACK --------
GUVI_CALLBACK_URL = os.getenv(
    "GUVI_CALLBACK_URL",
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
)
