# 🏗️ Architecture & Design Document

> Deep-dive into the technical design, data flow, ML pipeline, and component structure of the Credit Risk Analytics Platform.

---

## 📋 Table of Contents

- [High-Level Architecture](#-high-level-architecture)
- [Request Lifecycle](#-request-lifecycle)
- [ML Pipeline](#-ml-pipeline)
- [Frontend Component Tree](#-frontend-component-tree)
- [Backend State Management](#-backend-state-management)
- [Security Model](#-security-model)
- [Dependency Overview](#-dependency-overview)
- [Test Architecture](#-test-architecture)
- [Future Improvements](#-future-improvements)

---

## 🧱 High-Level Architecture

The platform follows a **Three-Tier Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1 — Presentation Layer                                │
│  React SPA @ localhost:5173                                 │
│                                                             │
│   Real-time Scorer  │  Model Training Hub  │  Dataset View  │
└────────────────────────────┬────────────────────────────────┘
                             │  REST API (Axios / HTTP)
┌────────────────────────────▼────────────────────────────────┐
│  TIER 2 — Application Layer                                 │
│  FastAPI @ localhost:8000                                   │
│                                                             │
│   /api/data-info  │  /api/train  │  /api/predict            │
│   /api/upload                                               │
│                                                             │
│   model_utils.py  →  preprocess → train → evaluate          │
└────────────────────────────┬────────────────────────────────┘
                             │  pandas + scikit-learn
┌────────────────────────────▼────────────────────────────────┐
│  TIER 3 — Data Layer                                        │
│  CSV File  +  In-Memory State                               │
│                                                             │
│   credit_data.csv (5,000 rows)                              │
│   state { df │ model │ scaler │ features │ metrics }        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔁 Request Lifecycle

### Training Flow

```
Client              FastAPI             model_utils.py
  │                    │                      │
  │  POST /api/train   │                      │
  │  { model_name }    │                      │
  │───────────────────▶│                      │
  │                    │  load_data()         │
  │                    │─────────────────────▶│
  │                    │  preprocess_data()   │
  │                    │─────────────────────▶│
  │                    │  train_model()       │
  │                    │─────────────────────▶│
  │                    │  ← fitted model      │
  │                    │  ← metrics           │
  │  { metrics }       │                      │
  │◀───────────────────│                      │
```

### Prediction Flow

```
Client              FastAPI             scikit-learn
  │                    │                      │
  │  POST /api/predict │                      │
  │  { inputs }        │                      │
  │───────────────────▶│                      │
  │                    │  validate inputs     │
  │                    │  scaler.transform()  │
  │                    │  model.predict()     │
  │                    │─────────────────────▶│
  │                    │  model.predict_proba │
  │                    │─────────────────────▶│
  │                    │  ← label, prob       │
  │  { prediction,     │                      │
  │    probability }   │                      │
  │◀───────────────────│                      │
```

---

## 🧬 ML Pipeline

```
Step 1 — Load
   pd.read_csv(path)
   df.dropna()

Step 2 — Preprocess
   X = df[feature_columns]
   y = df["target"]
   train_test_split(X, y, test_size=0.2)

Step 3 — Scale
   StandardScaler.fit(X_train)
   X_train_scaled = scaler.transform(X_train)
   X_test_scaled  = scaler.transform(X_test)

Step 4 — Train
   model = AlgorithmClassifier(**params)
   model.fit(X_train_scaled, y_train)

Step 5 — Evaluate
   y_pred  = model.predict(X_test_scaled)
   y_proba = model.predict_proba(X_test_scaled)[:,1]

   Precision = precision_score(y_test, y_pred)
   Recall    = recall_score(y_test, y_pred)
   F1-Score  = f1_score(y_test, y_pred)
   ROC-AUC   = roc_auc_score(y_test, y_proba)

Step 6 — Store (Global State)
   state["df"]           = df
   state["model"]        = model
   state["scaler"]       = scaler
   state["feature_cols"] = feature_columns
   state["model_name"]   = model_name
   state["metrics"]      = { Precision, Recall, F1, ROC-AUC }
```

### Algorithm Configuration

| Algorithm | Key Parameters |
|-----------|---------------|
| Logistic Regression | `max_iter=1000` |
| Decision Tree | `random_state=42` |
| Random Forest | `n_estimators=100`, `random_state=42` |
| Gradient Boosting | `n_estimators=100`, `random_state=42` |
| AdaBoost | `n_estimators=100`, `random_state=42` |
| K-Nearest Neighbors | `n_neighbors=5` |
| Naive Bayes | GaussianNB (no params) |
| SVM | `probability=True`, `random_state=42` |

---

## 🖥️ Frontend Component Tree

```
App.jsx
│
├── Header
│     └── Theme Toggle (Dark ↔ Light)
│
├── Tab: Real-time Scorer
│     ├── Feature Sliders
│     │     ├── income
│     │     ├── debts
│     │     ├── payment_history
│     │     ├── age
│     │     ├── credit_cards
│     │     └── loan_amount
│     ├── Predict Button  →  POST /api/predict
│     ├── Risk Gauge (0 – 100%)
│     └── Verdict Banner (Good Credit / Bad Credit)
│
├── Tab: Model Training Hub
│     ├── Algorithm Selector (8 models)
│     ├── Train Button  →  POST /api/train
│     ├── Metrics Cards (Precision · Recall · F1 · ROC-AUC)
│     └── Benchmark Bar Chart (ECharts)
│
└── Tab: Dataset Explorer
      ├── CSV Upload  →  POST /api/upload
      ├── Dataset Statistics Table
      ├── Class Distribution Pie Chart (ECharts)
      └── Data Preview Table (first 10 rows)
```

---

## 💾 Backend State Management

The backend uses a **global in-memory dictionary** shared across requests:

```python
state = {
    "df":           None,   # Active Pandas DataFrame
    "model":        None,   # Fitted scikit-learn classifier
    "scaler":       None,   # Fitted StandardScaler instance
    "feature_cols": [],     # List of input feature column names
    "model_name":   None,   # Name of the currently active model
    "metrics":      {}      # Last evaluation metrics dict
}
```

> **Note:** This is a single-user, single-session in-memory design.
> For multi-user production deployments, consider a model registry (e.g. MLflow) or database-backed sessions.

---

## 🔒 Security Model

| Concern | Mitigation |
|---------|-----------|
| Secrets exposure | All config in `.env`, excluded via `.gitignore` |
| Cross-origin requests | CORS restricted via `ALLOWED_ORIGINS` env variable |
| Malicious input | Pydantic models enforce types at API boundary |
| File upload abuse | Only `text/csv` MIME accepted; parsed with pandas |
| JSON serialization | All NumPy types cast to native Python before response |

---

## 📦 Dependency Overview

### Backend (`requirements.txt`)

| Package | Purpose |
|---------|---------|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `pydantic` | Request/response validation |
| `pandas` | DataFrame operations |
| `numpy` | Numerical computing |
| `scikit-learn` | ML algorithms & evaluation |
| `python-multipart` | File upload parsing |
| `httpx` | Async HTTP client for tests |
| `pytest` | Test runner |

### Frontend (`package.json`)

| Package | Purpose |
|---------|---------|
| `react` | UI component library |
| `react-dom` | DOM rendering |
| `vite` | Dev server & bundler |
| `echarts` | Chart visualizations |
| `axios` | HTTP client |
| `lucide-react` | SVG icon set |

---

## 🧪 Test Architecture

```
tests/
│
├── test_model_utils.py   (Unit Tests — 10 tests)
│     ├── test_load_data
│     ├── test_preprocess_data
│     └── test_train_model × 8 algorithms
│
└── test_server.py        (Integration Tests — 18 tests)
      ├── GET  /api/data-info  → loaded state
      ├── GET  /api/data-info  → no dataset state
      ├── POST /api/train      → each of 8 models
      ├── POST /api/train      → invalid model name
      ├── POST /api/predict    → valid inputs
      ├── POST /api/predict    → missing features
      ├── POST /api/upload     → valid CSV
      ├── POST /api/upload     → wrong file type
      └── POST /api/upload     → missing target column
```

### Running Tests

```bash
# Full suite
python -m pytest

# Verbose
python -m pytest -v

# Specific file
python -m pytest tests/test_server.py -v
```

---

## 🚧 Future Improvements

| Priority | Improvement | Effort |
|:--------:|------------|:------:|
| 🔴 High | Persistent model storage (joblib / pickle) | Medium |
| 🔴 High | User authentication (JWT / OAuth2) | High |
| 🟡 Medium | SHAP explainability scores in predictions | Medium |
| 🟡 Medium | PostgreSQL for multi-session support | High |
| 🟢 Low | Docker Compose for one-command setup | Low |
| 🟢 Low | Hyperparameter tuning UI (GridSearch) | Medium |
| 🟢 Low | Export trained model as `.pkl` download | Low |

---

*Last updated: June 2026 · [Back to README](./README.md)*
