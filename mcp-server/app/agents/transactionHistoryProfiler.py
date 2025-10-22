
# Agent 2: Transaction History Profiler
# app/models/transaction_history.py (AWS Dataset)
# Model: Prophet + KMeans Clustering
#
# Steps:
#
#     Forecast expected behavior
#
#     Cluster deviation
#
# Scoring: score = sigmoid(abs(actual - predicted)/threshold)
from prophet import Prophet
import pandas as pd
import numpy as np
from app.models.transaction_history import load_transaction_history, TransactionHistory

# 🔧 Training Function

def train_agent2():
    """
    Loads transaction history from S3 and trains Prophet model.
    Returns trained model.
    """
    df = load_transaction_history()

    # Prepare time series data
    df_ts = df[['event_timestamp', 'order_price']].copy()
    df_ts = df_ts.rename(columns={'event_timestamp': 'ds', 'order_price': 'y'})
    df_ts['ds'] = pd.to_datetime(df_ts['ds'])

    model = Prophet()
    model.fit(df_ts)
    return model

# 🔍 Evaluation Function

def evaluate_agent2(model, tx: TransactionHistory, threshold: float = 10.0):
    """
    Evaluates a single transaction using trained Prophet model.
    Returns deviation score using sigmoid.
    """
    future = pd.DataFrame({'ds': [pd.to_datetime(tx.event_timestamp)]})
    forecast = model.predict(future)
    predicted = forecast['yhat'][0]
    deviation = abs(tx.order_price - predicted)
    score = 1 / (1 + np.exp(deviation / threshold))
    return score
