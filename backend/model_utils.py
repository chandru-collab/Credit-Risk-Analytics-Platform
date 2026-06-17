import os
import time
import logging
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

VALID_MODELS = [
    "Logistic Regression",
    "Decision Tree",
    "Random Forest",
    "Gradient Boosting",
    "AdaBoost",
    "K-Nearest Neighbors",
    "Naive Bayes",
    "Support Vector Machine",
]


def load_data(path):
    """Load a CSV dataset from the given file path."""
    logger.info("Loading data from %s", path)
    return pd.read_csv(path)


def preprocess_data(df):
    """Drop NaN rows, split features/target, and scale with StandardScaler."""
    df = df.dropna()
    X = df.drop('target', axis=1)
    y = df['target']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    logger.info("Preprocessed %d rows with %d features", len(df), X.shape[1])
    return X_scaled, y, scaler


def train_model(X, y, model_name):
    """Train the selected model, evaluate it, and return (model, metrics)."""
    if model_name == "Logistic Regression":
        model = LogisticRegression(max_iter=1000)
    elif model_name == "Decision Tree":
        model = DecisionTreeClassifier()
    elif model_name == "Random Forest":
        model = RandomForestClassifier()
    elif model_name == "Gradient Boosting":
        model = GradientBoostingClassifier()
    elif model_name == "AdaBoost":
        model = AdaBoostClassifier()
    elif model_name == "K-Nearest Neighbors":
        model = KNeighborsClassifier()
    elif model_name == "Naive Bayes":
        model = GaussianNB()
    elif model_name == "Support Vector Machine":
        model = SVC(probability=True)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    start = time.perf_counter()
    model.fit(X_train, y_train)
    elapsed = time.perf_counter() - start

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    metrics = {
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1-Score": f1_score(y_test, y_pred),
        "ROC-AUC": roc_auc_score(y_test, y_prob) if y_prob is not None else "N/A",
    }

    logger.info(
        "Trained '%s' in %.3fs — Precision=%.3f  Recall=%.3f  F1=%.3f  AUC=%s",
        model_name, elapsed,
        metrics["Precision"], metrics["Recall"], metrics["F1-Score"],
        f'{metrics["ROC-AUC"]:.3f}' if isinstance(metrics["ROC-AUC"], float) else metrics["ROC-AUC"],
    )

    return model, metrics


def save_model(model, scaler, model_name, metrics):
    """Persist a trained model, its scaler, and metrics to disk via joblib."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    safe_name = model_name.lower().replace(" ", "_")
    payload = {
        "model": model,
        "scaler": scaler,
        "model_name": model_name,
        "metrics": metrics,
    }
    path = os.path.join(MODELS_DIR, f"{safe_name}.joblib")
    joblib.dump(payload, path)
    logger.info("Model '%s' saved to %s", model_name, path)
    return path


def load_saved_model(model_name):
    """Load a previously persisted model from disk. Returns dict or None."""
    safe_name = model_name.lower().replace(" ", "_")
    path = os.path.join(MODELS_DIR, f"{safe_name}.joblib")
    if os.path.exists(path):
        payload = joblib.load(path)
        logger.info("Model '%s' loaded from %s", model_name, path)
        return payload
    return None
