def calculate_risk(msg, upi, links, phones):
    score = 0

    keywords = [
        "urgent","otp","prize",
        "lottery","bank","transfer","reward"
    ]

    for k in keywords:
        if k in msg.lower():
            score += 15

    score += len(upi) * 20
    score += len(links) * 20
    score += len(phones) * 15

    return min(score, 100)
