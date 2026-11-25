# Component 1: Independent Cohort Validation & User Acceptance Testing (UAT) Manual

**Project:** Psychometric Learning Analytics Framework (`J26-DS-310`)  
**Component:** Component 1 – Explainable Cognitive Offloading Risk Prediction (`IT23426580`)  
**Blank Data Collection Template:** [`independent_cohort_template.csv`](independent_cohort_template.csv)  
**Evaluator Script:** [`evaluate_independent_cohort.py`](../scripts/evaluate_independent_cohort.py)  

> **Honest Status Disclosure:** All materials below are prepared and verified for prospective independent cohort collection. **No new external student responses or live UAT scores have been collected or fabricated.**

---

## Part A: Independent Cohort Data Collection Materials (Task 4)

### 1. Recommended Study Design & Identifier Format
- **Target Sample:** $N \ge 80$ minimum ($N = 120–150$ recommended), balanced across the 5 degree disciplines so each tertile stratum has $\ge 30$ students.
- **Anonymous Participant ID Format (`study_id`):** Assign sequential non-identifying tokens such as `IND_001` through `IND_150`. Never enter student registration numbers (`IT...`), emails, names, or phone numbers—`evaluate_independent_cohort.py` blocks rows matching PII patterns (`@`, `IT\d{6,}`) or duplicate `study_id` values.

### 2. Complete Variable Dictionary (27 Columns Matching `independent_cohort_template.csv`)

| Col # | Column Header | Type & Allowed Values | Role |
|---:|---|---|---|
| 1 | `study_id` | Unique anonymous string (e.g., `IND_001`), max 32 chars, no PII | Anonymous key |
| 2 | `degree_field` | Exact canonical slug: `Computing_IT`, `Engineering`, `Business_Economics`, `Natural_Applied_Sciences`, `Humanities_Health_Other` | UI Q1 predictor |
| 3 | `academic_year` | Integer `1..6` (`1`=1st Year .. `5`=5th Year, `6`=Postgraduate) | UI Q2 predictor |
| 4 | `age_group` | Integer `1..4` (`1`=18–20, `2`=21–23, `3`=24–26, `4`=27 or above) | UI Q3 predictor |
| 5 | `ai_usage_freq` | Integer `1..4` (`1`=Rarely, `2`=Sometimes, `3`=Frequently, `4`=Daily) | UI Q4 predictor |
| 6 | `ai_time_per_week` | Integer `1..5` (`1`=<1h, `2`=1–3h, `3`=4–6h, `4`=7–10h, `5`=>10h) | UI Q5 predictor |
| 7 | `tools_used` | Semicolon-separated (`;`) subset of: `ChatGPT`, `Google Gemini`, `Microsoft Copilot`, `Claude`, `Perplexity AI` | UI Q6 predictor |
| 8 | `Q20_task_delegation_freq` | Integer `1..5` (`1`=Never .. `5`=Very Often) | UI Q7 predictor |
| 9 | `tasks_delegated` | Semicolon-separated (`;`) subset of: `Writing assignments`, `Explaining concepts`, `Summarising materials`, `Creating presentations`, `Programming problems`, `Mathematical problems` | UI Q8 predictor |
| 10 | `Q1_direct_use_freq` | Integer `1..5` (`1`=Never .. `5`=Always) | UI Q9 predictor |
| 11 | `Q22_effort_on_ai_answers` | Integer `1..5` (`1`=No Effort .. `5`=Very High Effort) | UI Q10 predictor |
| 12 | `Q2_verify_info` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q11 predictor |
| 13 | `Q3_compare_sources` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q12 predictor |
| 14 | `Q4_check_accuracy` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q13 predictor |
| 15 | `Q5_understand_reasoning` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q14 predictor |
| 16 | `Q6_modify_content` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q15 predictor |
| 17 | `Q7_attempt_independently` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q16 predictor |
| 18 | `Q8_complete_without_ai` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q17 predictor |
| 19 | `Q9_learning_assistant` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q18 predictor |
| 20 | `Q30_trust_accuracy` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q19 predictor |
| 21 | `Q33_trust_appropriate_support` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | UI Q20 predictor |
| 22 | `Q10_rely_memory` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | Reference label only |
| 23 | `Q11_avoid_mental_effort` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | Reference label only |
| 24 | `Q12_accept_without_understanding` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | Reference label only |
| 25 | `Q13_less_problem_solving` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | Reference label only |
| 26 | `Q14_depend_on_ai` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | Reference label only |
| 27 | `Q15_reduces_thinking` | Likert integer `1..5` (`1`=Strongly Disagree .. `5`=Strongly Agree) | Reference label only |

---

### 3. Exact Questionnaire Wording & Response Options

#### Block 1: Model Predictor Items (`UI Q1–Q20`, Verbatim From `component1.html`)
1. **Q1 (`degree_field`):** *"Academic Field / Discipline — Select the discipline that best matches your undergraduate degree."*  
   Options: `Computing_IT` (Computer Science / IT / Software Engineering), `Engineering` (Engineering & Architecture), `Business_Economics` (Business / Economics / Management), `Natural_Applied_Sciences` (Natural & Applied Sciences), `Humanities_Health_Other` (Humanities / Social Sciences / Health / Law).
2. **Q2 (`academic_year`):** *"Current Academic Year — Current stage of study."* (`1` = 1st Year (Freshman), `2` = 2nd Year (Sophomore), `3` = 3rd Year (Junior), `4` = 4th Year (Senior), `5` = 5th Year, `6` = Postgraduate).
3. **Q3 (`age_group`):** *"Age Group — Select your age bracket."* (`1` = 18–20 years, `2` = 21–23 years, `3` = 24–26 years, `4` = 27 or above).
4. **Q4 (`ai_usage_freq`):** *"Frequency of Generative AI Usage for Coursework — How often do you interact with Generative AI tools during an active teaching semester?"* (`1` = Rarely [less than once a week], `2` = Sometimes [1–3 times/week], `3` = Frequently [4–6 times/week], `4` = Daily [every day]).
5. **Q5 (`ai_time_per_week`):** *"Estimated Cumulative AI Usage Time Per Week"* (`1` = Less than 1 hour, `2` = 1 to 3 hours, `3` = 4 to 6 hours, `4` = 7 to 10 hours, `5` = More than 10 hours).
6. **Q6 (`tools_used`):** *"Generative AI Tools Actively Utilized — Select all tools you actively use for academic work."* (`ChatGPT`, `Google Gemini`, `Microsoft Copilot`, `Claude`, `Perplexity AI`).
7. **Q7 (`Q20_task_delegation_freq`):** *"Frequency of Delegating Complete Academic Tasks to AI — How often do you prompt Generative AI to solve or complete entire coursework tasks for you?"* (`1` = Never, `2` = Rarely, `3` = Sometimes, `4` = Often, `5` = Very Often).
8. **Q8 (`tasks_delegated`):** *"Academic Tasks Typically Delegated to AI — Select all types of tasks you delegate to AI systems."* (`Writing assignments`, `Explaining concepts`, `Summarising materials`, `Creating presentations`, `Programming problems`, `Mathematical problems`).
9. **Q9 (`Q1_direct_use_freq`):** *"Direct Use of AI-Generated Content Without Modification — I directly submit or use AI-generated outputs in coursework without substantive personal editing."* (`1` = Never, `2` = Rarely, `3` = Sometimes, `4` = Often, `5` = Always).
10. **Q10 (`Q22_effort_on_ai_answers`):** *"Cognitive Effort Invested in Reviewing AI Outputs — How much analytical effort do you expend evaluating and verifying AI-generated solutions?"* (`1` = No Effort, `2` = Little Effort, `3` = Moderate Effort, `4` = High Effort, `5` = Very High Effort).
11. **Q11 (`Q2_verify_info`):** *"Verification of AI-Generated Claims — I verify the factual accuracy of AI-generated statements before using them in my work."* (`1` Strongly Disagree .. `5` Strongly Agree).
12. **Q12 (`Q3_compare_sources`):** *"Cross-Referencing Independent Sources — I compare AI-provided explanations with textbooks, lecture slides, or peer-reviewed literature."* (`1..5`).
13. **Q13 (`Q4_check_accuracy`):** *"Checking Numerical & Formula Accuracy — I actively test whether AI formulas, derivations, calculations, or code outputs are factually sound."* (`1..5`).
14. **Q14 (`Q5_understand_reasoning`):** *"Conceptual Comprehension Before Adoption — Before adopting an AI solution, I ensure I personally understand the underlying logic and derivation."* (`1..5`).
15. **Q15 (`Q6_modify_content`):** *"Personal Voice & Critical Synthesis — I rewrite and synthesize AI suggestions into my own academic phrasing and individual perspective."* (`1..5`).
16. **Q16 (`Q7_attempt_independently`):** *"Independent Problem-Solving Attempt Before Prompting — I make a serious personal attempt to solve difficult problems before turning to an AI tool."* (`1..5`).
17. **Q17 (`Q8_complete_without_ai`):** *"Confidence in Completing Coursework Without AI — I feel fully confident that I can successfully complete my coursework tasks without any AI assistance."* (`1..5`).
18. **Q18 (`Q9_learning_assistant`):** *"Use of AI as an Explanatory Study Companion — I view and use Generative AI as a learning assistant to clarify concepts rather than a substitute for my own thinking."* (`1..5`).
19. **Q19 (`Q30_trust_accuracy`):** *"Uncritical Trust in AI Accuracy — I generally assume that facts and solutions provided by Generative AI are correct and trustworthy without verification."* (`1..5`).
20. **Q20 (`Q33_trust_appropriate_support`):** *"Deference to AI Problem Guidance — I trust that Generative AI provides the most appropriate guidance for my coursework problems over my own reasoning."* (`1..5`).

#### Block 2: Separate Reference Ground-Truth Construct Items (`Section E`, NEVER Fed Into Model)
All rated `1 = Strongly Disagree` to `5 = Strongly Agree`:
- **`Q10_rely_memory`:** *"I rely on Generative AI to remember information that I could learn myself."*
- **`Q11_avoid_mental_effort`:** *"I use GenAI to avoid spending too much mental effort on difficult academic tasks."*
- **`Q12_accept_without_understanding`:** *"I sometimes accept AI-generated solutions without fully understanding the concepts."*
- **`Q13_less_problem_solving`:** *"I feel less need to develop my own problem-solving strategies when GenAI provides quick solutions."*
- **`Q14_depend_on_ai`:** *"I depend on GenAI for tasks that I previously performed using my own reasoning skills."*
- **`Q15_reduces_thinking`:** *"Using GenAI reduces the amount of independent thinking required for some academic activities."*

*(Ground-truth score = unweighted mean of `Q10–Q15`; reference risk class = `Low` $\le 2.667$, `Medium` $2.668–3.500$, `High` $> 3.500$.)*

---

### 4. Collection, Data Preparation & Evaluation Execution
1. **Collect Responses:** Administer consent notice + Block 1 (`Q1–Q20`) + Block 2 (`Q10–Q15`) anonymously via Google Forms / Microsoft Forms / offline sheet using sequential `IND_###` IDs. Keep the production Flask questionnaire UI untouched and non-persisting.
2. **Prepare CSV:** Export form responses, remove timestamp/email/student-ID columns, encode categorical responses using [`independent_cohort_template.csv`](independent_cohort_template.csv) exact headers/slugs, join multi-select checkboxes with `;`, and store CSV **outside Git** (or inside ignored `data/raw/`).
3. **Run Evaluator Command:**
```bash
.venv/bin/python component1_streamlit_v4/scripts/evaluate_independent_cohort.py \
  --input data/raw/independent_cohort_anonymized.csv \
  --out-json /tmp/c1_independent_cohort_report.json
```
4. **Expected JSON Output Format:**
```json
{
  "n_submitted": 120,
  "n_evaluated": 120,
  "n_dropped_incomplete_reference": 0,
  "zero_target_leakage_verified": true,
  "reference_scale_cronbach_alpha": 0.85,
  "thresholds_applied": { "cut1_low_max": 2.667, "cut2_med_max": 3.5 },
  "metrics": {
    "accuracy": 0.0,
    "macro_f1": 0.0,
    "weighted_f1": 0.0,
    "high_risk_recall": 0.0,
    "log_loss": 0.0,
    "continuous_rmse": 0.0,
    "continuous_mae": 0.0,
    "continuous_pearson_r": 0.0,
    "per_class": { "Low": {}, "Medium": {}, "High": {} },
    "confusion_matrix": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
  }
}
```
5. **Fail-Closed Rejection Checks Verified in Automated Tests:** The script strictly rejects duplicate `study_id`s, forbidden PII (`email`, `student_id`, `@`, `IT\d{6,}`), leakage/unexpected columns (`co_score`, `co_risk`, `Q37_important_part`), non-integer/out-of-range Likert entries, invalid `degree_field`/`tools_used`/`tasks_delegated` encodings, or missing reference questions `Q10–Q15`.

---

## Part B: Student Usability Testing (UAT) Instructions & Questionnaire (Task 5)

### 1. Conducting UAT Sessions (`N = 5–10` Pilot Undergraduates)
1. Open `/component1/` in a clean browser window (`1280×800` desktop and `375×812` mobile viewport) without pre-loading Viva presets.
2. Ask the student to complete Sections 1–4 independently (~3 minutes) while a facilitator observes passively using the 10-point checklist below (recording latency, validation triggers, and hesitation—without prompting answers).
3. After submission, ask the student to explain in their own words: (a) their predicted risk tier and spectrum score, (b) one top driver increasing or protecting risk, and (c) whether the research disclaimer is clear.

### 2. 10-Flow Observer Usability Checklist
| # | Flow Tested | Pass Criteria | Result |
|---:|---|---|---|
| 1 | First impression & clarity | Purpose understood as ~3-min study-habit reflection (not a test/grade). | `[ ] Pass  [ ] Fail` |
| 2 | Questionnaire readability | All 20 items read naturally without confusing jargon. | `[ ] Pass  [ ] Fail` |
| 3 | Validation behavior | Missing fields highlight clearly on *Next*/*Submit* without losing entered choices. | `[ ] Pass  [ ] Fail` |
| 4 | Multi-step navigation | *Back* and *Next* preserve dropdowns, radios, and checkboxes cleanly. | `[ ] Pass  [ ] Fail` |
| 5 | Progress tracking | Bar (`25%–100%`) and section pills accurately track progress. | `[ ] Pass  [ ] Fail` |
| 6 | Result clarity | Risk badge, `[1.0–5.0]` spectrum bar, and 3-tier probability split make sense together. | `[ ] Pass  [ ] Fail` |
| 7 | LinearSHAP drivers | Student identifies *Increasing Risk* vs. *Protecting Autonomy* factors accurately. | `[ ] Pass  [ ] Fail` |
| 8 | Study suggestions | Recommended study habits feel practical and actionable. | `[ ] Pass  [ ] Fail` |
| 9 | Mobile usability (`375px`) | Zero horizontal scroll, responsive Likert tiles (`>= 44px`), clean wrapping. | `[ ] Pass  [ ] Fail` |
| 10 | Disclaimer visibility | Non-diagnostic exploratory notice and zero-storage message are clearly noticed. | `[ ] Pass  [ ] Fail` |

### 3. Brief Student Feedback Questionnaire (Anonymous, 5-Point Likert)
*Rate `1 (Strongly Disagree)` to `5 (Strongly Agree)`:*
1. *"It was clear what this AI study habits reflection tool does and why each question was asked."* (`1 2 3 4 5`)
2. *"All 20 questions were easy to understand without needing extra explanation."* (`1 2 3 4 5`)
3. *"Moving across the 4 sections, correcting missing inputs, and submitting worked smoothly."* (`1 2 3 4 5`)
4. *"My risk tier, continuous score bar, and percentage likelihoods were easy to interpret."* (`1 2 3 4 5`)
5. *"The habit drivers clearly explained why my score was low, moderate, or high."* (`1 2 3 4 5`)
6. *"The recommended study strategies gave me practical ideas I can apply."* (`1 2 3 4 5`)
7. *Open-ended:* "Was any question wording, metric label, or explanation unclear?"
8. *Open-ended:* "What single improvement would make this reflection tool more useful?"
