# app/evaluate.py
from agents import contextAnalyzer, transactionHistoryProfiler
from models.schemas import TransactionInput

sample_tx = TransactionInput(
    amount=1000.0,
    oldbalanceOrg=500.0,
    newbalanceOrig=1500.0,
    event_timestamp="2025-10-21T12:00:00",
    order_price=1000.0
)

model1 = contextAnalyzer.train_agent1()
model2 = transactionHistoryProfiler.train_agent2()

s1 = contextAnalyzer.evaluate_agent1(model1, sample_tx)
s2 = transactionHistoryProfiler.evaluate_agent2(model2, sample_tx)

print(f"Agent 1 score: {s1:.4f}")
print(f"Agent 2 score: {s2:.4f}")
