# app/train_agent3.py  
# Agent 4: Fraud Pattern Matcher
#
#     Model: BERT + XGBoost
#
#     Steps:
#
#         Embed metadata
#
#         Classify with XGBoost
#
#     Scoring: score = model.predict_proba(X)[1]
from transformers import BertTokenizer, BertModel
from xgboost import XGBClassifier
import torch
import numpy as np
from models.metadata_text import load_metadata_text, MetadataText

# Training Function

def train_agent3():
    """
    Loads metadata from S3 and trains XGBoost classifier using BERT embeddings.
    Returns trained model.
    """
    df = load_metadata_text()
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert = BertModel.from_pretrained('bert-base-uncased')

    embeddings = []
    for text in df['metadata']:
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            output = bert(**inputs)
        pooled = output.last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings.append(pooled)

    X = np.array(embeddings)
    y = df['is_fraud'].map({'yes': 1, 'no': 0}).values

    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X, y)
    return model

# Evaluation Function

def evaluate_agent3(model, tx: MetadataText):
    """
    Evaluates a single transaction using trained XGBoost model and BERT embedding.
    Returns fraud probability score.
    """
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert = BertModel.from_pretrained('bert-base-uncased')

    inputs = tokenizer(tx.metadata, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        output = bert(**inputs)
    pooled = output.last_hidden_state.mean(dim=1).squeeze().numpy()

    score = model.predict_proba([pooled])[0][1]
    return score
