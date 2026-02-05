import requests
import time
import json

# ---------------- CONFIG ----------------
URL = "http://127.0.0.1:8000/honeypot/chat"

HEADERS = {
    "x-api-key": "hackathon-secret",
    "Content-Type": "application/json"
}

session_id = "eval-flow-001"

# Simulated scam flow (platform-like)
messages = [
    "Your SBI account will be blocked today. Verify immediately.",
    "Send OTP to avoid suspension.",
    "Share your UPI ID to receive refund.",
    "Click http://fakebank.link to update KYC.",
    "Transfer money to safe account 123456789012."
]

history = []

print("\n==============================")
print("🏆 EVALUATION FLOW TEST")
print("==============================\n")

for i, text in enumerate(messages):

    body = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": int(time.time()*1000)
        },
        "conversationHistory": history,
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }

    r = requests.post(URL, headers=HEADERS, json=body)

    print(f"\n--- Step {i+1} ---")
    print("Incoming scam message:", text)
    print("Status:", r.status_code)

    try:
        data = r.json()
        print("Response:", json.dumps(data, indent=2))

        # -------- SPEC CHECKS --------
        assert "reply" in data
        assert "scamDetected" in data
        assert "engagementMetrics" in data
        assert "extractedIntelligence" in data

        print("Response format valid")

        if data["scamDetected"]:
            print("Scam detected → Agent active")

        if data["extractedIntelligence"]["upiIds"]:
            print("UPI extracted")

        if data["extractedIntelligence"]["phishingLinks"]:
            print("Link extracted")

        # Update history like platform
        history.append({
            "sender": "scammer",
            "text": text,
            "timestamp": int(time.time()*1000)
        })

        history.append({
            "sender": "user",
            "text": data["reply"],
            "timestamp": int(time.time()*1000)
        })

    except Exception as e:
        print("Error:", e)

print("\n==============================")
print("TEST COMPLETE")
print("==============================")

print("\n Check server logs:")
print("You should see callback sent after enough intelligence.")
