# === report_agent.py ===
from .context import TransactionContext

def log(context: TransactionContext, result: dict):
    print("=== Transaction Audit ===")
    print(f"Transaction ID: {context.transaction_id}")
    print("Final Result:", result)
    print("Trace Log:")
    for entry in context.log:
        print(" -", entry)
    print("LLM Insights:")
    for insight in context.llm_insights:
        print(" -", insight.get("summary", "(no summary)"))