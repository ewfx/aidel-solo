# === scoring_agent.py ===
from sklearn.ensemble import IsolationForest
import numpy as np
from .context import TransactionContext
from src.config import CONFIG

contamination = CONFIG["scoring_agent"]["isolation_forest_contamination"]
donation_threshold = CONFIG["scoring_agent"]["large_donation_to_ngo_threshold"]
adjusted_score = CONFIG["scoring_agent"]["adjusted_score_for_large_donation"]

model = IsolationForest(contamination=contamination, random_state=42)
model.fit(np.random.rand(100, 3))

def score(context: TransactionContext) -> TransactionContext:
    amount = context.data['amount']
    is_large = int(context.data.get('is_large_transaction', False))
    high_risk_link = int(context.data.get('linked_to_high_risk', False))

    features = np.array([[amount, is_large, high_risk_link]])
    anomaly_score = model.decision_function(features)[0]
    risk_score = abs(anomaly_score) * 100

    if is_large and context.data.get("receiver_type") == "Non-Profit Organization":
        description_lower = context.data.get("description", "").lower()

        description_llm = next(
            (insight for insight in context.llm_insights if insight.get("label") in ["normal", "regular charitable contribution"]),
            None
        )
        description_is_regular = (
            description_llm is not None and
            description_llm["confidence"] > 0.75 and
            any(term in description_lower for term in ["monthly", "regular", "routine"])
        )

        if description_is_regular and amount <= donation_threshold:
            context.update("alert_level_override", "Low Risk")
            risk_score = min(risk_score, adjusted_score)
        elif description_is_regular:
            context.update("alert_level_override", "Medium Risk")
            risk_score = min(risk_score * 2, 85)
        elif amount > donation_threshold:
            context.update("alert_level_override", "High Risk")
            risk_score = min(risk_score * 3, 100)

    context.update("risk_score", risk_score)
    context.update("final_score", risk_score)
    return context
