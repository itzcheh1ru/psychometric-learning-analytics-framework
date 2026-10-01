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

## Component 3 Architecture – Longitudinal Study Pattern Analytics

### Weekly Participant Record Structure

Component 3 tracks study behaviour and academic prompt interactions across repeated weekly observations (4–6 weeks planned duration):

| Variable | Type / Constraints | Description |
|----------|-------------------|-------------|
| `participant_reference` | String (1–20 chars, regex `^[A-Za-z0-9\-]+$`) | Anonymised research participant identifier |
| `study_week` | Categorical ("Week 1" – "Week 6") | Observation week index |
| `ai_study_hours` | Float ($0.0 \le h \le 168.0$) | Weekly study hours involving active Generative AI assistance |
| `independent_study_hours` | Float ($0.0 \le h \le 168.0$) | Weekly study hours completed without direct AI assistance |
| `academic_period` | Categorical (5 academic contexts) | Academic context (regular week, assignments, exams, projects) |
| `learning_activity` | Categorical (7 academic activities) | Dominant learning activity for the study week |
| `prompt_count` | Integer ($0 \le n \le 2000$) | Weekly count of academic GenAI prompts (no raw text stored) |
| `prompt_purpose` | Categorical (7 academic purposes) | Primary academic purpose of student GenAI interactions |

### Methodological Boundaries and Pipeline Architecture

A strict boundary exists between prototype data validation and empirical longitudinal analytics:

```
┌────────────────────────────────────────────────────────┐
│           Weekly Diary Data Collection Layer           │
│  - Anonymised weekly observation submission            │
│  - Zero raw prompt text collection                     │
└───────────────────────────┬────────────────────────────┘
                            │ Validation & Preprocessing
                            ▼
┌────────────────────────────────────────────────────────┐
│          Longitudinal Research Dataset Boundary        │
│  - Multi-week participant consolidation (Weeks 1–6)    │
│  - Baseline vs. subsequent week alignment              │
│  - Missing-observation handling & screening            │
└───────────────────────────┬────────────────────────────┘
                            │ Preprocessed time series
                            ▼
┌────────────────────────────────────────────────────────┐
│           Behavioural Indicator Generation             │
│  - AI Study Share = AI Hours / (AI + Independent Hours)│
│  - Independent Study Share = Ind Hours / Total Hours   │
│  - Prompt Frequency = Weekly Interaction Count         │
│  - Study Pattern Shift Index across observation weeks  │
└───────────────────────────┬────────────────────────────┘
                            │ Indicator matrices
                            ▼
┌────────────────────────────────────────────────────────┐
│             Trend & Prompt Analytics Engine            │
│  - Time-series slope estimation & trajectory grouping  │
│  - Academic-period comparative analysis (e.g. exams)   │
│  - Prompt purpose distribution evolution               │
└───────────────────────────┬────────────────────────────┘
                            │ Validated findings
                            ▼
┌────────────────────────────────────────────────────────┐
│         Dashboard Presentation Layer (/component3/)    │
│  - Interactive prototype record validation             │
│  - Displays longitudinal trends only after dataset is   │
│    fully assembled and validated                       │
└────────────────────────────────────────────────────────┘
```

> **Research Integrity Principle:** **Prototype validation does not equal longitudinal research analysis.** The `/api/component3/validate-weekly-record` endpoint validates the structural soundness of an individual record; it does not calculate longitudinal trends, infer behavioural shifts, or persist data. Trend analysis will only be executed once the complete 4–6 week empirical dataset has been validated.

---

## Component 4 Architecture – Cognitive Engagement & Learning Retention Evaluation

### Experimental Protocol and Conditions

Component 4 evaluates writing output quality, cognitive effort, psychological ownership, and knowledge retention across two controlled writing conditions:
- **Condition A (Brain-Only Writing):** Student completes academic writing without Generative AI assistance.
- **Condition B (GenAI-Assisted Writing):** Student completes academic writing with permitted Generative AI assistance.

### Counterbalancing Protocol

To isolate treatment effects from ordering and topic confounding, a counterbalancing design is employed:
- **Sequence A:** Brain-only condition first, followed by GenAI-assisted condition.
- **Sequence B:** GenAI-assisted condition first, followed by brain-only condition.

Topic equivalence and washout intervals are enforced between sessions.

### Prototype Experimental Session Record Schema

| Variable | Type / Constraints | Description |
|---|---|---|
| `participant_reference` | String (2–20 chars, `^[A-Za-z0-9\-_]{2,20}$`) | Anonymised research participant identifier |
| `experimental_condition` | Categorical ("Brain-only writing", "GenAI-assisted writing") | Assigned experimental writing condition |
| `condition_order` | Categorical ("Brain-only first", "GenAI-assisted first") | Counterbalanced order assignment |
| `session_stage` | Categorical ("Writing task", "Immediate recall", "Ownership / cognitive effort", "Delayed recall") | Session experimental stage |
| `task_reference` | String (2–20 chars, `^[A-Za-z0-9\-_]{2,20}$`) | Anonymised writing task reference code |
| `consent_confirmed` | Boolean (`True`) | Explicit confirmation of research consent |

### Analytical Pipeline and Research Integrity Boundaries

A multi-stage architecture separates session metadata validation from subsequent NLP, rubric, and recall analytics:

```
┌────────────────────────────────────────────────────────┐
│         Controlled Experimental Session Layer          │
│  - Anonymised session metadata validation              │
│  - Zero raw essay text persistence in prototype        │
│  - Ethical consent verification                        │
└───────────────────────────┬────────────────────────────┘
                            │ Validated session records
                            ▼
┌────────────────────────────────────────────────────────┐
│        Anonymised Corpus Preprocessing Pipeline        │
│  - Text sanitisation and lemmatisation                 │
│  - spaCy dependency parsing & NLTK text processing    │
│  - Rater anonymisation for rubric scoring              │
└───────────────────────────┬────────────────────────────┘
                            │ Preprocessed data
                            ▼
┌────────────────────────────────────────────────────────┐
│          Multi-Branch Analytical Engine                │
│  - NLP Feature Extraction (TTR, readability, cosine)   │
│  - Independent Human Rubric Scoring (inter-rater kappa)│
│  - Immediate & Delayed Recall Assessment               │
│  - Psychological Ownership & Cognitive Effort Scales   │
└───────────────────────────┬────────────────────────────┘
                            │ Multi-modal measures
                            ▼
┌────────────────────────────────────────────────────────┐
│          Paired Condition Comparison Engine            │
│  - Within-participant paired difference testing        │
│  - Effect size estimation (Cohen's d) & 95% CIs        │
│  - Output quality vs. retention dissociation analysis  │
└───────────────────────────┬────────────────────────────┘
                            │ Validated empirical findings
                            ▼
┌────────────────────────────────────────────────────────┐
│         Dashboard Presentation Layer (/component4/)    │
│  - Interactive prototype session validation            │
│  - Condition comparison and analytical results         │
│    displayed only after experimental validation        │
└────────────────────────────────────────────────────────┘
```

> **Methodological Principle & Research Integrity Rule:** **Better writing output does not automatically imply better learning or retention.** High surface fluency produced by GenAI assistance must be decoupled from genuine conceptual integration and delayed recall.  
> **Prototype session validation is NOT experimental outcome analysis.** The `/api/component4/validate-session` endpoint validates the structural integrity of session metadata; it does not grade writing, evaluate recall, calculate NLP metrics, or persist participant data.

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

*Last updated: Feature 006 – Component 4 cognitive retention prototype workflow*
