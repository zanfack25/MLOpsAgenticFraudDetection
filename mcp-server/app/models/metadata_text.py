
from pydantic import BaseModel
import pandas as pd
from app.models.device_ip_logs import load_device_ip_logs
from app.models.transaction_history import load_transaction_history

class MetadataText(BaseModel):
    ip_address: str
    user_agent: str
    merchant: str
    product_category: str
    metadata: str  # Composite field for embedding

def load_metadata_text():
    """
    Loads and merges metadata from device/IP logs and transaction history.
    Returns a DataFrame with enriched metadata for Agent 4.
    """
    df_device = load_device_ip_logs()
    df_tx = load_transaction_history()

    # Select relevant fields from transaction history
    df_tx_meta = df_tx[['ip_address', 'user_agent', 'merchant', 'product_category', 'is_fraud']].copy()

    # Create a composite metadata field for embedding
    df_tx_meta['metadata'] = (
        df_tx_meta['ip_address'].astype(str) + " " +
        df_tx_meta['user_agent'].astype(str) + " " +
        df_tx_meta['merchant'].astype(str) + " " +
        df_tx_meta['product_category'].astype(str)
    )

    return df_tx_meta
