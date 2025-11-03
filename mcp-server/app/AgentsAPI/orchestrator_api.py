# app/api/orchestrator_api.py
# ------------------------------------------------------------
# Fraud Detection Orchestrator: Calls all agents and aggregates
# ------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests
import os
from typing import Optional, Dict

app = FastAPI(title="Fraud Detection Orchestrator (Full Features)")

# ------------------------------------------------------------
# Agent & Aggregator Endpoints
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
    ip_address: str
    user_agent: str
    merchant: str
    product_category: str
    metadata: str



# ------------------------------------------------------------
# Main Orchestration Endpoint
# ------------------------------------------------------------
@app.post("/fraud-check")
def fraud_check(data: FraudInput):
    """
    Orchestrates all 3 agents:
      1. Agent 1 → Context Analyzer
      2. Agent 2 → Transaction History Profiler
      3. Agent 3 → Metadata Fraud Pattern Matcher
    Aggregates scores into a final risk score using the aggregator agent.
    """
    payload = data.dict()

    try:
        # -------------------------------
        # Call Agent 1
        # -------------------------------
        agent1_resp = requests.post(AGENT1_URL, json=payload, timeout=20)
        agent1_resp.raise_for_status()
        agent1_score = agent1_resp.json().get("anomaly_score")

        # -------------------------------
        # Call Agent 2
        # -------------------------------
        agent2_resp = requests.post(AGENT2_URL, json=payload, timeout=20)
        agent2_resp.raise_for_status()
        agent2_score = agent2_resp.json().get("pattern_score")

        # -------------------------------
        # Call Agent 3
        # -------------------------------
        agent3_resp = requests.post(AGENT3_URL, json=payload, timeout=20)
        agent3_resp.raise_for_status()
        agent3_score = agent3_resp.json().get("fraud_probability")

        # Validate agent scores
        if None in (agent1_score, agent2_score, agent3_score):
            raise HTTPException(
                status_code=500,
                detail="One or more agent responses missing expected score."
            )

        # -------------------------------
        # Call Aggregator
        # -------------------------------
        agg_payload = {"scores": [agent1_score, agent2_score, agent3_score]}
        agg_resp = requests.post(AGGREGATOR_URL, json=agg_payload, timeout=10)
        agg_resp.raise_for_status()
        agg_data = agg_resp.json()

        # -------------------------------
        # Return Structured Response
        # -------------------------------
        return {
            "agent_scores": {
                "agent1_anomaly": agent1_score,
                "agent2_pattern": agent2_score,
                "agent3_metadata": agent3_score
            },
            "final_risk_score": agg_data.get("final_score"),
            "explanation": agg_data.get("explanation")
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error contacting one or more agents: {e}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
