from pydantic import BaseModel
import pandas as pd
import boto3
from io import StringIO
from urllib.parse import urlparse
import os

# Default path or environment override
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
    """
    Load transaction history from S3 bucket or public URL.
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
