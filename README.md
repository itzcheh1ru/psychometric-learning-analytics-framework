# Psychometric Learning Analytics Framework

## Research Project – J26-DS-310

![Research Area](https://img.shields.io/badge/Research-Data%20Science-blue)
![Domain](https://img.shields.io/badge/Domain-Educational%20Data%20Mining-green)
![AI](https://img.shields.io/badge/Focus-Generative%20AI-orange)
![Status](https://img.shields.io/badge/Status-Prototype%20%E2%80%93%20Data%20Collection%20in%20Progress-yellow)
![Branch](https://img.shields.io/badge/Dev%20Branch-it23426580-blueviolet)

---

## Prototype Status

> ⚠️ **This is an active research prototype.**
>
> Data collection from undergraduate student participants is **currently in progress**.
> No real research findings, model predictions, SEM coefficients, or statistical
> results are presented at this stage.
>
> All analytical modules will be populated with real results once data collection
> and analysis are complete.

### Development Progress

| Feature | Description | Status |
|---------|-------------|--------|
| Feature 001 | Flask application scaffold | ✅ Complete |
| Feature 002 | Responsive research dashboard shell | ✅ Complete |
| Feature 003 | Component 1 interactive prototype workflow | ✅ Complete |
| Feature 004 | Component 2 SEM analysis prototype workflow | ✅ Complete |
| Feature 005 | Component 3 longitudinal analytics prototype workflow | ✅ Complete |
| Feature 006 | Component 4 cognitive retention prototype workflow | ✅ Complete |

**Feature 006 notes:**
- Component 4 prototype: Implemented (specification API, status API, session validation, learning outcomes, NLP feature framework).
- Experimental condition schema: Implemented (Brain-only writing Condition A vs. GenAI-assisted writing Condition B).
- Counterbalancing design: Implemented (Sequence A vs. Sequence B, order control, task code references).
- Session validation: Implemented (safe in-memory sanitisation, required consent, rejection of unknown fields, no persistence).
- Experimental dataset: Pending collection (`dataset_ready = false`).
- NLP analysis: Not yet available (`nlp_analysis_available = false`, pending writing sample collection and spaCy/NLTK pipeline execution).
- Recall / retention analysis: Not yet available (`recall_analysis_available = false`, `paired_analysis_available = false`, `RetentionAnalysisService` raises `RetentionAnalysisNotAvailableError`).
- Final experimental findings: Not available (no fake essay texts, no simulated recall scores, no fabricated NLP metrics or effect sizes, no condition superiority claims).

**Feature 005 notes:**
- Component 3 prototype: Implemented (specification API, status API, weekly study-record validation, indicator definitions).
- Weekly data structure: Implemented (4–6 week observation schema, time distribution, prompt frequency, academic context).
- Longitudinal validation: Implemented (safe sanitisation, range checking, unknown field rejection, no persistence).
- Longitudinal dataset: Pending collection (`dataset_ready = false`).
- Trend analysis: Not yet enabled (`trend_analysis_available = false`, `LongitudinalAnalysisService` raises `LongitudinalAnalysisNotAvailableError`).
- Prompt behaviour analysis: Not yet enabled (`prompt_analysis_available = false`).
- Final longitudinal findings: Not available (no fake trends, no mock histories, no simulated participant patterns).

---

## Project Purpose

The rapid adoption of Generative AI tools (ChatGPT, Gemini, GitHub Copilot) has
transformed how university students learn and complete academic tasks. While GenAI
offers productivity benefits, excessive dependence may introduce:

- **Cognitive offloading** – reduced independent problem-solving ability
- **Verification gaps** – over-trust without critically evaluating AI outputs
- **Study pattern changes** – shifts in time spent on independent learning
- **Retention risks** – reduced knowledge ownership

This research proposes a **Psychometric Learning Analytics Framework** to analyse
these effects using explainable machine learning, structural equation modelling,
longitudinal analytics, and natural language processing.

---

## Four Research Components

### Component 1 – Explainable Cognitive Offloading Risk Prediction

Develops an explainable machine learning model to predict cognitive offloading
risk based on GenAI usage behaviour, verification practices, and learning strategies.

**Methods:** Logistic Regression, Random Forest, XGBoost, SHAP  
**Owner:** IT23426580 (Thisayuru E.L.H.)

---

### Component 2 – Algorithmic Trust & Verification Analysis

Models the psychological relationships between algorithmic trust, perceived
usefulness, verification behaviour, AI dependence, and learning confidence.

**Methods:** Confirmatory Factor Analysis (CFA), Structural Equation Modelling (SEM), R / lavaan  
**Owner:** IT23217904 (Kumari A.M.W.P.G.S.R.)

---

### Component 3 – Longitudinal Study Pattern Analytics

Analyses how AI-assisted and independent study patterns evolve over time
across the research cohort using longitudinal diary records.

**Methods:** Time-series analysis, trend modelling, prompt behaviour analysis, Pandas  
**Owner:** IT23426344 (Dissanayake H.M.S.U.)

---

### Component 4 – GenAI-Assisted Cognitive Engagement & Learning Retention

Evaluates writing quality, lexical diversity, semantic similarity and recall
in AI-assisted vs. brain-only writing conditions.

**Methods:** NLP (NLTK, spaCy), semantic analysis, readability scoring, SciPy  
**Owner:** IT23165220 (Sathsara G.L.H.G.)

---

## Technology Stack

### Backend
- **Python 3.11+**
- **Flask** – web framework
- **python-dotenv** – environment variable management

### Frontend
- **HTML5 / CSS3** – responsive academic UI
- **Vanilla JavaScript** – minimal interactions
- **Chart.js** – to be added in a later feature

### Analytics & ML (planned, added per feature)
- **Pandas, NumPy** – data processing
- **scikit-learn, XGBoost** – machine learning
- **SHAP** – explainable AI
- **SciPy** – statistical analysis
- **NLTK, spaCy** – natural language processing

### SEM (R environment, separate)
- **R / lavaan** – structural equation modelling
- Results to be integrated into dashboard via exported outputs

### Database (planned prototype)
- **SQLite** – lightweight prototype database

---

## Project Structure

```
psychometric-learning-analytics-framework/
│
├── app.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── README.md
├── .gitignore
│
├── app/
│   ├── __init__.py               # Flask application factory
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py               # / and /dashboard
│   │   ├── component1.py         # /component1/
│   │   ├── component2.py         # /component2/
│   │   ├── component3.py         # /component3/
│   │   └── component4.py         # /component4/
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cognitive_offloading/ # Component 1 service (pending)
│   │   ├── sem_analysis/         # Component 2 service (pending)
│   │   ├── longitudinal/         # Component 3 service (pending)
│   │   └── retention/            # Component 4 service (pending)
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   └── components/
│   │       └── component_placeholder.html
│   │
│   └── static/
│       ├── css/style.css
│       ├── js/main.js
│       └── images/
│
├── data/
│   ├── raw/          # Real participant data – NEVER committed to git
│   ├── processed/    # Processed data – NEVER committed to git
│   └── demo/         # Demo/prototype data only – clearly labelled
│
├── models/           # Trained model artefacts (added later)
├── notebooks/        # Jupyter analysis notebooks (added later)
│
├── tests/
│   ├── __init__.py
│   └── test_app.py   # Flask smoke tests
│
└── docs/
    └── architecture.md
```

---

## Installation

### Prerequisites
- Python 3.11 or later
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/itzcheh1ru/psychometric-learning-analytics-framework.git
cd psychometric-learning-analytics-framework

# 2. Create and activate a virtual environment
python -m venv .venv

# On macOS / Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running Locally

```bash
# Start the development server
python app.py
```

Then open your browser at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

Alternatively, using the Flask CLI:

```bash
flask --app app run --debug
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Branch & Development Convention

| Branch | Purpose |
|--------|---------|
| `main` | Stable, integration-ready code only |
| `it23426580` | Component 1 – Cognitive Offloading (this branch) |
| `it23217904` | Component 2 – Algorithmic Trust & SEM |
| `it23426344` | Component 3 – Longitudinal Analytics |
| `it23165220` | Component 4 – NLP Retention Analysis |

### Rules
- **Never commit directly to `main`.**
- All work must be committed to the relevant student branch.
- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Each feature must have its own separate commit.
- Do **not** commit: `.venv/`, `__pycache__/`, `.env`, `.db` files,
  real participant data, or IDE configuration files.

---

## Research Team

| Member | Student ID | Research Component |
|--------|------------|--------------------|
| Thisayuru E.L.H. | IT23426580 | Explainable Cognitive Offloading Risk Prediction |
| Kumari A.M.W.P.G.S.R. | IT23217904 | Algorithmic Trust & Verification SEM Model |
| Dissanayake H.M.S.U. | IT23426344 | Longitudinal Study Pattern Analytics |
| Sathsara G.L.H.G. | IT23165220 | NLP-Based Cognitive Retention Evaluation |

---

## Institution

**Sri Lanka Institute of Information Technology (SLIIT)**  
Centre of Excellence in Artificial Intelligence (CoEAI)  
Specialisation: Data Science

---

## Research Keywords

Generative Artificial Intelligence · Learning Analytics · Educational Data Mining ·
Cognitive Offloading · Algorithmic Trust · Explainable AI · Structural Equation Modelling ·
Natural Language Processing · Responsible AI · Higher Education Analytics

---

## License

This repository is developed for academic research purposes only.  
© 2024–2025 SLIIT Research Team – J26-DS-310
