# Component 1: Reproducibility, Deployment Plan, Security & PP2 Demonstration Guide

**Project:** Psychometric Learning Analytics Framework (`J26-DS-310`)  
**Component:** Component 1 – Explainable Cognitive Offloading Risk Prediction (`IT23426580`)  
**Production Model Artifacts:** [`models/thresholded_ridge_v4.joblib`](../../models/thresholded_ridge_v4.joblib), [`models/continuous_regressor_v4.joblib`](../../models/continuous_regressor_v4.joblib), [`models/pipeline_metadata_v4.json`](../../models/pipeline_metadata_v4.json)  

---

## 1. Authoritative Evaluation Metrics & Provenance Audit (Task 1)

All reported evaluation numbers across scripts, metadata, and README drafts were recalculated directly from saved model weights and historical dataset outputs ($N = 375$, `random_state = 42` split into $N = 300$ training / $N = 75$ exposed holdout).

### 1.1 Single Authoritative Performance Table (No Mixed Experiments)

| Experiment / Evaluation Context | Sample / Folds | Features | Accuracy | Macro-F1 | Med Recall | High Recall | ROC-AUC (OvR) | Log-Loss | Exact Source / Script |
|---|---|---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Training In-Sample Fit** | $N=300$ train | 68 | 59.33% | — | — | — | — | — | `Ridge(alpha=30).fit(X_train, co_train)` ($R^2 = 0.5451$) |
| **Training-Only CV (Deployed Feature Set)** | $N=300$, 5×5 CV | 68 | **53.93% ± 6.11%** | **0.5419 ± 0.0610** | **58.58%** | — | 0.7315 | 0.9600 | Blind selection CV (`FINAL_VALIDATION_AND_DEPLOYMENT_REPORT.md`) |
| **Training-Only CV (Compact Ablation Set)** | $N=300$, 5×5 CV | 51 | **54.67% ± 6.02%** | **0.5495 ± 0.0619** | **59.78%** | — | **0.7355** | **0.9376** | Compact 51-feature CV (`pipeline_metadata_v4.json` CV summary) |
| **Full-Sample Exploratory CV** *(includes test idx)* | $N=375$, 5×5 CV | 68 | 56.00% ± 5.85% | 0.5643 ± 0.0597 | 62.27% | — | 0.7508 | 0.9271 | `train_model_v4.py` → `v4_repeated_cv_metrics.csv` |
| **Full-Sample Exploratory CV (Compact)** | $N=375$, 5×5 CV | 51 | 56.64% ± 4.61% | 0.5711 ± 0.0470 | 64.17% | — | 0.7550 | 0.9143 | `train_model_v4.py` → `feature_ablation_study.csv` |
| **Historical Holdout — Full 68 Features** *(Exposed)* | $N=75$ holdout | 68 | **57.33%** (`43/75`) | **0.5815** | 73.08% | **50.00%** (`11/22`) | **0.7576** | **0.8803** | `v4_test_metrics.csv` (Weighted-F1 `0.5788`, $R^2=0.4459$, $f^2=0.8048$) |
| **Historical Holdout — 20-Input UI (Pre-Fix)** *(Exposed)* | $N=75$ holdout | 20→68 | 54.67% (`41/75`) | 0.5457 | 80.77% | 40.91% (`9/22`) | 0.7605 | 0.9006 | Pre-fix audit (`classify_meta_faculty` substring bug; `88.00%` agree) |
| **Historical Holdout — 20-Input UI (Post-Fix)** *(Exposed)* | $N=75$ holdout | 20→68 | **57.33%** (`43/75`) | **0.5796** | **80.77%** | **50.00%** (`11/22`) | 0.7562 | 0.9057 | [`analyze_ui_historical_errors.py`](../scripts/analyze_ui_historical_errors.py) (`90.67%` agree, High Prec `100%`) |

### 1.2 Calibration, Risk Threshold & Metadata Reconciliation Findings
- **Fitted Calibration Scale ($\sigma = 0.5588$):** Confirmed strictly computed on training residuals (`np.std(co_train - reg_.predict(X_train)) = 0.558760`) inside `models/thresholded_ridge_v4.joblib`. Earlier documentation mentioning $\sigma = 0.585$ quoted the unfitted `__init__` constructor default in `train_model_v4.py:150`.
- **Risk Thresholds ($\le 2.667$, $2.668–3.500$, $> 3.500$):** Empirical tertile bounds match `[2.6667, 3.500]` on both the `N=300` training split and full `N=375` dataset, though `preprocess_v4.py` computed `co_risk` across all `N=375` records before splitting.
- **Metadata & Historical CSV Clarifications:**
  1. `pipeline_metadata_v4.json` recorded the **Compact-51 training-CV score** (`0.5467` Acc / `0.5495` F1 / `59.78%` Med Recall) while deploying the **Full-68 Ridge estimator** (`53.93%` / `0.5419` training CV), and `historical_exposed_test_log_loss = 0.8776` differs slightly from `v4_test_metrics.csv` (`0.8803` verified here).
  2. `README.md` previously mixed `56.00%` / `0.5643` (Full-Sample $N=375$ CV) under a training-only $N=300$ heading; reconciled cleanly in `README.md` while keeping historical Version 4 CSV/reports preserved untouched as research evidence.

---

## 2. Fresh Installation, Reproducibility & Hardcoded Path Audit (Task 5)

### 2.1 Clean-Clone Reproducibility Check Results
Verified via `git clone --branch it23426580 . /tmp/c1_fresh_clone_check`:
- **Component 1 Model Artifacts Tracked on GitHub:** `.gitignore` force-includes `!models/thresholded_ridge_v4.joblib`, `!models/continuous_regressor_v4.joblib`, plus `models/pipeline_metadata_v4.json` and `component1_streamlit_v4/models/*`. All **13 Flask GET routes returned `HTTP 200`** and **all `242` automated tests passed (`3.82s`)** in the isolated clean clone. *(Note: Fresh PyPI installation in the sandbox was offline-blocked by network policy, so site-packages from `.venv` were reused to test the clean clone; full online install requires `pip install -r requirements.txt pytest`.)*
- **Untracked Local Files Missing From GitHub (Expected & Reported):**
  - Raw/cleaned Component 1 dataset (`cleaned_dataset_v4.csv`) stays intentionally external for participant privacy; only needed if re-running `train_model_v4.py` or `analyze_ui_historical_errors.py --dataset-path <path>`.
  - Teammate Component 4 `models/*.pkl` files are ignored via `.gitignore` (`models/*.pkl`), so they are present locally only and not tracked on GitHub. Component 4 routes/tests in clean clone still pass.
- **Component 2 R / `lavaan` Runtime Dependency:** **Not required** to install or run the Flask app (`docs/architecture.md:337` confirms Flask serves static specifications/results only and never invokes R at runtime).
- **Hardcoded Path Scan:** Zero `/Users/` or `C:\` paths exist in `app/`, `tests/`, `README.md`, `docs/`, or active validation scripts (`evaluate_independent_cohort.py`, `analyze_ui_historical_errors.py`). Legacy `/Users/...` strings exist only inside preserved historical PP1 Markdown/log archives under `component1_streamlit_v4/`.

### 2.2 Verified Cross-Platform Setup & Startup Commands
- **Requirements Note:** `pytest` is used by the test suite but omitted from runtime `requirements.txt`; `gunicorn==26.2.0` is POSIX-only (macOS/Linux) and does not run natively on Windows without WSL2 or `waitress`.
- **macOS / Linux:**
  ```bash
  git clone --branch it23426580 https://github.com/itzcheh1ru/psychometric-learning-analytics-framework.git
  cd psychometric-learning-analytics-framework
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt pytest
  python3 -m pytest tests/ -v
  FLASK_APP=app:create_app FLASK_ENV=production python3 -m flask run --port 5001
  ```
- **Windows (PowerShell):**
  ```powershell
  git clone --branch it23426580 https://github.com/itzcheh1ru/psychometric-learning-analytics-framework.git
  cd psychometric-learning-analytics-framework
  py -3.13 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install Flask==3.1.0 python-dotenv==1.0.1 openpyxl joblib scikit-learn==1.7.1 numpy pandas scipy matplotlib pytest waitress
  python -m pytest tests/ -v
  waitress-serve --host=127.0.0.1 --port=5001 --call app:create_app
  ```

---

## 3. Security Audit & Deployment Readiness Plan (Task 6)

### 3.1 Security & Privacy Controls Verified
- **Component 1 Hardening Applied:** Strict JSON-object request validation (`400` on arrays/scalars), bounded `top_factors_count` (`1..68`), sanitized HTTP `500` responses (no traceback/message exposure), canonical `degree_field` slug mapping, domain clamping `[1, 5]`, zero DOM XSS (`innerHTML`/`|safe` absent), zero raw response logging/storage, PII key scrubbing, and mandatory non-diagnostic disclaimer (`DISCLAIMER`).
- **Response Security Headers (`app/__init__.py`):** `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Cache-Control: no-store` on `/api/*`.

### 3.2 Shared Production Deployment Plan (Requires Team/Supervisor Sign-Off Before Hosting)
- **WSGI & Debug Mode:** Never run `python app.py` (`debug=True`) publicly. Deploy behind reverse-proxy HTTPS (Nginx / Caddy / managed TLS PaaS like Render, Railway, or university VM) executing `FLASK_ENV=production gunicorn --workers 2 --bind 127.0.0.1:8000 wsgi:app`.
- **Required Production Env Vars & Shared Config Hardening (Untouched Here):** Export strong random `SECRET_KEY` and `FLASK_ENV=production`; recommend adding `MAX_CONTENT_LENGTH = 1048576` (1 MB payload cap), `SESSION_COOKIE_*` secure flags, and explicit `Content-Security-Policy` to `app/config.py` / `app/__init__.py` once coordinated with teammates.
- **Runtime Resources & Artifact Checklist:** Python `3.11–3.13`, `~250–400 MB` RAM for WSGI workers, zero R runtime needed on the web server, and verify tracked `models/thresholded_ridge_v4.joblib` + `models/pipeline_metadata_v4.json` are present (`component1_streamlit_v4/` optional if hosting only Flask).
- **Governance & Ethics:** Obtain supervisor approval before exposing any participant link publicly; keep predictions stateless unless an ethics-approved data-collection consent workflow is separately deployed.

---

## 4. Concise PP2 Demonstration Guide & Panel Q&A (Task 7)

### 4.1 15-Point PP2 Technical Walkthrough
1. **Research Problem:** Undergraduate over-reliance on GenAI risks **cognitive offloading**—delegating memory retrieval, analytical reasoning, and problem-solving—eroding independent competency.
2. **Research Gap:** Prior tools rely on non-explainable black-box scores, circular self-report leakage, or lack student-facing self-reflection design grounded in behavioral antecedents.
3. **Individual Contribution (`IT23426580`):** Designed, audited, and integrated Component 1—end-to-end leakage-free ML pipeline, ordinal Ridge predictor, closed-form LinearSHAP explainer, 4-step Flask self-reflection UI, and independent cohort validator.
4. **Evidence-Backed Novelty:** Modeling ordinal continuous latent `co_score` via `Thresholded Ridge (alpha=30.0)` solved the **Medium-Risk collapse** observed in nominal tree models (`58.58%–59.78%` CV Medium recall vs. `28%–34%` in Extra Trees/XGBoost/LightGBM) while retaining exact deterministic LinearSHAP ($\phi_j = \beta_j (x_j - \bar{x}_j)$).
5. **System Architecture:** Blueprint modular Flask 3.1 service (`app/routes/component1.py` -> `model_service.py` -> `integration_service.py`) consuming frozen `.joblib` + metadata JSON alongside independent C2/C3/C4 blueprints.
6. **Data Preprocessing:** Strict removal of admin fields (Cols 0–4), Section E targets (`Q10–Q15`, Cronbach's $\alpha = 0.8649$), and Section G dependence items (`Q34–Q38` incl. leaked `Q37`). All subscales/interactions computed strictly row-by-row.
7. **Model Selection:** Selected via blind 5×5 Repeated Stratified CV strictly within `X_train` ($N=300$) prioritizing Macro-F1 (`0.5495` compact / `0.5419` full), Medium recall, lowest log-loss (`0.9376`/`0.9600`), and exact explainability.
8. **68-Feature Model & 20-Input UI Rationale:** Full dataset contains 68 predictors; collecting all ~45 raw items creates student fatigue, so the UI asks 20 targeted questions (`17` direct + `22` engineered = `39` observed + `27` fixed medians + `2` partially imputed hybrids), reaching **90.67%** class agreement and exact **57.33%** holdout accuracy parity.
9. **Live Demo — Low-Risk Sample:** Engineering Yr 4 preset -> **Low Risk** (`1.561 / 5.0`, probabilities: Low `97.6%`, Med `2.4%`, High `0.02%`; protective drivers: low passive adoption `-0.3064`, rare task delegation `-0.2680`, high confidence without AI `-0.1903`).
10. **Live Demo — Medium-Risk Sample:** Computing_IT Yr 2 preset -> **Medium Risk** (`2.976 / 5.0`, probabilities: Low `29.0%`, Med `53.6%`, High `17.4%`; mixed drivers: passive adoption `+0.0810`, low autonomy `+0.0775` vs. moderate usage `-0.0645`).
11. **Live Demo — High-Risk Sample:** Business_Economics Yr 1 preset -> **High Risk** (displayed clamped **`5.000 / 5.0`**, raw **`5.255`**, High prob `99.92%`; risk drivers: passive adoption `+0.8558`, low confidence without AI `+0.3453`, delegation intensity `+0.2394`).
12. **SHAP Explanation:** Two clear student columns (*Habits Protecting Cognitive Autonomy* vs. *Habits Increasing Offloading Risk*), faithful to exact Ridge weights (`0.00e+00` additive reconstruction error; `0/375` spurious imputed top-5 attributions).
13. **Verified Metrics Summary:** Blind `N=300` CV `53.93%` (`0.5419` F1, Full-68) / `54.67%` (`0.5495` F1, Compact-51); continuous signal $R^2 = 0.4459$ ($f^2 = 0.8048$); exposed `N=75` holdout `57.33%` acc (`50.00%` High recall, `80.77%` UI Med recall).
14. **Current Limitations (Honest Disclosure):** Modest `~54–57%` discrete accuracy due to `62.5%` boundary crowding near `2.667`/`3.500` cutoffs without circular leakage; single-institution baseline ($N=375$); empirical tertile bounds require normative validation; `N=75` holdout was historically exposed; imputation shrinks extreme UI cases inward (`-0.0808` High).
15. **Completed vs. Planned Work:** **Completed:** leakage-free V4 model, web assessment & SHAP UI, `N=75` UI error audit & faculty parsing fix, `evaluate_independent_cohort.py`, blank CSV template, UAT checklist, fresh-clone & security audits. **Planned (Next Phase):** collecting `N=120–150` external undergraduate cohort responses + running pilot UAT (`N=5–10`) with supervisor approval.

### 4.2 Rapid Panel Q&A Cheat Sheet
- **Why only ~57% accuracy instead of 85–90%?** Because target (`Q10–Q15`) and Section G (`Q34–Q38`) self-report items were strictly removed to prevent circular leakage; predicting a psychological construct solely from behavioral habits yields $R^2 = 0.446$ (large effect size $f^2 = 0.805$) while adjacent tertile boundary noise caps nominal 3-class accuracy near 57%.
- **Why did earlier validation report 54.67% UI accuracy while latest shows 57.33%?** Our error audit exposed a 2-letter substring bug in `classify_meta_faculty()` (`"cs"` in `Business_Economics`, `"it"` in `Humanities_Health_Other`); fixing string parsing without altering model weights recovered 2 borderline High-Risk students (`54.67% -> 57.33%`, High recall `40.91% -> 50.00%`).
- **How do you ensure independent validation stays leakage-free?** `evaluate_independent_cohort.py` parses only the 20 UI predictor keys into the model, validates reference `Q10–Q15` strictly post-prediction, and fails closed on PII, duplicate `study_id`s, or forbidden target/dependence columns.
- **Can someone clone and run Component 1 on another computer without raw student data?** Yes—`thresholded_ridge_v4.joblib` and `pipeline_metadata_v4.json` (which stores reference medians/means) are tracked in Git; clean clone boots all 13 endpoints (`HTTP 200`) and passes all `242+` tests without any CSV dataset.
