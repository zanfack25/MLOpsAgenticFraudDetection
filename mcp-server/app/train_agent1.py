# app/train_agent1.py  
import os 
import time
import joblib
import boto3
import traceback
from datetime import datetime

from agents import contextAnalyzer

# S3 configuration
REGION = "ca-central-1"
BUCKET_NAME = os.getenv("MODEL_BUCKET", "dav-fraud-detection-models")
s3 = boto3.client("s3", region_name=REGION)

# Local model output directory
LOCAL_MODEL_DIR = "models"
os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

def upload_model_to_s3(local_path: str, s3_key: str):
    """Uploads a model file to S3."""
    try:
        s3.upload_file(local_path, BUCKET_NAME, s3_key)
        print(f" Uploaded {s3_key} to S3 bucket {BUCKET_NAME}.")
    except Exception as e:
        print(f" Failed to upload {local_path} to S3: {e}")
        traceback.print_exc()

def main():
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    print(" Training Agent 1: Context Analyzer...")
    model1 = contextAnalyzer.train_agent1()
    model1_path = os.path.join(LOCAL_MODEL_DIR, f"agent1_{timestamp}.pkl")
    joblib.dump(model1, model1_path)
    upload_model_to_s3(model1_path, f"agents/agent1/{os.path.basename(model1_path)}")
    
    print("Agent 1 : Context Analyzer Trained successfully -->  models trained and uploaded successfully.")
    time.sleep(5)  # ensure uploads complete before Pod exits

if __name__ == "__main__":
    main()
