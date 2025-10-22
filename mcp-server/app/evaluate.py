# app/evaluate.py

from agents import contextAnalyzer, transactionHistoryProfiler, fraudPatternMatcher
from models.schemas import TransactionInput
from models.metadata_text import MetadataText

# Sample transaction input
sample_tx = TransactionInput(
    amount=1000.0,
    oldbalanceOrg=500.0,
    newbalanceOrig=1500.0,
    event_timestamp="2025-10-21T12:00:00",
    order_price=1000.0
)

# Sample metadata input for Agent 4
sample_meta = MetadataText(
    metadata="Customer reported suspicious activity on account after midnight."
)

# Train models
model1 = contextAnalyzer.train_agent1()
model2 = transactionHistoryProfiler.train_agent2()
model4 = fraudPatternMatcher.train_agent4()

# Evaluate transaction
s1 = contextAnalyzer.evaluate_agent1(model1, sample_tx)
s2 = transactionHistoryProfiler.evaluate_agent2(model2, sample_tx)
s4 = fraudPatternMatcher.evaluate_agent4(model4, sample_meta)

# Print scores
print(f"Agent 1 score (Isolation Forest): {s1:.4f}")
print(f"Agent 2 score (Prophet): {s2:.4f}")
print(f"Agent 4 score (BERT + XGBoost): {s4:.4f}")
