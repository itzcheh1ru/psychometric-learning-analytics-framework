"""
preprocess_v4.py
================
Final Research-Grade Preprocessing & Feature Engineering Pipeline
for Component 1 (Version 4): Explainable Cognitive Offloading Risk Model (J26-DS-310).

Target Definition:
------------------
Strictly the 6 approved Section E cognitive offloading items from Questionnaire & Proposal:
  - Q10_rely_memory (Col 21)
  - Q11_avoid_mental_effort (Col 22)
  - Q12_accept_without_understanding (Col 23)
  - Q13_less_problem_solving (Col 24)
  - Q14_depend_on_ai (Col 25)
  - Q15_reduces_thinking (Col 26)

Target Discretization:
  - Low Risk:    co_score <= 2.667 (empirical lower tertile)
  - Medium Risk: 2.668 <= co_score <= 3.500 (empirical middle tertile)
  - High Risk:   co_score > 3.500 (empirical upper tertile)

Exclusions:
  - Columns 0-4 (Administrative metadata: ID, timestamps, emails, names, consent)
  - Columns 21-26 (The 6 target-construction items)
  - Columns 45-49 (The 5 Section G Academic AI Dependence items, including Q37_important_part)
  - Target-derived variables (co_score, co_risk) excluded from feature matrix X

Outputs:
  - Model Training/v4_performance_experiments/data/cleaned_dataset_v4.csv
  - Model Training/v4_performance_experiments/reports/preprocessing_report_v4.txt
"""

import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent.parent  # PP1 Documents/
RAW_DATA_PATH = PROJECT_DIR / "Data Set" / "raw_data.xlsx"
V4_DATA_DIR = SCRIPT_DIR.parent / "data"
V4_REPORT_DIR = SCRIPT_DIR.parent / "reports"

V4_CLEANED_CSV = V4_DATA_DIR / "cleaned_dataset_v4.csv"
V4_REPORT_TXT = V4_REPORT_DIR / "preprocessing_report_v4.txt"

V4_DATA_DIR.mkdir(parents=True, exist_ok=True)
V4_REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ── Scale Mappings ─────────────────────────────────────────────────────────────
AGREE_MAP = {
    "strongly agree": 5,
    "agree": 4,
    "neutral": 3,
    "neither agree nor disagree": 3,
    "disagree": 2,
    "strongly disagree": 1,
}

FREQ_MAP = {
    "always": 5,
    "often": 4,
    "sometimes": 3,
    "rarely": 2,
    "never": 1,
}

USAGE_FREQ_MAP = {
    "daily": 4,
    "frequently (4–6 times per week)": 3,
    "frequently (4\u20136 times per week)": 3,
    "sometimes  (1–3 times per week)": 2,
    "sometimes  (1\u20133 times per week)": 2,
    "sometimes (1–3 times per week)": 2,
    "rarely (less than once a week)": 1,
}

TIME_MAP = {
    "more than 10 hours": 5,
    "7–10 hours": 4,
    "7\u201310 hours": 4,
    "4–6 hours": 3,
    "4\u20136 hours": 3,
    "1–3 hour": 2,
    "1\u20133 hour": 2,
    "less than 1 hour": 1,
}

TASK_FREQ_MAP = {
    "very often": 5,
    "often": 4,
    "sometimes": 3,
    "rarely": 2,
    "never": 1,
}

EFFORT_MAP = {
    "very high effort": 5,
    "high effort": 4,
    "moderate effort": 3,
    "little effort": 2,
    "no effort": 1,
}

AGE_MAP = {
    "18-20": 1,
    "21-23": 2,
    "24-26": 3,
    "above 26": 4,
    "27 or above": 4,
}

YEAR_MAP = {
    "1st year": 1,
    "2nd year": 2,
    "3rd year": 3,
    "4th year": 4,
    "5th year": 5,
    "postgraduate": 6,
}


def normalise(val):
    if pd.isna(val):
        return np.nan
    return str(val).strip().replace("\xa0", " ").lower()


def map_series(series, mapping, col_name, log_list):
    norm_s = series.map(normalise)
    norm_dict = {normalise(k): v for k, v in mapping.items()}
    mapped = norm_s.map(norm_dict)
    unmatched = norm_s[mapped.isna() & norm_s.notna()].unique()
    if len(unmatched) > 0:
        log_list.append(f"  [WARN] Unmatched in '{col_name}': {list(unmatched)}")
    return mapped


def classify_meta_faculty(val):
    """Group degree free-text entries into robust broad academic domains."""
    if pd.isna(val):
        return "Humanities_Health_Other"
    v = str(val).lower().strip()
    if any(k in v for k in ["software", "se", "computer", "cs", "it", "information", "computing", "data science", "cyber", "bis", "cis"]):
        return "Computing_IT"
    if any(k in v for k in ["engineering", "eng", "mechanical", "civil", "architecture"]):
        return "Engineering"
    if any(k in v for k in ["business", "management", "accounting", "finance", "economics", "commerce", "logistics"]):
        return "Business_Economics"
    if any(k in v for k in ["science", "bio", "food", "nutrition", "applied", "physical", "environmental", "chemistry", "mathematics", "statistics"]):
        return "Natural_Applied_Sciences"
    return "Humanities_Health_Other"


def make_dummies(series, prefix, keywords):
    dummies = {}
    for kw in keywords:
        safe_kw = kw.lower().replace(" ", "_").replace("/", "_").replace("&", "and")
        dummies[f"{prefix}_{safe_kw}"] = (
            series.fillna("").str.lower().str.contains(kw.lower(), regex=False).astype(int)
        )
    return pd.DataFrame(dummies, index=series.index)


def run_preprocessing_v4():
    logs = []
    logs.append("=" * 80)
    logs.append("COMPONENT 1: ADVANCED PREPROCESSING & FEATURE PIPELINE (Version 4)")
    logs.append("Explainable Cognitive Offloading Risk Model — Research Project J26-DS-310")
    logs.append("=" * 80)

    # 1. Load Raw Data
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw data file not found at: {RAW_DATA_PATH}")
    df_raw = pd.read_excel(RAW_DATA_PATH)
    logs.append(f"\n[Step 1] Loaded raw survey export: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")

    # 2. Consent Screening
    consent_col = df_raw.columns[4]
    df = df_raw[df_raw[consent_col] == "I agree to participate"].copy()
    logs.append(f"\n[Step 2] Consent screening: {len(df_raw) - len(df)} non-consenting removed -> {len(df)} retained.")

    # 3. Target Construct Extraction (Section E, Columns 21–26)
    logs.append("\n[Step 3] Cognitive Offloading Construct Formulation (Section E):")
    section_e_cols = [df.columns[i] for i in range(21, 27)]
    target_names = [
        "Q10_rely_memory",
        "Q11_avoid_mental_effort",
        "Q12_accept_without_understanding",
        "Q13_less_problem_solving",
        "Q14_depend_on_ai",
        "Q15_reduces_thinking",
    ]

    df_target = pd.DataFrame(index=df.index)
    for col_raw, col_short in zip(section_e_cols, target_names):
        df_target[col_short] = map_series(df[col_raw], AGREE_MAP, col_short, logs)
        logs.append(f"         - {col_short}: '{col_raw[:60]}...'")

    # Reliability & Score
    k = df_target.shape[1]
    item_vars = df_target.var(axis=0, ddof=1).sum()
    comp_var = df_target.sum(axis=1).var(ddof=1)
    cronbach_alpha = (k / (k - 1)) * (1.0 - item_vars / comp_var)
    co_score = df_target.mean(axis=1)

    logs.append(f"         Cronbach's Alpha: {cronbach_alpha:.4f}")
    logs.append(f"         Composite co_score: Mean = {co_score.mean():.4f}, Std = {co_score.std():.4f}")

    def assign_risk(score):
        if score <= 2.667:
            return "Low"
        elif score <= 3.500:
            return "Medium"
        else:
            return "High"

    co_risk = co_score.apply(assign_risk)
    risk_counts = co_risk.value_counts().loc[["Low", "Medium", "High"]]
    logs.append(f"         Tertile Risk Categories: Low={risk_counts['Low']}, Med={risk_counts['Medium']}, High={risk_counts['High']}")

    # 4. Strict Pruning of Circular Items
    admin_cols = [df.columns[i] for i in range(0, 5)]
    target_raw_cols = section_e_cols
    section_g_cols = [df.columns[i] for i in range(45, 50)]  # Columns 45-49

    prune_cols = admin_cols + target_raw_cols + section_g_cols
    df_features = df.drop(columns=prune_cols).copy()
    logs.append(f"\n[Step 4] Excluded {len(prune_cols)} columns (admin, target construct, and Section G dependence battery).")

    # 5. Rename Remaining Predictor Columns
    col_rename = {
        df_raw.columns[5]: "age_group",
        df_raw.columns[6]: "degree_field",
        df_raw.columns[7]: "academic_year",
        df_raw.columns[8]: "ai_usage_freq",
        df_raw.columns[9]: "ai_tools_used",
        df_raw.columns[10]: "ai_purposes",
        df_raw.columns[11]: "ai_time_per_week",
        df_raw.columns[12]: "Q1_direct_use_freq",
        df_raw.columns[13]: "Q2_verify_info",
        df_raw.columns[14]: "Q3_compare_sources",
        df_raw.columns[15]: "Q4_check_accuracy",
        df_raw.columns[16]: "Q5_understand_reasoning",
        df_raw.columns[17]: "Q6_modify_content",
        df_raw.columns[18]: "Q7_attempt_independently",
        df_raw.columns[19]: "Q8_complete_without_ai",
        df_raw.columns[20]: "Q9_learning_assistant",
        df_raw.columns[27]: "Q16_ai_improves_learning",
        df_raw.columns[28]: "Q17_ai_confidence",
        df_raw.columns[29]: "Q18_ai_efficiency",
        df_raw.columns[30]: "Q19_negative_affect_warning",
        df_raw.columns[31]: "Q20_task_delegation_freq",
        df_raw.columns[32]: "tasks_delegated_types",
        df_raw.columns[33]: "Q22_effort_on_ai_answers",
        df_raw.columns[34]: "Q23_pu_improves_understanding",
        df_raw.columns[35]: "Q24_pu_complete_effectively",
        df_raw.columns[36]: "Q25_pu_productivity",
        df_raw.columns[37]: "Q26_pu_useful_for_goals",
        df_raw.columns[38]: "Q27_pu_learn_difficult_topics",
        df_raw.columns[39]: "Q28_trust_reliable_info",
        df_raw.columns[40]: "Q29_trust_consistent",
        df_raw.columns[41]: "Q30_trust_accuracy",
        df_raw.columns[42]: "Q31_trust_explanations",
        df_raw.columns[43]: "Q32_trust_clear_explanations",
        df_raw.columns[44]: "Q33_trust_appropriate_support",
        df_raw.columns[50]: "Q39_feel_capable",
        df_raw.columns[51]: "Q40_feel_confident",
        df_raw.columns[52]: "Q41_more_capable_after",
        df_raw.columns[53]: "Q42_more_confident_after",
        df_raw.columns[54]: "Q43_approach_challenging",
    }
    df_features = df_features.rename(columns=col_rename)

    # 6. Apply Ordinal Mappings
    df_clean = pd.DataFrame(index=df.index)
    df_clean["age_group"] = map_series(df_features["age_group"], AGE_MAP, "age_group", logs)
    df_clean["academic_year"] = map_series(df_features["academic_year"], YEAR_MAP, "academic_year", logs)
    df_clean["ai_usage_freq"] = map_series(df_features["ai_usage_freq"], USAGE_FREQ_MAP, "ai_usage_freq", logs)
    df_clean["ai_time_per_week"] = map_series(df_features["ai_time_per_week"], TIME_MAP, "ai_time_per_week", logs)
    df_clean["Q1_direct_use_freq"] = map_series(df_features["Q1_direct_use_freq"], FREQ_MAP, "Q1_direct_use_freq", logs)
    df_clean["Q20_task_delegation_freq"] = map_series(df_features["Q20_task_delegation_freq"], TASK_FREQ_MAP, "Q20_task_delegation_freq", logs)
    df_clean["Q22_effort_on_ai_answers"] = map_series(df_features["Q22_effort_on_ai_answers"], EFFORT_MAP, "Q22_effort_on_ai_answers", logs)

    agree_cols = [
        "Q2_verify_info", "Q3_compare_sources", "Q4_check_accuracy",
        "Q5_understand_reasoning", "Q6_modify_content", "Q7_attempt_independently",
        "Q8_complete_without_ai", "Q9_learning_assistant", "Q16_ai_improves_learning",
        "Q17_ai_confidence", "Q18_ai_efficiency", "Q19_negative_affect_warning",
        "Q23_pu_improves_understanding", "Q24_pu_complete_effectively",
        "Q25_pu_productivity", "Q26_pu_useful_for_goals",
        "Q27_pu_learn_difficult_topics", "Q28_trust_reliable_info",
        "Q29_trust_consistent", "Q30_trust_accuracy", "Q31_trust_explanations",
        "Q32_trust_clear_explanations", "Q33_trust_appropriate_support",
        "Q39_feel_capable", "Q40_feel_confident", "Q41_more_capable_after",
        "Q42_more_confident_after", "Q43_approach_challenging",
    ]
    for c in agree_cols:
        df_clean[c] = map_series(df_features[c], AGREE_MAP, c, logs)

    # Impute any missing values with median
    df_clean = df_clean.fillna(df_clean.median())

    # 7. Theoretically Grounded Composites
    df_clean["composite_verification"] = df_clean[
        ["Q2_verify_info", "Q3_compare_sources", "Q4_check_accuracy", "Q5_understand_reasoning", "Q6_modify_content"]
    ].mean(axis=1)

    df_clean["composite_autonomy"] = df_clean[
        ["Q7_attempt_independently", "Q8_complete_without_ai", "Q9_learning_assistant"]
    ].mean(axis=1)

    df_clean["composite_trust"] = df_clean[
        ["Q28_trust_reliable_info", "Q29_trust_consistent", "Q30_trust_accuracy",
         "Q31_trust_explanations", "Q32_trust_clear_explanations", "Q33_trust_appropriate_support"]
    ].mean(axis=1)

    df_clean["composite_tam"] = df_clean[
        ["Q23_pu_improves_understanding", "Q24_pu_complete_effectively", "Q25_pu_productivity",
         "Q26_pu_useful_for_goals", "Q27_pu_learn_difficult_topics"]
    ].mean(axis=1)

    df_clean["composite_self_efficacy"] = df_clean[
        ["Q39_feel_capable", "Q40_feel_confident", "Q41_more_capable_after",
         "Q42_more_confident_after", "Q43_approach_challenging"]
    ].mean(axis=1)

    # 8. Behavioral Interaction Terms
    df_clean["idx_automation_bias"] = df_clean["composite_trust"] - df_clean["composite_verification"]
    df_clean["idx_delegation_intensity"] = df_clean["ai_usage_freq"] * df_clean["Q20_task_delegation_freq"]
    df_clean["idx_passive_adoption"] = df_clean["Q1_direct_use_freq"] * (6.0 - df_clean["Q22_effort_on_ai_answers"])

    # 9. Breadth Counts
    df_clean["count_tools_used"] = (
        df_features["ai_tools_used"].fillna("").apply(lambda x: len([p for p in str(x).split(";") if p.strip()]))
    )
    df_clean["count_tasks_delegated"] = (
        df_features["tasks_delegated_types"].fillna("").apply(lambda x: len([p for p in str(x).split(";") if p.strip()]))
    )
    df_clean["count_purposes"] = (
        df_features["ai_purposes"].fillna("").apply(lambda x: len([p for p in str(x).split(";") if p.strip()]))
    )

    # 10. Meta-Faculty Categorization (5 Domains)
    meta_faculties = df_features["degree_field"].apply(classify_meta_faculty)
    faculty_dummies = pd.get_dummies(meta_faculties, prefix="faculty", dtype=int)
    for col in [
        "faculty_Business_Economics", "faculty_Computing_IT", "faculty_Engineering",
        "faculty_Humanities_Health_Other", "faculty_Natural_Applied_Sciences"
    ]:
        if col not in faculty_dummies.columns:
            faculty_dummies[col] = 0
    df_clean = pd.concat([df_clean, faculty_dummies], axis=1)

    # 11. Multi-Select Dummies (Tools, Purposes, Delegated Tasks)
    tool_keywords = ["ChatGPT", "Google Gemini", "Microsoft Copilot", "Claude", "Perplexity"]
    purpose_keywords = [
        "Understanding concepts", "Assignment preparation", "Exam preparation",
        "Writing improvement", "Summarising content", "Generating ideas"
    ]
    task_keywords = [
        "Writing assignments", "Explaining concepts", "Summarising materials",
        "Creating presentations", "Programming problems", "Mathematical problems"
    ]

    tool_df = make_dummies(df_features["ai_tools_used"], "tool", tool_keywords)
    purpose_df = make_dummies(df_features["ai_purposes"], "purpose", purpose_keywords)
    task_df = make_dummies(df_features["tasks_delegated_types"], "delegate", task_keywords)

    df_clean = pd.concat([df_clean, tool_df, purpose_df, task_df], axis=1)

    # 12. Append Target Variables
    df_clean["co_score"] = co_score
    df_clean["co_risk"] = co_risk

    # 13. Save Cleaned Dataset
    df_clean.to_csv(V4_CLEANED_CSV, index=False)
    logs.append(f"\n[Step 5] Preprocessing complete. Cleaned shape: {df_clean.shape[0]} rows × {df_clean.shape[1]} columns")
    logs.append(f"         Exported to: {V4_CLEANED_CSV}")

    report_str = "\n".join(logs)
    with open(V4_REPORT_TXT, "w") as f:
        f.write(report_str)

    print(report_str)
    return df_clean


if __name__ == "__main__":
    run_preprocessing_v4()
