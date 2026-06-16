import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
import io

from server import app, state

@pytest.fixture(autouse=True)
def reset_state():
    # Store original state
    orig_df = state["df"]
    orig_model = state["model"]
    orig_scaler = state["scaler"]
    orig_features = state["features"]
    orig_model_name = state["model_name"]
    orig_metrics = state["metrics"]
    
    yield
    
    # Restore original state after test
    state["df"] = orig_df
    state["model"] = orig_model
    state["scaler"] = orig_scaler
    state["features"] = orig_features
    state["model_name"] = orig_model_name
    state["metrics"] = orig_metrics

def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "Credit Risk Analytics API is running" in response.json()["message"]

def test_api_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/api")
        assert response.status_code == 200
        assert "endpoints are under" in response.json()["message"]

def test_get_data_info_unloaded():
    with TestClient(app) as client:
        state["df"] = None
        response = client.get("/api/data-info")
        assert response.status_code == 404
        assert response.json()["detail"] == "No dataset loaded. Please upload a CSV."

def test_get_data_info_loaded():
    # Make sure default state is initialized
    with TestClient(app) as client:
        response = client.get("/api/data-info")
        assert response.status_code == 200
        data = response.json()
        assert "columns" in data
        assert "statistics" in data
        assert "preview" in data
        assert "target_distribution" in data
        assert "rows_count" in data
        assert data["model_name"] is not None

def test_predict_success():
    with TestClient(app) as client:
        # First check features
        info_resp = client.get("/api/data-info")
        assert info_resp.status_code == 200
        features = info_resp.json()["columns"]
        
        # Create valid input
        inputs = {feat: 10.0 for feat in features}
        
        response = client.post("/api/predict", json={"inputs": inputs})
        assert response.status_code == 200
        res = response.json()
        assert "prediction" in res
        assert res["prediction"] in [0, 1]
        assert "probability" in res
        assert "model_name" in res

def test_predict_missing_features():
    with TestClient(app) as client:
        response = client.post("/api/predict", json={"inputs": {"income": 50000.0}})
        assert response.status_code == 400
        assert "Missing input features" in response.json()["detail"]

def test_train_model_invalid_name():
    with TestClient(app) as client:
        response = client.post("/api/train", json={"model_name": "Deep Learning Neural Network"})
        assert response.status_code == 400
        assert "Invalid model name" in response.json()["detail"]

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
def test_train_model_success(model_name):
    with TestClient(app) as client:
        response = client.post("/api/train", json={"model_name": model_name})
        assert response.status_code == 200
        res = response.json()
        assert res["status"] == "success"
        assert res["model_name"] == model_name
        assert "metrics" in res
        assert "F1-Score" in res["metrics"]

def test_upload_invalid_file_type():
    with TestClient(app) as client:
        files = {"file": ("test.txt", b"some text content", "text/plain")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 400
        assert "Only CSV files are supported" in response.json()["detail"]

def test_upload_missing_target_column():
    csv_data = "income,debts,age\n50000,10000,30\n60000,12000,40"
    with TestClient(app) as client:
        files = {"file": ("test.csv", csv_data.encode("utf-8"), "text/csv")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 400
        assert "The dataset must contain a 'target' column" in response.json()["detail"]

def test_upload_success():
    csv_data = "income,debts,payment_history,age,credit_cards,loan_amount,target\n50000,10000,3,30,2,15000,1\n60000,12000,4,40,3,20000,0\n70000,14000,5,50,4,25000,1\n80000,16000,1,25,1,30000,0\n90000,18000,2,35,2,35000,1"
    with TestClient(app) as client:
        files = {"file": ("test_upload.csv", csv_data.encode("utf-8"), "text/csv")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 200
        res = response.json()
        assert "columns" in res
        assert "target_distribution" in res
        assert res["rows_count"] == 5
        assert res["model_name"] == "Logistic Regression"  # Should auto-train logistic regression
