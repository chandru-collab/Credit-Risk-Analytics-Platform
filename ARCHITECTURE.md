# 🏗️ Architecture & Design Document

> Deep-dive into the technical architecture, design decisions, and internals of the Credit Risk Analytics Platform.

---

## 📐 High-Level Design

```
╔══════════════════════════════════════════════════════════════════════╗
║                     THREE-TIER ARCHITECTURE                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   TIER 1 ──── Presentation    React SPA @ :5173                     ║
║                               └─ Real-time Scorer                   ║
║                               └─ Model Training Hub                  ║
║                               └─ Dataset Explorer                    ║
║                                                                      ║
║   TIER 2 ──── Application     FastAPI @ :8000                        ║
║                               └─ REST API Endpoints                  ║
║                               └─ ML Orchestration                    ║
║                               └─ Data Sanitization                   ║
║                                                                      ║
║   TIER 3 ──── Data            CSV (file-based)                       ║
║                               └─ In-Memory Pandas DataFrame          ║
║                               └─ scikit-learn Model State            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 🔁 Request Lifecycle

### Training Flow

```
  Client                  FastAPI                 model_utils.py
    │                        │                          │
    │  POST /api/train        │                          │
    │  { model_name }         │                          │
    │──────────────────────▶  │                          │
    │                        │  load_data()              │
    │                        │ ─────────────────────────▶│
    │                        │  preprocess_data()        │
    │                        │ ─────────────────────────▶│
    │                        │  train_model()            │
    │                        │ ─────────────────────────▶│
    │                        │         fit ML Model      │
    │                        │  ◀─────────────────────── │
    │                        │  update global state      │
    │  { metrics }           │                          │
    │ ◀──────────────────────│                          │
```

### Prediction Flow

```
  Client                  FastAPI                 scikit-learn
    │                        │                          │
    │  POST /api/predict      │                          │
    │  { inputs }             │                          │
    │──────────────────────▶  │                          │
    │                        │  validate inputs          │
    │                        │  scaler.transform(X)      │
    │                        │  model.predict(X_scaled)  │
    │                        │ ─────────────────────────▶│
    │                        │  model.predict_proba(X)   │
    │                        │ ─────────────────────────▶│
    │                        │         (label, prob)     │
    │                        │  ◀─────────────────────── │
    │  { prediction,         │                          │
    │    probability }       │                          │
    │ ◀──────────────────────│                          │
```

---

## 🧬 ML Pipeline Design

```
  Raw CSV Input
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  1. LOAD          pd.read_csv()              │
  │                   dropna()                   │
  └──────────────────────────────────────────────┘
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  2. PREPROCESS    X = df[feature_cols]       │
  │                   y = df["target"]           │
  │                   train_test_split(80/20)    │
  └──────────────────────────────────────────────┘
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  3. SCALE         StandardScaler.fit(X_train)│
  │                   transform(X_train, X_test) │
  └──────────────────────────────────────────────┘
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  4. TRAIN         model.fit(X_train_scaled,  │
  │                            y_train)          │
  └──────────────────────────────────────────────┘
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  5. EVALUATE      model.predict(X_test)      │
  │                   precision_score()          │
  │                   recall_score()             │
  │                   f1_score()                 │
  │                   roc_auc_score()            │
  └──────────────────────────────────────────────┘
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  6. STORE (Global State)                     │
  │     state["df"]       = df                   │
  │     state["model"]    = fitted_model         │
  │     state["scaler"]   = fitted_scaler        │
  │     state["metrics"]  = evaluation_metrics   │
  └──────────────────────────────────────────────┘
```

---

## 🌐 Frontend Component Architecture

```
  App.jsx  (Root Component)
  │
  ├── Header / Navigation
  │     └─ Theme Toggle (Dark ↔ Light)
  │
  ├── Tab: Real-time Scorer
  │     ├─ Feature Sliders (income, debts, payment_history, age, credit_cards, loan_amount)
  │     ├─ Predict Button → POST /api/predict
  │     ├─ Risk Gauge (0–100%)
  │     └─ Verdict Banner (✅ Good / ❌ Bad Credit)
  │
  ├── Tab: Model Training Hub
  │     ├─ Algorithm Selector (8 models)
  │     ├─ Train Button → POST /api/train
  │     ├─ Metrics Cards (Precision, Recall, F1, ROC-AUC)
  │     └─ Benchmark Bar Chart (ECharts)
  │
  └── Tab: Dataset Explorer
        ├─ CSV Upload → POST /api/upload
        ├─ Dataset Statistics Table
        ├─ Class Distribution Pie Chart (ECharts)
        └─ Preview Table (first 10 rows)
```

---

## 🔒 Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Secrets in code** | All config in `.env`, excluded via `.gitignore` |
| **CORS** | Restricted via `ALLOWED_ORIGINS` env variable |
| **Input validation** | Pydantic models enforce type and range at API layer |
| **CSV injection** | Only `text/csv` MIME type accepted; parsed with pandas (no eval) |
| **Serialization attacks** | All NumPy types cast to native Python before JSON response |

---

## 📦 Dependency Overview

### Backend (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.137.x | REST API framework |
| uvicorn | 0.49.x | ASGI server |
| pydantic | 2.x | Request validation |
| pandas | 3.x | DataFrame operations |
| numpy | 2.x | Numerical computing |
| scikit-learn | 1.9.x | ML algorithms & metrics |
| python-multipart | 0.0.x | File upload parsing |
| httpx | 0.28.x | Async HTTP test client |
| pytest | 9.x | Test framework |

### Frontend (`package.json`)

| Package | Purpose |
|---------|---------|
| react | UI component library |
| react-dom | DOM rendering |
| vite | Dev server & bundler |
| echarts | Chart visualizations |
| axios | HTTP client |
| lucide-react | SVG icon set |

---

## 🗂️ State Management (Backend)

The backend uses a **global in-memory dictionary** for simplicity:

```python
state = {
    "df": None,           # Active Pandas DataFrame
    "model": None,        # Fitted scikit-learn classifier
    "scaler": None,       # Fitted StandardScaler
    "feature_cols": [],   # List of feature column names
    "model_name": None,   # Name of active model
    "metrics": {}         # Last training evaluation metrics
}
```

> ⚠️ **Note**: This is a single-user, single-model in-memory design.
> For multi-user or production use, consider a database-backed session store or model registry (e.g. MLflow).

---

## 🧪 Test Architecture

```
  tests/
  ├── test_model_utils.py   (Unit Tests)
  │     ├── test_load_data()
  │     ├── test_preprocess_data()
  │     └── test_train_model[LogReg, DTree, RF, GBM, Ada, KNN, NB, SVM]
  │
  └── test_server.py        (Integration Tests)
        ├── GET  /api/data-info  (loaded state)
        ├── GET  /api/data-info  (no dataset)
        ├── POST /api/train      (all 8 models)
        ├── POST /api/train      (invalid model name)
        ├── POST /api/predict    (valid input)
        ├── POST /api/predict    (missing features)
        ├── POST /api/upload     (valid CSV)
        ├── POST /api/upload     (wrong file type)
        └── POST /api/upload     (missing target column)
```

---

## 🚧 Possible Improvements

| Priority | Improvement | Effort |
|----------|------------|--------|
| 🔴 High | Persistent model storage (joblib/pickle) | Medium |
| 🔴 High | User authentication (JWT/OAuth2) | High |
| 🟡 Medium | SHAP explainability scores in predictions | Medium |
| 🟡 Medium | PostgreSQL for multi-session support | High |
| 🟢 Low | Docker Compose for one-command setup | Low |
| 🟢 Low | Hyperparameter tuning UI (GridSearch) | Medium |
| 🟢 Low | Export model as `.pkl` download | Low |

---

*Last updated: June 2026*
