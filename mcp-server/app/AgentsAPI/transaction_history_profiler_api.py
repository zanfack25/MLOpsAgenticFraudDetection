# app/AgentsAPI/transaction_history_profiler_api.py
# ------------------------------------------------------------
# Agent 2: Transaction History Profiler (Prophet + KMeans, Full Features)
# ------------------------------------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import boto3
import joblib
import os

router = APIRouter()

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
REGION = "ca-central-1"
BUCKET_NAME = os.getenv("MODEL_BUCKET", "dav-fraud-detection-models")
LOCAL_MODEL_DIR = "models"
AGENT_PREFIX = "agents/agent2/"

os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

# ------------------------------------------------------------
# S3 Client
# ------------------------------------------------------------
s3 = boto3.client("s3", region_name=REGION)

# ------------------------------------------------------------
# Full Data Model
# ------------------------------------------------------------
class TransactionHistory(BaseModel):
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
        raise RuntimeError(f"No model found for prefix {AGENT_PREFIX}")

    local_path = download_model(key)
    print(f"Loading model from {local_path}")
    model_bundle = joblib.load(local_path)
    print("Model loaded successfully.")
    return model_bundle, key

# ------------------------------------------------------------
# Load Model at Startup
# ------------------------------------------------------------
model_bundle, model_key = load_latest_model()

# ------------------------------------------------------------
# Prediction Endpoint
# ------------------------------------------------------------
@router.post("/predict")
def predict(tx: TransactionHistory):
    """
    Evaluate a transaction history record using Prophet + KMeans.
    Returns a combined anomaly/pattern score.
    """
    try:
        df = pd.DataFrame([tx.dict()])

        # Drop label column if present
        df = df.drop(columns=["is_fraud"], errors="ignore")

        # Ensure numeric conversion where possible
        df = df.apply(pd.to_numeric, errors="ignore")

        # Load model components
        prophet_model = model_bundle.get("prophet")
        clust
