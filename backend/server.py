import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from model_utils import preprocess_data, train_model

app = FastAPI(title="Credit Scoring API", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Credit Risk Analytics API is running. Access the frontend at http://localhost:5173"}

@app.get("/api")
async def api_root():
    return {"message": "Credit Risk Analytics API endpoints are under /api/data-info, /api/upload, /api/train, /api/predict"}


# Global in-memory state
state = {
    "df": None,
    "model": None,
    "scaler": None,
    "features": [],
    "model_name": None,
    "metrics": None,
}

DEFAULT_DATASET_PATH = "credit_data.csv"

def sanitize_val(val):
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (float, np.float64, np.float32)):
        if pd.isna(val) or np.isinf(val):
            return None
        return float(val)
    return val

def sanitize_metrics(metrics):
    if metrics is None:
        return None
    serializable_metrics = {}
    for k, v in metrics.items():
        if isinstance(v, (float, np.float64, np.float32)):
            if pd.isna(v) or np.isinf(v):
                serializable_metrics[k] = "N/A"
            else:
                serializable_metrics[k] = float(v)
        else:
            serializable_metrics[k] = str(v)
    return serializable_metrics

def get_dataset_info(df: pd.DataFrame) -> Dict[str, Any]:
    if "target" not in df.columns:
        raise HTTPException(status_code=400, detail="Dataset must contain a 'target' column.")
    
    features = [col for col in df.columns if col != "target"]
    
    # Calculate statistics for each feature
    stats = {}
    for col in features:
        # Convert to native types for JSON serialization
        stats[col] = {
            "mean": sanitize_val(df[col].mean()),
            "min": sanitize_val(df[col].min()),
            "max": sanitize_val(df[col].max()),
            "std": sanitize_val(df[col].std())
        }
        
    # Preview rows (convert NaN/Inf to None, and numpy types to python native types)
    raw_preview = df.head(10).replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict(orient="records")
    preview = []
    for row in raw_preview:
        clean_row = {}
        for k, v in row.items():
            if v is None:
                clean_row[k] = None
            elif hasattr(v, "item"):
                clean_row[k] = v.item()
            elif isinstance(v, (np.integer, np.int64)):
                clean_row[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                clean_row[k] = float(v)
            else:
                clean_row[k] = v
        preview.append(clean_row)
    
    # Target distribution
    target_counts = df["target"].value_counts().to_dict()
    target_dist = {
        "Good Credit (1)": int(target_counts.get(1, 0)),
        "Bad Credit (0)": int(target_counts.get(0, 0))
    }
    
    return {
        "columns": features,
        "statistics": stats,
        "preview": preview,
        "target_distribution": target_dist,
        "rows_count": len(df)
    }

def initialize_default_state():
    if os.path.exists(DEFAULT_DATASET_PATH):
        try:
            df = pd.read_csv(DEFAULT_DATASET_PATH)
            state["df"] = df
            
            # Auto-train default model (Random Forest)
            X, y, scaler = preprocess_data(df)
            model, metrics = train_model(X, y, "Random Forest")
            state["model"] = model
            state["scaler"] = scaler
            state["features"] = [col for col in df.columns if col != "target"]
            state["model_name"] = "Random Forest"
            state["metrics"] = metrics
            print("Successfully initialized default dataset and Random Forest model.")
        except Exception as e:
            print(f"Error initializing default state: {e}")

@app.on_event("startup")
async def startup_event():
    initialize_default_state()

@app.get("/api/data-info")
async def get_data_info():
    if state["df"] is None:
        raise HTTPException(status_code=404, detail="No dataset loaded. Please upload a CSV.")
    
    info = get_dataset_info(state["df"])
    info["model_name"] = state["model_name"]
    info["metrics"] = sanitize_metrics(state["metrics"])
    return info

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    try:
        df = pd.read_csv(file.file)
        if "target" not in df.columns:
            raise HTTPException(status_code=400, detail="The dataset must contain a 'target' column.")
            
        state["df"] = df
        
        # Reset model state when new data is uploaded
        state["model"] = None
        state["scaler"] = None
        state["features"] = []
        state["model_name"] = None
        state["metrics"] = None
        
        # Auto-train default model (Logistic Regression) on new dataset
        X, y, scaler = preprocess_data(df)
        model, metrics = train_model(X, y, "Logistic Regression")
        state["model"] = model
        state["scaler"] = scaler
        state["features"] = [col for col in df.columns if col != "target"]
        state["model_name"] = "Logistic Regression"
        state["metrics"] = metrics
        
        info = get_dataset_info(df)
        info["model_name"] = state["model_name"]
        info["metrics"] = sanitize_metrics(state["metrics"])
        return info
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {str(e)}")

class TrainRequest(BaseModel):
    model_name: str

@app.post("/api/train")
async def train_model_endpoint(request: TrainRequest):
    if state["df"] is None:
        raise HTTPException(status_code=400, detail="No dataset loaded. Upload data first.")
        
    model_name = request.model_name
    valid_models = [
        "Logistic Regression", 
        "Decision Tree", 
        "Random Forest", 
        "Gradient Boosting", 
        "AdaBoost", 
        "K-Nearest Neighbors", 
        "Naive Bayes", 
        "Support Vector Machine"
    ]
    if model_name not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model name. Must be one of {valid_models}")
        
    try:
        X, y, scaler = preprocess_data(state["df"])
        model, metrics = train_model(X, y, model_name)
        
        # Save to state
        state["model"] = model
        state["scaler"] = scaler
        state["features"] = [col for col in state["df"].columns if col != "target"]
        state["model_name"] = model_name
        state["metrics"] = metrics
        
        # Convert values to serializable types
        serializable_metrics = sanitize_metrics(metrics)
                
        return {
            "status": "success",
            "model_name": model_name,
            "metrics": serializable_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

class PredictRequest(BaseModel):
    inputs: Dict[str, float]

@app.post("/api/predict")
async def predict_endpoint(request: PredictRequest):
    if state["model"] is None or state["scaler"] is None:
        # Try to train default if we have data
        if state["df"] is not None:
            X, y, scaler = preprocess_data(state["df"])
            model, metrics = train_model(X, y, "Random Forest")
            state["model"] = model
            state["scaler"] = scaler
            state["features"] = [col for col in state["df"].columns if col != "target"]
            state["model_name"] = "Random Forest"
            state["metrics"] = metrics
        else:
            raise HTTPException(status_code=400, detail="No model trained and no default dataset available.")
            
    # Verify inputs match expected features
    missing_features = [f for f in state["features"] if f not in request.inputs]
    if missing_features:
        raise HTTPException(status_code=400, detail=f"Missing input features: {missing_features}")
        
    try:
        # Ensure correct feature order
        ordered_input = [request.inputs[col] for col in state["features"]]
        input_df = pd.DataFrame([ordered_input], columns=state["features"])
        
        # Scale input
        input_scaled = state["scaler"].transform(input_df)
        
        # Predict
        prediction = int(state["model"].predict(input_scaled)[0])
        
        # Probability if supported
        prob = "N/A"
        if hasattr(state["model"], "predict_proba"):
            prob = float(state["model"].predict_proba(input_scaled)[0][1])
            
        return {
            "prediction": prediction,
            "probability": prob,
            "model_name": state["model_name"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
