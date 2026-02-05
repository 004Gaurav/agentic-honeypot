import requests
import time
import json

# ---------------- CONFIG ----------------
URL = "http://127.0.0.1:8000/honeypot/chat"

HEADERS = {
    "x-api-key": "hackathon-secret",
    "Content-Type": "application/json"
}

session_id = "e2e-session-001"

# Scam conversation simulation
messages = [
    "Your SBI account has been blocked. Verify now.",
    "Send OTP immediately to restore access.",
    "Transfer ₹1000 to secure account scam@upi",
    "Click http://fakebank.link to update KYC",
    "Share account 123456789012 for refund"
]

history = []

print("\n==============================")
print("STARTING E2E TEST")
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

    print(f"\n--- Message {i+1} ---")
    print("Status Code:", r.status_code)

    try:
        data = r.json()
        print(json.dumps(data, indent=2))

        # ---------- VALIDATIONS ----------
        assert r.status_code == 200
        assert "reply" in data
        assert "scamDetected" in data
        assert "engagementMetrics" in data
        assert "extractedIntelligence" in data

        print("Response structure valid")

        # Save to history
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
        print(" ERROR:", e)

print("\n==============================")
print("E2E TEST COMPLETE")
print("==============================")

print("\n Check your server logs now.")
print("You should see a callback sent after 5th message.")


# Final end-to-end test script