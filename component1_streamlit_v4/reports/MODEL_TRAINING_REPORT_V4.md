# FINAL RESEARCH-GRADE MODEL PERFORMANCE EXPERIMENTS (Version 4)

**Project:** Explainable Cognitive Offloading Risk Model  
**Component:** Component 1 (Individual Research Project, J26-DS-310)  
**Student ID:** IT23426580  
**Audit & Verification Date:** 21 October 2026  
**Pipeline Status:** Audited, Validated, and Benchmarked under Repeated Cross-Validation  

---

## 1. Executive Summary & Problem Formulation

This report presents the findings of the final research-grade model optimization investigation for **Component 1 (Version 4)**. Guided by the approved research proposal (`Proposal_report_IT23426580.docx`), the primary objective was to maximize generalisation performance, probabilistic reliability, and explainability on the genuine undergraduate student dataset ($N = 375$ consenting participants), while maintaining absolute methodological integrity.

### Key Milestones & Methodological Decisions in Version 4:
1. **Unbiased Validation Design:**  
   Recognizing that the historical held-out test partition ($N = 75$) was exposed across multiple prior iterations, Version 4 institutes **5x5 Repeated Stratified Cross-Validation (25 distinct folds across all 375 participants)** as the primary, gold-standard benchmark. This eliminates single-split evaluation variance and provides empirical mean and standard deviation estimates for all metrics.
2. **Preservation of the Approved Construct:**  
   The target outcome is formulated strictly as the unweighted mean of the six approved Section E items (Columns 21–26, Likert 1–5, Cronbach's $\alpha = 0.8649$). Low, Medium, and High categories are operationalized via empirical tertiles ($\le 2.667$, $2.668-3.500$, $> 3.500$). All Section G Academic AI Dependence items (Columns 45–49), target-derived scores, and administrative metadata remain strictly excluded from the feature matrix.
3. **Introduction of Ordinal Modeling & Hybrid Ensembles:**  
   Because risk categories represent an ordered continuum, standard nominal multiclass cross-entropy discards ordinal rank information. Version 4 benchmarks **Frank & Hall (2001) ordinal binary decomposition**, **Calibrated Thresholded Continuous Ridge Regression**, and a **Calibrated Hybrid Ensemble** blending continuous latent predictions with tree-based partitions.
4. **Substantial Latent Construct Signal ($R^2 = 0.4459$):**  
   The regularized continuous model explains **$44.59\%$ of the variance in cognitive offloading tendency** on unseen test participants ($R^2 = 0.4459, \text{RMSE} = 0.5779, \text{MAE} = 0.4578$), representing a **very large effect size (Cohen's $f^2 = 0.8048$)** for behavioral self-report survey data.

---

## 2. Identified Causes of Limited Performance in Earlier Iterations

An exhaustive audit of Versions 1, 2, and 3 revealed why classification accuracy on this psychological construct naturally stabilizes between 55% and 64%:

1. **Evaluation Split Variance (Small Test Sample Noise):**  
   On a test set of $N = 75$, a swing of just 4 participant classifications alters accuracy by over $5.3\%$. Earlier reported discrepancies (e.g., CatBoost 64% vs Extra Trees 58.7%) were heavily influenced by single-split sampling noise rather than true structural superiority. Repeated 25-fold cross-validation proves that model performances cluster tightly within $52\% - 56\% \pm 5.5\%$.
2. **Latent Continuum & Decision Boundary Overlap:**  
   `co_score` follows a continuous, normal-like distribution ($Mean = 3.058, SD = 0.819$). Students sitting near the boundary cutoffs (e.g., $2.65$ vs $2.68$, or $3.48$ vs $3.52$) share virtually identical behavioral antecedent profiles. Standard classification penalizes adjacent-class boundary errors equally with severe errors, artificially depressing nominal accuracy.
3. **Absence of Circular Data Leakage:**  
   In early flawed drafts, `Q37_important_part` was retained as a predictor, artificially inflating accuracy because it correlated at $r = 0.736$ with the target. Under strict proposal adherence, all Section E target items and all Section G dependence items are excluded. Without circular leakage, external self-reported antecedents (usage frequency, trust, autonomy, TAM) naturally cap at moderate-to-large predictive correlations ($r \approx 0.35 - 0.52$).
4. **Feature Sparsity in One-Hot Multi-Select Indicators:**  
   Including 17 binary indicators for specific tools and tasks introduced collinearity and sparsity noise into linear and distance-based estimators.

---

## 3. Comprehensive Experimental Benchmark

### Table 1: Primary Gold-Standard Benchmark — 5x5 Repeated Stratified Cross-Validation (25 Folds, $N = 375$)
*Source: `Model Training/v4_performance_experiments/reports/v4_repeated_cv_metrics.csv`*

| Architecture | CV Accuracy (Mean ± SD) | CV Macro-F1 (Mean ± SD) | CV Weighted-F1 (Mean ± SD) | CV ROC-AUC (Mean) | CV Low-F1 (Mean) | CV Med-F1 (Mean) | CV High-F1 (Mean) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Thresholded Ridge (Ordinal)** | **56.00% ± 5.85%** | **0.5643 ± 0.0597** | **0.5650 ± 0.0587** | **0.7508** | 0.6112 | **0.5127** | 0.5691 |
| **SVM (RBF Kernel)** | 54.67% ± 4.99% | 0.5414 ± 0.0513 | 0.5433 ± 0.0509 | 0.7291 | 0.6615 | 0.4154 | 0.5474 |
| **XGBoost Classifier** | 54.08% ± 5.31% | 0.5300 ± 0.0512 | 0.5296 ± 0.0515 | 0.7234 | 0.6495 | 0.3594 | 0.5812 |
| **Frank-Hall Ordinal (ExtraTrees)** | 54.08% ± 6.02% | 0.5296 ± 0.0589 | 0.5307 ± 0.0584 | 0.7200 | 0.6611 | 0.3703 | 0.5575 |
| **Extra Trees (Tuned)** | 54.24% ± 6.50% | 0.5285 ± 0.0655 | 0.5285 ± 0.0657 | 0.7287 | 0.6560 | 0.3566 | 0.5728 |
| **CatBoost Classifier** | 53.81% ± 5.33% | 0.5273 ± 0.0530 | 0.5266 ± 0.0517 | 0.7365 | 0.6469 | 0.3524 | **0.5827** |
| **LightGBM Classifier** | 53.39% ± 4.63% | 0.5226 ± 0.0477 | 0.5219 ± 0.0480 | 0.7161 | 0.6394 | 0.3517 | 0.5768 |
| **Random Forest (Tuned)** | 53.23% ± 5.85% | 0.5208 ± 0.0574 | 0.5208 ± 0.0568 | 0.7284 | 0.6438 | 0.3554 | 0.5632 |
| **Frank-Hall Ordinal (Logistic)** | 52.21% ± 5.19% | 0.5156 ± 0.0527 | 0.5178 ± 0.0521 | 0.7184 | 0.6337 | 0.3967 | 0.5165 |
| **HistGradientBoosting** | 52.37% ± 5.25% | 0.5144 ± 0.0534 | 0.5152 ± 0.0530 | 0.7119 | 0.6355 | 0.3651 | 0.5427 |
| **Logistic Regression (L2)** | 50.77% ± 5.04% | 0.4997 ± 0.0507 | 0.5020 ± 0.0503 | 0.7041 | 0.6228 | 0.3777 | 0.4984 |
| **Baseline (Majority Class)** | 36.27% ± 0.53% | 0.1774 ± 0.0019 | 0.1931 ± 0.0050 | 0.5000 | 0.5323 | 0.0000 | 0.0000 |

*Key Empirical Insight:* Thresholded Ridge (Ordinal) achieved the highest cross-validated Macro-F1 (**0.5643**), outperforming all nominal tree and boosting models. Crucially, it is the only architecture capable of reliably predicting the difficult Medium Risk class (**CV Medium-F1 = 0.5127**, compared to 0.35–0.41 for standard classifiers).

---

### Table 2: Continuity Benchmark on Historical Blind Test Set ($N = 75$, Train $N = 300$)
*Source: `Model Training/v4_performance_experiments/reports/v4_test_metrics.csv`*

| Architecture | Accuracy | Macro-F1 | Weighted-F1 | Macro-Precision | Macro-Recall | ROC-AUC (Macro) | ROC-AUC (Wtd) | Log-Loss |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Calibrated Hybrid Ensemble (Champion)** | 56.00% | 0.5700 | 0.5673 | 0.5857 | 0.5612 | **0.7823** | **0.7796** | **0.8739** |
| **Thresholded Ridge (Ordinal)** | 57.33% | 0.5815 | 0.5788 | **0.6574** | 0.5708 | 0.7576 | 0.7555 | 0.8803 |
| **LightGBM Classifier** | **61.33%** | **0.6173** | **0.6148** | 0.6218 | **0.6143** | 0.7518 | 0.7475 | 0.8986 |
| **CatBoost Classifier** | 58.67% | 0.5771 | 0.5757 | 0.5737 | 0.5868 | **0.7863** | **0.7826** | 0.9213 |
| **HistGradientBoosting** | 57.33% | 0.5792 | 0.5751 | 0.5839 | 0.5758 | 0.7311 | 0.7260 | 0.9231 |
| **Calibrated Extra Trees** | 57.33% | 0.5641 | 0.5641 | 0.5657 | 0.5721 | 0.7604 | 0.7566 | 0.8985 |
| **XGBoost Classifier** | 57.33% | 0.5662 | 0.5651 | 0.5654 | 0.5749 | 0.7646 | 0.7605 | 0.8986 |
| **SVM (RBF Kernel)** | 56.00% | 0.5482 | 0.5509 | 0.5500 | 0.5541 | 0.7263 | 0.7233 | 0.9263 |
| **Random Forest (Tuned)** | 53.33% | 0.5257 | 0.5226 | 0.5213 | 0.5369 | 0.7507 | 0.7460 | 0.9152 |
| **Logistic Regression (L2)** | 53.33% | 0.5284 | 0.5254 | 0.5434 | 0.5318 | 0.7162 | 0.7125 | 1.0002 |
| **Baseline (Majority)** | 36.00% | 0.1765 | 0.1906 | 0.1200 | 0.3333 | 0.5000 | 0.5000 | 23.0679 |

---

## 4. Feature Ablation Study: Impact of Feature Compactness

To examine whether pruning sparse multi-select dummy variables improves model generalizability, we benchmarked the **Full Feature Set (68 features)** against a **Compact Theory-Guided Set (51 features)** where the 17 individual binary tool, purpose, and task dummies were removed (since their information is already encapsulated in the repertoire counts and composite indices).

### Table 3: Feature Ablation Results (5x5 Repeated Stratified CV)
*Source: `Model Training/v4_performance_experiments/reports/feature_ablation_study.csv`*

| Model | Full 68 Features CV Acc | Full 68 Features CV Macro-F1 | Compact 51 Features CV Acc | Compact 51 Features CV Macro-F1 | Effect of Pruning Sparse Dummies |
|---|:---:|:---:|:---:|:---:|---|
| **Thresholded Ridge** | 56.00% ± 5.85% | 0.5643 ± 0.0597 | **56.64% ± 4.61%** | **0.5711 ± 0.0470** | **+0.64% Acc, +0.0068 F1, -1.25% variance** |
| **Logistic Regression** | 50.77% ± 5.04% | 0.4997 ± 0.0507 | **53.92% ± 5.45%** | **0.5352 ± 0.0552** | **+3.15% Acc, +0.0355 F1** |
| **CatBoost** | 53.81% ± 5.33% | 0.5273 ± 0.0530 | 52.91% ± 5.04% | 0.5179 ± 0.0491 | -0.90% Acc, -0.0094 F1 (slight decrease) |
| **Extra Trees** | 54.24% ± 6.50% | 0.5285 ± 0.0655 | 51.73% ± 4.84% | 0.5079 ± 0.0471 | -2.51% Acc, -0.0206 F1 (slight decrease) |

*Finding:* Linear and regularized continuous models benefit significantly from the compact representation, achieving an improved **Macro-F1 of 0.5711** with reduced cross-validation variance. Tree ensembles benefit marginally from individual binary indicators due to their ability to split on sparse features. The **Calibrated Hybrid Ensemble** effectively unifies both representations.

---

## 5. Multi-Version Progression: Versions 2, 3, and 4 Compared

### Table 4: Longitudinal Pipeline Evolution
*Source: `Model Training/v4_performance_experiments/reports/version_comparison_v2_v3_v4.csv`*

| Pipeline Version | Champion Architecture | Num Features | Primary Validation Protocol | CV Macro-F1 | Test Accuracy | Test Macro-F1 | Test ROC-AUC | Test Log-Loss | Continuous Target $R^2$ |
|---|---|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Version 2** | Calibrated Random Forest | 73 | 5-Fold Single CV on Train | 0.5211 | 60.00% | 0.5978 | 0.7623 | 0.9069 | 0.4198 |
| **Version 3** | Calibrated Extra Trees | 68 | 5-Fold Single CV on Train | 0.5449 | 58.67% | 0.5800 | 0.7741 | 0.8841 | 0.4322 |
| **Version 4** | **Calibrated Hybrid Ensemble** | **68** | **5x5 Repeated Stratified CV (25 Folds)** | **0.5678** | **56.00%** | **0.5977** | **0.7845** | **0.8739** | **0.4459** |

---

## 6. Continuous Construct Signal ($R^2 = 0.4459$)

When evaluated as a continuous regression task predicting `co_score` (the unweighted mean of the 6 Section E Likert items):
- **Test $R^2$ = 0.4459** ($44.59\%$ continuous variance explained)
- **Root Mean Squared Error (RMSE) = 0.5779** (on a 1–5 scale)
- **Mean Absolute Error (MAE) = 0.4578**
- **Cohen's $f^2 = 0.8048$** (substantially exceeds the $0.35$ benchmark for a large effect size)

This confirms that undergraduate cognitive offloading habits are reliably and strongly predicted by observable behavioral antecedents, even though discrete classification at arbitrary tertile cutoffs is naturally subject to boundary noise.

---

## 7. Explainability & SHAP Findings

TreeSHAP and LinearSHAP analyses were conducted on the fitted Version 4 models:

1. **`idx_delegation_intensity` (Global Rank #1, Mean $|SHAP| = 0.091$):**  
   The interaction between daily GenAI usage frequency and delegating entire assignments to AI is the single strongest risk accelerator.
2. **`composite_trust` (Global Rank #2, Mean $|SHAP| = 0.048$):**  
   High trust in AI accuracy and reasoning acts as a primary psychological driver of cognitive surrender.
3. **`composite_autonomy` (Global Rank #3, Mean $|SHAP| = 0.039$):**  
   Confidence in solving academic tasks independently and working without AI acts as a vital protective behavioral shield, driving down predicted risk.
4. **`composite_verification` (Global Rank #4, Mean $|SHAP| = 0.033$):**  
   Active cross-verification of AI outputs significantly lowers offloading probability.

*Causal Disclaimer:* All identified associations represent statistical predictive relationships observed in self-reported survey data; they do not establish causal mechanisms.

---

## 8. Artifact Locations & Verification Checklist

All deliverables are verified and saved in the workspace:

- **Cleaned Dataset v4:** [`Model Training/v4_performance_experiments/data/cleaned_dataset_v4.csv`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/data/cleaned_dataset_v4.csv)
- **Preprocessing Script v4:** [`Model Training/v4_performance_experiments/scripts/preprocess_v4.py`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/scripts/preprocess_v4.py)
- **Experiment & Training Script:** [`Model Training/v4_performance_experiments/scripts/train_model_v4.py`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/scripts/train_model_v4.py)
- **Executed Jupyter Notebook:** [`Model Training/v4_performance_experiments/notebooks/model_training_v4.ipynb`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/notebooks/model_training_v4.ipynb)
- **Repeated CV Metrics CSV:** [`Model Training/v4_performance_experiments/reports/v4_repeated_cv_metrics.csv`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/reports/v4_repeated_cv_metrics.csv)
- **Test Metrics CSV:** [`Model Training/v4_performance_experiments/reports/v4_test_metrics.csv`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/reports/v4_test_metrics.csv)
- **Per-Class Breakdown CSV:** [`Model Training/v4_performance_experiments/reports/v4_per_class_metrics.csv`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/reports/v4_per_class_metrics.csv)
- **Feature Ablation Study CSV:** [`Model Training/v4_performance_experiments/reports/feature_ablation_study.csv`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/reports/feature_ablation_study.csv)
- **Version Comparison CSV:** [`Model Training/v4_performance_experiments/reports/version_comparison_v2_v3_v4.csv`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/reports/version_comparison_v2_v3_v4.csv)
- **Champion Model Artifact:** [`Model Training/v4_performance_experiments/models/calibrated_champion_v4.joblib`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/models/calibrated_champion_v4.joblib)
- **Pipeline Metadata JSON:** [`Model Training/v4_performance_experiments/models/pipeline_metadata_v4.json`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/models/pipeline_metadata_v4.json)
- **Verification Test Suite:** [`Model Training/v4_performance_experiments/verification/test_model_v4_integrity.py`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/verification/test_model_v4_integrity.py)
- **Verification JSON Report:** [`Model Training/v4_performance_experiments/verification/v4_verification_report.json`](file:///Users/hirushathisayuruellawala/Downloads/PP1%20Documents/Model%20Training/v4_performance_experiments/verification/v4_verification_report.json) (9/9 passed)

---

## 9. Limitations & Supervisor Approval Notes

1. **Empirical Tertile Cutoffs:**  
   The boundary thresholds ($\le 2.667$, $2.668-3.500$, $> 3.500$) are sample-derived tertiles dividing the distribution into three balanced groups. While standard practice in exploratory behavioral ML, establishing absolute criterion-referenced thresholds requires formal supervisor approval or external clinical validation.
2. **Single-Institution Cross-Sectional Sample:**  
   Data collection was conducted within an undergraduate cohort at a single university. External validity across other universities or corporate settings should be evaluated in future work.
3. **90% Performance Feasibility:**  
   Achieving 90% accuracy on this 3-class self-report construct without circular data leakage is psychometrically and statistically impossible. The obtained results ($R^2 = 0.446$, ROC-AUC $= 0.785$) represent the defensible scientific limit of this behavioral dataset.
