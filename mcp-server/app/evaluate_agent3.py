# app/evaluate_agent3.py

import os
import boto3
import joblib
import json
from datetime import datetime

# Import existing agent modules and schema definitions
from agents import  fraudPatternMatcher
from models.schemas import TransactionInput
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
    # Agent 3 — Fraud Pattern Matcher (Full Metadata)
    # ----------------------------------------------------------------------
    if agent_id == 3:
        sample_meta = MetadataText(
            ip_address="172.16.5.21",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            merchant="eBay",
            product_category="Gift Cards",
            metadata="User accessed from new device, high-value purchase, late night."
        )
        score = fraudPatternMatcher.evaluate_agent3(model, sample_meta)

    else:
        print(f"Unknown agent ID: {agent_id}")
        return None

    print(f"Agent {agent_id} evaluation score: {score}")
    return score


def upload_evaluation_results(results):
    #"""Upload evaluation summary to S3."""
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    local_file = f"evaluation_results_{timestamp}.json"
    s3_key = f"evaluations/agent3/{local_file}"

    with open(local_file, "w") as f:
        json.dump(results, f, indent=4)

    s3.upload_file(local_file, BUCKET_NAME, s3_key)
    print(f"Uploaded evaluation report → s3://{BUCKET_NAME}/{s3_key}")


# ---------------------------------------------
# Main entrypoint
# ---------------------------------------------

def main():
    results = {}
    agent_ids = [3]

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
           # results[f"agent_{agent_id}"] = {"score": score, "model_key": key}
           results[f"agent_{agent_id}"] = {
                "score": float(score),
                "model_key": key
            }


    if results:
        upload_evaluation_results(results)
    else:
        print("No evaluations were completed successfully.")


if __name__ == "__main__":
    main()
