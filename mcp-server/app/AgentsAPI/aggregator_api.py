# app/AgentsAPI/aggregator_api.py
# ------------------------------------------------------------
# Aggregator Agent: ombines risk scores outputs from Agents 1, 2, and 3 into a final risk score.
# ------------------------------------------------------------

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi import APIRouter


router = APIRouter()

# ------------------------------------------------------------
# Default Ensemble Weights
# ------------------------------------------------------------
DEFAULT_WEIGHTS = [0.4, 0.3, 0.3]

# ------------------------------------------------------------
# Request Schema
# ------------------------------------------------------------
class ScoresInput(BaseModel):
    scores: List[float] = Field(..., description="List of scores from Agents 1, 2, and 3.")
    weights: Optional[List[float]] = Field(
        None, description="Optional custom weights for the agents (must match 3 scores)."
    )

# ------------------------------------------------------------
# Test endpoint
# ------------------------------------------------------------
@router.get("/")
def aggregator():
    return {"message": "Aggregator works"}

# ------------------------------------------------------------
# Aggregation Logic
# ------------------------------------------------------------
@router.post("/aggregate")
def aggregate(input: ScoresInput):
    """
    Aggregate risk scores from Agents 1, 2, and 3 into a single weighted score.
    Supports optional custom weighting for ensemble flexibility.
    """
    scores = input.scores
    weights = input.weights if input.weights else DEFAULT_WEIGHTS

    # Validate inputs
    if len(scores) != 3:
        return {
            "error": "Expected 3 scores from agents 1, 2, and 3.",
            "received": len(scores),
            "example": {"scores": [0.8, 0.6, 0.7]}
        }

    if len(weights) != 3:
        return {
            "error": "Weights must match number of scores (3).",
            "received": len(weights),
            "example": {"weights": [0.4, 0.3, 0.3]}
        }

    # Normalize weights if they don’t sum to 1
    weight_sum = sum(weights)
    if weight_sum != 1.0:
        weights = [w / weight_sum for w in weights]

    # Compute weighted ensemble score
    final_score = sum(w * s for w, s in zip(weights, scores))

    # SHAP-style explainability (relative agent contributions)
    explanation = {
        "agent_1_contribution": weights[0] * scores[0],
        "agent_2_contribution": weights[1] * scores[1],
        "agent_3_contribution": weights[2] * scores[2],
        "weights": weights,
        "final_score": final_score
    }

    return {
        "aggregator": "Weighted Ensemble (3 Agents)",
        "inputs": {"scores": scores, "weights": weights},
        "final_score": final_score,
        "explanation": explanation
    }
