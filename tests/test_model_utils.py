import pytest
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from model_utils import preprocess_data, train_model

@pytest.fixture
def sample_data():
    np.random.seed(42)
    rows = 100
    data = {
        "income": np.random.uniform(20000, 120000, rows),
        "debts": np.random.uniform(1000, 40000, rows),
        "payment_history": np.random.randint(0, 6, rows),
        "age": np.random.randint(18, 70, rows),
        "credit_cards": np.random.randint(0, 6, rows),
        "loan_amount": np.random.uniform(5000, 50000, rows),
        "target": np.random.choice([0, 1], rows, p=[0.3, 0.7])
    }
    return pd.DataFrame(data)

def test_preprocess_data_valid(sample_data):
    X_scaled, y, scaler = preprocess_data(sample_data)
    
    assert isinstance(scaler, StandardScaler)
    assert len(X_scaled) == len(sample_data)
    assert X_scaled.shape[1] == sample_data.shape[1] - 1  # Excludes 'target'
    assert len(y) == len(sample_data)
    assert (y == sample_data['target']).all()

def test_preprocess_data_missing_target(sample_data):
    bad_data = sample_data.drop('target', axis=1)
    with pytest.raises(KeyError):
        preprocess_data(bad_data)

@pytest.mark.parametrize("model_name", [
    "Logistic Regression", 
    "Decision Tree", 
    "Random Forest",
    "Gradient Boosting",
    "AdaBoost",
    "K-Nearest Neighbors",
    "Naive Bayes",
    "Support Vector Machine"
])
def test_train_model_valid(sample_data, model_name):
    X_scaled, y, scaler = preprocess_data(sample_data)
    model, metrics = train_model(X_scaled, y, model_name)
    
    assert model is not None
    assert isinstance(metrics, dict)
    for key in ["Precision", "Recall", "F1-Score", "ROC-AUC"]:
        assert key in metrics
        if key == "ROC-AUC" and metrics[key] == "N/A":
            pass
        else:
            assert isinstance(metrics[key], (float, np.floating))
