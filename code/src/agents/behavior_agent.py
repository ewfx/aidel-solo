# === behavior_agent.py ===
from transformers import pipeline
from .context import TransactionContext
from src.config import CONFIG

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
labels = CONFIG["behavior_agent"]["behavior_labels"]


def analyze(context: TransactionContext) -> TransactionContext:
    description = context.data.get("description", "")
    sender = context.data.get("sender", "")
    receiver = context.data.get("receiver", "")
    amount = context.data.get("amount", 0)

    statement = f"Sender: {sender}, Receiver: {receiver}, Amount: {amount}, Description: {description}"
    result = classifier(statement, labels)

    label = result['labels'][0]
    confidence = result['scores'][0]

    context.append_llm_response({
        "label": label,
        "confidence": confidence,
        "summary": f"Behavior analysis: '{label}' with confidence {confidence:.2f}"
    })

    threshold = CONFIG["behavior_agent"]["large_transaction_threshold"]
    context.update("is_large_transaction", amount >= threshold)

    return context
