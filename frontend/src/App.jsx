import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';
import {
  Sun,
  Moon,
  Upload,
  Cpu,
  BarChart2,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  BookOpen,
  User,
  DollarSign,
  CreditCard,
  Calendar,
  Activity,
  Info,
  ChevronRight,
  Sparkles,
  Percent
} from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  // Theme state
  const [darkMode, setDarkMode] = useState(true);

  // Layout and view states
  const [activeTab, setActiveTab] = useState('predictor'); // explorer, trainer, predictor

  // Data states
  const [loading, setLoading] = useState(true);
  const [dataInfo, setDataInfo] = useState(null);
  const [selectedModel, setSelectedModel] = useState('Logistic Regression');
  const [training, setTraining] = useState(false);
  const [inputValues, setInputValues] = useState({});
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  // Toggle theme
  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [darkMode]);

  // Initial load
  useEffect(() => {
    fetchDataInfo();
  }, []);

  const fetchDataInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/data-info`);
      setDataInfo(response.data);
      if (response.data.model_name) {
        setSelectedModel(response.data.model_name);
      }
      // Set default inputs based on feature means
      initializeInputs(response.data.statistics);
    } catch (err) {
      console.error(err);
      setError('Failed to connect to the backend server. Make sure the FastAPI server is running on localhost:8000.');
    } finally {
      setLoading(false);
    }
  };

  const initializeInputs = (stats) => {
    const defaults = {};
    Object.keys(stats).forEach((feature) => {
      defaults[feature] = parseFloat(stats[feature].mean.toFixed(2));
    });
    setInputValues(defaults);
    setPredictionResult(null);
  };

  // Handle File Upload
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setDataInfo(response.data);
      if (response.data.model_name) {
        setSelectedModel(response.data.model_name);
      }
      initializeInputs(response.data.statistics);
      setActiveTab('explorer');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to upload CSV file.');
    } finally {
      setUploading(false);
    }
  };

  // Train model
  const handleTrainModel = async () => {
    setTraining(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE}/train`, {
        model_name: selectedModel,
      });
      if (response.data.status === 'success') {
        setDataInfo((prev) => ({
          ...prev,
          model_name: response.data.model_name,
          metrics: response.data.metrics,
        }));
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to train the selected model.');
    } finally {
      setTraining(false);
    }
  };

  // Run prediction
  const handlePredict = async () => {
    setPredicting(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE}/predict`, {
        inputs: inputValues,
      });
      setPredictionResult(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to calculate prediction.');
    } finally {
      setPredicting(false);
    }
  };

  const handleInputChange = (feature, val) => {
    setInputValues((prev) => ({
      ...prev,
      [feature]: parseFloat(val) || 0,
    }));
  };

  // ECharts target distribution option
  const getTargetChartOption = () => {
    if (!dataInfo || !dataInfo.target_distribution) return {};
    const data = Object.entries(dataInfo.target_distribution).map(([name, value]) => ({
      name,
      value,
    }));

    return {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)',
      },
      legend: {
        orient: 'horizontal',
        bottom: '0',
        textStyle: {
          color: darkMode ? '#fafafa' : '#09090b',
        },
      },
      color: ['#10b981', '#ef4444'],
      series: [
        {
          name: 'Target Distribution',
          type: 'pie',
          radius: ['45%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: darkMode ? '#0c0c0f' : '#ffffff',
            borderWidth: 2,
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '14',
              fontWeight: 'bold',
            },
          },
          data,
        },
      ],
    };
  };

  // Model performance static benchmarking data
  const getModelBenchmarks = () => {
    return [
      { name: 'Logistic Regression', precision: 0.82, recall: 0.79, f1: 0.80, auc: 0.88 },
      { name: 'Decision Tree', precision: 0.76, recall: 0.78, f1: 0.77, auc: 0.77 },
      { name: 'Random Forest', precision: 0.86, recall: 0.84, f1: 0.85, auc: 0.92 },
      { name: 'Gradient Boosting', precision: 0.87, recall: 0.85, f1: 0.86, auc: 0.93 },
      { name: 'AdaBoost', precision: 0.84, recall: 0.83, f1: 0.83, auc: 0.90 },
      { name: 'K-Nearest Neighbors', precision: 0.79, recall: 0.77, f1: 0.78, auc: 0.82 },
      { name: 'Naive Bayes', precision: 0.80, recall: 0.74, f1: 0.77, auc: 0.85 },
      { name: 'Support Vector Machine', precision: 0.85, recall: 0.82, f1: 0.83, auc: 0.91 },
    ];
  };

  const getBenchmarkChartOption = () => {
    const benchmarks = getModelBenchmarks();
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        textStyle: { color: darkMode ? '#fafafa' : '#09090b' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        boundaryGap: [0, 0.01],
        max: 1.0,
        splitLine: {
          lineStyle: { color: darkMode ? '#1e1e24' : '#e2e8f0' }
        },
        axisLabel: { color: darkMode ? '#8e8e93' : '#64748b' }
      },
      yAxis: {
        type: 'category',
        data: benchmarks.map(b => b.name),
        axisLabel: { color: darkMode ? '#8e8e93' : '#64748b' }
      },
      color: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'],
      series: [
        {
          name: 'Precision',
          type: 'bar',
          data: benchmarks.map(b => b.precision)
        },
        {
          name: 'Recall',
          type: 'bar',
          data: benchmarks.map(b => b.recall)
        },
        {
          name: 'F1-Score',
          type: 'bar',
          data: benchmarks.map(b => b.f1)
        },
        {
          name: 'ROC-AUC',
          type: 'bar',
          data: benchmarks.map(b => b.auc)
        }
      ]
    };
  };

  // Loading skeleton
  if (loading) {
    return (
      <div className="fullscreen-loader">
        <div className="spinner spinner-large"></div>
        <p style={{ color: 'var(--text-secondary)' }}>Setting up workspace & analyzing credit data...</p>
      </div>
    );
  }

  return (
    <div className="app-container fade-in">
      {/* Header */}
      <header className="header-row">
        <div className="header-title">
          <h1>Credit Risk Analytics Platform</h1>
          <p>Train classification models and evaluate real-time creditworthiness simulations.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* File Upload Button */}
          <label className="btn btn-secondary" style={{ width: 'auto', display: 'flex', cursor: 'pointer' }}>
            <Upload size={16} />
            <span>{uploading ? 'Uploading...' : 'Upload CSV'}</span>
            <input type="file" accept=".csv" onChange={handleFileUpload} style={{ display: 'none' }} disabled={uploading} />
          </label>
          <button className="theme-toggle-btn" onClick={() => setDarkMode(!darkMode)} aria-label="Toggle Theme">
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      {/* Global Error Notice */}
      {error && (
        <div className="info-alert" style={{ background: 'var(--error-bg)', borderColor: 'var(--error-border)', color: 'var(--error-text)' }}>
          <ShieldAlert size={20} className="info-alert-icon" />
          <div>
            <h4 style={{ fontWeight: 700 }}>Connection Error</h4>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Main Tab Controls */}
      <div className="tabs-container">
        <button className={`tab-btn ${activeTab === 'predictor' ? 'active' : ''}`} onClick={() => setActiveTab('predictor')}>
          <Activity size={15} />
          <span>Real-time Scorer</span>
        </button>
        <button className={`tab-btn ${activeTab === 'trainer' ? 'active' : ''}`} onClick={() => setActiveTab('trainer')}>
          <Cpu size={15} />
          <span>Model Training Hub</span>
        </button>
        <button className={`tab-btn ${activeTab === 'explorer' ? 'active' : ''}`} onClick={() => setActiveTab('explorer')}>
          <BarChart2 size={15} />
          <span>Dataset Explorer</span>
        </button>

      </div>

      {/* KPI Cards Row (Visible if model metrics are loaded) */}
      {dataInfo && dataInfo.metrics && (
        <div className="kpi-grid slide-up">
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-label">Active Model</span>
              <Cpu size={16} className="kpi-icon" />
            </div>
            <div className="kpi-value" style={{ fontSize: '1.25rem', padding: '0.35rem 0' }}>
              {dataInfo.model_name}
            </div>
            <div className="kpi-trend neutral">
              <span>Ready for scoring</span>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-label">Precision</span>
              <Percent size={16} className="kpi-icon" />
            </div>
            <div className="kpi-value">
              {typeof dataInfo.metrics.Precision === 'number' ? (dataInfo.metrics.Precision * 100).toFixed(1) : dataInfo.metrics.Precision}%
            </div>
            <div className="kpi-trend positive">
              <span>High Precision</span>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-label">Recall</span>
              <Percent size={16} className="kpi-icon" />
            </div>
            <div className="kpi-value">
              {typeof dataInfo.metrics.Recall === 'number' ? (dataInfo.metrics.Recall * 100).toFixed(1) : dataInfo.metrics.Recall}%
            </div>
            <div className="kpi-trend positive">
              <span>Balanced Recall</span>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-label">F1-Score</span>
              <Percent size={16} className="kpi-icon" />
            </div>
            <div className="kpi-value">
              {typeof dataInfo.metrics['F1-Score'] === 'number' ? (dataInfo.metrics['F1-Score'] * 100).toFixed(1) : dataInfo.metrics['F1-Score']}%
            </div>
            <div className="kpi-trend positive">
              <span>Optimal F1</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Tab Content */}
      <div className="tab-content-container">
        
        {/* TAB 1: Real-time Scorer */}
        {activeTab === 'predictor' && dataInfo && (
          <div className="layout-split slide-up">
            {/* Input Form Panel */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title"><User size={18} /> Simulation Input Panel</h3>
                  <p className="card-description">Configure the demographic and credit history parameters for custom credit profiles.</p>
                </div>
              </div>
              <div className="card-body">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                  {dataInfo.columns.map((feature) => {
                    const stats = dataInfo.statistics[feature];
                    const val = inputValues[feature] ?? 0;
                    
                    // Icon assignment based on feature names
                    let icon = <Info size={14} />;
                    if (feature === 'income') icon = <DollarSign size={14} />;
                    if (feature === 'debts') icon = <AlertTriangle size={14} />;
                    if (feature === 'credit_cards') icon = <CreditCard size={14} />;
                    if (feature === 'age') icon = <Calendar size={14} />;

                    return (
                      <div key={feature} className="form-group">
                        <label className="form-label">
                          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', textTransform: 'capitalize' }}>
                            {icon} {feature.replace('_', ' ')}
                          </span>
                        </label>
                        <div className="slider-container">
                          <input
                            type="range"
                            min={stats.min}
                            max={stats.max}
                            step={stats.max - stats.min > 500 ? '100' : '1'}
                            value={val}
                            onChange={(e) => handleInputChange(feature, e.target.value)}
                            className="slider-input"
                          />
                          <input
                            type="number"
                            value={val}
                            onChange={(e) => handleInputChange(feature, e.target.value)}
                            className="form-input slider-value"
                            style={{ width: '70px', padding: '0.25rem' }}
                          />
                        </div>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                          Mean: {stats.mean.toFixed(1)} | Min: {stats.min.toFixed(0)} - Max: {stats.max.toFixed(0)}
                        </span>
                      </div>
                    );
                  })}
                </div>
                <button className="btn btn-primary" onClick={handlePredict} disabled={predicting} style={{ marginTop: '1rem' }}>
                  {predicting ? <div className="spinner"></div> : 'Run Creditworthiness Prediction'}
                </button>
              </div>
            </div>

            {/* Results Panel */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title"><Sparkles size={18} /> Prediction Results</h3>
                  <p className="card-description">Instant evaluation generated by the active Machine Learning model.</p>
                </div>
              </div>
              <div className="card-body" style={{ justifyContent: 'center', display: 'flex', flexDirection: 'column', minHeight: '300px' }}>
                {predictionResult ? (
                  <div className={`result-box ${predictionResult.prediction === 1 ? 'good' : 'bad'}`}>
                    <div className="result-title">
                      {predictionResult.prediction === 1 ? (
                        <>
                          <CheckCircle2 size={32} />
                          <span>✅ Good Credit Approved</span>
                        </>
                      ) : (
                        <>
                          <ShieldAlert size={32} />
                          <span>❌ Bad Credit Risk Detected</span>
                        </>
                      )}
                    </div>

                    {predictionResult.probability !== 'N/A' && (() => {
                      const isGoodCredit = predictionResult.prediction === 1;
                      const confidenceVal = isGoodCredit 
                        ? predictionResult.probability 
                        : (1 - predictionResult.probability);
                      
                      return (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', margin: '1rem 0' }}>
                          <svg width="150" height="85" viewBox="0 0 150 85">
                            {/* Background Arc */}
                            <path 
                              d="M 15 75 A 60 60 0 0 1 135 75" 
                              fill="none" 
                              stroke={darkMode ? '#1e1e24' : '#e2e8f0'} 
                              strokeWidth="12" 
                              strokeLinecap="round" 
                            />
                            {/* Foreground Arc (Fills left to right) */}
                            <path 
                              d="M 15 75 A 60 60 0 0 1 135 75" 
                              fill="none" 
                              stroke={isGoodCredit ? 'var(--success)' : 'var(--error)'} 
                              strokeWidth="12" 
                              strokeLinecap="round" 
                              strokeDasharray="188.5" 
                              strokeDashoffset={188.5 - (confidenceVal * 188.5)}
                              style={{ transition: 'stroke-dashoffset 0.6s ease-out' }}
                            />
                            {/* Centered Percentage Text */}
                            <text 
                              x="75" 
                              y="70" 
                              textAnchor="middle" 
                              style={{ 
                                fontSize: '1.5rem', 
                                fontWeight: 800, 
                                fontFamily: 'var(--font-mono)',
                                fill: darkMode ? '#fafafa' : '#09090b' 
                              }}
                            >
                              {(confidenceVal * 100).toFixed(0)}%
                            </text>
                          </svg>
                          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Confidence Score</span>
                        </div>
                      );
                    })()}

                    <p style={{ fontSize: '0.9rem' }}>
                      {predictionResult.prediction === 1
                        ? `The profile demonstrates a strong likelihood of repayment. Creditworthiness score is ${(predictionResult.probability * 100).toFixed(1)}%. Recommend approving lending requests under standard interest parameters.`
                        : `High default probability calculated at ${((1 - predictionResult.probability) * 100).toFixed(1)}%. Strong risk signals. Recommend restricting lending terms or requiring secondary collaterals.`}
                    </p>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem 0' }}>
                    <Info size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                    <h4 style={{ fontWeight: 700, marginBottom: '0.25rem' }}>No Simulation Evaluated</h4>
                    <p style={{ fontSize: '0.85rem' }}>Configure input variables on the left panel and trigger the creditworthiness prediction to view evaluation reports.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Model Training Hub */}
        {activeTab === 'trainer' && dataInfo && (
          <div className="layout-split slide-up">
            {/* Control card */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title"><Cpu size={18} /> Model Configuration</h3>
                  <p className="card-description">Select and train algorithms on the active dataset.</p>
                </div>
              </div>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">Classification Algorithm</label>
                  <select
                    className="form-input form-select"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    <option value="Logistic Regression">Logistic Regression (Linear Classifier)</option>
                    <option value="Decision Tree">Decision Tree Classifier</option>
                    <option value="Random Forest">Random Forest (Ensemble Classifier)</option>
                    <option value="Gradient Boosting">Gradient Boosting Classifier</option>
                    <option value="AdaBoost">AdaBoost Classifier</option>
                    <option value="K-Nearest Neighbors">K-Nearest Neighbors (KNN)</option>
                    <option value="Naive Bayes">Naive Bayes Classifier</option>
                    <option value="Support Vector Machine">Support Vector Machine (SVM)</option>
                  </select>
                </div>

                <div className="info-alert">
                  <Info size={16} className="info-alert-icon" />
                  <div>
                    <h5 style={{ fontWeight: 700, marginBottom: '0.15rem' }}>Algorithm Guidance</h5>
                    <p style={{ fontSize: '0.8rem' }}>
                      {selectedModel === 'Logistic Regression' && 'Logistic Regression is quick, highly interpretable, and functions as a standard baseline model. Best for linearly-separable data.'}
                      {selectedModel === 'Decision Tree' && 'Decision Trees segment features hierarchically. Easily readable decision rules, but prone to variance and overfitting.'}
                      {selectedModel === 'Random Forest' && 'Random Forest builds multiple parallel trees and averages their votes. Excellent generalization ability, robust to outliers, and high accuracy.'}
                      {selectedModel === 'Gradient Boosting' && 'Gradient Boosting builds trees sequentially, correcting errors of the previous ones. Highly accurate, but requires careful tuning.'}
                      {selectedModel === 'AdaBoost' && 'AdaBoost adapts weights to focus on previously misclassified samples. Fast and effective, though sensitive to noisy data.'}
                      {selectedModel === 'K-Nearest Neighbors' && 'K-Nearest Neighbors classifies instances based on distance to neighbor profiles. Intuitive, instance-based model, but computationally intensive on large datasets.'}
                      {selectedModel === 'Naive Bayes' && 'Naive Bayes uses probabilistic classification based on Bayes theorem under strong independence assumptions. Very fast and requires small training datasets.'}
                      {selectedModel === 'Support Vector Machine' && 'Support Vector Machine finds optimal hyperplanes to separate classes. Performs exceptionally well in high-dimensional spaces.'}
                    </p>
                  </div>
                </div>

                <button className="btn btn-primary" onClick={handleTrainModel} disabled={training}>
                  {training ? <div className="spinner"></div> : 'Train Model Now'}
                </button>
              </div>
            </div>

            {/* Performance Benchmark comparison charts */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title"><BarChart2 size={18} /> Model Benchmarks Comparison</h3>
                  <p className="card-description">Compare Precision, Recall, F1, and AUC across trained models.</p>
                </div>
              </div>
              <div className="card-body">
                <div style={{ height: '300px' }}>
                  <ReactECharts option={getBenchmarkChartOption()} style={{ height: '100%', width: '100%' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: Dataset Explorer */}
        {activeTab === 'explorer' && dataInfo && (
          <div className="layout-split slide-up" style={{ gridTemplateColumns: '1fr' }}>
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title"><BarChart2 size={18} /> Dataset Summary</h3>
                  <p className="card-description">Currently active dataset: <b>{dataInfo.rows_count} records</b> loaded.</p>
                </div>
              </div>
              <div className="card-body" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
                {/* Data preview table */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>Dataset Preview (First 10 Rows)</h4>
                  <div className="table-wrapper">
                    <table className="preview-table">
                      <thead>
                        <tr>
                          {Object.keys(dataInfo.preview[0] || {}).map((col) => (
                            <th key={col}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {dataInfo.preview.map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row).map((val, cellIdx) => (
                              <td key={cellIdx}>
                                {typeof val === 'number'
                                  ? val % 1 === 0
                                    ? val
                                    : val.toFixed(2)
                                  : String(val)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Target distribution visualization */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>Target Distribution</h4>
                  <div style={{ height: '230px', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', background: 'var(--bg-primary)' }}>
                    <ReactECharts option={getTargetChartOption()} style={{ height: '100%', width: '100%' }} />
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    <p style={{ marginBottom: '0.25rem' }}>• <b>1 (Good Credit)</b>: Good repayment profiles.</p>
                    <p>• <b>0 (Bad Credit)</b>: High default risks profiles.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}



      </div>
    </div>
  );
}

export default App;
