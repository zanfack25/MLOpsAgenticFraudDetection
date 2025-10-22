# Agent 5: Risk Aggregator
#
#     Model: Weighted Ensemble + SHAP
#
#     Steps:
#
#         Combine scores from agent 1, 2 and 3
#
#         Explain with SHAP
#
#     Scoring: final_score = w1*s1 + w2*s2 + ...
#
#     updated and enhanced version of your Agent 5: Risk Aggregator,
#     now tailored to combine scores from the remaining three agents—
#     -Initiation Context Analyzer (Agent 1),
#     -Transaction History Profiler (Agent 2),
#     - and Destination Risk Evaluator (Agent 3).
#     It includes weighted scoring and SHAP-based explanation logic.

import shap
import numpy as np
import xgboost as xgb

# Default weights for agents 1, 2, and 3
DEFAULT_WEIGHTS = [0.4, 0.3, 0.3]

def aggregate(scores, weights=DEFAULT_WEIGHTS):
    """
    Combines scores from Agent 1, 2, and 3 using weighted ensemble.
    Returns final risk score and SHAP-style explanation.
    """
    if len(scores) != 3:
        raise ValueError("Expected 3 scores from agents 1, 2, and 3.")

    # Weighted sum
    final_score = sum(w * s for w, s in zip(weights, scores))

    # SHAP-style explanation (simulated)
    explanation = {
        "agent_1_contribution": weights[0] * scores[0],
        "agent_2_contribution": weights[1] * scores[1],
        "agent_3_contribution": weights[2] * scores[2],
        "final_score": final_score
    }

    return final_score, explanation
