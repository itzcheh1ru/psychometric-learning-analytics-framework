# COMPONENT 1: EXECUTIVE BRIEFING SUMMARY
## Explainable Cognitive Offloading Risk Model

**Project:** Explainable Cognitive Offloading Risk Model Among Undergraduate GenAI Users  
**Project Code:** J26-DS-310 | **Student ID:** IT23426580  
**Milestone:** Final Progress Evaluation (Component 1) | **Date:** October 2026  
**Champion Model:** Calibrated Thresholded Ridge Regressor (Ordinal Formulation)  
**Primary Validation:** 25-Fold Repeated Stratified Cross-Validation on Training Partition ($N=300$)  
**Benchmark Note:** 75-Record Holdout Split is formally designated an *Exposed Historical Benchmark Split*  
**Interactive UI:** `http://localhost:8501` (Online & Verified)

---

## 1. Research Overview & Problem Statement
Undergraduate students increasingly rely on Generative AI (ChatGPT, Claude, Copilot) for academic coursework. While AI can assist learning, habitual **cognitive offloading**—delegating critical reasoning, problem-solving, and memory retrieval to algorithms—threatens core academic competencies and fosters automation bias. 

**Component 1** delivers an explainable machine learning risk model designed to:
1. Predict individual student risk tiers (**Low**, **Medium**, **High**).
2. Quantify continuous latent offloading tendencies.
3. Provide exact, actionable **LinearSHAP** explanations indicating which behavioral antecedents elevate or mitigate risk.

---

## 2. Target Formulation & Methodological Integrity
- **Approved Target Definition:** In strict accordance with Proposal Appendix B (Section E, Items 21–26), the target construct `co_score` is the unweighted mean of six approved Likert items measuring memory offloading, effort avoidance, superficial acceptance, strategy surrender, reasoning substitution, and autonomy reduction.
- **Psychometric Reliability:** Scale exhibits high internal consistency with **Cronbach's $\alpha = 0.8649$**.
- **Empirical Tertile Boundaries:** Low ($\le 2.667$), Medium ($2.668 - 3.500$), High ($> 3.500$). *(Flagged for supervisor approval as sample-dependent relative bounds).*
- **Zero Leakage Verified:** All target items, derived variables, and Section G Academic AI Dependence items (including `Q37_important_part`, which caused severe leakage in early prototypes) are 100% excluded from model predictors.

---

## 3. Champion Model Selection: Thresholded Ridge Regressor
Model selection was conducted strictly using **25-fold Repeated Stratified Cross-Validation on the training partition (`X_train`, $N=300$)**, blinding the decision entirely to test data:

```
+-------------------------------------------------------------------------------------------------+
|                         TRAINING PARTITION BENCHMARK (N=300, 25 CV FOLDS)                       |
+-------------------------------------------------------------------------------------------------+
| Architecture                   | CV Macro-F1 (±SD)  | CV Accuracy | Medium-Recall | CV Log-Loss |
|--------------------------------|:------------------:|:-----------:|:-------------:|:-----------:|
| Thresholded Ridge (Compact 51) | 0.5495 (± 0.0619)  |   54.67%    |    59.78%     |   0.9376    |
| Thresholded Ridge (Full 68)    | 0.5419 (± 0.0610)  |   53.93%    |    58.58%     |   0.9600    |
| SVM (RBF Kernel)               | 0.5414 (± 0.0513)  |   54.67%    |    41.54%     |   0.9267    |
| Extra Trees (Tuned Base)       | 0.5259 (± 0.0561)  |   53.93%    |    33.99%     |   0.9611    |
| Calibrated Extra Trees         | 0.5202 (± 0.0649)  |   54.00%    |    28.36%     |   0.9408    |
| CatBoost Classifier            | 0.5059 (± 0.0563)  |   51.93%    |    30.71%     |   0.9632    |
| Random Forest (Tuned)          | 0.4940 (± 0.0669)  |   50.60%    |    32.19%     |   0.9536    |
| XGBoost Classifier             | 0.4922 (± 0.0615)  |   50.53%    |    28.18%     |   0.9537    |
+-------------------------------------------------------------------------------------------------+
```

### Why Thresholded Ridge was Selected Over Tree Ensembles:
1. **Solves the "Medium Risk Collapse":** Standard nominal trees collapse on interior class boundaries, detecting Medium Risk with only $28\% - 34\%$ recall. Thresholded Ridge achieves **$59.78\%$ recall on Medium Risk** by modeling the continuous ordinal latent construct.
2. **Substantial Continuous Signal:** Directly predicting continuous `co_score` achieves $R^2 = 0.4459$ ($\text{RMSE} = 0.5779$), establishing a **large psychological effect size (Cohen's $f^2 = 0.8048$)**.
3. **Lowest Probabilistic Error:** Achieves the lowest multi-class cross-validated log-loss (**0.9376**).
4. **Exact LinearSHAP:** Instantaneous, deterministic feature contributions ($\phi_j = \beta_j (x_j - \bar{x}_j)$) without sampling variance.

---

## 4. Key Performance Results on Exposed Historical Split ($N=75$)
- **Accuracy:** **57.33%** | **Macro-F1:** **0.5815** | **Weighted-F1:** **0.5788**
- **Macro-Precision:** **0.6574** | **Macro-Recall:** **0.5708** | **ROC-AUC (Macro):** **0.7576**
- **Per-Class Metrics:**
  - **Low Risk:** Precision = 0.6842, Recall = 0.4815, F1 = 0.5652 (Support = 27)
  - **Medium Risk:** Precision = 0.4419, Recall = 0.7308, F1 = 0.5507 (Support = 26)
  - **High Risk:** Precision = 0.8462, Recall = 0.5000, F1 = 0.6286 (Support = 22)
- **Ordinal Error Structure:** Confusion matrix: `[[13, 14, 0], [5, 19, 2], [1, 10, 11]]`. Out of 32 total classification errors, **31 errors (96.9%) are adjacent off-by-one errors**. Zero True Low students were misclassified as High Risk.

---

## 5. Key SHAP Behavioral Antecedents
- **Top Risk-Elevating Factors:** Task delegation frequency (`Q20`, $\beta = +0.1253$), tool proliferation (`tool_perplexity` $+0.0919$, `tool_claude` $+0.0878$), usage frequency (`ai_usage_freq` $+0.0870$), and direct copy-pasting (`Q1` $+0.0719$).
- **Top Protective Factors:** Perceived academic autonomy (`Q8_complete_without_ai`, $\beta = -0.1339$), mature age group (`age_group` $-0.1413$), conceptual exploratory usage (`purpose_understanding_concepts` $-0.0724$), and cognitive verification effort (`Q22`).

---

## 6. Implementation Hardening & UI Verification
1. **Score Range Constraint:** Resolved continuous score anomaly where extreme profiles previously displayed `5.046 / 5.0`. Displayed score is strictly clamped to $[1.0, 5.0]$ while preserving the raw linear estimate (`5.265`) for statistical auditing.
2. **Input Validation Guard:** Submissions with empty inputs (`{}`) return `validation_error` (`MissingRequiredInput`), completely preventing silent misleading assessments of non-existent students.
3. **Robustness:** Safely handles $\text{NaN}$, $\pm\infty$, and unparseable strings with median imputation and transparent audit logging.
4. **Automated Verification:**
   - 9/9 Architectural checkpoints passed ([test_complete_integration_workflow_v4.py](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/verification/test_complete_integration_workflow_v4.py)).
   - 8/8 Specified regression scenarios passed ([test_regression_scenarios_v4.py](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/verification/test_regression_scenarios_v4.py)).
   - Streamlit UI running live on `http://localhost:8501`.

---

## 7. Limitations & Honest Academic Disclosures
- **Exposed Split:** The 75-record test set was exposed across earlier development versions; future validation requires a newly collected cohort.
- **Sample Scope:** $N = 375$ from a single institution; findings represent an initial baseline.
- **Probability Calibration Disclosure:** Class probabilities represent parametric normal density estimates derived from regression residuals ($\sigma = 0.5588$), rather than empirically calibrated frequentist probabilities via post-hoc Platt scaling.
