# 🏗️ Architecture & Design Document

> Technical deep-dive into the design, data flow, ML pipeline, and component structure of the Credit Risk Analytics Platform.

---

## 📋 Table of Contents

| Section | Description |
|---------|-------------|
| [🧱 High-Level Architecture](#-high-level-architecture) | Three-tier system overview |
| [🔁 Request Lifecycle](#-request-lifecycle) | Training & prediction flows |
| [🧬 ML Pipeline](#-ml-pipeline) | Step-by-step ML process |
| [🖥️ Frontend Components](#️-frontend-component-tree) | React component hierarchy |
| [💾 State Management](#-backend-state-management) | Global state design |
| [🔒 Security Model](#-security-model) | Threats and mitigations |
| [📦 Dependencies](#-dependency-overview) | All packages explained |
| [🧪 Test Architecture](#-test-architecture) | Test structure and coverage |
| [🚧 Future Improvements](#-future-improvements) | Roadmap |

---

## 🧱 High-Level Architecture

The platform uses a **Three-Tier Architecture**:

```mermaid
graph TB
    subgraph Tier1["Tier 1 — Presentation  :5173"]
        A[Real-time Scorer]
        B[Model Training Hub]
        C[Dataset Explorer]
    end

    subgraph Tier2["Tier 2 — Application  :8000"]
        D[FastAPI Router]
        E[model_utils.py]
        F[In-Memory State]
    end

    subgraph Tier3["Tier 3 — Data"]
        G[(credit_data.csv)]
    end

    A -->|HTTP POST /api/predict| D
    B -->|HTTP POST /api/train| D
    C -->|HTTP GET /api/data-info\nHTTP POST /api/upload| D
    D --> E
    E --> F
    F -.->|read/write| G
```

---

## 🔁 Request Lifecycle

### Training Flow

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8000
    participant M as model_utils.py
    participant S as scikit-learn

    C->>A: POST /api/train { model_name }
    A->>M: load_data(path)
    M-->>A: DataFrame
    A->>M: preprocess_data(df)
    M-->>A: X_train, X_test, y_train, y_test
    A->>M: train_model(name, X_train, y_train)
    M->>S: model.fit(X_scaled, y)
    S-->>M: fitted model
    M-->>A: model + metrics
    A-->>C: { status, model_name, metrics }
```

### Prediction Flow

```mermaid
sequenceDiagram
    participant C as Client (React)
    participant A as FastAPI :8000
    participant S as scikit-learn

    C->>A: POST /api/predict { inputs }
    A->>A: Pydantic validation
    A->>A: scaler.transform(X)
    A->>S: model.predict(X_scaled)
    S-->>A: label [0 or 1]
    A->>S: model.predict_proba(X_scaled)
    S-->>A: probability [0.0 – 1.0]
    A-->>C: { prediction, probability, model_name }
```

---

## 🧬 ML Pipeline

```mermaid
flowchart TD
    A[📂 CSV File] --> B[Load\npd.read_csv · dropna]
    B --> C[Split Features & Target\nX = features · y = target]
    C --> D[Train/Test Split\n80% train · 20% test]
    D --> E[Scale Features\nStandardScaler.fit on train]
    E --> F[Train Classifier\nmodel.fit on X_train_scaled]
    F --> G[Evaluate on Test Set\npredict · predict_proba]
    G --> H{Metrics}
    H --> H1[Precision]
    H --> H2[Recall]
    H --> H3[F1-Score]
    H --> H4[ROC-AUC]
    H1 & H2 & H3 & H4 --> I[(Global State\nmodel · scaler · metrics)]
```

### Algorithm Parameters

| Algorithm | Key Parameters |
|-----------|---------------|
| Logistic Regression | `max_iter=1000` |
| Decision Tree | `random_state=42` |
| Random Forest | `n_estimators=100`, `random_state=42` |
| Gradient Boosting | `n_estimators=100`, `random_state=42` |
| AdaBoost | `n_estimators=100`, `random_state=42` |
| K-Nearest Neighbors | `n_neighbors=5` |
| Naive Bayes | GaussianNB (defaults) |
| SVM | `probability=True`, `random_state=42` |

---

## 🖥️ Frontend Component Tree

```mermaid
graph TD
    App["App.jsx (Root)"]

    App --> Header["Header\nNav · Theme Toggle"]
    App --> Tab1["Tab: Real-time Scorer"]
    App --> Tab2["Tab: Model Training Hub"]
    App --> Tab3["Tab: Dataset Explorer"]

    Tab1 --> Sliders["Feature Sliders\nincome · debts · age\npayment_history · credit_cards · loan_amount"]
    Tab1 --> PredBtn["Predict Button\nPOST /api/predict"]
    Tab1 --> Gauge["Risk Gauge\n0 – 100%"]
    Tab1 --> Verdict["Verdict Banner\nGood / Bad Credit"]

    Tab2 --> ModelSel["Algorithm Selector\n8 models"]
    Tab2 --> TrainBtn["Train Button\nPOST /api/train"]
    Tab2 --> Metrics["Metrics Cards\nPrecision · Recall · F1 · ROC-AUC"]
    Tab2 --> Chart1["Benchmark Bar Chart\nECharts"]

    Tab3 --> Upload["CSV Upload\nPOST /api/upload"]
    Tab3 --> Stats["Statistics Table"]
    Tab3 --> Chart2["Distribution Pie Chart\nECharts"]
    Tab3 --> Preview["Data Preview\nfirst 10 rows"]
```

---

## 💾 Backend State Management

The backend uses a **global in-memory dictionary** shared across all requests:

```python
state = {
    "df":           None,   # Active Pandas DataFrame
    "model":        None,   # Fitted scikit-learn classifier
    "scaler":       None,   # Fitted StandardScaler instance
    "feature_cols": [],     # List of input feature column names
    "model_name":   None,   # Name of the currently active model
    "metrics":      {}      # Last evaluation: Precision, Recall, F1, ROC-AUC
}
```

### State Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Empty : App Start
    Empty --> Loaded : GET /api/data-info\nor POST /api/upload
    Loaded --> Trained : POST /api/train
    Trained --> Trained : POST /api/train (retrain)
    Trained --> Predicting : POST /api/predict
    Predicting --> Trained : Response Sent
```

> **Note:** Single-user, single-session design. For production, use a model registry (e.g. MLflow) or database-backed session store.

---

## 🔒 Security Model

| Threat | Mitigation |
|--------|-----------|
| Secrets in source code | All config in `.env` — excluded via `.gitignore` |
| Cross-origin attacks | CORS restricted via `ALLOWED_ORIGINS` env variable |
| Malformed inputs | Pydantic models enforce types and ranges at API boundary |
| Malicious CSV files | Only `text/csv` MIME accepted; parsed safely with pandas |
| JSON serialization | All NumPy types cast to native Python before response |
| Exposed internal files | `.dockerignore`, `.gitignore`, `.env.*` — never pushed |

---

## 📦 Dependency Overview

### Backend (`requirements.txt`)

| Package | Version | Purpose |
|---------|:-------:|---------|
| `fastapi` | 0.137 | REST API framework |
| `uvicorn` | 0.49 | ASGI server |
| `pydantic` | 2.x | Request/response validation |
| `pandas` | 3.x | DataFrame operations |
| `numpy` | 2.x | Numerical computing |
| `scikit-learn` | 1.9 | ML algorithms & evaluation |
| `python-multipart` | 0.0.x | File upload parsing |
| `httpx` | 0.28 | Async HTTP client for tests |
| `pytest` | 9.x | Test runner |

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

```mermaid
graph LR
    Tests["tests/"]
    Tests --> UnitTests["test_model_utils.py\n10 Unit Tests"]
    Tests --> IntTests["test_server.py\n18 Integration Tests"]

    UnitTests --> U1[test_load_data]
    UnitTests --> U2[test_preprocess_data]
    UnitTests --> U3["test_train_model\n× 8 algorithms"]

    IntTests --> I1["GET /api/data-info\nloaded & empty state"]
    IntTests --> I2["POST /api/train\n8 models + invalid"]
    IntTests --> I3["POST /api/predict\nvalid + missing features"]
    IntTests --> I4["POST /api/upload\nCSV + wrong type + no target"]
```

### Running Tests

```bash
# Full suite
python -m pytest

# With verbose output
python -m pytest -v

# Specific file
python -m pytest tests/test_server.py -v
```

---

## 🚧 Future Improvements

| Priority | Improvement | Effort | Impact |
|:--------:|-------------|:------:|:------:|
| 🔴 High | Persistent model storage (joblib) | Medium | High |
| 🔴 High | User authentication (JWT / OAuth2) | High | High |
| 🟡 Medium | SHAP explainability in predictions | Medium | Medium |
| 🟡 Medium | PostgreSQL for multi-session support | High | High |
| 🟢 Low | Docker Compose one-command setup | Low | Medium |
| 🟢 Low | Hyperparameter tuning UI (GridSearch) | Medium | Medium |
| 🟢 Low | Export trained model as `.pkl` download | Low | Low |

---

*Last updated: June 2026 · [← Back to README](./README.md)*
