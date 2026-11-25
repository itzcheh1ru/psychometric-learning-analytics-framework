# Component 1: Independent Cohort Validation & User Acceptance Testing (UAT) Protocol

**Project:** Psychometric Learning Analytics Framework (`J26-DS-310`)  
**Component:** Component 1 – Explainable Cognitive Offloading Risk Prediction (`IT23426580`)  
**Validation Script:** [`component1_streamlit_v4/scripts/evaluate_independent_cohort.py`](../scripts/evaluate_independent_cohort.py)  

> **Status Disclosure:** This protocol and automated evaluator are ready for prospective validation. **No independent new student cohort data or live participant UAT scores have been collected or fabricated in the repository.**

---

## Part A: Independent Student Cohort Validation Plan (Task 4)

### 1. Why Independent Cohort Validation Is Necessary
Because the historical `N = 75` holdout (`random_state=42`) was inspected during Versions 2–4, external generalization of the deployed **20-input web questionnaire** must be verified on **newly collected, unseen undergraduate students** using the frozen Version 4 model (`thresholded_ridge_v4.joblib`).

### 2. Recommended Cohort Design & Target Sample Size
- **Target Sample Size:** Minimum **`N = 80`** consenting undergraduates (recommended **`N = 120–150`**) from diverse faculties so each tertile risk stratum has $\ge 30$ respondents (bounding per-class binomial standard error below $\pm 9\%$ at $N=90$).
- **Sampling Balance:** Target representation across all five canonical UI degree domains (`Computing_IT`, `Engineering`, `Business_Economics`, `Natural_Applied_Sciences`, `Humanities_Health_Other`).
- **Model Freeze Rule:** Do **not** retrain, tune thresholds, or update reference medians prior to scoring the independent sample.

### 3. Data Separation & Anti-Leakage Collection Protocol
Participants complete an anonymous survey containing two logically separated blocks linked solely by an anonymous `study_id` (zero direct PII such as name, student ID, email, or phone):
1. **Model Input Block (20 UI Questions):** Exact 20 inputs collected by `/component1/` (`degree_field`, `academic_year`, `age_group`, `ai_usage_freq`, `ai_time_per_week`, `tools_used`, `Q20`, `tasks_delegated`, `Q1`, `Q22`, `Q2–Q6`, `Q7–Q9`, `Q30`, `Q33`).
2. **Ground-Truth Reference Block (Section E, 6 Items):** Separately collected Likert `[1–5]` ratings for `Q10_rely_memory`, `Q11_avoid_mental_effort`, `Q12_accept_without_understanding`, `Q13_less_problem_solving`, `Q14_depend_on_ai`, and `Q15_reduces_thinking`.
   - Reference `co_score` = unweighted mean of `Q10–Q15`.
   - Reference `co_risk` = approved Version 4 thresholds (`<= 2.667` Low, `2.668–3.500` Medium, `> 3.500` High).
   - **Leakage Guard:** `evaluate_independent_cohort.py` explicitly verifies `Q10–Q15`, `co_score`, and `co_risk` are absent from the predictor feature vector and rejects files containing PII columns.

### 4. Execution Command & Acceptance Benchmarks
```bash
.venv/bin/python component1_streamlit_v4/scripts/evaluate_independent_cohort.py \
  --input /path/to/anonymized_independent_cohort.csv \
  --out-json /tmp/c1_independent_cohort_metrics.json
```

| Evaluation Dimension | Primary Metric | Target Benchmark |
|---|---|---|
| Ground-Truth Scale Reliability | Cronbach's $\alpha$ (`Q10–Q15`) | $\ge 0.70$ ($\ge 0.80$ desirable) |
| Overall Balanced Classification | Macro-F1 / Accuracy | Macro-F1 $\ge 0.50$, Accuracy $\ge 52\%$ |
| Safety / Early Warning Sensitivity | High-Risk Recall & Confusion Matrix | High Recall $\ge 0.45–0.50$, minimal 2-tier misses |
| Latent Construct Fit | Continuous `co_score` RMSE / Pearson $r$ | $\text{RMSE} \le 0.65$, $r \ge 0.60$ |
| Privacy & Completeness | PII Column Audit & Missing Rate | 0 PII columns, missing UI cells documented |

---

## Part B: User Acceptance Testing (UAT) Usability Checklist (Task 5)

Execute this structured 10-point walkthrough with prospective undergraduate participants or academic reviewers on `GET /component1/`:

| # | Evaluation Flow | Pass Criteria Observed by Facilitator | Result (`Pass`/`Fail`/Notes) |
|---|---|---|---|
| 1 | **First Impression & Clarity** | Student understands the tool evaluates AI-assisted study habits and takes ~3 minutes without feeling graded or judged. | `[ ] Pass  [ ] Fail` |
| 2 | **Questionnaire Readability** | All 20 items across Sections 1–4 read clearly in natural student language without ambiguous survey jargon. | `[ ] Pass  [ ] Fail` |
| 3 | **Validation Behavior** | Clicking *Next* or *View Results* with missing responses highlights unanswered items and displays clear validation guidance without losing entered answers. | `[ ] Pass  [ ] Fail` |
| 4 | **Multi-Step Navigation** | Moving back and forth across Steps 1–4 preserves all dropdowns, Likert radios, and checkboxes reliably. | `[ ] Pass  [ ] Fail` |
| 5 | **Progress Tracking** | Progress bar (`25%` → `100%`) and numbered step pills accurately reflect the active and completed sections. | `[ ] Pass  [ ] Fail` |
| 6 | **Result Clarity** | Risk tier badge (`Low`/`Medium`/`High`), continuous score spectrum (`1.000–5.000`), and three-class likelihood split are understandable together. | `[ ] Pass  [ ] Fail` |
| 7 | **SHAP Factor Comprehension** | Student can accurately identify at least one personal habit in *Habits Increasing Risk* and/or *Habits Protecting Autonomy*. | `[ ] Pass  [ ] Fail` |
| 8 | **Actionable Study Guidance** | Recommended study strategies feel practical and tailored rather than generic boilerplate. | `[ ] Pass  [ ] Fail` |
| 9 | **Mobile Usability (`375px`)** | No horizontal scrolling, legible Likert targets (`>= 44px` tap area), and readable result cards on smartphone viewports. | `[ ] Pass  [ ] Fail` |
| 10 | **Research Disclaimer Visibility** | Exploratory self-reflection / non-diagnostic disclaimer and zero-storage notice are clearly visible before and after prediction. | `[ ] Pass  [ ] Fail` |

---

## Part C: Brief Participant Feedback Questionnaire (Anonymous UAT)

*Instructions for participant: Do not write your name, student number, or email address. Rate each statement from **1 (Strongly Disagree)** to **5 (Strongly Agree)**.*

1. **Purpose Clarity:** *"It was clear what this AI study habits assessment does and why each question was asked."* (`1  2  3  4  5`)
2. **Reading Ease:** *"All 20 questions were easy to understand without needing extra explanation."* (`1  2  3  4  5`)
3. **Navigation & Flow:** *"Moving across the 4 steps, fixing missing fields, and submitting worked smoothly."* (`1  2  3  4  5`)
4. **Result Understandability:** *"The predicted risk level, spectrum score, and percentage likelihoods were easy to interpret."* (`1  2  3  4  5`)
5. **Explanation Usefulness (LinearSHAP):** *"The habit drivers showed clear reasons why my score was high, moderate, or low."* (`1  2  3  4  5`)
6. **Practical Actionability:** *"The suggested study tips gave me useful ideas I could apply in my coursework."* (`1  2  3  4  5`)
7. **Open Feedback (Confusing Parts):** *"Was any question wording, result label, or explanation confusing?"*
8. **Open Feedback (Improvements):** *"What single small change would make this reflection tool clearer or more helpful?"*
