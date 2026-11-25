# Component 1: Security & Privacy Review and PP2 Viva Technical Reference

**Project:** Psychometric Learning Analytics Framework (`J26-DS-310`)  
**Component:** Component 1 – Explainable Cognitive Offloading Risk Prediction (`IT23426580`)  
**Model Artifact:** `models/thresholded_ridge_v4.joblib` (`pipeline_metadata_v4.json`)  

---

## Part A: Security & Privacy Review Summary (Task 6)

Verified through direct source inspection, automated grep scanning, and live Flask/HTTP test-client probing:

### 1. Component 1 Security & Privacy Verification Checklist

| Control Area | Verified Status | Evidence & Details |
|---|---|---|
| **Input Validation & Type Safety** | **Hardened** | `integration_service.py` coerces numeric inputs safely, clamps Likert ratings to `[1, 5]`, handles `NaN`/`±inf` via peer medians, rejects empty payloads (`400 MissingRequiredInput`), and fixes canonical `degree_field` slug mapping. `app/routes/component1.py` now validates JSON dict type (`[]`/scalars → HTTP `400`) and integer `top_factors_count` `[1, 68]`. |
| **XSS Protection (UI & Templates)** | **Clean** | Zero `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, or `eval()` in `component1.js`; zero `\|safe` Jinja overrides in `component1.html` or `base.html`. All user messages and SHAP descriptions render via safe DOM `textContent`. |
| **Error Message Leakage** | **Hardened** | `app/routes/component1.py` previously echoed `f"Inference execution error: {str(e)}"` on unexpected failures; updated to log full traceback server-side (`current_app.logger.exception`) and return generic `"An internal inference error occurred."`. |
| **Credentials & JS Secrets** | **Clean (App)** | Zero hardcoded passwords, tokens, API keys, or private datasets inside Component 1 templates, JS, or Python services. *(See shared config recommendation below for `SECRET_KEY`.)* |
| **Student Data Logging & Storage** | **Stateless / Zero PII** | Component 1 performs ephemeral in-memory inference; no student responses or predictions are written to server logs or databases, zero `localStorage`/`sessionStorage` persistence in `component1.js`, and forbidden PII keys (`name`, `email`, `student_id`, `it234`, `timestamp`, `participant_id`, `phone`) are scrubbed. |
| **Response Security Headers** | **Verified** | `app/__init__.py` attaches `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Cache-Control: no-store` on `/api/*`. |
| **Participant Privacy Notices** | **Present** | Both UI (`component1.html`) and JSON API (`DISCLAIMER`, 254 chars) disclose that assessments are exploratory educational reflections only and not psychological diagnoses or academic penalties. |

### 2. Read-Only Recommendations for Shared Flask Config & Team Layer
*(Untouched by design to respect shared infrastructure and Components 2/3/4 boundaries.)*
- **Debug / Environment Default (`app/__init__.py`, `app.py`, `app/config.py`):** `create_app()` defaults `FLASK_ENV` to `"development"` (`DEBUG = True`) and `app.py` calls `app.run(debug=True)`. Production hosting must export `FLASK_ENV=production` and serve behind WSGI (`gunicorn`) rather than `app.py`.
- **`SECRET_KEY` Fallback (`app/config.py:14`):** Sets fallback `"dev-fallback-key-j26-ds-310"`. Configure a strong runtime `SECRET_KEY` environment variable in deployment.
- **Request Size Limit & Cookie/CSP Headers (`app/config.py`, `app/__init__.py`):** Consider configuring `MAX_CONTENT_LENGTH = 1048576` (1 MB) in `Config`, setting explicit `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"`, `SESSION_COOKIE_SECURE = True` in `ProductionConfig` if sessions are introduced later, and adding an explicit `Content-Security-Policy` header in `app/__init__.py`.
- **Minor Non-Blocking UI Observations Noted:** On shared `/project`, the "Research Integrity Notice" container lacks right/left inner padding; on teammate `/component3/`, the long `<code>` command inside card `"2. Rebuild weekly data"` overflows card width at ~`817px`.

---

## Part B: Concise PP2 Viva Technical Reference & Q&A (Task 7)

### Exact Verified Reference Figures (Zero Ambiguity)

- **Target Construct (`co_score`):** Unweighted mean of 6 Section E Likert items (`Q10–Q15`: memory offloading, effort avoidance, superficial acceptance, strategy surrender, AI dependence, reduced independent thinking). Psychometric reliability: **Cronbach's $\alpha = 0.8649$** ($N = 375$).
- **Excluded Circular Features:** Zero predictor overlap with `Q10–Q15`, `co_score`, `co_risk`, Section G (`Q34–Q38` including leaked `Q37_important_part` from early prototypes), or administrative PII columns.
- **Primary Model Selection (Training-Only CV, $N = 300$, 5×5 = 25 Repeated Stratified Folds):**
  - **Calibrated Thresholded Ridge Regressor (Ordinal)** ($\alpha = 30.0$, 68 deployed predictors, Gaussian probability residual scale $\sigma = 0.5588$ stored inside `models/thresholded_ridge_v4.joblib` vs `0.585` default docstring value in earlier README drafts).
  - **Audited `X_train` CV (`pipeline_metadata_v4.json`):** Macro-F1 **`0.5495 ± 0.0619`** (compact 51) / `0.5419` (full 68), CV Accuracy **`54.67%`**, Medium-Risk Recall **`59.78%`** (vs `28%–34%` in nominal tree ensembles), Log-Loss **`0.9376`**. *(Note for panel transparency: `MODEL_TRAINING_REPORT_V4.md` & `README.md` also quote an earlier `N=375` 25-fold CV figure of `56.00%` / `0.5643` Macro-F1; `X_train`-only `0.5495` is the strictly blind selection metric).*
- **Continuous Signal ($N=75$ Holdout):** $R^2 = \mathbf{0.4459}$, RMSE $= \mathbf{0.5779}$, MAE $= \mathbf{0.4578}$, **Cohen's $f^2 = 0.8048$** (large behavioral effect size).
- **Decision Cutoffs:** Sample tertiles: **Low $\le 2.667$**, **Medium $2.668–3.500$**, **High $> 3.500$**; displayed risk score clamped strictly to $[1.0, 5.0]$ while preserving raw linear estimates for audit.
- **Historical 75-Student Holdout ($N=75$, Exposed Benchmark Split):**
  - **Full 68-Feature Model:** Accuracy **`57.33%`**, Macro-F1 **`0.5815`**, High-Risk Recall **`50.00%`** (`11/22`), Medium Recall **`73.08%`**.
  - **20-Input Web UI (Pre-Fix Audit Baseline):** Accuracy `54.67%`, Macro-F1 `0.5457`, High Recall `40.91%`, 68-feature agreement `88.00%` — partially degraded by canonical faculty slug collision in `classify_meta_faculty()`.
  - **20-Input Web UI (Post-Fix Verified):** Accuracy **`57.33%`** (exact 68-feature parity), Macro-F1 **`0.5796`**, High-Risk Recall **`50.00%`** (`11/22`, **Precision `100.00%`**), Medium Recall **`80.77%`**, 68-feature agreement **`90.67%` (`68/75`)**, Top-3 LinearSHAP overlap **`83.56%`** (`0/375` spurious imputed top-5 attributions).

### 12 Quick Panel Q&A Talking Points

1. **How is cognitive offloading defined and measured?**  
   *Answer:* Unweighted mean of the 6 approved Section E Likert items (`Q10–Q15`, Cronbach's $\alpha = 0.8649$), partitioned via empirical tertiles ($\le 2.667$, $2.668–3.500$, $> 3.500$).
2. **How did you guarantee zero data leakage?**  
   *Answer:* All target items (`Q10–Q15`), target scores (`co_score`, `co_risk`), Section G AI dependence items (`Q34–Q38`, including the high-correlation `Q37` item removed after early audits), and admin fields are excluded from all 68 model predictors; unit tests assert their absence.
3. **Why use Thresholded Ridge Regressor instead of LightGBM, CatBoost, or Random Forest?**  
   *Answer:* Nominal trees ignored ordinal order and collapsed on the middle tier (`28%–34%` Medium recall). Regressing continuous `co_score` first with Ridge ($\alpha = 30.0$) and applying ordinal cutoffs lifted Medium-Risk CV recall to **`59.78%`**, topped blind training CV Macro-F1 (`0.5495`), and gave exact closed-form LinearSHAP.
4. **Why is accuracy ~57% rather than 85–90%?**  
   *Answer:* Behavioral survey prediction of a latent psychometric trait without circular self-report leakage cannot achieve 90%. Explaining **$44.59\%$ variance ($f^2 = 0.805$)** and **ROC-AUC `0.758`** is a strong effect size; `62.5%` of UI errors lie within `±0.25` points of a continuous tertile boundary.
5. **Why collect 20 inputs in the UI instead of all 68 features?**  
   *Answer:* Collecting ~45 raw survey items in a live tool causes respondent fatigue and drop-off. The 20 UI inputs preserve all direct demographics, usage habits, task delegation, verification, autonomy, and key trust antecedents, generating `32` dynamic model features and shrinking missing secondary sub-items via training medians—achieving **`57.33%` accuracy** and **`90.67%` agreement** with the 68-feature vector.
6. **Wait — earlier verification showed `54.67%` accuracy for the 20-input UI, why is it `57.33%` now?**  
   *Answer:* During our error audit, we found `classify_meta_faculty()` had a 2-letter substring bug (`"cs"` inside `"Business_Economics"`, `"it"` inside `"Humanities_Health_Other"`) misrouting those dropdown values to `Computing_IT`. Fixing canonical string matching without touching model weights, medians, or thresholds recovered two borderline High-Risk cases and restored **`57.33%`** accuracy and **`50.00%`** High-Risk recall.
7. **How are calibrated probabilities calculated?**  
   *Answer:* Using cumulative normal density around the continuous prediction score ($\sigma = 0.5588$ from training residuals) across cutoffs $2.667$ and $3.500$, ensuring borderline predictions show balanced uncertainty (~`47–53%`) rather than overconfidence (`ECE = 0.0761`).
8. **How does LinearSHAP work mathematically and why trust its top factors in the 20-input UI?**  
   *Answer:* Closed-form exact Shapley attribution $\phi_j = \beta_j (x_j - \bar{x}_j)$, summing identically to the predicted score (`0.00e+00` error). Because median-imputed variables sit near $\bar{x}_j$, they produce `0/375` spurious top-5 explanations on the UI while retaining `83.56%` top-3 agreement with full features.
9. **Are risk cutoffs universal clinical criteria?**  
   *Answer:* No—they are empirical cohort tertiles flagged transparently as relative benchmarks paired with a mandatory non-diagnostic disclaimer.
10. **What about extreme profiles scoring above `5.0`?**  
    *Answer:* A linear model can extrapolate past `[1, 5]`; Component 1 clamps the user-facing score to `[1.0, 5.0]` while preserving `raw_regression_score` in the API response for auditability.
11. **How does Component 1 protect student privacy?**  
    *Answer:* Stateless in-memory inference, zero database/log persistence of user responses, zero client storage, strict rejection of PII keys, and anonymous `study_id`-only cohort scripts.
12. **What is the next validation milestone after PP2?**  
    *Answer:* Recruiting an independent anonymized cohort (`N = 120–150`) collected with both the 20 UI inputs and separated `Q10–Q15` reference items, scored through `evaluate_independent_cohort.py` alongside the 10-flow student UAT checklist.
