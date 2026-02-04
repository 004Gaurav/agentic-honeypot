import requests
import json
import time

URL = "http://127.0.0.1:8000/honeypot/chat"

HEADERS = {
    "x-api-key": "hackathon-secret",
    "Content-Type": "application/json"
}

session_id = "test-session-123"

messages = [
    "Your SBI account is blocked. Verify now.",
    "Send your OTP to reactivate.",
    "Pay ₹500 to unlock. UPI scam@upi",
    "Click http://fakebank.link to update KYC",
    "Share account 123456789012 for refund"
]

history = []

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
    print("Status:", r.status_code)

    try:
        data = r.json()
        print(json.dumps(data, indent=2))

        # Basic checks
        assert "reply" in data
        assert "scamDetected" in data
        assert "engagementMetrics" in data
        assert "extractedIntelligence" in data

        print("Structure OK")

        # Update history
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
