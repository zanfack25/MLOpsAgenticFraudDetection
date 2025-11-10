# app/train_agent3.py  
# Agent 4: Fraud Pattern Matcher
#
#     Model: BERT + XGBoost
#
#     Steps:
#
#         Embed metadata
#
#         Classify with XGBoost
#
#     Scoring: score = model.predict_proba(X)[1]
from transformers import BertTokenizer, BertModel
from xgboost import XGBClassifier
import torch
import numpy as np
from models.metadata_text import load_metadata_text, MetadataText
from aagents import fraudPatternMatcher

# Training Function

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

    print(" Training Agent 3: Fraud Pattern Matcher...")
    model3 = fraudPatternMatcher.train_agent3()
    model3_path = os.path.join(LOCAL_MODEL_DIR, f"agent3_{timestamp}.pkl")
    joblib.dump(model2, model3_path)
    upload_model_to_s3(model3_path, f"agents/agent3/{os.path.basename(model3_path)}")
    
    print("Agent 3 : Fraud Pattern Matcher trained and uploaded successfully.")
    time.sleep(5)  # ensure uploads complete before Pod exits

if __name__ == "__main__":
    main()
