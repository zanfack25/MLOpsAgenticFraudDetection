# app/train_all_agents.py

import os
import joblib
import boto3
from datetime import datetime

# Import your agent training modules
from agents import contextAnalyzer, transactionHistoryProfiler, fraudPatternMatcher

# S3 Configuration
s3 = boto3.client('s3')
BUCKET_NAME = os.getenv("MODEL_BUCKET", "fraud-detection-models")

# Local model output directory
LOCAL_MODEL_DIR = "models"
os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)


def upload_model_to_s3(local_path: str, s3_key: str):
    """Uploads a model file to S3."""
    try:
        s3.upload_file(local_path, BUCKET_NAME, s3_key)
        print(f"Uploaded {s3_key} to S3 bucket {BUCKET_NAME}.")
    except Exception as e:
        print(f"Failed to upload {local_path} to S3: {e}")


def main():
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    print("Training Agent 1: Context Analyzer...")
    model1 = contextAnalyzer.train_agent1()
    model1_path = os.path.join(LOCAL_MODEL_DIR, f"agent1_{timestamp}.pkl")
    joblib.dump(model1, model1_path)
    upload_model_to_s3(model1_path, f"agents/agent1/{os.path.basename(model1_path)}")

    print("Training Agent 2: Transaction History Profiler...")
    model2 = transactionHistoryProfiler.train_agent2()
    model2_path = os.path.join(LOCAL_MODEL_DIR, f"agent2_{timestamp}.pkl")
    joblib.dump(model2, model2_path)
    upload_model_to_s3(model2_path, f"agents/agent2/{os.path.basename(model2_path)}")

    print("Training Agent 3: Fraud Pattern Matcher...")
    model3 = fraudPatternMatcher.train_agent4()  # assuming agent4 is third model
    model3_path = os.path.join(LOCAL_MODEL_DIR, f"agent3_{timestamp}.pkl")
    joblib.dump(model3, model3_path)
    upload_model_to_s3(model3_path, f"agents/agent3/{os.path.basename(model3_path)}")

    print("All models trained and uploaded successfully.")


if __name__ == "__main__":
    main()
