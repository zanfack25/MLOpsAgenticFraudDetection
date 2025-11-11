
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

def train_agent1(sample_size: int = 10000):
    """
    Loads device/IP logs and trains a Random Forest classifier for fraud detection.
    Returns trained model.
    """
    df = load_device_ip_logs()
    
    # Downsample if dataset is larger than sample_size
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)

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
    
    # Identify missing columns
    missing_cols = [c for c in model.feature_names_in_ if c not in df_encoded.columns]
    if missing_cols:
        # Add missing columns all at once (avoids fragmentation warnings)
        df_encoded = pd.concat([df_encoded, pd.DataFrame(0, index=df_encoded.index, columns=missing_cols)], axis=1)
    
    # Reorder columns to match training features
    df_encoded = df_encoded[model.feature_names_in_]
    
    # Compute probability of fraud using Random Forest
    score = model.predict_proba(df_encoded)[0][1]
    return float(score)
