
# app/AgentsAPI/orchestrator_api.py
# ------------------------------------------------------------
# Fraud Detection Orchestrator: Calls all agents and aggregates
# ------------------------------------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Dict, Any, List

router = APIRouter()

# ------------------------------------------------------------
# Agent & Aggregator Endpoints (Configurable via Env)
# ------------------------------------------------------------
# app/AgentsAPI/orchestrator_api.py
# ------------------------------------------------------------
# Update agent & aggregator URLs to use single port routes
# ------------------------------------------------------------
AGENT1_URL = "http://localhost:80/context-analyser/predict"        # context_router
AGENT2_URL = "http://localhost:80/transaction-history/predict"     # profiler_router
AGENT3_URL = "http://localhost:80/fraud-matcher/predict"           # matcher_router
AGGREGATOR_URL = "http://localhost:80/aggregator/aggregate"        # aggregator_router

class FraudInput(BaseModel):
    # ------------------------------------------------------------
    # Agent 1: Context Analyzer (transactional details)
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Agent 2: Transaction History Profiler (customer & card context)
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Agent 3: Fraud Pattern Matcher (metadata & device info)
    # ------------------------------------------------------------
    # ip_address: str : already exist in Agent 2
    # merchant: str : already exist in Agent 2
    # product_category: str : already exist in Agent 2
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

    # -----------------------------
    # Prepare per-agent payloads
    # -----------------------------

    #  Agent 1 – Context Analyzer
    agent1_payload = {
        "step": payload["step"],
        "type": payload["type"],
        "amount": payload["amount"],
        "nameOrig": payload["nameOrig"],
        "oldbalanceOrg": payload["oldbalanceOrg"],
        "newbalanceOrig": payload["newbalanceOrig"],
        "nameDest": payload["nameDest"],
        "oldbalanceDest": payload["oldbalanceDest"],
        "newbalanceDest": payload["newbalanceDest"],
        "isFraud": payload["isFraud"],
        "isFlaggedFraud": payload["isFlaggedFraud"],
    }

    # Agent 2 – Transaction History Profiler
    agent2_payload = {
        "event_timestamp": payload["event_timestamp"],
        "event_id": payload["event_id"],
        "entity_type": payload["entity_type"],
        "entity_id": payload["entity_id"],
        "card_bin": payload["card_bin"],
        "customer_name": payload["customer_name"],
        "billing_city": payload["billing_city"],
        "billing_state": payload["billing_state"],
        "billing_zip": payload["billing_zip"],
        "billing_latitude": payload["billing_latitude"],
        "billing_longitude": payload["billing_longitude"],
        "ip_address": payload["ip_address"],
        "product_category": payload["product_category"],
        "order_price": payload["order_price"],
        "merchant": payload["merchant"],
        "is_fraud": payload["is_fraud"],
    }

    # Agent 3 – Fraud Matcher
    agent3_payload = {
        "ip_address": payload["ip_address"],
        "user_agent": payload["user_agent"],
        "merchant": payload["merchant"],
        "product_category": payload["product_category"],
        "metadata": payload["metadata"],
    }

    # -----------------------------
    # Call agents
    # -----------------------------
    a1_score = call_agent(AGENT1_URL, agent1_payload, "anomaly_score")
    a2_score = call_agent(AGENT2_URL, agent2_payload, "pattern_score")
    a3_score = call_agent(AGENT3_URL, agent3_payload, "fraud_probability")

    # -----------------------------
    # Aggregate results
    # -----------------------------
    aggregator_result = call_aggregator([a1_score, a2_score, a3_score])

    return {
        "agent_scores": {"agent1": a1_score, "agent2": a2_score, "agent3": a3_score},
        "final_risk_score": aggregator_result.get("final_score"),
        "explanation": aggregator_result.get("explanation"),
    }

    
@router.get("/status")
async def orchestrator_status():
    return {"status": "orchestrator active"}