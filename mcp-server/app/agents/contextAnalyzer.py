
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
# agents/transactionAnomalyDetector.py
# ---------------------------------------------------------------------------
# Agent 1: Initiation Context Analyzer
#
# Model: Random Forest Classifier (simpler, supervised)
#
# Steps:
#     1. Load device/IP logs
#     2. Preprocess categorical features
#     3. Train Random Forest on labeled fraud
#     4. Use probability of fraud as score
# ---------------------------------------------------------------------------

from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from models.device_ip_logs import load_device_ip_logs, DeviceIPLog

def train_agent1():
    """
    Loads device/IP logs and trains a Random Forest classifier for fraud detection.
    Returns trained model.
    """
    df = load_device_ip_logs()
    
    # Features for training
    features = df[['step','type','amount','nameOrig','oldbalanceOrg','newbalanceOrig',
                   'nameDest','oldbalanceDest','newbalanceDest']]
    
    # One-hot encode categorical features
    categorical_cols = features.select_dtypes(include=["object"]).columns
    features = pd.get_dummies(features, columns=categorical_cols)
    
    # Target
    y = df['isFraud'].values
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features, y)
    
    # Save column structure for evaluation
    model.feature_names_in_ = features.columns.tolist()
    return model

def evaluate_agent1(model, tx: DeviceIPLog):
    """
    Evaluates a single transaction using trained Random Forest model.
    Returns fraud probability score.
    """
    # Convert transaction to DataFrame
    df = pd.DataFrame([{
        "step": tx.step,
        "type": tx.type,
        "amount": tx.amount,
        "nameOrig": tx.nameOrig,
        "oldbalanceOrg": tx.oldbalanceOrg,
        "newbalanceOrig": tx.newbalanceOrig,
        "nameDest": tx.nameDest,
        "oldbalanceDest": tx.oldbalanceDest,
        "newbalanceDest": tx.newbalanceDest
    }])
    
    # One-hot encode categorical features
    df_encoded = pd.get_dummies(df)
    
    # Align columns with training features
    for col in model.feature_names_in_:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[model.feature_names_in_]
    
    # Compute probability of fraud
    score = 1 - model.decision_function(df_encoded)[0]
    return float(score)
