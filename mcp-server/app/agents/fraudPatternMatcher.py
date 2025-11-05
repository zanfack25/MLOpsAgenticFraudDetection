# agents/fraudPatternMatcher.py
# ---------------------------------------------------------------------------
# Agent 3: Fraud Pattern Matcher
#
# Model: BERT + XGBoost
#
# Steps:
#     1. Combine all metadata fields into a composite text
#     2. Encode with BERT embeddings (batched)
#     3. Train an XGBoost classifier
#     4. Use probability of fraud as the score
# ---------------------------------------------------------------------------

from transformers import BertTokenizer, BertModel
from xgboost import XGBClassifier
import torch
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader
from models.metadata_text import load_metadata_text, MetadataText

# ---------------------------------------------------------------------------
# Global tokenizer and model (loaded once, reused for training + evaluation)
# ---------------------------------------------------------------------------
print("Loading BERT tokenizer and model...")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert = BertModel.from_pretrained("bert-base-uncased")


# ---------------------------------------------------------------------------
# Helper: Generate embeddings in batches with progress logging
# ---------------------------------------------------------------------------
def generate_embeddings(texts, batch_size: int = 16):
    """
    Generate BERT embeddings for a list of texts in batches.
    """
    all_embeddings = []
    dataloader = DataLoader(texts, batch_size=batch_size)

    total = len(texts)
    processed = 0

    for batch in dataloader:
        inputs = tokenizer(batch, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            output = bert(**inputs)
        pooled = output.last_hidden_state.mean(dim=1).numpy()
        all_embeddings.extend(pooled)

        processed += len(batch)
        print(f"Processed {processed}/{total} samples")

    return np.array(all_embeddings)


# ---------------------------------------------------------------------------
# Training Function
# ---------------------------------------------------------------------------
def train_agent3():
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
    X = generate_embeddings(df["full_metadata"].tolist(), batch_size=16)

    y = df["is_fraud"].map({"yes": 1, "no": 0}).values

    print(f"Training XGBoost on {len(X)} samples...")
    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X, y)

    print("Agent 3 full-feature model trained successfully.")
    return model


# ---------------------------------------------------------------------------
# Evaluation Function
# ---------------------------------------------------------------------------
def evaluate_agent3(model, tx: MetadataText):
    """
    Evaluates a single transaction using the full MetadataText model.
    Combines all fields into a composite text for embedding and classification.
    Returns fraud probability score.
    """
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
