<div align="center">

```
╔═══════════════════════════════════════════════════════════════╗
║     ██████╗██████╗ ███████╗██████╗ ██╗████████╗              ║
║    ██╔════╝██╔══██╗██╔════╝██╔══██╗██║╚══██╔══╝              ║
║    ██║     ██████╔╝█████╗  ██║  ██║██║   ██║                 ║
║    ██║     ██╔══██╗██╔══╝  ██║  ██║██║   ██║                 ║
║    ╚██████╗██║  ██║███████╗██████╔╝██║   ██║                 ║
║     ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝   ╚═╝                ║
║          RISK  ANALYTICS  PLATFORM  v1.0                      ║
╚═══════════════════════════════════════════════════════════════╝
```

# 🏦 Credit Risk Analytics & Simulation Platform

> **Evaluate borrower creditworthiness in real-time using 8 advanced Machine Learning algorithms with interactive dashboards, live predictions, and explainable metrics.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.137-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/Tests-28%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](./tests)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

<br/>

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  📊 EXPLORE  │────▶│  🤖 TRAIN    │────▶│  ⚡ PREDICT  │
│   Dataset    │     │  8 ML Models │     │  Real-time   │
└──────────────┘     └──────────────┘     └──────────────┘
```

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ System Architecture](#️-system-architecture)
- [📊 ML Models & Benchmarks](#-ml-models--benchmarks)
- [🚀 Quick Start – Clone & Run](#-quick-start--clone--run)
- [📁 Project Structure](#-project-structure)
- [🔌 API Reference](#-api-reference)
- [🧪 Testing](#-testing)
- [⚙️ Environment Configuration](#️-environment-configuration)
- [🛠️ Tech Stack](#️-tech-stack)
- [📈 Performance](#-performance)

---

## ✨ Features

```
 ╔════════════════════════════════════════════════════════════╗
 ║  CORE CAPABILITIES                                         ║
 ╠════════════════════════════════════════════════════════════╣
 ║  🤖  8 Classification Algorithms (train on-demand)        ║
 ║  ⚡  Real-time Credit Scoring with Confidence Meters       ║
 ║  📂  CSV Upload & Auto Model Training                      ║
 ║  📊  Live Benchmark Comparison Charts (ECharts)            ║
 ║  🌗  Dark / Light Theme Toggle                             ║
 ║  🧪  28 Automated Tests (Model + API)                      ║
 ║  🔒  .env-based Secrets Management                         ║
 ║  📐  Robust JSON Serialization (NaN/Inf safe)              ║
 ╚════════════════════════════════════════════════════════════╝
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                           │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              React + Vite Frontend  :5173               │  │
│   │                                                         │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│   │   │  Real-time   │  │    Model     │  │  Dataset    │  │  │
│   │   │   Scorer     │  │ Training Hub │  │  Explorer   │  │  │
│   │   └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │  │
│   │          │                 │                  │         │  │
│   │          └─────────────────┴──────────────────┘         │  │
│   │                            │  axios HTTP                 │  │
│   └────────────────────────────┼────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────┘
                                 │ REST API
┌────────────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend  :8000                         │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    API Router                            │  │
│   │                                                          │  │
│   │   GET /api/data-info    POST /api/train                  │  │
│   │   POST /api/predict     POST /api/upload                 │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│   ┌─────────────────────── ▼ ───────────────────────────────┐   │
│   │                  model_utils.py                          │   │
│   │                                                          │   │
│   │   preprocess_data()   train_model()   load_data()        │   │
│   └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│   ┌────────────────────────▼────────────────────────────────┐   │
│   │               scikit-learn ML Engine                     │   │
│   │                                                          │   │
│   │   LogReg  │  DTree  │  RF  │  GBM  │  Ada  │  KNN      │   │
│   │                   NaiveBayes  │  SVM                     │   │
│   └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│   ┌────────────────────────▼────────────────────────────────┐   │
│   │              In-Memory State (Global)                    │   │
│   │                                                          │   │
│   │   df  │  model  │  scaler  │  features  │  metrics      │   │
│   └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                    credit_data.csv  (5000 rows)                   │
│                                                                   │
│   income │ debts │ payment_history │ age │ credit_cards │ target  │
└───────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
  User Input
      │
      ▼
  ┌─────────┐    CSV Upload     ┌────────────────┐
  │ Browser │ ───────────────▶ │  /api/upload   │
  │  (React)│                  │  Auto-trains   │
  └────┬────┘                  │  LogReg        │
       │                       └────────────────┘
       │ Select Algorithm
       ▼
  ┌─────────┐  POST model_name  ┌────────────────┐
  │ Trainer │ ───────────────▶ │  /api/train    │──▶ StandardScaler
  │   Tab   │                  │  Fits model    │──▶ ML Algorithm
  └─────────┘                  └────────────────┘──▶ Returns Metrics
       │
       │ Adjust sliders
       ▼
  ┌─────────┐  POST inputs      ┌────────────────┐
  │ Scorer  │ ───────────────▶ │  /api/predict  │──▶ Scale Input
  │   Tab   │                  │  Returns:      │──▶ model.predict()
  └─────────┘                  │  prediction    │──▶ predict_proba()
                               │  probability   │
                               └────────────────┘
```

---

## 📊 ML Models & Benchmarks

### Supported Classification Algorithms

| # | Algorithm | Type | Speed | Interpretability | Best For |
|---|-----------|------|-------|-----------------|---------|
| 1 | **Logistic Regression** | Linear | ⚡⚡⚡ | ⭐⭐⭐ | Baseline, linear data |
| 2 | **Decision Tree** | Tree | ⚡⚡⚡ | ⭐⭐⭐ | Rule extraction |
| 3 | **Random Forest** | Ensemble | ⚡⚡ | ⭐⭐ | General purpose |
| 4 | **Gradient Boosting** | Ensemble | ⚡ | ⭐⭐ | High accuracy |
| 5 | **AdaBoost** | Ensemble | ⚡⚡ | ⭐⭐ | Noisy-free data |
| 6 | **K-Nearest Neighbors** | Instance | ⚡ | ⭐⭐⭐ | Small datasets |
| 7 | **Naive Bayes** | Probabilistic | ⚡⚡⚡ | ⭐⭐⭐ | Quick baseline |
| 8 | **Support Vector Machine** | Kernel | ⚡ | ⭐ | High-dimensional |

### Performance Benchmarks (Reference)

| Algorithm | Precision | Recall | F1-Score | ROC-AUC | Rank |
|-----------|:---------:|:------:|:--------:|:-------:|:----:|
| 🥇 Gradient Boosting | **0.87** | **0.85** | **0.86** | **0.93** | 1st |
| 🥈 Random Forest | 0.86 | 0.84 | 0.85 | 0.92 | 2nd |
| 🥉 Support Vector Machine | 0.85 | 0.82 | 0.83 | 0.91 | 3rd |
| AdaBoost | 0.84 | 0.83 | 0.83 | 0.90 | 4th |
| Logistic Regression | 0.82 | 0.79 | 0.80 | 0.88 | 5th |
| Naive Bayes | 0.80 | 0.74 | 0.77 | 0.85 | 6th |
| K-Nearest Neighbors | 0.79 | 0.77 | 0.78 | 0.82 | 7th |
| Decision Tree | 0.76 | 0.78 | 0.77 | 0.77 | 8th |

### Dataset Overview

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `income` | Continuous | 20K – 120K | Annual income in USD |
| `debts` | Continuous | 1K – 48K | Total outstanding debts |
| `payment_history` | Ordinal | 0 – 5 | Past payment behavior score |
| `age` | Discrete | 18 – 70 | Borrower age in years |
| `credit_cards` | Discrete | 0 – 5 | Number of active credit cards |
| `loan_amount` | Continuous | 2K – 57K | Requested loan amount |
| `target` | Binary | 0 / 1 | **0** = Bad Credit, **1** = Good Credit |

```
  Dataset Distribution (5,000 records)
  
  Good Credit ████████████████████████████ ~50%
  Bad Credit  █████████████████████████    ~50%
  
  Training Set  ████████████████████████████████████████ 80% (4,000)
  Test Set      ██████████ 20% (1,000)
```

---

## 🚀 Quick Start – Clone & Run

### Prerequisites

```
  ✅  Python 3.10+
  ✅  Node.js 18+
  ✅  npm 9+
  ✅  Git
```

### Step 1 — Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/YOUR_USERNAME/credit-scoring-model.git

# Navigate into the project
cd credit-scoring-model
```

### Step 2 — Backend Setup (Python + FastAPI)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Open .env and adjust values if needed (defaults work out of the box)
```

### Step 4 — Start the Backend Server

```bash
python server.py
# ✅  Uvicorn running on http://127.0.0.1:8000
# ✅  Default dataset loaded & Random Forest auto-trained
```

### Step 5 — Frontend Setup (React + Vite)

```bash
# Open a new terminal, navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start the dev server
npm run dev
# ✅  VITE ready → http://localhost:5173
```

### Step 6 — Open the App 🎉

```
  Browser → http://localhost:5173
  
  ┌────────────────────────────────────────────┐
  │   Credit Risk Analytics Platform           │
  │                                            │
  │   [Real-time Scorer] [Training Hub] [Data] │
  │                                            │
  │   ✅ Backend connected – 5,000 records     │
  └────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
credit-scoring-model/
│
├── 📄 server.py              ← FastAPI application & all API endpoints
├── 📄 model_utils.py         ← ML preprocessing & training logic
├── 📄 credit_data.csv        ← Default dataset (5,000 records)
├── 📄 requirements.txt       ← Python dependencies
├── 📄 .env                   ← Local secrets (git-ignored)
├── 📄 .env.example           ← Environment template (committed)
├── 📄 .gitignore             ← Git ignore rules
│
├── 📁 tests/
│   ├── 📄 test_model_utils.py ← Unit tests for ML logic (10 tests)
│   └── 📄 test_server.py      ← API integration tests (18 tests)
│
└── 📁 frontend/
    ├── 📄 index.html          ← HTML entry point
    ├── 📄 package.json        ← Node dependencies & scripts
    ├── 📄 vite.config.js      ← Vite configuration
    └── 📁 src/
        ├── 📄 main.jsx        ← React entry point
        ├── 📄 App.jsx         ← Main application component
        ├── 📄 App.css         ← Component styles
        └── 📄 index.css       ← Global design system
```

---

## 🔌 API Reference

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|---------|
| `GET` | `/` | Health check | — | `{ message }` |
| `GET` | `/api/data-info` | Dataset stats + active model metrics | — | `{ columns, statistics, preview, target_distribution, rows_count, model_name, metrics }` |
| `POST` | `/api/train` | Train a selected ML model | `{ model_name }` | `{ status, model_name, metrics }` |
| `POST` | `/api/predict` | Predict credit risk for input | `{ inputs: { feature: value } }` | `{ prediction, probability, model_name }` |
| `POST` | `/api/upload` | Upload CSV and auto-train | `multipart/form-data` (file) | Dataset info + model metrics |

### Example: Train a Model

```bash
curl -X POST http://localhost:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{"model_name": "Gradient Boosting"}'
```

```json
{
  "status": "success",
  "model_name": "Gradient Boosting",
  "metrics": {
    "Precision": 0.871,
    "Recall": 0.853,
    "F1-Score": 0.862,
    "ROC-AUC": 0.934
  }
}
```

### Example: Run a Prediction

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "income": 85000,
      "debts": 12000,
      "payment_history": 4,
      "age": 35,
      "credit_cards": 2,
      "loan_amount": 25000
    }
  }'
```

```json
{
  "prediction": 1,
  "probability": 0.892,
  "model_name": "Gradient Boosting"
}
```

---

## 🧪 Testing

```bash
# Activate virtual environment first
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # macOS/Linux

# Run full test suite
python -m pytest

# Run with verbose output
python -m pytest -v

# Run only model logic tests
python -m pytest tests/test_model_utils.py -v

# Run only API tests
python -m pytest tests/test_server.py -v
```

### Test Coverage

```
  Test Results ──────────────────────────────────────────
  
  test_model_utils.py   ██████████  10 / 10 passed ✅
  test_server.py        ██████████  18 / 18 passed ✅
  
  Total                 ██████████  28 / 28 passed ✅
  Duration              ~14.6 seconds
  
  Tests cover:
  ├── Data preprocessing (dropna, scaling, feature split)
  ├── Model training for all 8 algorithms
  ├── GET /api/data-info (loaded & unloaded states)
  ├── POST /api/predict (valid & missing features)
  ├── POST /api/train (all 8 models + invalid name)
  └── POST /api/upload (CSV, wrong type, missing target)
```

---

## ⚙️ Environment Configuration

```bash
# .env (copy from .env.example — never commit this file)

HOST=127.0.0.1                              # Server bind address
PORT=8000                                   # Server port
ALLOWED_ORIGINS=http://localhost:5173       # CORS allowed origins
DEFAULT_DATASET_PATH=credit_data.csv        # Dataset file path
DEFAULT_MODEL=Random Forest                 # Auto-trained model on startup
```

---

## 🛠️ Tech Stack

```
  ┌─────────────────────────────────────────────────────┐
  │  BACKEND                                            │
  │                                                     │
  │  Python 3.12     ────  Core language                │
  │  FastAPI 0.137   ────  REST API framework           │
  │  Uvicorn 0.49    ────  ASGI server                  │
  │  scikit-learn    ────  ML algorithms & metrics      │
  │  pandas 3.x      ────  Data manipulation            │
  │  numpy 2.x       ────  Numerical operations         │
  │  pydantic 2.x    ────  Request/Response validation  │
  └─────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────┐
  │  FRONTEND                                           │
  │                                                     │
  │  React 18        ────  UI component library         │
  │  Vite 8          ────  Build tool & dev server      │
  │  ECharts         ────  Charts & visualizations      │
  │  Axios           ────  HTTP client                  │
  │  Lucide React    ────  Icon library                 │
  │  Vanilla CSS     ────  Custom design system         │
  └─────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────┐
  │  TOOLING                                            │
  │                                                     │
  │  pytest 9.1      ────  Test framework               │
  │  httpx 0.28      ────  HTTP test client             │
  │  Git             ────  Version control              │
  └─────────────────────────────────────────────────────┘
```

---

## 📈 Performance

```
  API Response Times (approximate)
  ─────────────────────────────────────────────
  GET  /api/data-info          ~  5 ms
  POST /api/predict            ~ 10 ms
  POST /api/train (LogReg)     ~ 200 ms
  POST /api/train (Random Forest)  ~ 800 ms
  POST /api/train (Gradient Boosting) ~ 2 s
  POST /api/train (SVM)        ~ 3 s
  POST /api/upload (5000 rows) ~ 1 s
```

---

## 🤝 Contributing

```
  1.  Fork the repository
  2.  Create your feature branch  →  git checkout -b feature/amazing-feature
  3.  Commit your changes         →  git commit -m 'Add amazing feature'
  4.  Push to the branch          →  git push origin feature/amazing-feature
  5.  Open a Pull Request
```

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

```
  Built with ❤️ using Python, FastAPI, React & scikit-learn
  
  ⭐ Star this repo if you found it useful!
```

[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/credit-scoring-model?style=social)](https://github.com/YOUR_USERNAME/credit-scoring-model)

</div>
