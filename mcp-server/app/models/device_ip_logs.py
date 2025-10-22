from pydantic import BaseModel
import pandas as pd
import boto3
from io import StringIO
from urllib.parse import urlparse
import os

# Optional: Load from environment variable or fallback to default URL
INPUT_S3_PATH = os.getenv("INPUT_S3_PATH", "s3://dav-fraud-detection-bucket/ContextDataLogs/Cifer-Fraud-Detection-Dataset-AF-part-10-14.csv")

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
    """
    Load Device/IP anomaly logs from S3 bucket or public URL.
    Returns a pandas DataFrame.
    """
    parsed = urlparse(INPUT_S3_PATH)

    if parsed.scheme == "s3":
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(StringIO(obj["Body"].read().decode("utf-8")))
    elif parsed.scheme in ["http", "https"]:
        df = pd.read_csv(INPUT_S3_PATH)
    else:
        raise ValueError("Unsupported path format. Use s3:// or https://")

    return df
