# UI Redesign & Implementation Report: Component 1 (Version 4)
**Explainable Cognitive Offloading Risk Model Among Undergraduate Students**  
*Project Code: J26-DS-310 | Component 1: Individual Research Model*  
*Student ID: IT23426580 | Date: October 22, 2026*

---

## Executive Summary

The Component 1 application has been transformed from an internal testing harness into a modern, beginner-friendly, and non-stigmatizing self-reflection web application entitled **"AI-Assisted Learning Self-Reflection"**. 

The redesign maintains strict adherence to all scientific constraints established in the approved methodology:
1. **Model & Architecture Preserved**: The champion **Calibrated Thresholded Ridge Regressor (Ordinal)** remains identical, with decision boundaries at $\text{cut}_1 = 2.667$ and $\text{cut}_2 = 3.500$, residual scale $\sigma = 0.585$, and all 68 predictor feature weights unchanged.
2. **Score Range Constraint Enforced**: The continuous cognitive offloading risk score is bounded within the theoretical Likert construct scale $[1.000, 5.000]$, while raw latent linear regression estimates exceeding boundaries are transparently logged and preserved for academic audit.
3. **Genuine Questionnaire Fidelity**: All survey prompts strictly follow the approved research instrument across Sections B, C, D, and F without invented variables.
4. **Explainable AI Integration**: Leading drivers and mitigating habits are displayed using plain-English interpretations derived directly from exact **LinearSHAP** mathematical contributions ($\phi_j = \beta_j (x_j - \bar{x}_j)$).
5. **Testing & Demonstration Continuity**: An integrated examiner sidebar expander enables evaluation panel members to load and verify any of the 8 benchmark regression scenarios with a single click.

All three automated test suites (`test_complete_integration_workflow_v4.py`, `test_regression_scenarios_v4.py`, and `test_ui_pages_and_navigation_v4.py`) pass 100%.

---

## 1. Application Architecture & Multi-Step User Flow

The redesigned application adopts a guided, multi-step conversational format designed specifically for undergraduate students. Navigation is managed through Streamlit `st.session_state`, ensuring seamless forward and backward transitions without data loss.

### Screen Progression Breakdown

| Screen / Step | Purpose | Student-Facing Content | Technical Feature Handled |
|---|---|---|---|
| **Home Screen** | Welcome & Context | Explains cognitive offloading in everyday terms; assures anonymity (no PII); sets time expectation (~3 mins). | Session state initialization, research disclaimer display. |
| **Section 1: AI Usage Habits** | Academic Profile | Degree field, academic year, age bracket, general AI frequency, weekly hours, multi-select tools used. | `degree_field`, `academic_year`, `age_group`, `ai_usage_freq`, `ai_time_per_week`, `tools_used`. |
| **Section 2: Task Delegation** | Delegation & Review | Frequency of delegating entire tasks, kinds of tasks delegated, direct copying frequency, effort verifying outputs. | `Q20_task_delegation_freq`, `tasks_delegated`, `Q1_direct_use_freq`, `Q22_effort_on_ai_answers`. |
| **Section 3: Verification** | Critical Thinking | External source verification, coursework comparison, accuracy checking, understanding reasoning, personalizing output. | `Q2_verify_info`, `Q3_compare_sources`, `Q4_check_accuracy`, `Q5_understand_reasoning`, `Q6_modify_content`. |
| **Section 4: Autonomy & Trust** | Independent Mindset | Attempting independently first, completing work without AI, AI as assistant, belief in AI accuracy, trust in support. | `Q7_attempt_independently`, `Q8_complete_without_ai`, `Q9_learning_assistant`, `Q30_trust_accuracy`, `Q33_trust_appropriate_support`. |
| **Review Screen** | Answer Inspection | Clean 4-card summary of all entered responses with "Edit Section" buttons. | Pre-submission state verification; prevents accidental or empty submissions. |
| **Results Screen** | Actionable Reflection | Visual category card, clamped score ($1.00 - 5.00$), LinearSHAP factor cards, model category distribution, and self-regulated learning recommendations. | Model inference, LinearSHAP ranking, Gaussian residual density probability estimation, clamping audit. |

---

## 2. Explainability & Human-Centered Feature Interpretation

To make machine-learning explanations comprehensible to undergraduate students without sacrificing mathematical rigor, `integration_service_v4.py` was enhanced with:
1. **Human-Readable Labels (`FEATURE_HUMAN_LABELS`)**: Replaces technical survey codes (e.g., `Q20_task_delegation_freq`, `idx_passive_adoption`) with clear student-centered titles (e.g., *"Frequency of delegating complete tasks"*, *"Passive Adoption Index"*).
2. **Directional Educational Explanations (`FEATURE_PLAIN_EXPLANATIONS`)**: Provides plain-English rationales for how a specific habit influences cognitive engagement.
3. **Dual-Badge Visual Cards**: Distinctly separates habits that protect independent learning (green border, positive reinforcement) from habits that elevate offloading tendencies (amber/red border, constructive awareness).

### Sample LinearSHAP Plain Explanations

| Feature Identifier | Human-Readable Label | Mitigating Effect Explanation | Risk-Increasing Effect Explanation |
|---|---|---|---|
| `Q20_task_delegation_freq` | Frequency of delegating complete tasks | *Rarely or never delegating entire tasks keeps your independent problem-solving active.* | *Frequently delegating whole tasks shifts analytical thinking from you to the AI tool.* |
| `Q8_complete_without_ai` | Ability to complete coursework without AI | *Confidence that you can complete assignments independently strongly protects against cognitive offloading.* | *Feeling unable to complete coursework without AI signals an emerging reliance.* |
| `Q7_attempt_independently` | Attempting tasks independently before AI | *Attempting tasks independently first engages your critical reasoning before using AI support.* | *Turning to AI immediately before trying on your own bypasses early problem-solving practice.* |
| `Q1_direct_use_freq` | Direct use of AI answers without editing | *Submitting coursework in your own words rather than raw AI answers reinforces active learning.* | *Directly copying AI-generated answers with minimal editing increases reliance on automated content.* |
| `Q22_effort_on_ai_answers` | Effort analyzing & improving AI outputs | *Critically examining and improving AI outputs keeps you cognitively engaged with the material.* | *Spending little or no effort checking AI answers increases susceptibility to errors and offloading.* |
| `Q2_verify_info` | Verifying AI output against sources | *Routinely checking facts against lecture notes or textbooks actively strengthens critical thinking.* | *Accepting AI claims without source-checking elevates risk of passive acceptance.* |

---

## 3. Results Screen Architecture & Non-Stigmatizing Feedback

The results presentation replaces harsh automated classifications with constructive, self-regulated learning feedback:

- **Low Risk (Green Card)**: *"Low Cognitive Offloading Tendency — Balanced & Independent AI Learner"*  
  Emphasizes disciplined inquiry and reinforces student autonomy.
- **Medium Risk (Yellow/Amber Card)**: *"Moderate Cognitive Offloading Tendency — Emerging Reliance / Opportunity to Strengthen Verification"*  
  Highlights areas where task delegation can be complemented with deeper critical review.
- **High Risk (Rose/Red Card)**: *"High Cognitive Offloading Tendency — Elevated Task Delegation / Action Recommended"*  
  Offers clear, non-punitive steps to regain problem-solving autonomy before major exams.

Each result is accompanied by:
- **Continuous Latent Construct Score**: Clearly explained as an unweighted Likert mean on the $1.0 - 5.0$ scale ($1.0 = \text{Highly Autonomous}$, $5.0 = \text{Heavy Offloading}$).
- **Score Range Constraint Note**: In the event that extreme student profiles produce raw regression estimates outside $[1.0, 5.0]$, the score is clamped to domain bounds, with the raw latent estimate logged for statistical transparency.
- **LinearSHAP Insights**: Ranked leading drivers and mitigating factors with human titles and plain explanations.
- **Category Probability Distribution**: Gaussian residual predictive densities ($\sigma = 0.585$) summing strictly to 100%, accurately contextualized as peer-cohort statistical likelihoods rather than dogmatic certainty.
- **Self-Regulated Learning Strategies**: 3 actionable, evidence-based recommendations tailored to the student's category tier (e.g., the 15-Minute Draft Rule, Socratic prompt critiquing, dual-source lecture note checks).

---

## 4. Verification Suite Results

Three automated test suites confirm system integrity and complete backward compatibility:

### 1. Integration & Reliability Suite (`test_complete_integration_workflow_v4.py`)
- **Execution Date**: October 22, 2026
- **Test Result**: **9 / 9 Tests Passed (100%)**
- **Duration**: 0.195s
- **Verified Items**:
  1. Serialized disk model loading without retraining.
  2. Full raw-survey profile inference.
  3. Defensive imputation on NaN, missing, or dirty values.
  4. Feature-schema mismatch protection and empty input guard.
  5. Simulated model loading failure handling (`FileNotFoundError`).
  6. Strict probability validation (sums to 1.0, range $[0.0, 1.0]$).
  7. LinearSHAP mathematical attribution compatibility.
  8. API payload simulation.
  9. Privacy enforcement (zero PII leakage) and research disclaimer.

### 2. Regression Scenarios Suite (`test_regression_scenarios_v4.py`)
- **Execution Date**: October 22, 2026
- **Test Result**: **8 / 8 Scenarios Passed (100%)**
- **Verified Items**:
  - Scenario 1 (Low-Risk): Score 1.724, Low probability 95.42%.
  - Scenario 2 (Medium-Risk): Score 3.002, Medium probability 53.91%.
  - Scenario 3 (Extreme High-Risk): Raw latent score 5.265 clamped cleanly to **5.000 / 5.0**.
  - Scenario 4 (Empty Input): Validation guard triggered cleanly (`MissingRequiredInput`).
  - Scenario 5 (Missing Optional Values): Handled 66 unobserved items via cohort medians.
  - Scenario 6 (Dirty Text / Infinities): Graceful coercion and warnings generated.
  - Scenario 7 (Out-of-Range Clamping): Domain boundaries enforced.
  - Scenario 8 (Borderlines): Continuous score near cutoffs evaluated with realistic confidence spread.

### 3. UI Navigation & Preset Suite (`test_ui_pages_and_navigation_v4.py`)
- **Execution Date**: October 22, 2026
- **Test Result**: **4 / 4 Checkpoints Passed (100%)**
- **Duration**: 0.010s
- **Verified Items**:
  1. Default survey answers dictionary completeness (all 20 high-level questionnaire fields defined).
  2. Default student profile prediction with full LinearSHAP human labels and plain explanations.
  3. Clean execution of all 8 presets without throwing runtime exceptions.
  4. Extreme high-risk clamping verified (clamped: 5.000, raw: 5.180).

---

## 5. Live Application Status & Daemon Details

The redesigned Streamlit application is actively serving requests locally:
- **Local URL**: `http://localhost:8501`
- **Network URL**: `http://192.168.1.104:8501`
- **Service Process**: Active daemon (PID task-972)
- **HTTP Status Code**: `200 OK`
- **Primary Source File**: `Model Training/v4_performance_experiments/integration/app_ui_v4.py`
- **Inference Engine**: `Model Training/v4_performance_experiments/integration/integration_service_v4.py`

---

## 6. Examiner Demonstration Quick-Reference

When demonstrating the application to university progress evaluation panels:
1. **For Student User Experience**:
   - Open `http://localhost:8501`.
   - Click **"🚀 Begin Reflection"** from the home screen.
   - Walk through Sections 1–4 using the natural step progression.
   - Review responses on the summary screen.
   - Click **"🚀 Submit & Generate My Reflection"** to show the personalized, explainable results.
2. **For Rapid Examiner Stress-Testing**:
   - Expand the **"🧪 Examiner & Research Tools"** section in the left sidebar.
   - Select any scenario (e.g., *"High-Risk Student Profile (Extreme)"* or *"Borderline Medium/High"*).
   - Click **"Evaluate Now"** to jump straight to the results screen and inspect the clamped construct score, calibrated distribution, and LinearSHAP attributions.
