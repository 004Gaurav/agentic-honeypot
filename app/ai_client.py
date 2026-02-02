import os
import ollama

AI_MODE = os.getenv("AI_MODE", "fallback")

SYSTEM_PROMPT = """
You are roleplaying as a scam victim.
Polite, confused, human-like.
"""

def get_ai_reply(history):

    # LOCAL OLLAMA MODE
    if AI_MODE == "ollama":
        try:
            response = ollama.chat(
                model="qwen2.5:3b",
                messages=[{"role":"system","content":SYSTEM_PROMPT}] + history
            )
            return response["message"]["content"]
        except:
            return "I am not very good with banking... can you explain?"

    # CLOUD FALLBACK MODE
    return "I am not very good with banking... can you explain step by step?"
