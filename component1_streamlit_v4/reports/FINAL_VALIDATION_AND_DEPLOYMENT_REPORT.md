# FINAL MODEL VALIDATION & COMPONENT 1 DEPLOYMENT READINESS REPORT

**Project:** Explainable Cognitive Offloading Risk Model  
**Component:** Component 1 (Individual Undergraduate Research Project, J26-DS-310)  
**Student ID:** IT23426580  
**Audit & Validation Date:** 21 October 2026  
**Pipeline Status:** Audited, Reconciled, and Ready for Deployment Integration  

---

## 1. Audit of the Version 4 Evaluation Design

An independent methodological audit was conducted on the Version 4 training script (`train_model_v4.py`), notebook, model artifacts, metadata, and metric reports. The findings are documented below:

### 1.1 Data Partitioning & Test Set Exposure
- **Cohort Division:** The 375 consenting undergraduate student responses were split into a training partition of $N = 300$ ($80\%$) and a test partition of $N = 75$ ($20\%$) using stratified sampling (`random_state = 42`).
- **Test Set Exposure Audit:**
  1. In `train_model_v4.py`, the 5x5 Repeated Stratified Cross-Validation (25 folds) was executed on the full dataset of $N = 375$ samples. Consequently, the 75 records assigned to the test set were included inside the cross-validation evaluation pool.
  2. The exact same 75-record holdout split was evaluated in Version 2, Version 3, and Version 4.
  3. **Audit Verdict:** The 75-record test set is **heavily exposed** to repeated model comparisons. It **cannot be claimed as a truly blind, independent final test set**. In this report, it is explicitly classified as an **Exposed Historical Benchmark Split**. Unbiased generalization must be judged via training-only cross-validation.

### 1.2 Preprocessing & Feature Engineering Isolation
- All questionnaire cleaning, Likert conversions, subscale composite formulations, and interaction index multiplications operate strictly **row-by-row** (intra-participant). No feature values were calculated across multiple respondents, preventing cross-row information leakage.
- Standard scaling for linear and support vector models was wrapped inside scikit-learn `Pipeline([('scaler', StandardScaler()), ...])`, fitting mean and variance strictly on training folds.

### 1.3 Audit of the Hybrid Ensemble Selection Flaw
- In the initial Version 4 draft, the Calibrated Hybrid Ensemble was proposed as champion partly because it achieved the lowest log-loss ($0.8739$) on the 75-sample test split.
- **Audit Verdict:** The hybrid ensemble weights ($0.40$ Ridge, $0.30$ Extra Trees, $0.30$ CatBoost) were chosen heuristically rather than fitted strictly via out-of-fold cross-validation on `X_train`. Selecting this model based on its test set performance represents post-hoc test-set consultation. This decision is revoked and corrected below.

---

## 2. Corrected Model Selection Protocol & Rationale

### 2.1 Model Selection Criteria (Pre-Specified & Training-Only)
Model selection was re-executed strictly on **training-only cross-validation (`X_train`, $N = 300$)**, blinding the decision entirely to `X_test`:
1. **Primary Criterion:** Highest Cross-Validation Macro-F1 across 25 repeated stratified folds on `X_train`.
2. **Secondary Criterion:** Balanced Per-Class Recall on `X_train`, specifically avoiding the collapse of the Medium Risk class.
3. **Tertiary Criterion:** Probabilistic Calibration (lowest cross-validated multi-class log-loss).
4. **Fourth Criterion:** Direct, mathematically exact SHAP explainability suitable for real-time educational counseling.

### 2.2 Empirical Benchmark on Training Data Only ($N = 300$, 25 Repeated Folds)
*All metrics computed strictly within `X_train` across 5x5 Repeated Stratified CV.*

| Candidate Architecture | CV Accuracy | CV Macro-F1 (Mean ± SD) | CV Medium-Risk Recall | CV Medium-Risk F1 | CV Multi-Class Log-Loss | CV ROC-AUC (OvR Macro) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Thresholded Ridge (Compact 51)** | **54.67%** | **0.5495 ± 0.0619** | **59.78%** | **0.4951** | **0.9376** | **0.7355** |
| **Thresholded Ridge (Full 68)** | 53.93% | 0.5419 ± 0.0610 | 58.58% | 0.4876 | 0.9600 | 0.7315 |
| **Extra Trees (Base)** | 53.93% | 0.5259 ± 0.0561 | 33.99% | 0.3666 | 0.9611 | 0.7122 |
| **Calibrated Extra Trees** | 54.00% | 0.5202 ± 0.0649 | 28.36% | 0.3220 | 0.9408 | 0.7190 |
| **CatBoost (depth=3)** | 51.93% | 0.5059 ± 0.0563 | 30.71% | 0.3351 | 0.9632 | 0.7150 |
| **Random Forest (Tuned)** | 50.60% | 0.4940 ± 0.0669 | 32.19% | 0.3390 | 0.9536 | 0.7074 |
| **XGBoost Classifier** | 50.53% | 0.4922 ± 0.0615 | 28.18% | 0.3090 | 0.9537 | 0.7003 |
| **LightGBM Classifier** | 49.40% | 0.4818 ± 0.0638 | 28.40% | 0.3064 | 0.9746 | 0.6862 |
| **HistGradientBoosting** | 49.20% | 0.4803 ± 0.0740 | 30.15% | 0.3186 | 0.9918 | 0.6865 |
| **Logistic Regression (L2)** | 48.40% | 0.4760 ± 0.0562 | 31.43% | 0.3245 | 1.1234 | 0.6747 |

### 2.3 Defensible Selection Decision: Calibrated Thresholded Ridge Regressor
Based on the pre-specified training-only criteria:
1. **Superior Overall Generalization:** Thresholded Ridge achieved the highest training CV Macro-F1 (**0.5495** on compact features, **0.5419** on full features) and the highest CV accuracy (**54.67%**).
2. **Preservation of the Medium Risk Class:** Standard tree and boosting models suffer from severe majority-class boundary collapse, detecting Medium Risk with only $28\% - 34\%$ recall. In contrast, Thresholded Ridge models the continuous latent construct, detecting Medium Risk with **$59.78\%$ recall**.
3. **Lowest Probabilistic Log-Loss:** Achieves the lowest training CV log-loss (**0.9376**).
4. **Strong Continuous Predictive Power:** Explains **$44.59\%$ of the variance in cognitive offloading tendency** ($R^2 = 0.4459, \text{RMSE} = 0.5779, \text{MAE} = 0.4578$), representing a **large effect size (Cohen's $f^2 = 0.8048$)**.
5. **Exact LinearSHAP Interpretability:** Closed-form, instantaneous feature attribution without sampling noise.

*Comparator Retention:* **Calibrated Extra Trees** is retained as the secondary benchmark comparator, representing the top-performing non-linear tree model (**CV Macro-F1 = 0.5259**).

---

## 3. Performance Metrics on the Exposed Historical Test Split ($N = 75$)

For academic transparency and continuity across project iterations, performance on the historical 75-participant partition is reported below. Readers must interpret these scores with the explicit disclosure that this partition was previously exposed:

### Table 2: Performance on Exposed Historical Test Split ($N = 75$)
*Source: `Model Training/v4_performance_experiments/reports/v4_test_metrics.csv`*

| Architecture | Accuracy | Macro-F1 | Weighted-F1 | Macro-Precision | Macro-Recall | ROC-AUC (Macro) | Log-Loss |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Thresholded Ridge (Selected Champion)** | **57.33%** | **0.5815** | **0.5788** | **0.6574** | **0.5708** | **0.7576** | **0.8776** |
| **LightGBM Classifier** | 61.33% | 0.6173 | 0.6148 | 0.6218 | 0.6143 | 0.7518 | 0.8986 |
| **CatBoost Classifier** | 58.67% | 0.5771 | 0.5757 | 0.5737 | 0.5868 | 0.7863 | 0.9213 |
| **HistGradientBoosting** | 57.33% | 0.5792 | 0.5751 | 0.5839 | 0.5758 | 0.7311 | 0.9231 |
| **Calibrated Extra Trees (Tree Comparator)** | 57.33% | 0.5641 | 0.5641 | 0.5657 | 0.5721 | 0.7604 | 0.8985 |
| **XGBoost Classifier** | 57.33% | 0.5662 | 0.5651 | 0.5654 | 0.5749 | 0.7646 | 0.8986 |
| **SVM (RBF Kernel)** | 56.00% | 0.5482 | 0.5509 | 0.5500 | 0.5541 | 0.7263 | 0.9263 |
| **Random Forest (Tuned)** | 53.33% | 0.5257 | 0.5226 | 0.5213 | 0.5369 | 0.7507 | 0.9152 |
| **Logistic Regression (L2)** | 53.33% | 0.5284 | 0.5254 | 0.5434 | 0.5318 | 0.7162 | 1.0002 |
| **Baseline (Majority Class)** | 36.00% | 0.1765 | 0.1906 | 0.1200 | 0.3333 | 0.5000 | 23.0679 |

### Table 3: Per-Class Precision, Recall, and F1 for Selected Champion (Thresholded Ridge)
*Test Partition $N = 75$*

| Risk Tier | Precision | Recall | F1-Score | Support |
|---|:---:|:---:|:---:|:---:|
| **Low Risk** ($\text{co\_score} \le 2.667$) | 0.6842 | 0.4815 | 0.5652 | 27 |
| **Medium Risk** ($2.668 \le \text{co\_score} \le 3.500$) | 0.4419 | 0.7308 | 0.5507 | 26 |
| **High Risk** ($\text{co\_score} > 3.500$) | 0.8462 | 0.5000 | 0.6286 | 22 |
| **Macro Average** | **0.6574** | **0.5708** | **0.5815** | 75 |
| **Weighted Average** | **0.6481** | **0.5733** | **0.5788** | 75 |

---

## 4. Verification of Target Integrity and Explainability

1. **Target Formulation:** Unweighted mean of the six Section E items (Columns 21–26, Likert 1–5):
   $$\text{co\_score} = \frac{1}{6} \sum_{i=1}^6 Q_i$$
   The scale achieves Cronbach's $\alpha = 0.8649$, indicating high psychometric reliability.
2. **Zero Leakage Verified:** All target-construction items, derived target variables (`co_score`, `co_risk`), all Section G Academic AI Dependence items (Columns 45–49, including `Q37_important_part`), and administrative metadata (Columns 0–4) are strictly excluded from the feature space.
3. **Supervisor Approval Flag on Risk Thresholds:** Risk cutoffs ($\le 2.667$, $2.668-3.500$, $> 3.500$) are empirical tertiles established from this undergraduate cohort. While standard in exploratory modeling, establishing normative criterion-referenced boundaries requires formal supervisor sign-off.
4. **SHAP Explanation Alignment:** LinearSHAP explanations correspond strictly to the selected Thresholded Ridge model, computed via closed-form Shapley values $\phi_j = \beta_j (x_j - \bar{x}_j)$.

---

## 5. Deployment Readiness & Integration Architecture

The production integration service was developed and verified under [`Model Training/v4_performance_experiments/integration/`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/integration/):
- **Singleton Inference Service (`integration_service_v4.py`):** Automatically maps survey questions to the 68-feature space, clamps out-of-range Likert inputs, handles missing values via reference medians, computes calibrated probabilities, and returns top LinearSHAP explanations.
- **REST API Microservice (`api_v4.py`):** FastAPI app exposing `/health` and `/api/v1/predict`.
- **Interactive UI (`app_ui_v4.py`):** Streamlit dashboard providing real-time risk assessment, probability charts, and feature contribution tables.

### 5.1 Automated Reliability Suite Results
The automated test suite ([`test_complete_integration_workflow_v4.py`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/verification/test_complete_integration_workflow_v4.py)) was executed:

```text
EXECUTING COMPLETE INTEGRATION & RELIABILITY TEST SUITE (Version 4)
  ✓ Checkpoint 1: Model loaded successfully from disk without retraining.
  ✓ Checkpoint 2: Valid request succeeded. Predicted: Medium (Conf: 0.52, Score: 3.27)
  ✓ Checkpoint 3: Missing, NaN, and dirty out-of-range inputs handled safely.
  ✓ Checkpoint 4: Schema mismatch handled cleanly with reference median fallback.
  ✓ Checkpoint 5: Model-loading failure simulation raised expected FileNotFoundError.
  ✓ Checkpoint 6: Probability distribution strictly valid (sums to 1.0, range [0, 1]).
  ✓ Checkpoint 7: LinearSHAP explanations compatible with exact directional alignment.
  ✓ Checkpoint 8: API payload simulation executed with exact schema conformance.
  ✓ Checkpoint 9: Privacy verified (zero PII exposure) & research disclaimer enforced.

Ran 9 tests in 0.220s — OK (ALL 9 CHECKPOINTS PASSED)
```

---

## 6. Verified Artifact Paths

| Artifact Description | Verified Path |
|---|---|
| Cleaned Dataset (v4) | `Model Training/v4_performance_experiments/data/cleaned_dataset_v4.csv` |
| Champion Model Artifact | `Model Training/v4_performance_experiments/models/calibrated_champion_v4.joblib` |
| Continuous Regressor | `Model Training/v4_performance_experiments/models/continuous_regressor_v4.joblib` |
| Extra Trees Comparator | `Model Training/v4_performance_experiments/models/extra_trees_v4.joblib` |
| CatBoost Comparator | `Model Training/v4_performance_experiments/models/catboost_v4.joblib` |
| Pipeline Metadata | `Model Training/v4_performance_experiments/models/pipeline_metadata_v4.json` |
| Integration Engine | `Model Training/v4_performance_experiments/integration/integration_service_v4.py` |
| FastAPI Microservice | `Model Training/v4_performance_experiments/integration/api_v4.py` |
| Streamlit Dashboard | `Model Training/v4_performance_experiments/integration/app_ui_v4.py` |
| Executed Jupyter Notebook | `Model Training/v4_performance_experiments/notebooks/model_training_v4.ipynb` |
| Automated Integration Suite | `Model Training/v4_performance_experiments/verification/test_complete_integration_workflow_v4.py` |
| Test Execution Report | `Model Training/v4_performance_experiments/verification/workflow_integration_test_report_v4.json` |
