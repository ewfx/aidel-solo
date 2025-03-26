# === enrichment_agent.py ===
from transformers import pipeline
from .context import TransactionContext

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
risk_labels = [
    "suspicious or fraudulent transaction",
    "unusually large transfer",
    "regular charitable contribution",
    "payment to shell company",
    "international wire transfer",
    "safe",
    "normal"
]

async def enrich(context: TransactionContext) -> TransactionContext:
    description = context.data.get("description", "")
    if description:
        result = classifier(description, risk_labels)
        label = result['labels'][0]
        confidence = result['scores'][0]
        context.append_llm_response({
            "label": label,
            "confidence": confidence,
            "summary": f"LLM categorized description as '{label}' with confidence {confidence:.2f}"
        })
        context.update("description_flagged", label in [
            "suspicious or fraudulent transaction",
            "unusually large transfer",
            "payment to shell company",
            "international wire transfer"
        ])
    return context
