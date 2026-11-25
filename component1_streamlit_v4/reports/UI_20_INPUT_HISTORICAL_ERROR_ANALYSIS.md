# Component 1: Historical 75-Student Error Analysis & Complete 68-Feature Mapping

**Project:** Psychometric Learning Analytics Framework (`J26-DS-310`)  
**Component:** Component 1 – Explainable Cognitive Offloading Risk Prediction (`IT23426580`)  
**Model:** Version 4 Calibrated Thresholded Ridge Regressor (`models/thresholded_ridge_v4.joblib`)  
**Reproducible Script:** [`component1_streamlit_v4/scripts/analyze_ui_historical_errors.py`](../scripts/analyze_ui_historical_errors.py)  
**Benchmark Split:** Stratified holdout partition ($N = 75$, `test_size=75`, `random_state=42`) from the de-identified Version 4 cohort ($N = 375$).  

> **Methodological Disclosure:** This 75-student partition was reused across Versions 2, 3, and 4 and is therefore formally classified as an **Exposed Historical Benchmark Split**, not a newly collected independent external validation cohort.

---

## 1. Mutually Exclusive 68-Feature UI Input Breakdown (Resolution of 29 vs. 36 vs. 51)

Inspecting [`transform_inputs()`](../../app/services/cognitive_offloading/integration_service.py#L374-L488) against the 20-input web questionnaire yields an **exact, mutually exclusive partition totaling 68 model features**:

| Category | Count | Definition in Production `transform_inputs()` |
|---|:---:|---|
| **A. Directly Collected Numeric Inputs** | **17** | Matched directly by feature column name from the 20 UI inputs (`age_group`, `academic_year`, `ai_usage_freq`, `ai_time_per_week`, `Q1`, `Q20`, `Q22`, `Q2–Q6`, `Q7–Q9`, `Q30`, `Q33`). |
| **B. Purely Engineered from UI Inputs** | **22** | Derived dynamically inside `transform_inputs()` with **zero imputed dependents**: 5 `faculty_*` from `degree_field`, 5 `tool_*` + `count_tools_used` from `tools_used`, 6 `delegate_*` + `count_tasks_delegated` from `tasks_delegated`, 2 fully observed subscales (`composite_verification`, `composite_autonomy`), and 2 fully observed interaction indices (`idx_delegation_intensity`, `idx_passive_adoption`). |
| **C. Fully Imputed / Fixed Reference Features** | **27** | Strictly constant under all 20-input UI submissions: **25** uncollected survey variables (`Q16–Q19`, `Q23–Q27`, `Q28/Q29/Q31/Q32`, `Q39–Q43`, 6 `purpose_*`, `count_purposes`) + **2** subscales whose input batteries are entirely absent from the UI (`composite_tam` fixed at `3.800`, `composite_self_efficacy` fixed at `3.600`). |
| **D. Partially Imputed Hybrid Engineered Features** | **2** | Engineered dynamically from a mix of UI answers and imputed medians: `composite_trust` averages `2` UI items (`Q30`, `Q33`) with `4` imputed trust items (`Q28=3.0, Q29=3.0, Q31=3.0, Q32=4.0`), and `idx_automation_bias` = `composite_trust` (partial) minus `composite_verification` (full UI). |
| **Total Model Features** | **68** | **$17 + 22 + 27 + 2 = 68$** (i.e., **39** purely observed + **29** fully or partly imputed). |

### Why Earlier Notes Mentioned "36 Imputed" or "51 Missing Optional Features"
1. **Why "36" appeared in an earlier check:** A two-profile toggle probe compared two synthetic UI payloads without toggling 9 valid categorical options (`3` unused `faculty_*`, `2` unused `tool_*`, `4` unused `delegate_*`), making `27 + 9 = 36` columns temporarily identical across those two samples. When all valid UI choices vary across students, exactly **`27`** features are completely fixed and **`2`** are partially imputed (**`29` total**, matching the original audit figure).
2. **Why `transform_inputs()` logs `51` missing optional features:** Line 483 counts exact key matches inside `self.feature_names` before resolving multi-value helper keys (`68 - 17 = 51`), even though lines 410–472 deterministically compute `22` purely UI-driven engineered features and `2` partially imputed hybrids. *Per research freeze rules, this runtime log string was left unchanged.*
3. **Key conceptual distinction:** `Q28_trust_reliable_info` (median `3.0`) is **directly/fully imputed**, whereas `composite_trust` and `idx_automation_bias` are **engineered features partially dependent on imputed inputs**—they still respond to student answers on `Q30`, `Q33`, and `Q2–Q6`, but their trust variation is damped by `4/6` imputed items.

---

## 2. Complete Mapping of All 68 Model Features (`pipeline_metadata_v4.json` Order)

| # | Feature Name | Original Survey Variable | UI Q# & Input Key | Generation Method | Direct | Engineered | Fully Imputed | Partial Imputed | Ref Median |
|---:|---|---|---|---|:-:|:-:|:-:|:-:|---:|
| 1 | `age_group` | Col 5 (Demographics) | Q3 (`age_group`) | Ordinal `{1..4}` from UI | Y | N | N | N | `2.000` |
| 2 | `academic_year` | Col 7 (Demographics) | Q2 (`academic_year`) | Ordinal `{1..6}` from UI | Y | N | N | N | `3.000` |
| 3 | `ai_usage_freq` | Col 8 (Usage Habits) | Q4 (`ai_usage_freq`) | Ordinal `{1..4}` from UI | Y | N | N | N | `3.000` |
| 4 | `ai_time_per_week` | Col 11 (Usage Hours) | Q5 (`ai_time_per_week`) | Ordinal `{1..5}` from UI | Y | N | N | N | `3.000` |
| 5 | `Q1_direct_use_freq` | Col 12 (`Q1`) | Q9 (`Q1_direct_use_freq`) | Likert `1–5` from UI | Y | N | N | N | `3.000` |
| 6 | `Q20_task_delegation_freq` | Col 31 (`Q20`) | Q7 (`Q20_task_delegation_freq`) | Likert `1–5` from UI | Y | N | N | N | `3.000` |
| 7 | `Q22_effort_on_ai_answers` | Col 33 (`Q22`) | Q10 (`Q22_effort_on_ai_answers`) | Likert `1–5` from UI | Y | N | N | N | `3.000` |
| 8 | `Q2_verify_info` | Col 13 (`Q2`) | Q11 (`Q2_verify_info`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 9 | `Q3_compare_sources` | Col 14 (`Q3`) | Q12 (`Q3_compare_sources`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 10 | `Q4_check_accuracy` | Col 15 (`Q4`) | Q13 (`Q4_check_accuracy`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 11 | `Q5_understand_reasoning` | Col 16 (`Q5`) | Q14 (`Q5_understand_reasoning`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 12 | `Q6_modify_content` | Col 17 (`Q6`) | Q15 (`Q6_modify_content`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 13 | `Q7_attempt_independently` | Col 18 (`Q7`) | Q16 (`Q7_attempt_independently`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 14 | `Q8_complete_without_ai` | Col 19 (`Q8`) | Q17 (`Q8_complete_without_ai`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 15 | `Q9_learning_assistant` | Col 20 (`Q9`) | Q18 (`Q9_learning_assistant`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 16 | `Q16_ai_improves_learning` | Col 27 (`Q16`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 17 | `Q17_ai_confidence` | Col 28 (`Q17`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 18 | `Q18_ai_efficiency` | Col 29 (`Q18`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 19 | `Q19_negative_affect_warning` | Col 30 (`Q19`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 20 | `Q23_pu_improves_understanding` | Col 34 (`Q23`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 21 | `Q24_pu_complete_effectively` | Col 35 (`Q24`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 22 | `Q25_pu_productivity` | Col 36 (`Q25`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 23 | `Q26_pu_useful_for_goals` | Col 37 (`Q26`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 24 | `Q27_pu_learn_difficult_topics` | Col 38 (`Q27`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 25 | `Q28_trust_reliable_info` | Col 39 (`Q28`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `3.000` |
| 26 | `Q29_trust_consistent` | Col 40 (`Q29`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `3.000` |
| 27 | `Q30_trust_accuracy` | Col 41 (`Q30`) | Q19 (`Q30_trust_accuracy`) | Likert `1–5` from UI | Y | N | N | N | `3.000` |
| 28 | `Q31_trust_explanations` | Col 42 (`Q31`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `3.000` |
| 29 | `Q32_trust_clear_explanations` | Col 43 (`Q32`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 30 | `Q33_trust_appropriate_support` | Col 44 (`Q33`) | Q20 (`Q33_trust_appropriate_support`) | Likert `1–5` from UI | Y | N | N | N | `4.000` |
| 31 | `Q39_feel_capable` | Col 50 (`Q39`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 32 | `Q40_feel_confident` | Col 51 (`Q40`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 33 | `Q41_more_capable_after` | Col 52 (`Q41`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 34 | `Q42_more_confident_after` | Col 53 (`Q42`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 35 | `Q43_approach_challenging` | Col 54 (`Q43`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `4.000` |
| 36 | `composite_verification` | Mean(Cols 13–17) | UI Q11–Q15 | Mean(`Q2..Q6`) from UI | N | Y | N | N | `3.800` |
| 37 | `composite_autonomy` | Mean(Cols 18–20) | UI Q16–Q18 | Mean(`Q7..Q9`) from UI | N | Y | N | N | `3.667` |
| 38 | `composite_trust` | Mean(Cols 39–44) | UI Q19–Q20 + 4 med. | Mean(`Q28..Q33`) mixed | N | Y | N | **Y** | `3.333` |
| 39 | `composite_tam` | Mean(Cols 34–38) | — *(Not in UI)* | Fixed training median (ref.) | N | Y*(dev)* | **Y**(UI) | N | `3.800` |
| 40 | `composite_self_efficacy` | Mean(Cols 50–54) | — *(Not in UI)* | Fixed training median (ref.) | N | Y*(dev)* | **Y**(UI) | N | `3.600` |
| 41 | `idx_automation_bias` | Trust − Verification | UI Q11–15,19–20+med. | `composite_trust - composite_verification` | N | Y | N | **Y** | `-0.300` |
| 42 | `idx_delegation_intensity` | Col 8 × Col 31 | UI Q4 × Q7 | `ai_usage_freq * Q20` | N | Y | N | N | `8.000` |
| 43 | `idx_passive_adoption` | Col 12 × (6−Col 33) | UI Q9, Q10 | `Q1 * (6.0 - Q22)` | N | Y | N | N | `6.000` |
| 44 | `count_tools_used` | Col 9 (`ai_tools_used`) | Q6 (`tools_used`) | `len(tools_used)` | N | Y | N | N | `2.000` |
| 45 | `count_tasks_delegated` | Col 32 (`tasks_delegated_types`) | Q8 (`tasks_delegated`) | `len(tasks_delegated)` | N | Y | N | N | `3.000` |
| 46 | `count_purposes` | Col 10 (`ai_purposes`) | — *(Not in UI)* | Training reference median | N | Y*(dev)* | **Y**(UI) | N | `4.000` |
| 47 | `faculty_Business_Economics` | Col 6 (`degree_field`) | Q1 (`degree_field`) | Canonical/regex one-hot | N | Y | N | N | `0.000` |
| 48 | `faculty_Computing_IT` | Col 6 (`degree_field`) | Q1 (`degree_field`) | Canonical/regex one-hot | N | Y | N | N | `1.000` |
| 49 | `faculty_Engineering` | Col 6 (`degree_field`) | Q1 (`degree_field`) | Canonical/regex one-hot | N | Y | N | N | `0.000` |
| 50 | `faculty_Humanities_Health_Other` | Col 6 (`degree_field`) | Q1 (`degree_field`) | Canonical/regex one-hot | N | Y | N | N | `0.000` |
| 51 | `faculty_Natural_Applied_Sciences` | Col 6 (`degree_field`) | Q1 (`degree_field`) | Canonical/regex one-hot | N | Y | N | N | `0.000` |
| 52 | `tool_chatgpt` | Col 9 (`ai_tools_used`) | Q6 (`tools_used`) | Substring one-hot | N | Y | N | N | `1.000` |
| 53 | `tool_google_gemini` | Col 9 (`ai_tools_used`) | Q6 (`tools_used`) | Substring one-hot | N | Y | N | N | `1.000` |
| 54 | `tool_microsoft_copilot` | Col 9 (`ai_tools_used`) | Q6 (`tools_used`) | Substring one-hot | N | Y | N | N | `0.000` |
| 55 | `tool_claude` | Col 9 (`ai_tools_used`) | Q6 (`tools_used`) | Substring one-hot | N | Y | N | N | `0.000` |
| 56 | `tool_perplexity` | Col 9 (`ai_tools_used`) | Q6 (`tools_used`) | Substring one-hot | N | Y | N | N | `0.000` |
| 57 | `purpose_understanding_concepts` | Col 10 (`ai_purposes`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `1.000` |
| 58 | `purpose_assignment_preparation` | Col 10 (`ai_purposes`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `1.000` |
| 59 | `purpose_exam_preparation` | Col 10 (`ai_purposes`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `1.000` |
| 60 | `purpose_writing_improvement` | Col 10 (`ai_purposes`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `1.000` |
| 61 | `purpose_summarising_content` | Col 10 (`ai_purposes`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `1.000` |
| 62 | `purpose_generating_ideas` | Col 10 (`ai_purposes`) | — *(Not in UI)* | Training reference median | N | N | Y | N | `0.000` |
| 63 | `delegate_writing_assignments` | Col 32 (`tasks_delegated_types`) | Q8 (`tasks_delegated`) | Substring one-hot | N | Y | N | N | `1.000` |
| 64 | `delegate_explaining_concepts` | Col 32 (`tasks_delegated_types`) | Q8 (`tasks_delegated`) | Substring one-hot | N | Y | N | N | `1.000` |
| 65 | `delegate_summarising_materials` | Col 32 (`tasks_delegated_types`) | Q8 (`tasks_delegated`) | Substring one-hot | N | Y | N | N | `1.000` |
| 66 | `delegate_creating_presentations` | Col 32 (`tasks_delegated_types`) | Q8 (`tasks_delegated`) | Substring one-hot | N | Y | N | N | `0.000` |
| 67 | `delegate_programming_problems` | Col 32 (`tasks_delegated_types`) | Q8 (`tasks_delegated`) | Substring one-hot | N | Y | N | N | `0.000` |
| 68 | `delegate_mathematical_problems` | Col 32 (`tasks_delegated_types`) | Q8 (`tasks_delegated`) | Substring one-hot | N | Y | N | N | `0.000` |

*(Note: Features `39`, `40`, and `46` were engineered during offline dataset preprocessing over 68-column training CSVs, so under the 20-input UI runtime where none of their source items appear, `transform_inputs()` keeps their constant training-median reference values.)*

---

## 3. Historical 75-Student Error Analysis (`test_size=75`, `random_state=42`)

### 3.1 Pre-Fix Baseline vs. Post-Fix Verified Comparison
Before fixing `classify_meta_faculty()` in `integration_service.py`, naive substring checks (`"cs"` inside `"Business_Economics"`, `"it"` inside `"Humanities_Health_Other"`) routed both dropdown values to `faculty_Computing_IT`. Adding exact canonical lookup and word-boundary matching—without modifying trained model weights, thresholds, or medians—restored UI accuracy to parity with the 68-feature model:

| Metric ($N = 75$ Historical Split) | Full 68-Feature Model | 20-Input UI (Pre-Fix Audit Baseline) | 20-Input UI (Post-Fix Verified) |
|---|:---:|:---:|:---:|
| **Accuracy (%)** | **57.33%** (`43/75`) | 54.67% (`41/75`) | **57.33%** (`43/75`) |
| **Macro-F1 / Weighted-F1** | **0.5815** / **0.5788** | 0.5457 / 0.5431 | **0.5796** / **0.5738** |
| **Low P / R / F1** (`n=27`) | 68.42% / 48.15% / 0.5652 | 61.11% / 40.74% / 0.4889 | 61.11% / 40.74% / 0.4889 |
| **Medium P / R / F1** (`n=26`) | 44.19% / 73.08% / 0.5507 | 43.75% / **80.77%** / 0.5676 | 45.65% / **80.77%** / **0.5833** |
| **High P / R / F1** (`n=22`) | 84.62% / **50.00%** / 0.6286 | **100.00%** / 40.91% / 0.5806 | **100.00%** / **50.00%** / **0.6667** |
| **ROC-AUC (OvR Macro)** | 0.7576 | **0.7605** | 0.7562 |
| **Multi-Class Log-Loss** | **0.8803** | 0.9006 | 0.9057 |
| **RMSE / MAE (Raw Score vs `co_score`)** | 0.5779 / **0.4578** | **0.5718** / 0.4611 | 0.5749 / 0.4619 |
| **Agreement vs. Full-68 Model** | 100.00% (`75/75`) | 88.00% (`66/75`) | **90.67%** (`68/75`, $r = 0.9570$) |

- **Full-68 Confusion Matrix (`[Low, Med, High]`):** `[[13, 14, 0], [5, 19, 2], [1, 10, 11]]`  
- **20-Input UI Pre-Fix Confusion Matrix:** `[[11, 16, 0], [5, 21, 0], [2, 11, 9]]`  
- **20-Input UI Post-Fix Confusion Matrix:** `[[11, 16, 0], [5, 21, 0], [2, 9, 11]]`  
- **68-vs-UI Agreement Matrix (Post-Fix):** `[[16, 3, 0], [2, 41, 0], [0, 2, 11]]` — all `7` disagreements (`9.33%`) are adjacent off-by-one shifts; `0` Low↔High flips.

### 3.2 High-Risk Miss Breakdown ($N = 22$ True High Risk)
- **Correctly Classified High Risk (`11 / 22`, `50.00%` Recall, `100.00%` Precision):** Holdout rows `0, 2, 4, 9, 14, 29, 30, 50, 59, 60, 65` (with Rows `2` and `65` recovered from Medium to High after fixing `Business_Economics` faculty parsing: `3.476 -> 3.552` and `3.492 -> 3.568`).
- **Predicted Medium (`9 / 22`, adjacent boundary misses):** Rows `7, 15, 20, 25, 43, 54, 56, 67, 70` (predicted UI scores `2.821–3.447`; Row `7` missed `3.500` by only `-0.053` and Row `67` by `-0.087`).
- **Predicted Low (`2 / 22`, two-tier misses):** Row `5` (`true co_score = 3.833`, `pred_68 = 2.408 Low`, `pred_ui = 2.399 Low` — low-risk antecedent pattern even with all 68 features) and Row `53` (`true co_score = 3.833`, `pred_68 = 2.863 Medium`, `pred_ui = 2.609 Low`).

### 3.3 Why Errors Occur & Honest Limitations
1. **Boundary Crowding:** `20 / 32 (62.5%)` post-fix UI errors have predicted scores within `±0.25` Likert points of cutoffs `2.667` or `3.500`.
2. **Median Shrinkage Toward the Center:** Imputing 27 invariant columns + 4/6 `composite_trust` items pulls predictions slightly inward (`+0.0435` Low, `-0.0116` Medium, `-0.0808` High), inflating Medium recall (`80.77%`) while lowering sensitivity on subtle High and Low profiles.
3. **LinearSHAP Fidelity & Probability Calibration:** Top-3 SHAP overlap vs full-68 is `83.56%` (`top-5`: `80.53%`), with **`0 / 375` spurious imputed columns entering UI top-5**. Top-label ECE is `0.0761` (`Brier = 0.5350`), showing balanced confidence near decision boundaries (`[0.4, 0.5]`: mean conf `47.5%`, emp. acc `37.5%`; `[0.6, 0.7]`: `90.0%` acc).
4. **Raw vs. Clipped Score Distinction:** Model classification and probabilities always use `raw_regression_score`; `continuous_risk_score` is clamped to `[1.0, 5.0]` strictly for Likert scale presentation (`raw_regression_score` stays preserved in API JSON for auditability).
