# Architecture – Psychometric Learning Analytics Framework

**Project ID:** J26-DS-310  
**Institution:** SLIIT – Centre of Excellence in Artificial Intelligence (CoEAI)  
**Status:** Prototype scaffold – research data collection in progress

---

## Overview

The Psychometric Learning Analytics Framework is composed of **four fully
independent analytical components**. Each component is self-contained in its
own service layer (`app/services/`) and route blueprint (`app/routes/`), and
produces its own set of analytical outputs.

The outputs of all four components are designed to be **integrated into a
single shared research analytics dashboard** once data collection and analysis
are complete.

---

## Component Independence

Each component operates independently in the following sense:

- It has its own data inputs (separate survey instruments, study diaries,
  experimental outputs).
- It applies its own analytical methodology (ML, SEM, time-series, NLP).
- It produces its own result artefacts (risk predictions, path coefficients,
  trend curves, NLP metrics).
- It is developed by an independent team member.

This independence ensures that delays or changes in one component do not
block the others.

---

## Four Analytical Components

| # | Component | Methodology | Team Member |
|---|-----------|-------------|-------------|
| 1 | Explainable Cognitive Offloading Risk Prediction | Logistic Regression, Random Forest, XGBoost, SHAP | IT23426580 |
| 2 | Algorithmic Trust & Verification Analysis | CFA, SEM, R/lavaan | IT23217904 |
| 3 | Longitudinal Study Pattern Analytics | Time-Series, Trend Analysis, Pandas | IT23426344 |
| 4 | GenAI-Assisted Cognitive Engagement & Retention | NLP, NLTK, spaCy, Statistical Analysis | IT23165220 |

---

## Application Architecture

```
app.py  (entry point)
└── app/__init__.py  (application factory: create_app())
    │
    ├── app/routes/
    │   ├── main.py          → /  and  /dashboard
    │   ├── component1.py    → /component1/
    │   ├── component2.py    → /component2/
    │   ├── component3.py    → /component3/
    │   └── component4.py    → /component4/
    │
    ├── app/services/
    │   ├── cognitive_offloading/    (Component 1 – ML analysis)
    │   ├── sem_analysis/            (Component 2 – SEM / R integration)
    │   ├── longitudinal/            (Component 3 – Time-series analytics)
    │   └── retention/               (Component 4 – NLP analysis)
    │
    ├── app/templates/               (Jinja2 templates)
    └── app/static/                  (CSS, JS, images)
```

---

## Data Flow (planned)

```
[Data Collection]
    ↓
[data/raw/]  (never committed to git)
    ↓
[Preprocessing – notebooks/ or services/]
    ↓
[data/processed/]  (never committed to git)
    ↓
[Component 1–4 Service Layers]
    ↓
[Dashboard – /dashboard]
```

---

## Component 1 Architecture – Cognitive Offloading Risk Prediction

### Target Construction vs. Predictor Preparation Separation

To uphold research integrity and eliminate **data leakage**, the pipeline strictly separates:

```
[Survey Administration]
      │
      ├─────────────────────────────────────────────┐
      ▼                                             ▼
Target Construction Items                     Predictor Items
(validated cognitive offloading scale)         (GenAI usage, verification, independent learning)
      │                                             │
      ▼                                             ▼
Target Variable: Binary / Ordinal Risk        Feature Engineering / Preprocessing
      │                                             │
      └─────────────────────┬───────────────────────┘
                            ▼
                Train / Test Separation
                            ▼
               Stratified Cross-Validation
                            ▼
                     Model Training
          (Logistic Regression, RF, XGBoost)
                            ▼
                     Selected Model
                            ▼
                    SHAP Explainability
                            ▼
                   Dashboard Presentation
```

> **Target Leakage Rule:** Cognitive-offloading scale items used to construct the
> target label are **strictly excluded** from the predictor feature set.

### Service Layer Design

- `schemas.py`: Allowed category enumerations, regex pattern for anonymous participant IDs.
- `validation.py`: Pure validation and sanitization. Rejects any out-of-schema values.
- `model_service.py`: `CognitiveOffloadingModelService` singleton. All prediction methods
  raise `ModelNotAvailableError` until an evaluated model file is loaded.
- `routes/component1.py`:
  - `GET /component1/`: interactive prototype UI
  - `GET /api/component1/status`: reports `model_trained: false`, `prediction_available: false`
  - `POST /api/component1/validate-input`: validates prototype payload; does NOT predict or persist

---

## Component 2 Architecture – Algorithmic Trust & Verification Analysis

### Latent Constructs

Component 2 investigates five theoretical constructs operationalised via psychometric survey scales:

| Code | Construct Name | Role in Structural Model |
|------|----------------|--------------------------|
| **AT** | Algorithmic Trust | Antecedent Construct |
| **PU** | Perceived Usefulness | Antecedent Construct |
| **VB** | Verification Behaviour | Behavioural Mechanism (Mediator) |
| **AD** | AI Dependence | Learning / Reliance Outcome |
| **LC** | Learning Confidence | Learning / Reliance Outcome |

### Methodological Stages

1. **Measurement Model Stage (Confirmatory Factor Analysis):**
   - Evaluates indicator factor loadings ($\lambda \ge 0.70$).
   - Tests construct reliability using Composite Reliability ($\text{CR} \ge 0.70$) and Cronbach's $\alpha \ge 0.70$.
   - Assesses convergent validity via Average Variance Extracted ($\text{AVE} \ge 0.50$).
   - Evaluates discriminant validity using the Fornell-Larcker criterion and Heterotrait-Monotrait ratio ($\text{HTMT} < 0.85 / 0.90$).

2. **Structural Model Stage (Structural Equation Modelling):**
   - Assesses hypothesised direct pathways from antecedents to outcomes.
   - Evaluates overall goodness of fit using $\chi^2/\text{df}$, CFI, TLI, RMSEA, and SRMR.

3. **Mediation Analysis Stage:**
   - Evaluates whether Verification Behaviour serves as an indirect behavioural mechanism linking Algorithmic Trust to AI Dependence and Learning Confidence.
   - Applies non-parametric bootstrapping (5,000 resamples) with 95% bias-corrected confidence intervals.

### Analytical and Architectural Boundary: R/lavaan vs. Flask

A strict separation of concerns is maintained between statistical estimation and web visualization:

```
┌────────────────────────────────────────────────────────┐
│            R / lavaan Research Environment             │
│  - Survey data screening & psychometric cleaning       │
│  - CFA measurement model estimation (MLR estimator)     │
│  - Structural Equation Model path estimation           │
│  - Bootstrapped mediation analysis (5,000 resamples)   │
│  - Parameter estimate & fit index export               │
└───────────────────────────┬────────────────────────────┘
                            │ Validated JSON / CSV export
                            ▼
┌────────────────────────────────────────────────────────┐
│            Flask Web Application Backend               │
│  - `app/services/sem_analysis/schemas.py`: metadata   │
│  - `app/services/sem_analysis/status_service.py`       │
│  - `app/services/sem_analysis/result_service.py`       │
│    (SemResultService raises error if unvalidated)     │
│  - `GET /api/component2/status`                        │
│  - `GET /api/component2/specification`                 │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│          Dashboard Presentation Layer (/component2/)   │
│  - Interactive construct exploration                   │
│  - Planned model specification visualisations          │
│  - Results display only after empirical validation     │
└────────────────────────────────────────────────────────┘
```

> **Architectural Boundary Rule:** All statistical SEM calculations (factor extraction, covariance estimation, fit indices, bootstrap resampling) remain strictly governed within the **R / lavaan** psychometric research environment. The Flask application does **not** estimate SEM or simulate statistics in real-time; it serves exclusively as an analytics consumer and presentation layer for validated empirical outputs.

---

## Dashboard Integration (planned)

Once all four components have been analysed, their outputs will be surfaced
in the shared research dashboard at `/dashboard`:

- **Component 1**: Risk prediction distributions, SHAP feature importance charts
- **Component 2**: SEM path diagrams, fit indices (CFI, RMSEA, SRMR)
- **Component 3**: AI/independent study trend curves, prompt behaviour heatmaps
- **Component 4**: Writing quality comparisons, recall score summaries

> ⚠️ No real findings are presented in the current prototype.
> All analytical content will reflect actual research results after
> data collection is complete.

---

## Technology Decisions

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Web framework | Flask | Lightweight, suitable for research prototype |
| Frontend | HTML5 + CSS3 + Vanilla JS | No framework overhead; Chart.js added later |
| ML pipeline | scikit-learn, XGBoost, SHAP | Standard research toolchain |
| SEM | R / lavaan | Standard academic SEM tool |
| NLP | NLTK, spaCy | Well-documented, research-grade |
| Database | SQLite (planned) | Sufficient for prototype scale |
| Data format | CSV / Pandas DataFrames | Flexible, notebook-compatible |

---

*Last updated: Feature 004 – Component 2 SEM analysis prototype workflow*
