# app/evaluate_agent1.py

import os
import boto3
import joblib
import json
from datetime import datetime

# Import existing agent modules and schema definitions
from agents import contextAnalyzer
from models.device_ip_logs import DeviceIPLog



# Initialize S3 client
s3 = boto3.client("s3")
BUCKET_NAME = os.getenv("MODEL_BUCKET", "dav-fraud-detection-models")
LOCAL_MODEL_DIR = "models"
os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)


# ---------------------------------------------
# Utility functions
# ---------------------------------------------

def get_latest_model_key(agent_prefix):
    #"""Retrieve the latest model file for a given agent prefix from S3."""
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=agent_prefix)
    if "Contents" not in response:
        print(f"No models found for {agent_prefix}")
        return None
    latest = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]
    return latest["Key"]


def download_model(s3_key):
    #"""Download model from S3 to local directory."""
    local_path = os.path.join(LOCAL_MODEL_DIR, os.path.basename(s3_key))
    s3.download_file(BUCKET_NAME, s3_key, local_path)
    print(f"Downloaded model: {s3_key} → {local_path}")
    return local_path
def evaluate_model(model):
    """Run evaluation for Agent 1 using a sample DeviceIPLog transaction."""
    print("Evaluating Agent 1 (Context Analyzer)...")

    # Sample transaction
    sample_tx = DeviceIPLog(
        step=5,
        type="PAYMENT",
        amount=1200.50,
        nameOrig="C123456789",
        oldbalanceOrg=3000.0,
        newbalanceOrig=1800.0,
        nameDest="M987654321",
        oldbalanceDest=5000.0,
        newbalanceDest=6200.0,
        isFraud=0,
        isFlaggedFraud=0
    )

    score = contextAnalyzer.evaluate_agent1(model, sample_tx)
    print(f"Agent 1 evaluation score: {score}")
    return float(score)


def upload_evaluation_results(score, model_key):
    """Upload evaluation summary to S3."""
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    local_file = f"evaluation_results_{timestamp}.json"
    s3_key = f"evaluations/agent1/{local_file}"

    results = {"agent_1": {"score": score, "model_key": model_key}}
    with open(local_file, "w") as f:
        json.dump(results, f, indent=4)

    s3.upload_file(local_file, BUCKET_NAME, s3_key)
    print(f"Uploaded Agent 1 evaluation report → s3://{BUCKET_NAME}/{s3_key}")

# ---------------------------------------------
# Main entrypoint
# ---------------------------------------------

def main():
    agent_prefix = "agents/agent1/"
    key = get_latest_model_key(agent_prefix)
    if not key:
        print("No Agent 1 models found in S3.")
        return

    local_model_path = download_model(key)

    try:
        model = joblib.load(local_model_path)
    except Exception as e:
        print(f"Failed to load Agent 1 model: {e}")
        return

    score = evaluate_model(model)
    upload_evaluation_results(score, key)




if __name__ == "__main__":
    main()
