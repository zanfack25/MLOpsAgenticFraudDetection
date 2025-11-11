# app/AgentsAPI/context_analyser_api.py
# ------------------------------------------------------------
# Agent 1: Context Analyzer (Isolation Forest – Full Features)
#
# Uses all fields from DeviceIPLog as model input.
# Model loaded from S3 and exposed via FastAPI.
# ------------------------------------------------------------
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI
import boto3
import joblib
import tempfile
import os
import pandas as pd


router = APIRouter()

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
REGION = "ca-central-1"
BUCKET_NAME = os.getenv("MODEL_BUCKET", "dav-fraud-detection-models")
LOCAL_MODEL_DIR = "models"
AGENT_PREFIX = "agents/agent1/"

os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

# ------------------------------------------------------------
# S3 Client
# ------------------------------------------------------------
s3 = boto3.client("s3", region_name=REGION)

# ------------------------------------------------------------
# Input Schema Data Model
# ------------------------------------------------------------
class DeviceIPLog(BaseModel):
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
# Model Loader Utilities
# ------------------------------------------------------------
def get_latest_model_key(agent_prefix: str):
    """Retrieve the latest model file for a given agent prefix from S3."""
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=agent_prefix)
    if "Contents" not in response:
        print(f"No models found for prefix {agent_prefix}")
        return None
    latest = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]
    return latest["Key"]

def download_model(s3_key: str):
    """Download model from S3 to local directory."""
    local_path = os.path.join(LOCAL_MODEL_DIR, os.path.basename(s3_key))
    s3.download_file(BUCKET_NAME, s3_key, local_path)
    print(f"Downloaded model: s3://{BUCKET_NAME}/{s3_key} → {local_path}")
    return local_path

def load_latest_model():
    """Load the latest model from S3 at startup."""
    print("Searching for the latest model in S3...")
    key = get_latest_model_key(AGENT_PREFIX)
    if not key:
        raise RuntimeError(f"No model found for prefix {AGENT_PREFIX}")

    local_path = download_model(key)
    print(f"Loading model from {local_path}")
    model = joblib.load(local_path)
    print("Model loaded successfully.")
    return model, key

# ------------------------------------------------------------
# Load model on startup
# ------------------------------------------------------------
model, model_key = load_latest_model()

# ------------------------------------------------------------
# Prediction Endpoint
# ------------------------------------------------------------
@router.post("/predict")
def predict(tx: DeviceIPLog):
    """
    Evaluate a transaction log using the Isolation Forest model.
    """
    try:
        df = pd.DataFrame([tx.dict()])
        df_encoded = pd.get_dummies(df)

        # Add missing columns in batch
        missing_cols = [c for c in model.feature_names_in_ if c not in df_encoded.columns]
        if missing_cols:
            df_encoded = pd.concat(
                [df_encoded, pd.DataFrame(0, index=df_encoded.index, columns=missing_cols)], axis=1
            )
        df_encoded = df_encoded[model.feature_names_in_]

        score = model.predict_proba(df_encoded)[0][1]
        return {
            "agent_id": 1,
            "model_key": model_key,
            "model_name": "RandomForestClassifier",
            "anomaly_score": float(score),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
