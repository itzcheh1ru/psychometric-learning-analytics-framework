# Psychometric Learning Analytics Framework for Generative AI-Assisted Learning

## Research Project – J26-DS-310

![Research Area](https://img.shields.io/badge/Research-Data%20Science-blue)
![Domain](https://img.shields.io/badge/Domain-Educational%20Data%20Mining-green)
![AI](https://img.shields.io/badge/Focus-Generative%20AI-orange)

---

## Overview

The rapid adoption of Generative Artificial Intelligence (GenAI) tools such as ChatGPT, Gemini, and GitHub Copilot has transformed how university students learn, complete assignments, and solve technical problems.

While GenAI provides significant benefits in productivity and personalized learning support, excessive dependence may introduce risks such as cognitive offloading, reduced independent problem-solving ability, insufficient verification of AI outputs, and over-trust in AI-generated information.

This research proposes a **Psychometric Learning Analytics Framework** to analyze the relationship between Generative AI usage and undergraduate students' learning behaviour, cognitive engagement, algorithmic trust, verification practices, and academic performance.

The framework integrates:

- Explainable Machine Learning
- Structural Equation Modelling (SEM)
- Longitudinal Learning Analytics
- Natural Language Processing (NLP)

to provide evidence-based insights for responsible AI adoption in higher education.

---

# Research Problem

Current higher education systems mainly capture traditional learning indicators such as grades, attendance, and assignment submissions. However, they do not adequately measure:

- How students interact with external Generative AI tools
- Whether students become overly dependent on AI assistance
- How trust in AI affects verification behaviour
- How AI usage changes study patterns over time
- Whether AI-assisted learning influences knowledge retention

This research addresses these limitations by developing a data-driven framework capable of analysing student-level GenAI usage behaviour and generating interpretable insights.

---

# Research Objectives

The main objective of this research is:

> To develop and evaluate a Psychometric Learning Analytics Framework that integrates explainable predictive modelling, Structural Equation Modelling, longitudinal analytics, and Natural Language Processing to analyse the impact of Generative AI usage on undergraduate learning behaviour and provide recommendations for responsible AI integration.

---

# Research Framework

The proposed framework consists of four analytical modules:

```
Student Data Collection
          |
          ↓
Psychometric Survey
Study Diaries
GenAI Interaction Data
Writing Experiments
          |
          ↓
Data Processing & Feature Engineering
          |
 ┌────────────────────────────────────────────┐
 |                                            |
 ↓                                            ↓

Module 1                                 Module 2
Cognitive Offloading                    Algorithmic Trust
Risk Prediction                          Pathway Analysis

ML Models                                SEM / CFA
XGBoost                                  Trust Modelling
Random Forest                            Verification Behaviour
SHAP Explainability                      Learning Confidence


 ↓                                            ↓

Module 3                                 Module 4
Longitudinal Study                      NLP Cognitive
Pattern Analytics                       Retention Evaluation

Time-Series Analysis                    Writing Analysis
Prompt Behaviour                        Recall Testing
Study Trend Analysis                    NLP Features


          |
          ↓

Integrated Learning Analytics Framework

          |
          ↓

Responsible AI Recommendations
```

---

# Research Components

## Module 1: Explainable Cognitive Offloading Risk Model

### Objective

Develop an explainable machine learning model to predict students' cognitive offloading risk based on:

- Generative AI usage behaviour
- Verification practices
- Learning strategies

### Methodologies

- Logistic Regression
- Random Forest
- XGBoost
- Stratified Cross Validation
- SHAP Explainable AI

### Outputs

- Cognitive offloading risk prediction
- Important behavioural factors
- Individual prediction explanations
- Risk-based intervention recommendations

---

## Module 2: Structural Equation Model for Algorithmic Trust

### Objective

Analyse the psychological relationships between:

- Algorithmic trust
- Perceived usefulness
- Verification behaviour
- AI dependence
- Learning confidence

### Methodologies

- Confirmatory Factor Analysis (CFA)
- Structural Equation Modelling (SEM)
- Path Analysis
- Reliability and Validity Testing

### Outputs

- Validated trust model
- Behavioural pathway analysis
- Evidence-based AI verification recommendations

---

## Module 3: Longitudinal Study Pattern Analytics

### Objective

Analyse how students' learning patterns change over time with continuous GenAI usage.

### Data Sources

- Weekly study diaries
- AI-assisted study hours
- Independent study hours
- Academic GenAI prompt samples

### Methodologies

- Time-series analysis
- Trend analysis
- Moving averages
- Behaviour evolution modelling

### Outputs

- AI usage evolution curves
- Study habit changes
- Prompt behaviour trends
- Learning pattern profiles

---

## Module 4: NLP-Based Cognitive Retention Framework

### Objective

Evaluate the impact of GenAI-assisted learning on cognitive engagement and knowledge retention.

### Experimental Approach

Comparison between:

- Brain-only writing condition
- GenAI-assisted writing condition

### Methodologies

- Natural Language Processing
- Lexical diversity analysis
- Semantic similarity analysis
- Readability analysis
- Recall evaluation

### Outputs

- Writing quality comparison
- Cognitive retention analysis
- Learning ownership evaluation

---

# Dataset

The research collects primary data from undergraduate students.

## Data Sources

### 1. Psychometric Survey

Includes:

- GenAI usage behaviour
- Cognitive offloading indicators
- Algorithmic trust
- Verification behaviour
- Learning strategies
- Responsible AI practices

### 2. Longitudinal Study Records

Includes:

- Weekly study patterns
- AI-assisted learning time
- Independent learning time
- Academic task information

### 3. GenAI Interaction Data

Includes:

- Voluntary anonymized academic prompt samples
- Prompt categories
- Usage behaviour patterns

### 4. Controlled Writing Experiment

Includes:

- AI-assisted writing outputs
- Brain-only writing outputs
- Recall measurements
- NLP-based writing features

---

# Technology Stack

## Programming Languages

- Python
- R

## Machine Learning

- Scikit-learn
- XGBoost
- Random Forest

## Explainable AI

- SHAP

## Statistical Analysis

- R Studio
- lavaan

## Natural Language Processing

- NLTK
- spaCy
- TF-IDF
- Semantic Analysis

## Data Processing

- Pandas
- NumPy

## Visualization

- Matplotlib
- Seaborn
- Power BI / Analytics Dashboard

---

# Evaluation Metrics

## Machine Learning

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Calibration Analysis

## Clustering / Behaviour Analysis

- Silhouette Score
- Cluster Validation Metrics

## SEM

- CFI
- TLI
- RMSEA
- SRMR
- Composite Reliability

## NLP

- Text similarity metrics
- Readability scores
- Lexical diversity
- Human evaluation agreement

---

# Repository Structure

```
J26-DS-310-genai-learning-analytics/

│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── preprocessing/
│   ├── cognitive_offloading_model/
│   ├── sem_analysis/
│   ├── time_series_analysis/
│   └── nlp_analysis/
│
├── src/
│   ├── data_processing/
│   ├── machine_learning/
│   ├── explainability/
│   ├── statistics/
│   └── nlp/
│
├── survey/
│   └── questionnaire/
│
├── experiments/
│   └── writing_tasks/
│
├── reports/
│
└── README.md
```

---

# Research Team

| Member | Research Component |
|---|---|
| Thisayuru E.L.H. (IT23426580) | Explainable Cognitive Offloading Risk Prediction |
| A.M.W.P.G.S.R. Kumari (IT23217904) | Algorithmic Trust & Verification SEM Model |
| H.M.S.U. Dissanayake (IT23426344) | Longitudinal Study Pattern Analytics |
| G.L.H.G. Sathsara (IT23165220) | NLP-Based Cognitive Retention Evaluation |

---

# Research Keywords

- Generative Artificial Intelligence
- Learning Analytics
- Educational Data Mining
- Cognitive Offloading
- Algorithmic Trust
- Explainable Artificial Intelligence
- Structural Equation Modelling
- Natural Language Processing
- Responsible AI
- Higher Education Analytics

---

# Institution

**Sri Lanka Institute of Information Technology (SLIIT)**

Research Cluster:

**Centre of Excellence in Artificial Intelligence (CoEAI)**

Specialization:

**Data Science**

---

# License

This repository is developed for academic research purposes only.
