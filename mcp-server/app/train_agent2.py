# app/train_all_agents.py  
import os 
import psutil
import time
import joblib
import boto3
import traceback
from datetime import datetime

from agents import transactionHistoryProfiler

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

    print(" Training Agent 2: Transaction History Profiler...")
    model2 = transactionHistoryProfiler.train_agent2()
    model2_path = os.path.join(LOCAL_MODEL_DIR, f"agent2_{timestamp}.pkl")
    joblib.dump(model2, model2_path)
    upload_model_to_s3(model2_path, f"agents/agent2/{os.path.basename(model2_path)}")

    print(f"Memory usage: {psutil.Process(os.getpid()).memory_info().rss / (1024**3):.2f} GiB")
    
    print("Agent 2 : transaction History Profiler trained and uploaded successfully.")
    time.sleep(5)  # ensure uploads complete before Pod exits

if __name__ == "__main__":
    main()
