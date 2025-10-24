
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
from models.transaction_history import load_transaction_history, TransactionHistory

# 🔧 Training Function
def train_agent2():
    df = load_transaction_history()
    df_ts = df[['event_timestamp', 'order_price']].copy()
    df_ts = df_ts.rename(columns={'event_timestamp': 'ds', 'order_price': 'y'})
    df_ts['ds'] = pd.to_datetime(df_ts['ds']).dt.tz_localize(None)

    model = Prophet()
    model.fit(df_ts)
    return model

def evaluate_agent2(model, tx: TransactionHistory, threshold: float = 10.0):
    future = pd.DataFrame({'ds': [pd.to_datetime(tx.event_timestamp).tz_localize(None)]})
    forecast = model.predict(future)
    predicted = forecast['yhat'][0]
    deviation = abs(tx.order_price - predicted)
    score = 1 / (1 + np.exp(deviation / threshold))
    return score

