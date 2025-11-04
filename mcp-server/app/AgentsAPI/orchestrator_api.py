
# app/AgentsAPI/orchestrator_api.py
# ------------------------------------------------------------
# Fraud Detection Orchestrator: Calls all agents and aggregates
# ------------------------------------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Dict, Any, List

router = APIRouter(title="Fraud Detection Orchestrator")

# ------------------------------------------------------------
# Agent & Aggregator Endpoints (Configurable via Env)
# ------------------------------------------------------------
AGENT1_URL = os.getenv("AGENT1_URL", "http://localhost:8001/predict")
AGENT2_URL = os.getenv("AGENT2_URL", "http://localhost:8002/predict")
AGENT3_URL = os.getenv("AGENT3_URL", "http://localhost:8003/predict")
AGGREGATOR_URL = os.getenv("AGGREGATOR_URL", "http://localhost:8004/aggregate")

# ------------------------------------------------------------
# Unified Input Model
# ------------------------------------------------------------
class FraudInput(BaseModel):
    # Agent 1 fields
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

    # Agent 2 fields
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

    # Agent 3 fields
    user_agent: str
    metadata: str

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def call_agent(url: str, payload: Dict[str, Any], score_key: str, timeout: int = 20) -> float:
    """Call an agent endpoint and extract the expected score."""
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        score = resp.json().get(score_key)
        if score is None:
            raise ValueError(f"Missing expected key '{score_key}' in response from {url}")
        return float(score)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting agent at {url}: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

def call_aggregator(scores: List[float]) -> Dict[str, Any]:
    """Call aggregator service to compute final risk score."""
    try:
        resp = requests.post(AGGREGATOR_URL, json={"scores": scores}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting aggregator: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------
# Main Orchestration Endpoint
# ------------------------------------------------------------
@router.post("/fraud-check")
def fraud_check(data: FraudInput):
    """
    Orchestrates all 3 agents and aggregates their scores.
    Returns structured agent scores and a final risk score.
    """
    payload = data.dict()

    # Call agents individually
    agent1_score = call_agent(AGENT1_URL, payload, "anomaly_score")
    agent2_score = call_agent(AGENT2_URL, payload, "pattern_score")
    agent3_score = call_agent(AGENT3_URL, payload, "fraud_probability")

    # Aggregate final score
    agg_data = call_aggregator([agent1_score, agent2_score, agent3_score])

    # Return structured response
    return {
        "agent_scores": {
            "agent1_anomaly": agent1_score,
            "agent2_pattern": agent2_score,
            "agent3_metadata": agent3_score
        },
        "final_risk_score": agg_data.get("final_score"),
        "explanation": agg_data.get("explanation")
    }

  
