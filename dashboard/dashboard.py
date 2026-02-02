import streamlit as st
import requests
import pandas as pd

# ---------------------------
# CONFIG
# ---------------------------
API_URL = "http://127.0.0.1:8000/honeypot/chat"
API_KEY = "hackathon-secret"

st.set_page_config(
    page_title="Agentic Honeypot Dashboard",
    layout="wide"
)

# ---------------------------
# SESSION STORAGE
# ---------------------------
if "logs" not in st.session_state:
    st.session_state.logs = []

# ---------------------------
# UI HEADER
# ---------------------------
st.title("🛡️ Agentic Honeypot Dashboard")
st.caption("AI-Powered Scam Detection & Intelligence Extraction")

# ---------------------------
# METRICS
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Scams Analyzed", len(st.session_state.logs))

with col2:
    high_risk = sum(1 for log in st.session_state.logs if log["risk_score"] > 70)
    st.metric("High Risk Scams", high_risk)

st.divider()

# ---------------------------
# INPUT SECTION
# ---------------------------
st.subheader("🔍 Analyze Suspicious Message")

msg = st.text_input("Enter message:")

if st.button("Analyze") and msg:

    payload = {
        "session_id": "dashboard",
        "message": msg
    }

    headers = {
        "x-api-key": API_KEY
    }

    try:
        res = requests.post(API_URL, json=payload, headers=headers)

        if res.status_code == 200:
            data = res.json()
            st.session_state.logs.append(data)
            st.success("Analysis Complete ✅")
        else:
            st.error(f"API Error: {res.text}")

    except Exception as e:
        st.error(f"Connection Error: {e}")

st.divider()

# ---------------------------
# DASHBOARD DISPLAY
# ---------------------------
if st.session_state.logs:

    st.subheader("📊 Threat Analytics")

    df = pd.DataFrame(st.session_state.logs)

    st.bar_chart(df["risk_score"])

    st.divider()

    st.subheader("🧾 Intelligence Reports")

    # Show latest first
    for log in st.session_state.logs[::-1]:

        st.markdown("### 📌 Scam Analysis")

        # HIGH RISK ALERT
        if log["risk_score"] > 70:
            st.error("⚠️ HIGH RISK SCAM DETECTED")

        st.write("**Risk Score:**", log["risk_score"])

        st.write("**🤖 AI Reply:**")
        st.info(log["reply"])

        st.write("**💳 UPI IDs Found:**")
        st.write(log["extracted_info"]["upi_id"])

        st.write("**🔗 Links Found:**")
        st.write(log["extracted_info"]["links"])

        st.write("**📞 Phone Numbers:**")
        st.write(log["extracted_info"]["phone_numbers"])

        st.divider()

else:
    st.info("No scam analyses yet. Enter a message above.")
