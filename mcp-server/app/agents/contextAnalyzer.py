
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
    # One-hot encode categorical features
    categorical_cols = features.select_dtypes(include=["object"]).columns
    features = pd.get_dummies(features, columns=categorical_cols)

    model = IsolationForest(random_state=42)
    model.fit(features)
    # Save column structure for consistent evaluation
    model.feature_names_in_ = features.columns.tolist()
    return model

# Evaluation Function

def evaluate_agent1(model, tx: DeviceIPLog):
    """
    Evaluates a single transaction using trained Isolation Forest model.
    Returns anomaly score.
    """
    # Convert the single transaction into a DataFrame
    df = pd.DataFrame([{
        "step": tx.step,
        "type": tx.type,
        "amount": tx.amount,
        "nameOrig": tx.nameOrig,
        "oldbalanceOrg": tx.oldbalanceOrg,
        "newbalanceOrig": tx.newbalanceOrig,
        "nameDest": tx.nameDest,
        "oldbalanceDest": tx.oldbalanceDest,
        "newbalanceDest": tx.newbalanceDest,
        "isFraud": tx.isFraud,
        "isFlaggedFraud": tx.isFlaggedFraud
    }])
    
    # One-hot encode same categorical features
    df_encoded = pd.get_dummies(df)
    
    # Align columns with training features
    for col in model.feature_names_in_:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[model.feature_names_in_]
    
    # Compute anomaly score
    score = 1 - model.decision_function(df_encoded)[0]
    return float(score)
