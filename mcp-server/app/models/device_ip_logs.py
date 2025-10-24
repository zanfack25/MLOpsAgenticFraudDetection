from pydantic import BaseModel
import pandas as pd
import boto3
from io import StringIO
from urllib.parse import urlparse
import os
# Local dataset path
LOCAL_PATH = "/app/data/device_ip_logs.csv"
INPUT_S3_PATH = os.getenv(
    "INPUT_S3_PATH",
    "s3://dav-fraud-detection-bucket/ContextDataLogs/Cifer-Fraud-Detection-Dataset-AF-part-10-14.csv"
)

class DeviceIPLog(BaseModel):
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int
    isFlaggedFraud: int

def load_device_ip_logs():
    """Load Device/IP logs from local file (preferred) or S3."""
    if os.path.exists(LOCAL_PATH):
        print(f"Loading local dataset from {LOCAL_PATH}")
        return pd.read_csv(LOCAL_PATH)

    print("Local dataset not found. Falling back to S3...")
    parsed = urlparse(INPUT_S3_PATH)
    if parsed.scheme == "s3":
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(StringIO(obj["Body"].read().decode("utf-8")))
    else:
        return pd.read_csv(INPUT_S3_PATH)
