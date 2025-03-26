# === ingestion_agent.py ===
from .context import TransactionContext

def ingest(context: TransactionContext) -> TransactionContext:
    context.update("sender", context.data['sender'].strip().lower())
    context.update("receiver", context.data['receiver'].strip().lower())
    context.update("description", context.data.get("description", "").strip().lower())
    return context