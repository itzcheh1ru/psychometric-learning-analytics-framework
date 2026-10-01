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

*Last updated: Feature 001 – Initial scaffold*
