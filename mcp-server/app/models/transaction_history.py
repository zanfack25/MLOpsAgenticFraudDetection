from pydantic import BaseModel
import pandas as pd
import boto3
from io import StringIO
from urllib.parse import urlparse
import os

# Default path or environment override
LOCAL_PATH = "/app/data/transaction_history.csv"
INPUT_S3_PATH = os.getenv(
    "INPUT_S3_PATH",
    "s3://dav-fraud-detection-bucket/TransactionsHistoryLogs/transactions_context_data_logs_100k.csv"
)


class TransactionHistory(BaseModel):
    event_timestamp: str
    event_id: str
    entity_type: str
    entity_id: str
    card_bin: int
    customer_name: str
    billing_city: str
    billing_state: str
    billing_zip: str
    billing_latitude: float
    billing_longitude: float
    ip_address: str
    product_category: str
    order_price: float
    merchant: str
    is_fraud: str

def load_transaction_history():
    """Load transaction history from local or S3."""
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
