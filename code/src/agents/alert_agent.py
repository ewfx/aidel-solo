# === alert_agent.py ===
from .context import TransactionContext
from src.config import CONFIG

high = CONFIG["alert_agent"]["high_risk_threshold"]
medium = CONFIG["alert_agent"]["medium_risk_threshold"]

def generate_alert(context: TransactionContext) -> dict:
    score = context.data.get("risk_score", 0)

    if "alert_level_override" in context.data:
        level = context.data["alert_level_override"]
    else:
        if score >= high:
            level = "High Risk"
        elif score >= medium:
            level = "Medium Risk"
        else:
            level = "Low Risk"

    return {"alert_level": level, "risk_score": score}
