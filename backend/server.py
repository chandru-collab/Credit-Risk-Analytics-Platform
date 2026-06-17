import os
import logging
import sys
from contextlib import asynccontextmanager

import pandas as pd
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from model_utils import (
    preprocess_data,
    train_model,
    save_model,
    load_saved_model,
    VALID_MODELS,
)

# ─── Environment & Configuration ────────────────────────────────
load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
DEFAULT_DATASET_PATH = os.getenv("DEFAULT_DATASET_PATH", "credit_data.csv")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Random Forest")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

# ─── Structured Logging ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("credit_risk_api")

# ─── Rate Limiter ────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ─── Global In-Memory State ─────────────────────────────────────
state: Dict[str, Any] = {
    "df": None,
    "model": None,
    "scaler": None,
    "features": [],
    "model_name": None,
    "metrics": None,
}


# ─── JSON Serialization Helpers ──────────────────────────────────
def sanitize_val(val):
    """Convert numpy/pandas scalar types to native Python for JSON."""
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (float, np.float64, np.float32)):
        if pd.isna(val) or np.isinf(val):
            return None
        return float(val)
    return val


def sanitize_metrics(metrics):
    """Make metric values JSON-serializable."""
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
    """Extract column statistics, preview rows, and target distribution."""
    if "target" not in df.columns:
        raise HTTPException(status_code=400, detail="Dataset must contain a 'target' column.")

    features = [col for col in df.columns if col != "target"]

    # Calculate statistics for each feature
    stats = {}
    for col in features:
        stats[col] = {
            "mean": sanitize_val(df[col].mean()),
            "min": sanitize_val(df[col].min()),
            "max": sanitize_val(df[col].max()),
            "std": sanitize_val(df[col].std()),
        }

    # Preview rows — sanitize numpy types for JSON
    raw_preview = (
        df.head(10)
        .replace({np.nan: None, np.inf: None, -np.inf: None})
        .to_dict(orient="records")
    )
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
        "Bad Credit (0)": int(target_counts.get(0, 0)),
    }

    return {
        "columns": features,
        "statistics": stats,
        "preview": preview,
        "target_distribution": target_dist,
        "rows_count": len(df),
    }


# ─── Startup / Shutdown Lifecycle ────────────────────────────────
def initialize_default_state():
    """Load default dataset and attempt to restore or train a model."""
    dataset_path = DEFAULT_DATASET_PATH
    if not os.path.exists(dataset_path):
        # Fallback to backend folder relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(base_dir, DEFAULT_DATASET_PATH)
        if os.path.exists(alt_path):
            dataset_path = alt_path
        else:
            logger.warning("Default dataset not found at '%s' or '%s'", DEFAULT_DATASET_PATH, alt_path)
            return

    try:
        df = pd.read_csv(dataset_path)
        state["df"] = df
        state["features"] = [col for col in df.columns if col != "target"]

        # Try to restore a previously saved model first
        saved = load_saved_model(DEFAULT_MODEL)
        if saved is not None:
            state["model"] = saved["model"]
            state["scaler"] = saved["scaler"]
            state["model_name"] = saved["model_name"]
            state["metrics"] = saved["metrics"]
            logger.info("Restored saved model '%s' from disk", DEFAULT_MODEL)
            return

        # No saved model — train from scratch
        X, y, scaler = preprocess_data(df)
        model, metrics = train_model(X, y, DEFAULT_MODEL)
        state["model"] = model
        state["scaler"] = scaler
        state["model_name"] = DEFAULT_MODEL
        state["metrics"] = metrics

        # Persist for next restart
        save_model(model, scaler, DEFAULT_MODEL, metrics)
        logger.info("Initialized and persisted default model '%s'", DEFAULT_MODEL)

    except Exception:
        logger.exception("Error initializing default state")


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Modern lifespan handler — replaces deprecated @app.on_event."""
    logger.info("Starting Credit Risk Analytics API — origins=%s", ALLOWED_ORIGINS)
    initialize_default_state()
    yield
    logger.info("Shutting down Credit Risk Analytics API")


# ─── FastAPI Application ─────────────────────────────────────────
app = FastAPI(
    title="Credit Scoring API",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restricted to configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


# ═══════════════════════════════════════════════════════════════════
#  API Routes — v1 (canonical) + legacy aliases
# ═══════════════════════════════════════════════════════════════════


@app.get("/")
async def root():
    """Root health check."""
    return {"message": "Credit Risk Analytics API is running. Access the frontend at http://localhost:5173"}


@app.get("/api")
async def api_root():
    """API route listing."""
    return {
        "message": "Credit Risk Analytics API endpoints are under /api/v1/health, /api/v1/data-info, /api/v1/upload, /api/v1/train, /api/v1/predict"
    }


# ── Health ────────────────────────────────────────────────────────
@app.get("/api/v1/health")
@app.get("/api/health")
async def health_check():
    """Structured health check for monitoring and load balancers."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": state["model"] is not None,
        "active_model": state["model_name"],
        "dataset_loaded": state["df"] is not None,
        "dataset_rows": len(state["df"]) if state["df"] is not None else 0,
    }


# ── Data Info ─────────────────────────────────────────────────────
@app.get("/api/v1/data-info")
@app.get("/api/data-info")
async def get_data_info():
    """Return dataset statistics, preview, and active model metrics."""
    if state["df"] is None:
        raise HTTPException(status_code=404, detail="No dataset loaded. Please upload a CSV.")

    info = get_dataset_info(state["df"])
    info["model_name"] = state["model_name"]
    info["metrics"] = sanitize_metrics(state["metrics"])
    return info


# ── Upload CSV ────────────────────────────────────────────────────
@app.post("/api/v1/upload")
@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Upload a CSV dataset, validate it, and auto-train a baseline model."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Read file contents and enforce size limit
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Maximum allowed is {MAX_UPLOAD_SIZE_MB} MB.",
        )

    try:
        import io
        df = pd.read_csv(io.BytesIO(contents))
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

        save_model(model, scaler, "Logistic Regression", metrics)
        logger.info("Uploaded dataset (%d rows) and auto-trained Logistic Regression", len(df))

        info = get_dataset_info(df)
        info["model_name"] = state["model_name"]
        info["metrics"] = sanitize_metrics(state["metrics"])
        return info

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to process uploaded CSV")
        raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {str(e)}")


# ── Train Model ──────────────────────────────────────────────────
class TrainRequest(BaseModel):
    model_name: str


@app.post("/api/v1/train")
@app.post("/api/train")
@limiter.limit("20/minute")
async def train_model_endpoint(request: Request, body: TrainRequest):
    """Train the requested ML algorithm on the current dataset."""
    if state["df"] is None:
        raise HTTPException(status_code=400, detail="No dataset loaded. Upload data first.")

    model_name = body.model_name
    if model_name not in VALID_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model name. Must be one of {VALID_MODELS}")

    try:
        X, y, scaler = preprocess_data(state["df"])
        model, metrics = train_model(X, y, model_name)

        # Save to state
        state["model"] = model
        state["scaler"] = scaler
        state["features"] = [col for col in state["df"].columns if col != "target"]
        state["model_name"] = model_name
        state["metrics"] = metrics

        # Persist to disk
        save_model(model, scaler, model_name, metrics)

        serializable_metrics = sanitize_metrics(metrics)

        return {
            "status": "success",
            "model_name": model_name,
            "metrics": serializable_metrics,
        }
    except Exception as e:
        logger.exception("Training failed for model '%s'", model_name)
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


# ── Predict ──────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    inputs: Dict[str, float]


@app.post("/api/v1/predict")
@app.post("/api/predict")
@limiter.limit("60/minute")
async def predict_endpoint(request: Request, body: PredictRequest):
    """Run a credit-risk prediction using the active model."""
    if state["model"] is None or state["scaler"] is None:
        # Try to train default if we have data
        if state["df"] is not None:
            X, y, scaler = preprocess_data(state["df"])
            model, metrics = train_model(X, y, DEFAULT_MODEL)
            state["model"] = model
            state["scaler"] = scaler
            state["features"] = [col for col in state["df"].columns if col != "target"]
            state["model_name"] = DEFAULT_MODEL
            state["metrics"] = metrics
            save_model(model, scaler, DEFAULT_MODEL, metrics)
        else:
            raise HTTPException(status_code=400, detail="No model trained and no default dataset available.")

    # Verify inputs match expected features
    missing_features = [f for f in state["features"] if f not in body.inputs]
    if missing_features:
        raise HTTPException(status_code=400, detail=f"Missing input features: {missing_features}")

    try:
        # Ensure correct feature order
        ordered_input = [body.inputs[col] for col in state["features"]]
        input_df = pd.DataFrame([ordered_input], columns=state["features"])

        # Scale input
        input_scaled = state["scaler"].transform(input_df)

        # Predict
        prediction = int(state["model"].predict(input_scaled)[0])

        # Probability if supported
        prob = "N/A"
        if hasattr(state["model"], "predict_proba"):
            prob = float(state["model"].predict_proba(input_scaled)[0][1])

        logger.info("Prediction: %d (prob=%.3f) via '%s'", prediction, prob if isinstance(prob, float) else 0, state["model_name"])

        return {
            "prediction": prediction,
            "probability": prob,
            "model_name": state["model_name"],
        }
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ─── Entrypoint ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
