import requests
import time

URL = "http://127.0.0.1:8000/honeypot/chat"

HEADERS = {
    "x-api-key": "hackathon-secret",
    "Content-Type": "application/json"
}

session_id = "llm-test-session"

messages = [
    "Your bank account is blocked.",
    "Send OTP now to verify.",
    "Transfer money to scam@upi",
]

replies = []

for text in messages:

    body = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": int(time.time()*1000)
        },
        "conversationHistory": []
    }

    r = requests.post(URL, headers=HEADERS, json=body)
    data = r.json()

    reply = data.get("reply", "")
    replies.append(reply)

    print("\nMessage:", text)
    print("Reply:", reply)

# ---- CHECKS ----

print("\n=== LLM CHECK RESULTS ===")

unique_replies = len(set(replies))

if unique_replies > 1:
    print("✅ Replies vary → Likely LLM-generated")
else:
    print("❌ Replies identical → Possibly hardcoded")

# Context relevance check
if any("otp" in r.lower() or "bank" in r.lower() for r in replies):
    print("✅ Replies reference context → LLM likely active")
else:
    print("⚠️ Replies generic → Check LLM usage")
