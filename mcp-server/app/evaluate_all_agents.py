# app/evaluate_all_agents.py

import os
import boto3
import joblib
import json
from datetime import datetime

# Import existing agent modules and schema definitions
from agents import contextAnalyzer, transactionHistoryProfiler, fraudPatternMatcher
from models.schemas import TransactionInput
from models.device_ip_logs import DeviceIPLog
from models.transaction_history import TransactionHistory
from models.metadata_text import MetadataText


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


def evaluate_model(agent_id, model):
    # """Run evaluation for a given agent using its full data model."""
    print(f" Evaluating Agent {agent_id}...")

    # ----------------------------------------------------------------------
    # Agent 1 — Context Analyzer
    # ----------------------------------------------------------------------
    if agent_id == 1:
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

    # ----------------------------------------------------------------------
    # Agent 2 — Transaction History Profiler (Full Features)
    # ----------------------------------------------------------------------
    elif agent_id == 2:
        sample_tx = TransactionHistory(
            event_timestamp="2025-10-21T12:00:00Z",
            event_id="evt-123",
            entity_type="card",
            entity_id="ent-789",
            card_bin=543210,
            customer_name="John Doe",
            billing_city="Toronto",
            billing_state="ON",
            billing_zip="M5H 2N2",
            billing_latitude=43.6532,
            billing_longitude=-79.3832,
            ip_address="192.168.1.10",
            product_category="Electronics",
            order_price=899.99,
            merchant="Amazon",
            is_fraud="no"
        )

        # New full-feature evaluator
        score = transactionHistoryProfiler.evaluate_agent2(model, sample_tx)

    # ----------------------------------------------------------------------
    # Agent 3 — Fraud Pattern Matcher (Full Metadata)
    # ----------------------------------------------------------------------
    elif agent_id == 3:
        sample_meta = MetadataText(
            ip_address="172.16.5.21",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            merchant="eBay",
            product_category="Gift Cards",
            metadata="User accessed from new device, high-value purchase, late night."
        )
        score = fraudPatternMatcher.evaluate_agent4(model, sample_meta)

    else:
        print(f"Unknown agent ID: {agent_id}")
        return None

    print(f"Agent {agent_id} evaluation score: {score}")
    return score


def upload_evaluation_results(results):
    #"""Upload evaluation summary to S3."""
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    local_file = f"evaluation_results_{timestamp}.json"
    s3_key = f"evaluations/{local_file}"

    with open(local_file, "w") as f:
        json.dump(results, f, indent=4)

    s3.upload_file(local_file, BUCKET_NAME, s3_key)
    print(f"Uploaded evaluation report → s3://{BUCKET_NAME}/{s3_key}")


# ---------------------------------------------
# Main entrypoint
# ---------------------------------------------

def main():
    results = {}
    agent_ids = [1, 2, 3]

    for agent_id in agent_ids:
        prefix = f"agents/agent{agent_id}/"
        key = get_latest_model_key(prefix)
        if not key:
            continue

        local_model_path = download_model(key)

        try:
            model = joblib.load(local_model_path)
        except Exception as e:
            print(f"Failed to load model for agent {agent_id}: {e}")
            continue

        score = evaluate_model(agent_id, model)
        if score is not None:
            results[f"agent_{agent_id}"] = {"score": score, "model_key": key}

    if results:
        upload_evaluation_results(results)
    else:
        print("No evaluations were completed successfully.")


if __name__ == "__main__":
    main()
