
# app/AgentsAPI/orchestrator_api.py
# ------------------------------------------------------------
# Fraud Detection Orchestrator: Calls all agents and aggregates
# ------------------------------------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Dict, Any, List

router = APIRouter(prefix="/orchestrator", tags=["Fraud Detection Orchestrator"])

# ------------------------------------------------------------
# Agent & Aggregator Endpoints (Configurable via Env)
# ------------------------------------------------------------

AGENT1_URL = os.getenv("AGENT1_URL", "http://localhost:8001/context-analyser/predict")
AGENT2_URL = os.getenv("AGENT2_URL", "http://localhost:8002/transaction-history/predict")
AGENT3_URL = os.getenv("AGENT3_URL", "http://localhost:8003/fraud-matcher/predict")
AGGREGATOR_URL = os.getenv("AGGREGATOR_URL", "http://localhost:8004/aggregator/aggregate")

class FraudInput(BaseModel):
    # all shared fields (see your version)
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int
    isFlaggedFraud: int
    event_timestamp: str
    event_id: str
    entity_type: str
    entity_id: str
    card_bin: int
    customer_name: str
    billing_city: str
    billing_state: str
    billing_zip: str
    billing_latitude: float
    billing_longitude: float
    ip_address: str
    product_category: str
    order_price: float
    merchant: str
    is_fraud: str
    user_agent: str
    metadata: str

def call_agent(url: str, payload: Dict[str, Any], key: str) -> float:
    try:
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return float(data.get(key, 0.0))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling {url}: {e}")

def call_aggregator(scores: List[float]) -> Dict[str, Any]:
    resp = requests.post(AGGREGATOR_URL, json={"scores": scores})
    resp.raise_for_status()
    return resp.json()

@router.post("/fraud-check")
def fraud_check(data: FraudInput):
    payload = data.dict()

    a1 = call_agent(AGENT1_URL, payload, "anomaly_score")
    a2 = call_agent(AGENT2_URL, payload, "pattern_score")
    a3 = call_agent(AGENT3_URL, payload, "fraud_probability")

    agg = call_aggregator([a1, a2, a3])

    return {
        "agent_scores": {"agent1": a1, "agent2": a2, "agent3": a3},
        "final_risk_score": agg.get("final_score"),
        "explanation": agg.get("explanation"),
    }
    
@router.get("/status")
async def orchestrator_status():
    return {"status": "orchestrator active"}