# ui_app.py (Streamlit UI for AI Fraud Detection System)
import streamlit as st
import requests
import json
from pathlib import Path

CONFIG_PATH = Path("src/config.json")

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)

st.set_page_config(page_title="AI Fraud Detection", layout="wide")
st.title("AI Fraud & Risk Detection")

config = load_config()
st.sidebar.header("Configuration")

# Scoring Agent Settings
st.sidebar.subheader("Scoring Agent")
config['scoring_agent']['isolation_forest_contamination'] = st.sidebar.slider(
    "Isolation Forest Contamination", 0.01, 0.5, config['scoring_agent']['isolation_forest_contamination'], 0.01)
config['scoring_agent']['large_donation_to_ngo_threshold'] = st.sidebar.number_input(
    "Large Donation Threshold", 1000, 1000000, config['scoring_agent']['large_donation_to_ngo_threshold'], 5000)
config['scoring_agent']['adjusted_score_for_large_donation'] = st.sidebar.number_input(
    "Adjusted Score for Low-Risk Donations", 1, 100, config['scoring_agent']['adjusted_score_for_large_donation'], 1)

# Alert Thresholds
st.sidebar.subheader("Alert Thresholds")
config['alert_agent']['high_risk_threshold'] = st.sidebar.number_input(
    "High Risk Threshold", 50, 100, config['alert_agent']['high_risk_threshold'], 5)
config['alert_agent']['medium_risk_threshold'] = st.sidebar.number_input(
    "Medium Risk Threshold", 10, 49, config['alert_agent']['medium_risk_threshold'], 5)

# Save
if st.sidebar.button("Save Configuration"):
    save_config(config)
    st.sidebar.success("Config saved!")

st.markdown("---")
st.header("Enter Transaction(s)")

input_mode = st.radio("Select Input Type", ["Single", "Batch"])

if input_mode == "Single":
    sender = st.text_input("Sender", "John Doe")
    receiver = st.text_input("Receiver", "ABC Charity")
    amount = st.number_input("Amount ($)", value=50000.0)
    timestamp = st.text_input("Timestamp", "2024-03-27T14:30:00Z")
    description = st.text_area("Description", "Monthly charity donation")

    transactions = [{
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "timestamp": timestamp,
        "description": description
    }]
else:
    raw_json = st.text_area("Paste JSON list of transactions:")
    try:
        transactions = json.loads(raw_json)
    except Exception:
        st.error("Invalid JSON")
        transactions = []

if st.button("Run Detection") and transactions:
    with st.spinner("Analyzing..."):
        try:
            response = requests.post("http://localhost:8000/analyze_transactions", json=transactions)
            response.raise_for_status()
            results = response.json()["transactions_analysis"]

            for tx in results:
                st.subheader(f"Transaction ID: {tx['transaction_id']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"- **Sender:** {tx['sender']}")
                    st.markdown(f"- **Receiver:** {tx['receiver']}")
                    st.markdown(f"- **Amount:** ${tx['amount']}")
                    st.markdown(f"- **Time:** {tx['timestamp']}")
                    st.markdown(f"- **Description:** {tx['description']}")
                with col2:
                    st.markdown(f"- **Alert Level:** `{tx['alert_level']}`")
                    st.markdown(f"- **Risk Score:** `{tx['risk_score']:.2f}`")
                    st.markdown(f"- **Final Score:** `{tx['final_score']:.2f}`")

                with st.expander("LLM Insights"):
                    for i in tx['llm_insights']:
                        st.write(f"- {i['summary']} (Conf: {i['confidence']:.2f})")

                with st.expander("Audit Log"):
                    for log in tx['audit_log']:
                        st.text(log)

                st.markdown("---")

        except Exception as e:
            st.error(f"Error: {e}")
