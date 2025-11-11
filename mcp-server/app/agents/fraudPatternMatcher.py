
# Training Function
# agents/fraudPatternMatcher.py
# ---------------------------------------------------------------------------
# Agent 3: Fraud Pattern Matcher (Simplified)
#
# Model: TF-IDF + Logistic Regression
# Steps:
#     1. Vectorize metadata text using TF-IDF
#     2. Train a Logistic Regression classifier
#     3. Use probability of fraud as the score
# ---------------------------------------------------------------------------

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np
from models.metadata_text import load_metadata_text, MetadataText
import joblib

def train_agent3():
    """
    Loads metadata and trains a Logistic Regression classifier using TF-IDF.
    Returns trained model pipeline.
    """
    df = load_metadata_text()
    
    # Labels
    y = df['is_fraud'].map({'yes': 1, 'no': 0}).values
    
    # TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X = vectorizer.fit_transform(df['metadata'])
    
    # Logistic Regression classifier
    model = LogisticRegression(max_iter=500)
    model.fit(X, y)
    
    # Return a simple dict with vectorizer + model
    return {'vectorizer': vectorizer, 'model': model}

def evaluate_agent3(agent_model, tx: MetadataText):
    """
    Evaluates a single transaction using TF-IDF + Logistic Regression.
    Returns fraud probability score.
    """
    vectorizer = agent_model['vectorizer']
    model = agent_model['model']
    
    X_tx = vectorizer.transform([tx.metadata])
    score = model.predict_proba(X_tx)[0][1]
    return score
