# app/evaluate_all_agents.py

import os
import boto3
import joblib
import json
from datetime import datetime

# Import existing agent modules and schema definitions
from agents import contextAnalyzer, transactionHistoryProfiler, fraudPatternMatcher
from models.schemas import TransactionInput
from models.metadata_text import MetadataText

# Initialize S3 client
s3 = boto3.client("s3")
BUCKET_NAME = os.getenv("MODEL_BUCKET", "fraud-detection-models")
LOCAL_MODEL_DIR = "models"
os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)


# ---------------------------------------------
# Utility functions
# ---------------------------------------------

def get_latest_model_key(agent_prefix):
    """Retrieve the latest model file for a given agent prefix from S3."""
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=agent_prefix)
    if "Contents" not in response:
        print(f"No models found for {agent_prefix}")
        return None
    latest = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]
    return latest["Key"]


def download_model(s3_key):
    """Download model from S3 to local directory."""
    local_path = os.path.join(LOCAL_MODEL_DIR, os.path.basename(s3_key))
    s3.download_file(BUCKET_NAME, s3_key, local_path)
    print(f"Downloaded model: {s3_key} → {local_path}")
    return local_path


def evaluate_model(agent_id, model):
    """Run evaluation for a given agent."""
    print(f"Evaluating Agent {agent_id}...")

    # Sample test data (in real-world, pull from dataset)
    sample_tx = TransactionInput(
        amount=1000.0,
        oldbalanceOrg=500.0,
        newbalanceOrig=1500.0,
        event_timestamp="2025-10-21T12:00:00",
        order_price=1000.0
    )
    sample_meta = MetadataText(
        metadata="Customer reported suspicious activity on account after midnight."
    )

    # Run evaluations based on agent
    if agent_id == 1:
        score = contextAnalyzer.evaluate_agent1(model, sample_tx)
    elif agent_id == 2:
        score = transactionHistoryProfiler.evaluate_agent2(model, sample_tx)
    elif agent_id == 4:
        score = fraudPatternMatcher.evaluate_agent4(model, sample_meta)
    else:
        print(f"Unknown agent ID {agent_id}")
        score = None

    print(f"Agent {agent_id} evaluation score: {score}")
    return score


def upload_evaluation_results(results):
    """Upload evaluation summary to S3."""
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
    agent_ids = [1, 2, 4]

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
        print(" No evaluations were completed successfully.")


if __name__ == "__main__":
    main()
