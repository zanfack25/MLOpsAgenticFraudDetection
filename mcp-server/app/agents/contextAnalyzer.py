
# Agent 1: Initiation Context Analyzer
#   app/models/device_ip_logs.py (Cyfer Dataset)
#
#     Model: Isolation Forest
#
#     Steps:
#
#         Train on device/IP/time anomalies
#
#         Score new input
#
#     Scoring: score = 1 - model.decision_function(X)
from sklearn.ensemble import IsolationForest
from models.device_ip_logs import load_device_ip_logs, DeviceIPLog
import pandas as pd

# Training Function

def train_agent1():
    """
    Loads Cyfer dataset from S3 and trains Isolation Forest model.
    Returns trained model.
    """
    df = load_device_ip_logs()
    features = df[['step','type','amount','nameOrig','oldbalanceOrg','newbalanceOrig','nameDest','oldbalanceDest','newbalanceDest','isFraud','isFlaggedFraud']]
    model = IsolationForest(random_state=42)
    categorical_cols = features.select_dtypes(include=["object"]).columns
    features = pd.get_dummies(features, columns=categorical_cols)
    model.fit(features)
    return model

# Evaluation Function

def evaluate_agent1(model, tx: DeviceIPLog):
    """
    Evaluates a single transaction using trained Isolation Forest model.
    Returns anomaly score.
    """
    features = [[tx.step,tx.type,tx.amount,tx.nameOrig,tx.oldbalanceOrg,tx.newbalanceOrig,tx.nameDest,tx.oldbalanceDest,tx.newbalanceDest,tx.isFraud,tx.isFlaggedFraud]]
    score = 1 - model.decision_function(features)[0]
    return score
