# 🏦 Credit Risk Analytics & Simulation Platform

> A data-driven platform that uses **8 Machine Learning algorithms** to assess credit risk, predict loan defaults, and evaluate borrower creditworthiness in real-time.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.137-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Vite-8.0-646CFF?style=flat-square&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/scikit--learn-1.9-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Tests-28%20Passing-28a745?style=flat-square&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [ML Models & Benchmarks](#-ml-models--benchmarks)
- [Dataset Overview](#-dataset-overview)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Tech Stack](#-tech-stack)

---

## 🎯 Overview

The **Credit Risk Analytics Platform** helps financial institutions make smarter lending decisions by evaluating borrower profiles against trained ML models. It features a live scoring dashboard, model comparison charts, and a dataset explorer — all in one responsive web application.

| Component | Technology | Port |
|-----------|-----------|------|
| Frontend UI | React + Vite | `5173` |
| Backend API | Python + FastAPI | `8000` |
| ML Engine | scikit-learn | — |
| Data Source | CSV (Pandas) | — |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **8 ML Algorithms** | Train and compare models on-demand |
| ⚡ **Real-time Scoring** | Live credit score with probability meter |
| 📂 **CSV Upload** | Upload your own dataset and auto-train |
| 📊 **Benchmark Charts** | Side-by-side model performance comparison |
| 🌗 **Theme Toggle** | Dark & Light mode support |
| 🧪 **28 Automated Tests** | Full model + API test coverage |
| 🔒 **Secrets Management** | Environment-based config via `.env` |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    BROWSER  :5173                        │
│                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │
│   │  Real-time  │  │   Model     │  │   Dataset     │  │
│   │   Scorer    │  │ Training Hub│  │   Explorer    │  │
│   └──────┬──────┘  └──────┬──────┘  └──────┬────────┘  │
│          └────────────────┴─────────────────┘           │
│                           │  HTTP / Axios               │
└───────────────────────────┼─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                  FastAPI Backend  :8000                  │
│                                                          │
│   GET  /api/data-info     POST /api/train               │
│   POST /api/predict        POST /api/upload              │
│                            │                             │
│   ┌────────────────────────▼──────────────────────────┐ │
│   │              model_utils.py                       │ │
│   │   load → preprocess → scale → train → evaluate   │ │
│   └────────────────────────┬──────────────────────────┘ │
│                            │                             │
│   ┌────────────────────────▼──────────────────────────┐ │
│   │          In-Memory State (Global Dict)            │ │
│   │   df | model | scaler | features | metrics        │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│           credit_data.csv  (5,000 records)               │
│   income │ debts │ payment_history │ age │ target        │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 ML Models & Benchmarks

### Supported Algorithms

| # | Algorithm | Type | Speed | Best For |
|---|-----------|------|:-----:|---------|
| 1 | Logistic Regression | Linear | ⚡⚡⚡ | Baseline & linear data |
| 2 | Decision Tree | Tree-based | ⚡⚡⚡ | Interpretable rules |
| 3 | Random Forest | Ensemble | ⚡⚡ | General purpose |
| 4 | Gradient Boosting | Ensemble | ⚡ | Highest accuracy |
| 5 | AdaBoost | Ensemble | ⚡⚡ | Low-noise datasets |
| 6 | K-Nearest Neighbors | Instance-based | ⚡ | Small datasets |
| 7 | Naive Bayes | Probabilistic | ⚡⚡⚡ | Quick baseline |
| 8 | Support Vector Machine | Kernel-based | ⚡ | High-dimensional data |

### Performance Comparison

| Algorithm | Precision | Recall | F1-Score | ROC-AUC |
|-----------|:---------:|:------:|:--------:|:-------:|
| 🥇 Gradient Boosting | **0.87** | **0.85** | **0.86** | **0.93** |
| 🥈 Random Forest | 0.86 | 0.84 | 0.85 | 0.92 |
| 🥉 SVM | 0.85 | 0.82 | 0.83 | 0.91 |
| AdaBoost | 0.84 | 0.83 | 0.83 | 0.90 |
| Logistic Regression | 0.82 | 0.79 | 0.80 | 0.88 |
| Naive Bayes | 0.80 | 0.74 | 0.77 | 0.85 |
| KNN | 0.79 | 0.77 | 0.78 | 0.82 |
| Decision Tree | 0.76 | 0.78 | 0.77 | 0.77 |

---

## 📁 Dataset Overview

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `income` | Continuous | 20K – 120K | Annual income (USD) |
| `debts` | Continuous | 1K – 48K | Total outstanding debts |
| `payment_history` | Ordinal | 0 – 5 | Past payment behavior score |
| `age` | Discrete | 18 – 70 | Borrower age |
| `credit_cards` | Discrete | 0 – 5 | Number of active credit cards |
| `loan_amount` | Continuous | 2K – 57K | Requested loan amount |
| `target` | Binary | 0 / 1 | `0` = Bad Credit · `1` = Good Credit |

> **5,000 total records** — 80% training / 20% test split

---

## 🚀 Getting Started

### Prerequisites

- Python `3.10+`
- Node.js `18+`
- npm `9+`
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/chandru-collab/Credit-Risk-Analytics-Platform.git
cd Credit-Risk-Analytics-Platform
```

### Step 2 — Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Configure Environment

```bash
# Create your local env file
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

Edit `.env` with your values:

```env
HOST=127.0.0.1
PORT=8000
ALLOWED_ORIGINS=http://localhost:5173
DEFAULT_DATASET_PATH=credit_data.csv
DEFAULT_MODEL=Random Forest
```

### Step 4 — Start Backend

```bash
python server.py
# ✅ Uvicorn running on http://127.0.0.1:8000
```

### Step 5 — Start Frontend

```bash
# Open a new terminal
cd frontend
npm install
npm run dev
# ✅ VITE ready → http://localhost:5173
```

### Step 6 — Open the App

```
http://localhost:5173
```

---

## 📂 Project Structure

```
Credit-Risk-Analytics-Platform/
│
├── server.py                   ← FastAPI app & all API endpoints
├── model_utils.py              ← ML preprocessing & training logic
├── credit_data.csv             ← Default dataset (5,000 records)
├── requirements.txt            ← Python dependencies
│
├── tests/
│   ├── test_model_utils.py     ← Unit tests for ML logic (10 tests)
│   └── test_server.py          ← API integration tests (18 tests)
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx             ← Main application component
        ├── App.css
        └── index.css
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/data-info` | Dataset stats + active model metrics |
| `POST` | `/api/train` | Train a selected ML model |
| `POST` | `/api/predict` | Predict credit risk for input |
| `POST` | `/api/upload` | Upload CSV and auto-train |

### Train a Model

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

### Run a Prediction

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
# Run all 28 tests
python -m pytest

# Verbose output
python -m pytest -v

# Run specific test files
python -m pytest tests/test_model_utils.py -v
python -m pytest tests/test_server.py -v
```

### Test Coverage

| Test File | Tests | Coverage |
|-----------|------:|---------|
| `test_model_utils.py` | 10 | Data loading, preprocessing, all 8 model trains |
| `test_server.py` | 18 | All endpoints, edge cases, error handling |
| **Total** | **28** | **100% passing ✅** |

---

## 🛠️ Tech Stack

### Backend

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.12 | Core language |
| FastAPI | 0.137 | REST API framework |
| Uvicorn | 0.49 | ASGI server |
| scikit-learn | 1.9 | ML algorithms & metrics |
| Pandas | 3.x | Data manipulation |
| NumPy | 2.x | Numerical operations |
| Pydantic | 2.x | Request validation |
| pytest + httpx | 9.x / 0.28 | Testing framework |

### Frontend

| Package | Purpose |
|---------|---------|
| React 18 | UI component library |
| Vite 8 | Build tool & dev server |
| ECharts | Charts & visualizations |
| Axios | HTTP client |
| Lucide React | Icon library |

---

## 📄 License

This project is licensed under the **MIT License**.

---

<p align="center">
  Built with ❤️ using Python · FastAPI · React · scikit-learn
  <br/>
  ⭐ Star this repo if you found it useful!
</p>
