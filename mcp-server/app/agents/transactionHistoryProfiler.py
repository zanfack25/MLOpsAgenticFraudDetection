
# Agent 2: Transaction History Profiler
# app/models/transaction_history.py (AWS Dataset)
# Model: Prophet + KMeans Clustering
# Steps:
# - Uses all available fields (numeric and encoded categorical) from the dataset.
# - Combines time-based forecasting (Prophet) with clustering (KMeans) for richer behavioral profiling.
# - Produces a fraud risk score based on deviation from expected behavior and cluster anomaly distance.
# ===========================================

from prophet import Prophet
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import joblib
import boto3, tempfile, os
from io import StringIO
from models.transaction_history import load_transaction_history, TransactionHistory


# ============================================================
#  Training Function
# ============================================================
def train_agent2(n_clusters: int = 5):
    """
    Trains the enhanced Transaction History Profiler using all fields from the dataset.
    Combines Prophet (temporal forecasting) + KMeans (behavior clustering).
    """
    print("Loading transaction history dataset...")
    df = load_transaction_history()

    # ---------------------------------
    # Step 1: Clean & preprocess
    # ---------------------------------
    df = df.copy()
    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'], errors='coerce')
    df = df.dropna(subset=['event_timestamp', 'order_price'])
    df = df.fillna('missing')

    # ---------------------------------
    # Step 2: Train Prophet model
    # ---------------------------------
    df_ts = df[['event_timestamp', 'order_price']].rename(columns={'event_timestamp': 'ds', 'order_price': 'y'})
    df_ts['ds'] = pd.to_datetime(df_ts['ds']).dt.tz_localize(None)

    print(" Training Prophet model (temporal forecasting)...")
    prophet_model = Prophet()
    prophet_model.fit(df_ts)

    # ---------------------------------
    # Step 3: Prepare features for KMeans clustering
    # ---------------------------------
    categorical_cols = [
        'entity_type', 'customer_name', 'billing_city', 'billing_state',
        'billing_zip', 'ip_address', 'product_category', 'merchant', 'is_fraud'
    ]
    numeric_cols = [
        'card_bin', 'billing_latitude', 'billing_longitude', 'order_price'
    ]

    X = df[categorical_cols + numeric_cols].copy()

    print("Building preprocessing and clustering pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
        ]
    )

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('cluster', kmeans)])
    pipeline.fit(X)

    # ---------------------------------
    # Step 4: Package trained models
    # ---------------------------------
    model_bundle = {
        "prophet": prophet_model,
        "cluster_pipeline": pipeline,
        "columns": X.columns.tolist()
    }

    print("Agent 2 model bundle created successfully.")

    return model_bundle


# ============================================================
# Evaluation Function
# ============================================================
def evaluate_agent2(model_bundle, tx: TransactionHistory, threshold: float = 10.0):
    """
    Evaluates a single transaction using:
      - Prophet forecast deviation
      - Cluster distance anomaly
    Combines both into a fraud risk score.
    """

    prophet_model = model_bundle["prophet"]
    pipeline = model_bundle["cluster_pipeline"]

    # Forecast order price expectation
    future = pd.DataFrame({'ds': [pd.to_datetime(tx.event_timestamp).tz_localize(None)]})
    forecast = prophet_model.predict(future)
    predicted = forecast['yhat'][0]
    deviation = abs(tx.order_price - predicted)

    # Compute cluster distance
    tx_df = pd.DataFrame([tx.dict()])
    tx_df = tx_df.fillna('missing')
    X_tx = tx_df[pipeline.named_steps['preprocessor'].get_feature_names_out()]
    cluster_label = pipeline.named_steps['cluster'].predict(X_tx)[0]
    cluster_center = pipeline.named_steps['cluster'].cluster_centers_[cluster_label]
    distance = np.linalg.norm(X_tx.values[0] - cluster_center)

    # Combine both anomaly indicators
    deviation_score = np.tanh(deviation / threshold)  # normalize deviation
    cluster_score = np.tanh(distance / (threshold * 10))

    # Final fraud likelihood score (bounded 0–1)
    combined_score = (deviation_score + cluster_score) / 2

    return float(combined_score)
