# agents/fraudPatternMatcher.py
# ---------------------------------------------------------------------------
# Agent 4: Fraud Pattern Matcher
#
# Model: BERT + XGBoost
#
# Steps:
#     1. Combine all metadata fields into a composite text
#     2. Encode with BERT embeddings
#     3. Train an XGBoost classifier
#     4. Use probability of fraud as the score
# ---------------------------------------------------------------------------

from transformers import BertTokenizer, BertModel
from xgboost import XGBClassifier
import torch
import numpy as np
import pandas as pd
from models.metadata_text import load_metadata_text, MetadataText

# Training Function
def train_agent4():
    """
    Loads metadata from S3/local and trains an XGBoost classifier using BERT embeddings.
    Takes into account all fields: ip_address, user_agent, merchant, product_category, metadata.
    """
    print("Loading metadata dataset...")
    df = load_metadata_text()

    # Build a full composite text string per row
    df["full_metadata"] = (
        df["ip_address"].astype(str) + " " +
        df["user_agent"].astype(str) + " " +
        df["merchant"].astype(str) + " " +
        df["product_category"].astype(str) + " " +
        df["metadata"].astype(str)
    )

    print("Generating BERT embeddings for full metadata...")
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    bert = BertModel.from_pretrained("bert-base-uncased")

    embeddings = []
    for text in df["full_metadata"]:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            output = bert(**inputs)
        pooled = output.last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings.append(pooled)

    X = np.array(embeddings)
    y = df["is_fraud"].map({"yes": 1, "no": 0}).values

    print(f"Training XGBoost on {len(X)} samples...")
    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X, y)

    print("Agent 4 full-feature model trained successfully.")
    return model


# Evaluation Function
def evaluate_agent4(model, tx: MetadataText):
    """
    Evaluates a single transaction using the full MetadataText model.
    Combines all fields into a composite text for embedding and classification.
    Returns fraud probability score.
    """
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    bert = BertModel.from_pretrained("bert-base-uncased")

    # Combine all available fields into one composite input string
    composite_text = (
        f"{tx.ip_address} {tx.user_agent} {tx.merchant} {tx.product_category} {tx.metadata}"
    )

    inputs = tokenizer(composite_text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        output = bert(**inputs)
    pooled = output.last_hidden_state.mean(dim=1).squeeze().numpy()

    # Compute fraud probability
    score = model.predict_proba([pooled])[0][1]
    return float(score)
