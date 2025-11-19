# app/AgentsApi/fraud_pattern_matcher_api.py
# ------------------------------------------------------------
# Agent 3: Fraud Pattern Matcher (BERT + XGBoost, Full Features)
# ------------------------------------------------------------

from fastapi import APIRouter, HTTPException
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import BertTokenizer, BertModel
import torch
import pandas as pd
import numpy as np
import boto3
import tempfile
import joblib
import os

router = APIRouter()

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
REGION = "ca-central-1"
BUCKET_NAME = os.getenv("MODEL_BUCKET", "dav-fraud-detection-models")
LOCAL_MODEL_DIR = "models"
AGENT_PREFIX = "agents/agent3/"

os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

# ------------------------------------------------------------
# S3 Client
# ------------------------------------------------------------
s3 = boto3.client("s3", region_name=REGION)

# ------------------------------------------------------------
# Full Data Model
# ------------------------------------------------------------
class MetadataText(BaseModel):
    ip_address: str
    user_agent: str
    merchant: str
    product_category: str
    metadata: str

# ------------------------------------------------------------
# Utility Functions
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
    """Load latest model from S3 at startup."""
    print("Searching for the latest model in S3...")
    key = get_latest_model_key(AGENT_PREFIX)
    if not key:
        raise RuntimeError(f"No model found for Agent 3.")

    local_path = download_model(key)
    print(f"Loading model from {local_path}")
    model_bundle = joblib.load(local_path)
    print("Model loaded successfully.")
    return model_bundle, key

# ------------------------------------------------------------
# Load Model and BERT Components
# ------------------------------------------------------------
model_bundle, model_key = load_latest_model()
vectorizer = model_bundle["vectorizer"]
model = model_bundle["model"]

# ------------------------------------------------------------
# Prediction Endpoint
# ------------------------------------------------------------
@router.post("/predict")
def predict(tx: MetadataText):
    """
    Evaluate a metadata record using TF-IDF + Logistic Regression.
    Returns fraud probability.
    """
    try:
        # Vectorize metadata text
        X_tx = vectorizer.transform([tx.metadata])

        # Predict fraud probability
        score = float(model.predict_proba(X_tx)[0][1])

        return {
            "agent_id": 3,
            "model_key": model_key,
            "model_name": "TF-IDF + Logistic Regression",
            "fraud_probability": score
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))