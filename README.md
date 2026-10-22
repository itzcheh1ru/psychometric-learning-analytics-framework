# Psychometric Learning Analytics Framework

## Research Project – J26-DS-310

![Research Area](https://img.shields.io/badge/Research-Data%20Science-blue)
![Domain](https://img.shields.io/badge/Domain-Educational%20Data%20Mining-green)
![AI](https://img.shields.io/badge/Focus-Generative%20AI-orange)
![Status](https://img.shields.io/badge/Status-Integrated%20Research%20Platform-brightgreen)
![Dev Branch](https://img.shields.io/badge/Dev%20Branch-it23426580-blueviolet)
![Tests](https://img.shields.io/badge/Tests-204%20Passing-success)

---

## Project Overview

The **Psychometric Learning Analytics Framework (J26-DS-310)** is an academic research platform developed at the Sri Lanka Institute of Information Technology (SLIIT) Centre of Excellence in Artificial Intelligence (CoEAI). The project investigates the multifaceted behavioral, psychometric, and cognitive impacts of Generative AI (GenAI) tool adoption among undergraduate university students.

The framework integrates four complementary research streams into a unified analytics dashboard:
1. **Component 1 (Cognitive Offloading Risk):** Explainable machine learning model evaluating the risk of cognitive offloading using observable behavioral habits and LinearSHAP attributions.
2. **Component 2 (Algorithmic Trust & Verification):** Structural Equation Modeling (SEM) and Confirmatory Factor Analysis (CFA) exploring psychological pathways between trust, verification, and dependence.
3. **Component 3 (Longitudinal Study Patterns):** Time-series tracking of weekly GenAI vs. independent study time allocation and prompt interaction habits across multi-week academic periods.
4. **Component 4 (Cognitive Engagement & Retention):** Counterbalanced experimental evaluation of conceptual knowledge retention and psychological ownership comparing GenAI-assisted and brain-only writing conditions.

---

## Framework Integration Principle: Complementary Evidence

> ℹ️ **Integration Principle:** The framework integrates component findings as **complementary evidence** rather than mathematically collapsing them into a single aggregated score or cross-component prediction matrix. Each component addresses a distinct research question, and their outputs are interpreted holistically side-by-side on the dashboard (`/dashboard` and `/framework`).

---

## Four Research Components & Current Implementation Status

| Component | Focus Area | Methodology / Technology | Current Implementation Status | Owner |
|---|---|---|---|---|
| **Component 1** | Explainable Cognitive Offloading Risk Prediction | Calibrated Thresholded Ridge Regressor (Ordinal), LinearSHAP, scikit-learn 1.7.1 | **Model Integrated & Active** (`/component1/`): Real-time predictions, continuous scores [1.0–5.0], calibrated probabilities, and directional LinearSHAP factor explanations. | IT23426580 (Thisayuru E.L.H.) |
| **Component 2** | Algorithmic Trust & Verification Analysis | Confirmatory Factor Analysis (CFA), Structural Equation Modelling (SEM), R / lavaan | **Prototype Workflow & UI Implemented** (`/component2/`): Interactive latent construct explorer, path diagrams, specification API, and R/lavaan result gateway. | IT23217904 (Kumari A.M.W.P.G.S.R.) |
| **Component 3** | Longitudinal Study Pattern Analytics | Time-Series Analytics, Weekly Diary Tracking, openpyxl, Pandas | **Analytics & Chart Engine Implemented** (`/component3/`): Multi-week diary data consolidation, prompt frequency breakdown, study-share shifts, and browser-local preview storage. | IT23426344 (Dissanayake H.M.S.U.) |
| **Component 4** | Cognitive Engagement & Learning Retention | Controlled Counterbalanced Experiments, NLP Analysis, Lexical Metrics | **Experimental Protocol Implemented** (`/component4/`): Counterbalanced Condition A (Brain-only) vs. Condition B (GenAI-assisted) validation workflow, session metadata validation, and retention comparison structure. | IT23165220 (Sathsara G.L.H.G.) |

---

## Component 1 — Version 4 Model Architecture & Performance

### Champion Architecture
- **Model:** Calibrated Thresholded Ridge Regressor (Ordinal)
- **Deployment Artifacts:**
  - Primary Model: [`models/thresholded_ridge_v4.joblib`](models/thresholded_ridge_v4.joblib)
  - Continuous Regressor: [`models/continuous_regressor_v4.joblib`](models/continuous_regressor_v4.joblib)
  - Metadata & Medians: [`models/pipeline_metadata_v4.json`](models/pipeline_metadata_v4.json)
- **Feature Space:** Exactly **68** deployed predictor features derived from survey antecedents, interaction terms, and composite indices.
- **Zero Target Leakage:** Cognitive offloading construct items ($\text{CO}_1$ to $\text{CO}_5$), target variable `co_score`, survey identifiers, and personal information are strictly excluded from the predictor space.

### Empirical Validation Performance
- **Primary Selection Protocol:** 25-fold Repeated Stratified Cross-Validation (5 folds $\times$ 5 repeats) on the training set ($N=300$).
  - **CV Macro-F1:** **$0.5643 \pm 0.0597$** (compact 51 features: **$0.5711 \pm 0.0470$**)
  - **CV Accuracy:** **$56.00\% \pm 5.85\%$**
  - **Medium-Risk Recall:** **$59.78\%$** (solves the boundary collapse of nominal tree ensembles, which achieved only 28%–34%)
  - **CV ROC-AUC:** **$0.7508$** | **CV Log-Loss:** **$0.9271$**
- **Continuous Latent Construct Signal:**
  - **Variance Explained ($R^2$):** **$0.4459$** ($44.59\%$ continuous construct variance explained)
  - **RMSE:** **$0.5779$** (on 1.0–5.0 Likert construct scale) | **MAE:** **$0.4578$**
  - **Effect Size:** Cohen's **$f^2 = 0.8048$** (large effect size in behavioral research)
- **Historical Holdout Test Split ($N=75$):** Accuracy: $57.33\%$, Macro-F1: $0.5815$, ROC-AUC: $0.7576$ (documented in metadata as an exposed exploratory split; Repeated CV is reported as primary).
- **Decision Cutoffs (Sample Tertiles):**
  - **Low Risk:** Continuous Score $\le 2.667$
  - **Medium Risk:** Continuous Score $> 2.667$ and $\le 3.500$
  - **High Risk:** Continuous Score $> 3.500$

### Scientific Limitation Disclaimer
> ⚠️ Achieving 90% classification accuracy on this 3-class self-report psychometric construct without circular item leakage is psychometrically and statistically impossible. The obtained results ($R^2 = 0.446$, ROC-AUC $= 0.758$) represent the defensible scientific limit of this behavioral survey dataset.

---

## Technology Stack

- **Runtime:** Python 3.11 – 3.13 (Verified on Python 3.13.3 macOS/ARM64)
- **Web Framework:** Flask 3.1.0, Jinja2, Werkzeug 3.1.3
- **Machine Learning & Inference:** scikit-learn 1.7.1 (pinned to match trained model serialization), joblib 1.6.0, NumPy 2.5.4, SciPy 1.18.1
- **Data Processing & Analytics:** Pandas 3.0.6, openpyxl 3.1.5
- **Production Server:** Gunicorn 26.2.0 (WSGI)
- **Testing:** pytest 9.1.1
- **Frontend:** Responsive Semantic HTML5, CSS3 Custom Properties (Design System), Vanilla JavaScript (No heavy frameworks)
- **Alternative Development Suite:** Streamlit (standalone interactive research app in `component1_streamlit_v4/`)

---

## Repository Structure

```
psychometric-learning-analytics-framework/
├── app.py                                # Local development entry point
├── wsgi.py                               # Production WSGI entry point
├── requirements.txt                      # Pinned Python dependencies (scikit-learn==1.7.1)
├── pytest.ini                            # Test configuration (testpaths = tests)
├── README.md                             # Project overview and instructions
├── .gitignore                            # Comprehensive ignore rules
│
├── app/                                  # Main Flask Web Application
│   ├── __init__.py                       # Application factory & security headers
│   ├── config.py                         # Dev, Testing, and Production configs
│   ├── routes/
│   │   ├── main.py                       # / and /dashboard routes
│   │   ├── framework.py                  # /framework/ and /api/framework/*
│   │   ├── component1.py                 # /component1/ and /api/component1/* (Active C1)
│   │   ├── component2.py                 # /component2/ and /api/component2/* (CFA/SEM)
│   │   ├── component3.py                 # /component3/ and /api/component3/* (Longitudinal)
│   │   └── component4.py                 # /component4/ and /api/component4/* (Retention)
│   ├── services/
│   │   ├── cognitive_offloading/         # Component 1 inference, validation, LinearSHAP
│   │   ├── sem_analysis/                 # Component 2 SEM status & result gateway
│   │   ├── longitudinal/                 # Component 3 data preparation & analysis
│   │   ├── retention/                    # Component 4 experimental session validation
│   │   └── framework/                    # Shared governance & status aggregation
│   ├── templates/                        # Jinja2 HTML templates
│   │   ├── base.html                     # Global shell & presentation-mode class
│   │   ├── dashboard.html                # Shared research overview dashboard
│   │   ├── framework.html                # Framework integration view
│   │   ├── components/                   # Component-specific templates (1-4)
│   │   ├── partials/                     # Header, footer, sidebar, empty states
│   │   └── errors/                       # Academic 404 & 500 error pages
│   └── static/                           # CSS stylesheets & client JavaScript
│       ├── css/                          # style.css, component1.css - component4.css
│       └── js/                           # main.js, component1.js - component4.js
│
├── models/                               # Deployed Version 4 Model Artifacts
│   ├── thresholded_ridge_v4.joblib       # Primary ordinal classifier
│   ├── continuous_regressor_v4.joblib    # Latent continuous regressor
│   └── pipeline_metadata_v4.json         # 68 feature names, means, medians, cuts
│
├── component1_streamlit_v4/              # Standalone Streamlit Research App
│   ├── integration/                      # app_ui_v4.py, integration_service_v4.py
│   ├── models/                           # Full experiment candidate models
│   ├── notebooks/                        # model_training_v4.ipynb
│   ├── plots/                            # Calibration, ROC, SHAP waterfall/beeswarm plots
│   ├── progress_evaluation/              # Panel reports & executive summaries
│   ├── reports/                          # CV, test, and per-class evaluation CSVs
│   ├── scripts/                          # preprocess_v4.py, train_model_v4.py
│   └── verification/                     # Model integrity & scenario verification suites
│
├── data/                                 # Research Data Directories (No PII Committed)
│   ├── raw/                              # Raw participant surveys (.gitkeep)
│   ├── processed/                        # Cleaned analytical datasets (.gitkeep)
│   └── demo/                             # Demo prototype records (.gitkeep)
│
├── docs/
│   └── architecture.md                   # Complete architectural specification
│
└── tests/                                # Automated Test Suites (204 Tests)
    ├── conftest.py                       # Test client fixtures & env setup
    ├── test_app.py                       # Shared application & route tests (184 tests)
    ├── test_component1_v4_scenarios.py   # C1 eight regression scenarios (8 tests)
    ├── test_component1_v4_workflow.py    # C1 pipeline & LinearSHAP workflow (12 tests)
    └── test_component3_longitudinal_charts.py # C3 longitudinal chart analytics (17 tests)
```

---

## Installation & Environment Setup

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed
- Git installed
- Recommended virtual environment tool: `venv`

### 2. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/itzcheh1ru/psychometric-learning-analytics-framework.git
cd psychometric-learning-analytics-framework

# Create virtual environment
python3 -m venv .venv

# Activate environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows (cmd.exe):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install exact pinned dependencies
pip install -r requirements.txt
```

---

## Running the Application

### 1. Shared Flask Research Dashboard (Primary Integrated Application)
```bash
# Start local development server
python app.py
```
Or with Flask CLI in debug mode:
```bash
flask --app app run --debug
```
Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### 2. Production WSGI Server (Gunicorn)
```bash
# Run using the dedicated WSGI module
gunicorn wsgi:app

# Custom binding on port 8000
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

### 3. Standalone Streamlit Research App (Component 1 Standalone Suite)
If you wish to explore the standalone research development suite and evaluation charts:
```bash
streamlit run component1_streamlit_v4/integration/app_ui_v4.py
```
Open your browser at: **[http://localhost:8501](http://localhost:8501)**

---

## Localhost Application Navigation URLs

| Page / View | URL | Purpose |
|---|---|---|
| **Home / Overview** | `http://127.0.0.1:5000/` | Research framework landing page and introduction |
| **Research Dashboard** | `http://127.0.0.1:5000/dashboard` | Main shared dashboard with component summaries and presentation mode |
| **Presentation Mode** | `http://127.0.0.1:5000/dashboard?presentation=1` | Widescreen projector view (sidebar collapsed, expanded charts) |
| **Framework Integration** | `http://127.0.0.1:5000/framework/` | Multi-component complementary evidence integration view |
| **Component 1 (Active)** | `http://127.0.0.1:5000/component1/` | **AI-Assisted Learning Self-Reflection** assessment & prediction tool |
| **Component 2** | `http://127.0.0.1:5000/component2/` | Algorithmic Trust & Verification SEM construct explorer |
| **Component 3** | `http://127.0.0.1:5000/component3/` | Longitudinal study pattern analytics and weekly diary preview |
| **Component 4** | `http://127.0.0.1:5000/component4/` | Cognitive engagement and recall retention protocol explorer |

---

## Key API Endpoints

### Framework & Health
- `GET /health` — Lightweight application health check.
  - Response: `{"application": "Psychometric Learning Analytics Framework", "project_id": "J26-DS-310", "status": "ok"}`
- `GET /api/framework/status` — Reports analytical readiness of all four components.

### Component 1 (Cognitive Offloading)
- `GET /api/component1/status` — Reports model status, architecture (`Calibrated Thresholded Ridge Regressor`), feature count (68), and readiness (`model_trained: true`).
- `POST /api/component1/predict` — Executes model prediction and returns continuous score, risk tier, probabilities, and LinearSHAP attributions.
  - **Request Body:** JSON object with Likert responses (1–5), GenAI tools, study frequency, and academic field.
  - **Sample Request:**
    ```json
    {
      "ai_usage_freq": 2,
      "Q20_task_delegation_freq": 3,
      "Q1_direct_use_freq": 3,
      "Q22_effort_on_ai_answers": 3,
      "Q8_complete_without_ai": 3,
      "Q7_attempt_independently": 3,
      "Q2_verify_info": 3,
      "Q30_trust_accuracy": 3,
      "Q33_trust_appropriate_support": 3,
      "degree_field": "Computer Science / IT"
    }
    ```
  - **Sample Response (`HTTP 200 OK`):**
    ```json
    {
      "status": "success",
      "predicted_category": "Medium",
      "continuous_risk_score": 3.002,
      "confidence": 0.5391,
      "probabilities": {
        "low": 0.2747,
        "medium": 0.5391,
        "high": 0.1862
      },
      "model_architecture": "Thresholded Ridge Regressor (Ordinal)",
      "top_contributing_factors": [
        {
          "feature_name": "idx_passive_adoption",
          "human_label": "Passive Adoption (Direct Copying × Low Effort)",
          "linear_shap_contribution": 0.142,
          "effect": "increases predicted risk",
          "plain_explanation": "Directly copying outputs while investing little effort in review increases reliance.",
          "student_value": 9.0
        }
      ],
      "disclaimer": "RESEARCH DISCLAIMER: This risk prediction is generated by an academic machine learning model (Component 1, J26-DS-310) for exploratory educational purposes only..."
    }
    ```
  - **Validation Guard:** Submitting `{}` returns `HTTP 400` with `error_type: "MissingRequiredInput"`.

### Components 2, 3, and 4
- `GET /api/component2/status` — Algorithmic trust SEM model readiness and status.
- `GET /api/component3/status` — Longitudinal dataset metrics and status.
- `GET /api/component3/summary` — Weekly study share, hours, and prompt distributions.
- `GET /api/component4/status` — Experimental retention evaluation stage and readiness.

---

## Automated Test Suite

The test suite covers shared application routes, security headers, Component 1 inference scenarios, LinearSHAP explanations, and Component 3 longitudinal chart logic.

```bash
# Run complete test suite (204 tests)
.venv/bin/pytest tests/ -v

# Run targeted Component 1 regression scenarios
.venv/bin/pytest tests/test_component1_v4_scenarios.py -v

# Run targeted Component 1 pipeline workflow & SHAP tests
.venv/bin/pytest tests/test_component1_v4_workflow.py -v
```

### Verified Test Results: **204 passed, 0 failed, 0 warnings (100% pass rate)**
- `tests/test_app.py`: **184 passed** (Framework integration, security headers, WSGI, presentation mode, error handlers)
- `tests/test_component1_v4_scenarios.py`: **8 passed** (Low, Medium, High risk, empty input guard, out-of-range clamping, dirty text handling)
- `tests/test_component1_v4_workflow.py`: **12 passed** (Model loading, 68-feature schema, zero target leakage, calibrated probabilities, LinearSHAP)
- `tests/test_component3_longitudinal_charts.py`: **17 passed** (Weekly study shares, prompt counts, workload comparisons, coverage tables)

---

## Research Ethics & Privacy

1. **Zero Real Participant Data Committed:** The repository contains zero participant personal information (PII), student IDs, email addresses, or unaggregated survey records.
2. **Academic Purpose Only:** Predictions are generated for exploratory self-reflection and academic research only. They do not constitute a psychological evaluation, cognitive diagnosis, or academic penalty.
3. **No Circular Data Leakage:** Target construct items ($\text{CO}_1$ to $\text{CO}_5$) are strictly excluded from predictors.

---

## Research Team & Branch Conventions

| Member | Student ID | Research Component | Git Branch |
|---|---|---|---|
| **Thisayuru E.L.H.** | **IT23426580** | **Component 1 — Cognitive Offloading Risk Prediction** | `it23426580` |
| Kumari A.M.W.P.G.S.R. | IT23217904 | Component 2 — Algorithmic Trust & SEM | `it23217904` |
| Dissanayake H.M.S.U. | IT23426344 | Component 3 — Longitudinal Study Analytics | `it23426344` |
| Sathsara G.L.H.G. | IT23165220 | Component 4 — Cognitive Retention Evaluation | `it23165220` |

### Permanent Development Rules
- **Never commit directly to `main`.** All work is committed to the component developer's student branch.
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Merges into `main` require code review and verified passing automated tests.

---

## Institution & License

- **Institution:** Sri Lanka Institute of Information Technology (SLIIT)
- **Centre:** Centre of Excellence in Artificial Intelligence (CoEAI) — Specialisation: Data Science
- **Research Project Code:** J26-DS-310
- **License:** Licensed for academic research purposes only. © 2024–2026 SLIIT Research Team.
