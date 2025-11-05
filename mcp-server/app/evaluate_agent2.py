# app/evaluate_all_agents.py

import os
import boto3
import joblib
import json
from datetime import datetime

# Import existing agent modules and schema definitions
from agents import transactionHistoryProfiler
from models.schemas import TransactionInput
from models.transaction_history import TransactionHistory



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
    # Agent 2 — Transaction History Profiler (Full Features)
    # ----------------------------------------------------------------------
    if agent_id == 2:
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
    agent_ids = [2]

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
