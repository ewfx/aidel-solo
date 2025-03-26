# === main.py (FastAPI Orchestrator) ===
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import uuid4
from typing import List, Union
import traceback
from .config import CONFIG

from src.agents import (
    context as ctx,
    ingestion_agent,
    enrichment_agent,
    classification_agent,
    behavior_agent,
    network_agent,
    scoring_agent,
    alert_agent,
    report_agent
)

app = FastAPI(title="AI Fraud Detection System")

# Global exception handler clearly logging detailed exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(f"\n[Global Exception]\n{traceback_str}\n")
    return JSONResponse(
        status_code=500,
        content={"detail": f"{exc.__class__.__name__}: {str(exc)}"},
    )

class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: float
    timestamp: str
    description: str = ""

@app.post("/analyze_transactions")
async def analyze_transactions(transactions: Union[Transaction, List[Transaction]]):
    if isinstance(transactions, Transaction):
        transactions = [transactions]

    results = []

    for tx in transactions:
        transaction_id = str(uuid4())
        try:
            context = ctx.TransactionContext(transaction_id=transaction_id, data=tx.model_dump())
            context = ingestion_agent.ingest(context)
            context = await enrichment_agent.enrich(context)
            context = classification_agent.classify(context)
            context = behavior_agent.analyze(context)
            context = network_agent.analyze(context)
            context = scoring_agent.score(context)
            result = alert_agent.generate_alert(context)

            # Final score is fully managed by scoring_agent clearly
            final_score = context.data.get("final_score", context.data.get("risk_score", 0))

            report_agent.log(context, result)

            results.append({
                "transaction_id": transaction_id,
                "sender": tx.sender,
                "receiver": tx.receiver,
                "amount": tx.amount,
                "timestamp": tx.timestamp,
                "description": tx.description,
                "alert_level": result['alert_level'],
                "risk_score": result['risk_score'],
                "final_score": final_score,
                "llm_insights": context.llm_insights,
                "audit_log": context.log
            })

        except Exception as e:
            traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"\n[Exception in Transaction ID: {transaction_id}]\n{traceback_str}\n")
            raise HTTPException(status_code=500, detail=str(e))

    return {"transactions_analysis": results}
