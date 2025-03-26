from transformers import pipeline
from .context import TransactionContext
# from src.main import CONFIG
from src.config import CONFIG

entity_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
entity_labels = CONFIG["classification_agent"]["entity_labels"]

def classify(context: TransactionContext) -> TransactionContext:
    def classify_entity(name: str):
        result = entity_classifier(name, entity_labels)
        top_label = result['labels'][0]
        confidence = result['scores'][0]
        context.append_llm_response({
            "entity_name": name,
            "entity_label": top_label,
            "confidence": confidence,
            "summary": f"{name} classified as '{top_label}' ({confidence:.2f})"
        })
        return top_label if confidence > 0.5 else "Unknown Entity"

    context.update("sender_type", classify_entity(context.data['sender']))
    context.update("receiver_type", classify_entity(context.data['receiver']))
    return context
