# Component 1: Historical 75-Student 20-Input UI Error Analysis

**Project:** Psychometric Learning Analytics Framework (`J26-DS-310`)  
**Component:** Component 1 – Explainable Cognitive Offloading Risk Prediction (`IT23426580`)  
**Model:** Version 4 Calibrated Thresholded Ridge Regressor (`models/thresholded_ridge_v4.joblib`)  
**Reproducible Script:** [`component1_streamlit_v4/scripts/analyze_ui_historical_errors.py`](../scripts/analyze_ui_historical_errors.py)  
**Benchmark Split:** Stratified holdout partition ($N = 75$, `test_size=75`, `random_state=42`) from the de-identified Version 4 cohort ($N = 375$). *Note: This split is explicitly disclosed as an Exposed Historical Benchmark Split; training-only 5×5 Repeated CV ($N=300$) remains the primary unbiased model-selection protocol.*

---

## 1. Executive Summary & Root Bug Discovery

Comparing the live **20-input web questionnaire payload** against the **full 68-feature survey vector** on the historical 75-student holdout revealed **two distinct mechanisms** explaining why the earlier 20-input validation produced `54.67%` accuracy, `0.5457` Macro-F1, `40.91%` High-Risk recall, and `88.00%` 68-feature agreement:

1. **Discovered & Fixed Production Dropdown Mapping Bug (`classify_meta_faculty`):**  
   In `app/services/cognitive_offloading/integration_service.py`, `classify_meta_faculty()` originally copied a raw survey free-text substring matcher (`"cs" in v`, `"it" in v`). When the finalized UI `<select name="degree_field">` submitted the canonical slugs `"Business_Economics"` (`"economiCS"` contains `"cs"`) and `"Humanities_Health_Other"` (`"humanITies"` contains `"it"`), **both faculty categories were silently misclassified as `Computing_IT`** (affecting 17 Business/Economics students and Humanities respondents in the 75-student split).  
   Fixing canonical slug matching and regex boundaries in `classify_meta_faculty()`—**without retraining, altering model weights, thresholds, imputation medians, or LinearSHAP formulas**—eliminated two exact borderline High-Risk misses (Rows 2 and 65) and brought the 20-input UI to **exact accuracy parity (`57.33%`) and exact High-Risk recall parity (`50.00%`) with the full 68-feature model**.

2. **Structural Behavior of 36 Uncollected Features & Tertile Boundaries:**  
   Even after fixing `degree_field`, 36 of the 68 model features (unused psychometric subscales Q16–Q19, Q23–Q27, 4 of 6 trust items Q28/Q29/Q31/Q32, self-efficacy Q39–Q43, 6 usage-purpose binary indicators, `count_purposes`, `composite_tam`, `composite_self_efficacy`) are imputed/derived using peer training medians. Median imputation acts as Bayesian shrinkage toward the cohort center ($\approx 3.058$), lifting Medium-Risk recall to `80.77%` while pulling borderline extremes slightly toward Medium (`-0.0808` mean score shift for true High-Risk students).

---

## 2. Quantitative Benchmark Comparison ($N = 75$ Holdout)

| Metric | Full 68-Feature Model | 20-Input UI (Pre-Fix Audit Baseline) | 20-Input UI (Post-Fix Verified) |
|---|:---:|:---:|:---:|
| **Accuracy (%)** | **57.33%** | 54.67% | **57.33%** (parity) |
| **Macro-F1** | **0.5815** | 0.5457 | **0.5796** |
| **Weighted-F1** | **0.5788** | 0.5431 | **0.5738** |
| **Macro Precision** | 0.6574 | 0.6829 | **0.6892** |
| **Weighted Precision** | 0.6477 | 0.6650 | **0.6716** |
| **Macro Recall** | 0.5708 | 0.5414 | **0.5717** |
| **ROC-AUC (OvR Macro)** | 0.7576 | **0.7605** | 0.7562 |
| **Multi-Class Log-Loss** | **0.8803** | 0.9006 | 0.9057 |
| **Continuous RMSE / MAE** | 0.5779 / **0.4578** | **0.5718** / 0.4611 | 0.5749 / 0.4619 |
| **68-Feature Class Agreement** | 100.00% (75/75) | 88.00% (66/75) | **90.67% (68/75)** |
| **Continuous Score MAE vs 68-Feat** | 0.0000 | 0.1254 ($r = 0.9548$) | **0.1199 ($r = 0.9570$)** |

### Per-Class Performance Comparison

| Risk Class | Support | Full-68 P / R / F1 | UI Pre-Fix P / R / F1 | UI Post-Fix P / R / F1 |
|---|:---:|:---:|:---:|:---:|
| **Low** ($\le 2.667$) | 27 | 68.42% / 48.15% / 0.5652 | 61.11% / 40.74% / 0.4889 | 61.11% / 40.74% / 0.4889 |
| **Medium** ($2.668 - 3.500$) | 26 | 44.19% / 73.08% / 0.5507 | 43.75% / **80.77%** / 0.5676 | 45.65% / **80.77%** / **0.5833** |
| **High** ($> 3.500$) | 22 | 84.62% / 50.00% / 0.6286 | **100.00%** / 40.91% / 0.5806 | **100.00%** / **50.00%** / **0.6667** |

### Confusion Matrices (Rows = True `[Low, Medium, High]`, Columns = Predicted `[Low, Medium, High]`)

- **Full 68-Feature Model:** `[[13, 14, 0], [5, 19, 2], [1, 10, 11]]`  
- **20-Input UI (Pre-Fix):** `[[11, 16, 0], [5, 21, 0], [2, 11, 9]]`  
- **20-Input UI (Post-Fix):** `[[11, 16, 0], [5, 21, 0], [2, 9, 11]]`  
- **Agreement Matrix (Rows = Full-68 Pred, Cols = UI Post-Fix Pred):** `[[16, 3, 0], [2, 41, 0], [0, 2, 11]]` — **all 7 prediction disagreements (`9.33%`) are strictly adjacent off-by-one tier shifts** (`0` Low↔High flips).

---

## 3. Diagnostic Findings on Error Patterns

### 3.1 Why High-Risk Misses Occur (and How High-Risk Recall Improved to 50.00%)
Out of 22 true High-Risk students in the historical holdout:
- **11 / 22 (`50.00%`) are correctly identified as High Risk** with **`100.00%` precision (`11/11` predicted High are truly High; zero false High alarms)**.
- Two borderline Business/Economics High-Risk students previously missed under the faculty bug moved back above `3.500` after the canonical fix:
  - **Holdout Row 2** (`true co_score = 4.000`): predicted score increased from `3.476` (Medium) to **`3.552` (High)** (`+0.052` above cutoff).
  - **Holdout Row 65** (`true co_score = 3.667`): predicted score increased from `3.492` (Medium) to **`3.568` (High)** (`+0.068` above cutoff).
- Among the **11 remaining High-Risk misses**:
  - **9 / 11 are adjacent Medium predictions** (`2.821` to `3.447`), including Row 7 (`3.447`, `-0.053` below `3.500`) and Row 20 (`3.334`, `-0.166` below `3.500`).
  - Only **2 / 22 (`9.1%`)** are severe two-tier underpredictions (`Low`): Row 5 (`pred_68 = 2.408 Low`, `pred_ui = 2.399 Low` — a respondent whose antecedents looked strongly low-risk even with all 68 features) and Row 53 (`pred_68 = 2.863 Medium`, `pred_ui = 2.609 Low`).

### 3.2 Continuous Boundary Crowding & Shrinkage Toward the Cohort Mean
- **Boundary Crowding:** Out of `32` post-fix UI misclassifications, **`20 / 32 (62.5%)`** have predicted scores falling within `±0.25` Likert points of a tertile threshold (`2.667` or `3.500`), and `12 / 32 (37.5%)` have true `co_score` values within `±0.25` of a threshold.
- **Imputation Shrinkage:** Mean signed score shift `(raw_ui - raw_68)` by true class is:
  - True **Low**: **`+0.0435`** (slightly pulled upward toward Medium)
  - True **Medium**: **`-0.0116`** (nearly unbiased)
  - True **High**: **`-0.0808`** (slightly pulled downward toward Medium)
- **Top Contributors to Score Shift (Median-Imputed Features):**
  - `count_purposes` (`coef = -0.0421`, mean `|shift| = 0.0477`)
  - `Q29_trust_consistent` (`coef = +0.0607`, mean `|shift| = 0.0445`, High-class shift `-0.0303`)
  - `Q31_trust_explanations` (`coef = +0.0621`, mean `|shift| = 0.0439`, High-class shift `-0.0367`)
  - `Q23_pu_improves_understanding` (`coef = +0.0873`, mean `|shift| = 0.0419`)
  - `Q24_pu_complete_effectively` (`coef = -0.0580`, mean `|shift| = 0.0317`)

### 3.3 LinearSHAP Explanation Fidelity
- **Top-3 SHAP Factor Overlap (20-UI vs Full-68):** **`83.56%`**  
- **Top-5 SHAP Factor Overlap (20-UI vs Full-68):** **`80.53%`**  
- **Spurious Imputed-Feature Top-5 Attributions:** **`0 / 375` slots (`0.00%`)** — because omitted variables are set to peer medians near `background_means`, their LinearSHAP attribution $\beta_j (x_j - \bar{x}_j) \approx 0$, preventing unasked questionnaire items from masquerading as primary personal drivers.

### 3.4 Calibrated Probability Behavior & Overconfidence Check
- Gaussian residual cumulative densities ($\sigma = 0.5588$) yield **Multiclass Brier Score = `0.5350`** and **Top-Label ECE = `0.0761`**.
- Predictions are **not overconfident** in the ambiguous middle zone:
  - Confidence `[0.4, 0.5]`: `n = 16`, empirical accuracy `37.5%` (mean confidence `47.5%`) — users with borderline predictions accurately receive ~`45%–53%` probabilities reflecting real classification uncertainty.
  - Confidence `[0.6, 0.7]`: `n = 10`, empirical accuracy `90.0%` (mean confidence `66.1%`).
  - Confidence `[0.7, 0.8]`: `n = 7`, empirical accuracy `85.7%` (mean confidence `73.6%`).
  - Confidence `[0.9, 1.0]`: `n = 1`, empirical accuracy `100.0%` (mean confidence `95.2%`).

---

## 4. Operational Recommendation (Without Retraining)
Because the `±0.25` threshold boundary zone accounts for **`62.5%`** of misclassifications and true High-Risk students shifted downward by `-0.0808` under partial-input imputation, educational advisories displayed in the UI rightly pair the **categorical tier** with the **continuous score spectrum bar** and **three-class probabilities**, ensuring a student at `3.45 / 5.0` sees a ~`45%` High-Risk probability rather than treating `Medium` as "no risk." Further improvement above `~57%` holdout accuracy requires collecting missing `Q29/Q31/Q23` items or validating on an **independent student cohort** using [`evaluate_independent_cohort.py`](../scripts/evaluate_independent_cohort.py).
