# === context.py ===
from typing import Dict, List, Any
from pydantic import BaseModel

class TransactionContext(BaseModel):
    transaction_id: str
    data: Dict[str, Any]
    log: List[str] = []
    llm_insights: List[Dict[str, Any]] = []

    def update(self, key: str, value: Any):
        self.data[key] = value
        self.log.append(f"[update] {key} = {value}")

    def append_llm_response(self, response: Dict[str, Any]):
        self.llm_insights.append(response)
        self.log.append(f"[llm] insight added: {response.get('summary', '')}")