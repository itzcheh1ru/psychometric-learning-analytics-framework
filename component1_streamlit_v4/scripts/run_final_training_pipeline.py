"""
run_final_training_pipeline.py
==============================
Future-ready, leakage-free training and evaluation workflow for Component 1:
Explainable Cognitive Offloading Risk Prediction Model (J26-DS-310).

Designed to accept an expanded dataset (any valid cohort size N != 375) once
ongoing data collection finishes, while preserving Version 4 artifacts intact
for baseline comparison and safe rollback.

Pipeline Stages:
  1. Import raw survey export (.xlsx) or cleaned pre-split CSV.
  2. Validate consent, filter invalid records, deduplicate respondents cleanly.
  3. Extract features row-by-row with zero Section E (Q10-Q15) / G (Q34-Q38) leakage.
  4. Partition train vs. untouched evaluation set proportionally BEFORE imputation,
     scaling, threshold derivation, calibration, or model comparison.
  5. Benchmark candidate models via 5x5 Repeated Stratified CV on training data only.
  6. Fit training-only reference medians, means, scaler, and Ridge calibration sigma.
  7. Evaluate final model once on untouched test split (Full features + 20-input UI).
  8. Export drop-in compatible artifacts & comparison summary vs. Version 4 baseline.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

SCRIPT_DIR = Path(__file__).resolve().parent
COMPONENT1_DIR = SCRIPT_DIR.parent
REPO_ROOT = COMPONENT1_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.cognitive_offloading.integration_service import classify_meta_faculty  # noqa: E402
from component1_streamlit_v4.scripts.analyze_ui_historical_errors import row_to_ui_payload  # noqa: E402

try:
    from xgboost import XGBClassifier  # type: ignore
except ImportError:
    XGBClassifier = None

try:
    from lightgbm import LGBMClassifier  # type: ignore
except ImportError:
    LGBMClassifier = None

try:
    from catboost import CatBoostClassifier  # type: ignore
except ImportError:
    CatBoostClassifier = None

DEFAULT_CUT1 = 2.667
DEFAULT_CUT2 = 3.500
TARGET_MAPPING = {"Low": 0, "Medium": 1, "High": 2}
INV_TARGET_MAPPING = {0: "Low", 1: "Medium", 2: "High"}

SECTION_E_ITEMS = [
    "Q10_rely_memory",
    "Q11_avoid_mental_effort",
    "Q12_accept_without_understanding",
    "Q13_less_problem_solving",
    "Q14_depend_on_ai",
    "Q15_reduces_thinking",
]

AGREE_MAP = {
    "strongly agree": 5.0,
    "agree": 4.0,
    "neutral": 3.0,
    "neither agree nor disagree": 3.0,
    "disagree": 2.0,
    "strongly disagree": 1.0,
}
FREQ_MAP = {"always": 5.0, "often": 4.0, "sometimes": 3.0, "rarely": 2.0, "never": 1.0}
USAGE_FREQ_MAP = {
    "daily": 4.0,
    "frequently (4–6 times per week)": 3.0,
    "frequently (4-6 times per week)": 3.0,
    "sometimes  (1–3 times per week)": 2.0,
    "sometimes (1–3 times per week)": 2.0,
    "sometimes (1-3 times per week)": 2.0,
    "rarely (less than once a week)": 1.0,
}
TIME_MAP = {
    "more than 10 hours": 5.0,
    "7–10 hours": 4.0,
    "7-10 hours": 4.0,
    "4–6 hours": 3.0,
    "4-6 hours": 3.0,
    "1–3 hour": 2.0,
    "1-3 hour": 2.0,
    "1-3 hours": 2.0,
    "less than 1 hour": 1.0,
}
TASK_FREQ_MAP = {"very often": 5.0, "often": 4.0, "sometimes": 3.0, "rarely": 2.0, "never": 1.0}
EFFORT_MAP = {
    "very high effort": 5.0,
    "high effort": 4.0,
    "moderate effort": 3.0,
    "little effort": 2.0,
    "no effort": 1.0,
}
AGE_MAP = {"18-20": 1.0, "21-23": 2.0, "24-26": 3.0, "above 26": 4.0, "27 or above": 4.0}
YEAR_MAP = {
    "1st year": 1.0,
    "2nd year": 2.0,
    "3rd year": 3.0,
    "4th year": 4.0,
    "5th year": 5.0,
    "postgraduate": 6.0,
}


class CalibratedThresholdedRidgeEstimator(BaseEstimator, ClassifierMixin):
    """Ordinal continuous Ridge regressor paired with Gaussian residual calibration."""

    def __init__(self, alpha: float = 30.0, cut1: float = DEFAULT_CUT1, cut2: float = DEFAULT_CUT2):
        self.alpha = alpha
        self.cut1 = cut1
        self.cut2 = cut2
        self.residual_std = 0.585

    def fit(self, X, y, co_scores=None):
        self.reg_ = Ridge(alpha=self.alpha)
        if co_scores is None:
            pseudo_co = np.where(y == 0, 2.0, np.where(y == 1, 3.0, 4.0))
            self.reg_.fit(X, pseudo_co)
            self.residual_std = float(np.std(pseudo_co - self.reg_.predict(X))) or 0.585
        else:
            self.reg_.fit(X, co_scores)
            preds = self.reg_.predict(X)
            res_std = float(np.std(co_scores - preds))
            self.residual_std = res_std if res_std > 1e-6 else 0.585
        self.classes_ = np.array([0, 1, 2])
        return self

    def predict_proba(self, X):
        y_hat = self.reg_.predict(X)
        p0 = norm.cdf(self.cut1, loc=y_hat, scale=self.residual_std)
        p1 = norm.cdf(self.cut2, loc=y_hat, scale=self.residual_std) - p0
        p2 = 1.0 - norm.cdf(self.cut2, loc=y_hat, scale=self.residual_std)
        probs = np.clip(np.column_stack([p0, p1, p2]), 1e-6, 1.0)
        return probs / probs.sum(axis=1, keepdims=True)

    def predict(self, X):
        y_hat = self.reg_.predict(X)
        preds = np.zeros(len(y_hat), dtype=int)
        preds[(y_hat > self.cut1) & (y_hat <= self.cut2)] = 1
        preds[y_hat > self.cut2] = 2
        return preds


def _map_ordinal_series(series: pd.Series, mapping: Dict[str, float]) -> pd.Series:
    """Convert text categories or numeric ratings cleanly; coerce unknown tokens to NaN."""
    norm_dict = {k.strip().replace("\xa0", " ").lower(): v for k, v in mapping.items()}

    def _conv(val: Any) -> float:
        if val is None or pd.isna(val):
            return np.nan
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val) if np.isfinite(float(val)) else np.nan
        txt = str(val).strip().replace("\xa0", " ").lower()
        if not txt:
            return np.nan
        if txt in norm_dict:
            return norm_dict[txt]
        try:
            num = float(txt)
            return num if np.isfinite(num) else np.nan
        except ValueError:
            return np.nan

    return series.map(_conv)


def _compute_cronbach_alpha(df_items: pd.DataFrame) -> Optional[float]:
    clean = df_items.dropna()
    if len(clean) < 2 or clean.shape[1] < 2:
        return None
    k = clean.shape[1]
    item_vars = float(clean.var(axis=0, ddof=1).sum())
    total_var = float(clean.sum(axis=1).var(ddof=1))
    if total_var <= 0.0:
        return None
    return round(float((k / (k - 1)) * (1.0 - item_vars / total_var)), 4)


def load_and_prepare_raw_survey(input_path: Path, feature_order: List[str]) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
    """
    Load either a raw survey .xlsx export or pre-engineered feature CSV, validate consent
    and deduplicate rows cleanly, keeping missing feature values un-imputed until after split.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {input_path}")

    suffix = input_path.suffix.lower()
    audit: Dict[str, Any] = {"input_file": str(input_path), "format": suffix}

    if suffix == ".csv":
        df = pd.read_csv(input_path)
        audit["n_raw_rows"] = int(len(df))
        # Deduplicate rows deterministically if duplicated
        n_before_dup = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        audit["n_duplicates_removed"] = int(n_before_dup - len(df))

        missing_cols = [c for c in feature_order + ["co_score"] if c not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV input missing required columns: {missing_cols[:5]}")
        co_scores = pd.to_numeric(df["co_score"], errors="coerce")
        valid_target = co_scores.notna() & (co_scores >= 1.0) & (co_scores <= 5.0)
        audit["n_invalid_target_removed"] = int((~valid_target).sum())
        df = df.loc[valid_target].reset_index(drop=True)
        co_scores = co_scores.loc[valid_target].reset_index(drop=True)
        return df[feature_order].copy(), co_scores.astype(float), audit

    if suffix in {".xlsx", ".xls"}:
        df_raw = pd.read_excel(input_path)
        audit["n_raw_rows"] = int(len(df_raw))
        if df_raw.shape[1] < 55:
            raise ValueError(
                f"Expected raw survey Excel export with >=55 columns; found {df_raw.shape[1]}."
            )

        # 1. Consent screening
        consent_col = df_raw.columns[4]
        df = df_raw[df_raw[consent_col].astype(str).str.strip() == "I agree to participate"].copy()
        audit["n_non_consenting_removed"] = int(len(df_raw) - len(df))

        # 2. Deduplicate respondent IDs (email/student-id columns) and identical response vectors before dropping PII
        id_cols = [
            c
            for c in df.columns[:4]
            if any(term in str(c).lower() for term in ("email", "student", "id", "reg"))
        ]
        n_before_dup = len(df)
        if id_cols:
            df = df.drop_duplicates(subset=[id_cols[0]], keep="first")
        df = df.drop_duplicates(subset=list(df.columns[5:55]), keep="first").reset_index(drop=True)
        audit["n_duplicates_removed"] = int(n_before_dup - len(df))

        # 3. Extract Section E targets (Cols 21-26) strictly
        df_target = pd.DataFrame(index=df.index)
        for col_raw, target_name in zip([df.columns[i] for i in range(21, 27)], SECTION_E_ITEMS):
            df_target[target_name] = _map_ordinal_series(df[col_raw], AGREE_MAP)
        valid_target = df_target.notna().all(axis=1)
        audit["n_incomplete_target_removed"] = int((~valid_target).sum())
        df = df.loc[valid_target].reset_index(drop=True)
        df_target = df_target.loc[valid_target].reset_index(drop=True)

        co_scores = df_target.mean(axis=1).astype(float)
        audit["section_e_cronbach_alpha"] = _compute_cronbach_alpha(df_target)

        # 4. Prune PII (Cols 0-4), Section E targets (21-26), and Section G dependence (45-49)
        col_rename = {
            df.columns[5]: "age_group",
            df.columns[6]: "degree_field",
            df.columns[7]: "academic_year",
            df.columns[8]: "ai_usage_freq",
            df.columns[9]: "ai_tools_used",
            df.columns[10]: "ai_purposes",
            df.columns[11]: "ai_time_per_week",
            df.columns[12]: "Q1_direct_use_freq",
            df.columns[13]: "Q2_verify_info",
            df.columns[14]: "Q3_compare_sources",
            df.columns[15]: "Q4_check_accuracy",
            df.columns[16]: "Q5_understand_reasoning",
            df.columns[17]: "Q6_modify_content",
            df.columns[18]: "Q7_attempt_independently",
            df.columns[19]: "Q8_complete_without_ai",
            df.columns[20]: "Q9_learning_assistant",
            df.columns[27]: "Q16_ai_improves_learning",
            df.columns[28]: "Q17_ai_confidence",
            df.columns[29]: "Q18_ai_efficiency",
            df.columns[30]: "Q19_negative_affect_warning",
            df.columns[31]: "Q20_task_delegation_freq",
            df.columns[32]: "tasks_delegated_types",
            df.columns[33]: "Q22_effort_on_ai_answers",
            df.columns[34]: "Q23_pu_improves_understanding",
            df.columns[35]: "Q24_pu_complete_effectively",
            df.columns[36]: "Q25_pu_productivity",
            df.columns[37]: "Q26_pu_useful_for_goals",
            df.columns[38]: "Q27_pu_learn_difficult_topics",
            df.columns[39]: "Q28_trust_reliable_info",
            df.columns[40]: "Q29_trust_consistent",
            df.columns[41]: "Q30_trust_accuracy",
            df.columns[42]: "Q31_trust_explanations",
            df.columns[43]: "Q32_trust_clear_explanations",
            df.columns[44]: "Q33_trust_appropriate_support",
            df.columns[50]: "Q39_feel_capable",
            df.columns[51]: "Q40_feel_confident",
            df.columns[52]: "Q41_more_capable_after",
            df.columns[53]: "Q42_more_confident_after",
            df.columns[54]: "Q43_approach_challenging",
        }
        df_feat_raw = df.rename(columns=col_rename)

        df_x = pd.DataFrame(index=df.index)
        df_x["age_group"] = _map_ordinal_series(df_feat_raw["age_group"], AGE_MAP)
        df_x["academic_year"] = _map_ordinal_series(df_feat_raw["academic_year"], YEAR_MAP)
        df_x["ai_usage_freq"] = _map_ordinal_series(df_feat_raw["ai_usage_freq"], USAGE_FREQ_MAP)
        df_x["ai_time_per_week"] = _map_ordinal_series(df_feat_raw["ai_time_per_week"], TIME_MAP)
        df_x["Q1_direct_use_freq"] = _map_ordinal_series(df_feat_raw["Q1_direct_use_freq"], FREQ_MAP)
        df_x["Q20_task_delegation_freq"] = _map_ordinal_series(df_feat_raw["Q20_task_delegation_freq"], TASK_FREQ_MAP)
        df_x["Q22_effort_on_ai_answers"] = _map_ordinal_series(df_feat_raw["Q22_effort_on_ai_answers"], EFFORT_MAP)

        agree_cols = [c for c in feature_order if c.startswith("Q") and c not in {
            "Q1_direct_use_freq", "Q20_task_delegation_freq", "Q22_effort_on_ai_answers"
        }]
        for c in agree_cols:
            df_x[c] = _map_ordinal_series(df_feat_raw[c], AGREE_MAP)

        # Intra-row composites (skipna=True preserves row completeness without cross-row leakage)
        df_x["composite_verification"] = df_x[
            ["Q2_verify_info", "Q3_compare_sources", "Q4_check_accuracy", "Q5_understand_reasoning", "Q6_modify_content"]
        ].mean(axis=1)
        df_x["composite_autonomy"] = df_x[
            ["Q7_attempt_independently", "Q8_complete_without_ai", "Q9_learning_assistant"]
        ].mean(axis=1)
        df_x["composite_trust"] = df_x[
            ["Q28_trust_reliable_info", "Q29_trust_consistent", "Q30_trust_accuracy",
             "Q31_trust_explanations", "Q32_trust_clear_explanations", "Q33_trust_appropriate_support"]
        ].mean(axis=1)
        df_x["composite_tam"] = df_x[
            ["Q23_pu_improves_understanding", "Q24_pu_complete_effectively", "Q25_pu_productivity",
             "Q26_pu_useful_for_goals", "Q27_pu_learn_difficult_topics"]
        ].mean(axis=1)
        df_x["composite_self_efficacy"] = df_x[
            ["Q39_feel_capable", "Q40_feel_confident", "Q41_more_capable_after",
             "Q42_more_confident_after", "Q43_approach_challenging"]
        ].mean(axis=1)

        df_x["idx_automation_bias"] = df_x["composite_trust"] - df_x["composite_verification"]
        df_x["idx_delegation_intensity"] = df_x["ai_usage_freq"] * df_x["Q20_task_delegation_freq"]
        df_x["idx_passive_adoption"] = df_x["Q1_direct_use_freq"] * (6.0 - df_x["Q22_effort_on_ai_answers"])

        df_x["count_tools_used"] = df_feat_raw["ai_tools_used"].fillna("").apply(
            lambda x: len([p for p in str(x).split(";") if p.strip()])
        )
        df_x["count_tasks_delegated"] = df_feat_raw["tasks_delegated_types"].fillna("").apply(
            lambda x: len([p for p in str(x).split(";") if p.strip()])
        )
        df_x["count_purposes"] = df_feat_raw["ai_purposes"].fillna("").apply(
            lambda x: len([p for p in str(x).split(";") if p.strip()])
        )

        fac_series = df_feat_raw["degree_field"].apply(classify_meta_faculty)
        for fac in [
            "Business_Economics", "Computing_IT", "Engineering",
            "Humanities_Health_Other", "Natural_Applied_Sciences",
        ]:
            df_x[f"faculty_{fac}"] = (fac_series == fac).astype(float)

        for prefix, col_src, keywords in [
            ("tool", "ai_tools_used", ["ChatGPT", "Google Gemini", "Microsoft Copilot", "Claude", "Perplexity"]),
            ("purpose", "ai_purposes", ["Understanding concepts", "Assignment preparation", "Exam preparation", "Writing improvement", "Summarising content", "Generating ideas"]),
            ("delegate", "tasks_delegated_types", ["Writing assignments", "Explaining concepts", "Summarising materials", "Creating presentations", "Programming problems", "Mathematical problems"]),
        ]:
            src = df_feat_raw[col_src].fillna("").str.lower()
            for kw in keywords:
                safe_kw = kw.lower().replace(" ", "_").replace("/", "_").replace("&", "and")
                df_x[f"{prefix}_{safe_kw}"] = src.str.contains(kw.lower(), regex=False).astype(float)

        return df_x[feature_order].copy(), co_scores, audit

    raise ValueError(f"Unsupported dataset format: {suffix}. Use .xlsx or .csv.")


def _discretize(scores: np.ndarray, cut1: float, cut2: float) -> np.ndarray:
    return np.where(scores <= cut1, 0, np.where(scores <= cut2, 1, 2)).astype(int)


def run_final_training_workflow(
    input_path: Path,
    output_dir: Path,
    version_tag: str = "final_candidate",
    test_size: float = 0.20,
    random_state: int = 42,
    thresholds_mode: str = "preserve-v4",
    baseline_meta_path: Optional[Path] = None,
    min_samples: int = 30,
) -> Dict[str, Any]:
    """
    Execute complete zero-leakage final training workflow on an arbitrary valid cohort size N.
    Never modifies active production Version 4 files unless explicitly written to output_dir.
    """
    v4_meta_path = baseline_meta_path or (REPO_ROOT / "models" / "pipeline_metadata_v4.json")
    v4_meta = json.loads(v4_meta_path.read_text(encoding="utf-8"))
    feature_order: List[str] = v4_meta["feature_names"]

    X_raw, co_scores, prep_audit = load_and_prepare_raw_survey(input_path, feature_order)
    if len(X_raw) < min_samples:
        raise ValueError(
            f"Dataset contains {len(X_raw)} valid records, below min_samples={min_samples}."
        )
    if not (0.05 <= test_size <= 0.45):
        raise ValueError(f"test_size must be a proportion between 0.05 and 0.45; got {test_size}.")

    # Stratify cleanly via rank-based tertile bins prior to exact threshold selection
    strat_bins = pd.qcut(co_scores.rank(method="first"), q=3, labels=[0, 1, 2]).astype(int).values
    X_train_raw, X_test_raw, co_train, co_test = train_test_split(
        X_raw,
        co_scores.values,
        test_size=test_size,
        stratify=strat_bins,
        random_state=random_state,
    )

    # Determine cutoffs strictly without touching test data
    if thresholds_mode == "preserve-v4":
        cut1, cut2 = DEFAULT_CUT1, DEFAULT_CUT2
        threshold_note = "Preserved V4 baseline thresholds (2.667, 3.500) for direct comparability."
    elif thresholds_mode == "training-tertiles":
        q1, q2 = np.quantile(co_train, [1.0 / 3.0, 2.0 / 3.0])
        cut1, cut2 = round(float(q1), 3), round(float(q2), 3)
        threshold_note = (
            f"Recalculated strictly from training co_score tertiles ({cut1}, {cut2}); "
            "direct class-rate comparability against historical V4 (2.667, 3.500) shifts accordingly."
        )
    else:
        raise ValueError("thresholds_mode must be 'preserve-v4' or 'training-tertiles'.")

    y_train = _discretize(co_train, cut1, cut2)
    y_test = _discretize(co_test, cut1, cut2)

    # Compute training-only imputation medians & background means
    train_medians = X_train_raw.median().fillna(3.0).to_dict()
    train_means = X_train_raw.mean().fillna(3.0).to_dict()
    X_train_imp = X_train_raw.fillna(train_medians)
    X_test_imp = X_test_raw.fillna(train_medians)

    # Candidate evaluation strictly inside X_train via 5x5 Repeated Stratified CV
    n_splits = min(5, max(2, int(np.min(np.bincount(y_train)))))
    rskf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=5, random_state=random_state)

    candidates = {
        "Baseline (Majority)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression (L2)": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=0.1, max_iter=1000, random_state=random_state)),
        ]),
        "SVM (RBF Kernel)": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", SVC(C=1.0, kernel="rbf", probability=True, random_state=random_state)),
        ]),
        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("clf", RandomForestClassifier(n_estimators=150, max_depth=5, min_samples_leaf=3, random_state=random_state)),
        ]),
        "Extra Trees": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("clf", ExtraTreesClassifier(n_estimators=150, max_depth=6, min_samples_leaf=2, random_state=random_state)),
        ]),
        "HistGradientBoosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("clf", HistGradientBoostingClassifier(max_iter=80, max_depth=3, learning_rate=0.03, random_state=random_state)),
        ]),
        "Thresholded Ridge (Ordinal)": CalibratedThresholdedRidgeEstimator(
            alpha=30.0, cut1=cut1, cut2=cut2
        ),
    }

    cv_summary = []
    for name, est in candidates.items():
        accs, f1s, med_recs, lls = [], [], [], []
        for tr_i, va_i in rskf.split(X_train_raw, y_train):
            X_tr_f, X_va_f = X_train_raw.iloc[tr_i], X_train_raw.iloc[va_i]
            y_tr_f, y_va_f = y_train[tr_i], y_train[va_i]
            co_tr_f = co_train[tr_i]
            if isinstance(est, CalibratedThresholdedRidgeEstimator):
                med_fold = X_tr_f.median().fillna(3.0).to_dict()
                m = clone(est).fit(X_tr_f.fillna(med_fold), y_tr_f, co_scores=co_tr_f)
                preds = m.predict(X_va_f.fillna(med_fold))
                probs = m.predict_proba(X_va_f.fillna(med_fold))
            else:
                m = clone(est).fit(X_tr_f, y_tr_f)
                preds = m.predict(X_va_f)
                probs = m.predict_proba(X_va_f)
            accs.append(accuracy_score(y_va_f, preds))
            f1s.append(f1_score(y_va_f, preds, average="macro", zero_division=0))
            rec_vec = precision_recall_fscore_support(y_va_f, preds, labels=[0, 1, 2], zero_division=0)[1]
            med_recs.append(rec_vec[1])
            lls.append(log_loss(y_va_f, probs, labels=[0, 1, 2]))
        cv_summary.append({
            "model": name,
            "cv_accuracy_mean": round(float(np.mean(accs)), 4),
            "cv_macro_f1_mean": round(float(np.mean(f1s)), 4),
            "cv_medium_recall_mean": round(float(np.mean(med_recs)), 4),
            "cv_log_loss_mean": round(float(np.mean(lls)), 4),
        })

    # Fit deployed Thresholded Ridge architecture strictly on X_train_imp
    final_ridge = CalibratedThresholdedRidgeEstimator(alpha=30.0, cut1=cut1, cut2=cut2)
    final_ridge.fit(X_train_imp, y_train, co_scores=co_train)
    continuous_reg = final_ridge.reg_

    # Untouched Holdout Evaluation: Full Features
    raw_test = final_ridge.reg_.predict(X_test_imp)
    y_pred_test = final_ridge.predict(X_test_imp)
    prob_test = final_ridge.predict_proba(X_test_imp)

    r2_val = float(r2_score(co_test, raw_test))
    rmse_val = float(np.sqrt(mean_squared_error(co_test, raw_test)))
    mae_val = float(mean_absolute_error(co_test, raw_test))
    prec, rec, f1c, sup = precision_recall_fscore_support(y_test, y_pred_test, labels=[0, 1, 2], zero_division=0)

    try:
        roc_auc_val = round(float(roc_auc_score(y_test, prob_test, multi_class="ovr", average="macro")), 4)
    except ValueError:
        roc_auc_val = None

    full_holdout_metrics = {
        "n_test": int(len(X_test_imp)),
        "accuracy": round(float(accuracy_score(y_test, y_pred_test)), 4),
        "macro_f1": round(float(f1_score(y_test, y_pred_test, labels=[0, 1, 2], average="macro", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(y_test, y_pred_test, labels=[0, 1, 2], average="weighted", zero_division=0)), 4),
        "high_risk_recall": round(float(rec[2]), 4),
        "medium_risk_recall": round(float(rec[1]), 4),
        "log_loss": round(float(log_loss(y_test, prob_test, labels=[0, 1, 2])), 4),
        "roc_auc_ovr_macro": roc_auc_val,
        "continuous_r2": round(r2_val, 4),
        "continuous_rmse": round(rmse_val, 4),
        "continuous_mae": round(mae_val, 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred_test, labels=[0, 1, 2]).tolist(),
    }

    # Export drop-in artifacts safely in isolated output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    ridge_path = output_dir / f"thresholded_ridge_{version_tag}.joblib"
    cont_path = output_dir / f"continuous_regressor_{version_tag}.joblib"
    meta_path = output_dir / f"pipeline_metadata_{version_tag}.json"

    joblib.dump(
        {
            "model_type": "Calibrated Thresholded Ridge Regressor (Ordinal)",
            "estimator": continuous_reg,
            "alpha": 30.0,
            "cut1": cut1,
            "cut2": cut2,
            "residual_std": final_ridge.residual_std,
            "feature_names": feature_order,
            "target_mapping": TARGET_MAPPING,
            "version_tag": version_tag,
        },
        ridge_path,
    )
    joblib.dump(continuous_reg, cont_path)

    ridge_cv_row = next(r for r in cv_summary if r["model"] == "Thresholded Ridge (Ordinal)")
    new_meta = {
        "project": v4_meta.get("project", "Explainable Cognitive Offloading Risk Model — J26-DS-310"),
        "pipeline_version": version_tag,
        "data_collection_status": "completed",
        "is_preliminary": False,
        "n_samples_total": int(len(X_raw)),
        "n_samples_train": int(len(X_train_raw)),
        "n_samples_test": int(len(X_test_raw)),
        "n_features": len(feature_order),
        "champion_model": "Calibrated Thresholded Ridge Regressor (Ordinal)",
        "selection_protocol": f"Train-Only {n_splits}x5 Repeated Stratified CV (N={len(X_train_raw)})",
        "training_cv_accuracy_mean": ridge_cv_row["cv_accuracy_mean"],
        "training_cv_macro_f1_mean": ridge_cv_row["cv_macro_f1_mean"],
        "training_cv_medium_recall": ridge_cv_row["cv_medium_recall_mean"],
        "training_cv_log_loss": ridge_cv_row["cv_log_loss_mean"],
        "untouched_test_accuracy": full_holdout_metrics["accuracy"],
        "untouched_test_macro_f1": full_holdout_metrics["macro_f1"],
        "untouched_test_high_recall": full_holdout_metrics["high_risk_recall"],
        "untouched_test_log_loss": full_holdout_metrics["log_loss"],
        "continuous_r2": full_holdout_metrics["continuous_r2"],
        "continuous_rmse": full_holdout_metrics["continuous_rmse"],
        "residual_std": round(float(final_ridge.residual_std), 6),
        "thresholds_note": threshold_note,
        "feature_names": feature_order,
        "target_mapping": TARGET_MAPPING,
        "tertile_thresholds": {
            "low": f"<= {cut1}",
            "medium": f"{cut1} < score <= {cut2}",
            "high": f"> {cut2}",
        },
        "reference_medians": {k: float(v) for k, v in train_medians.items()},
        "reference_means": {k: float(v) for k, v in train_means.items()},
    }
    meta_path.write_text(json.dumps(new_meta, indent=2) + "\n", encoding="utf-8")

    # Stage 8: Evaluate actual 20-input UI production workflow using isolated service instance
    from app.services.cognitive_offloading.integration_service import Component1IntegrationServiceV4

    ui_service = Component1IntegrationServiceV4.from_paths(
        model_file=ridge_path,
        meta_file=meta_path,
        continuous_file=cont_path,
        data_file=None,
    )
    ui_preds, ui_raw_scores = [], []
    for _, row in X_test_imp.iterrows():
        payload = row_to_ui_payload(row)
        out = ui_service.predict(payload, top_factors_count=5)
        ui_preds.append(TARGET_MAPPING[out["predicted_category"]])
        ui_raw_scores.append(float(out["raw_regression_score"]))

    y_pred_ui = np.asarray(ui_preds, dtype=int)
    ui_prec, ui_rec, _, _ = precision_recall_fscore_support(
        y_test, y_pred_ui, labels=[0, 1, 2], zero_division=0
    )
    ui_holdout_metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred_ui)), 4),
        "macro_f1": round(float(f1_score(y_test, y_pred_ui, labels=[0, 1, 2], average="macro", zero_division=0)), 4),
        "high_risk_recall": round(float(ui_rec[2]), 4),
        "medium_risk_recall": round(float(ui_rec[1]), 4),
        "agreement_vs_full_features": round(float(np.mean(y_pred_ui == y_pred_test)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred_ui, labels=[0, 1, 2]).tolist(),
    }

    comparison_vs_v4 = {
        "v4_preliminary_reference": {
            "n_total": int(v4_meta.get("n_samples_total", 375)),
            "train_cv_full68_macro_f1": 0.5419,
            "historical_exposed_holdout_accuracy": float(v4_meta.get("historical_exposed_test_accuracy", 0.5733)),
            "historical_exposed_holdout_macro_f1": float(v4_meta.get("historical_exposed_test_macro_f1", 0.5815)),
        },
        "new_candidate": {
            "version_tag": version_tag,
            "n_total": int(len(X_raw)),
            "train_cv_full68_macro_f1": ridge_cv_row["cv_macro_f1_mean"],
            "untouched_test_full_accuracy": full_holdout_metrics["accuracy"],
            "untouched_test_full_macro_f1": full_holdout_metrics["macro_f1"],
            "untouched_test_ui20_accuracy": ui_holdout_metrics["accuracy"],
            "untouched_test_ui20_macro_f1": ui_holdout_metrics["macro_f1"],
        },
    }

    summary = {
        "preprocessing_audit": prep_audit,
        "thresholds": {"cut1": cut1, "cut2": cut2, "mode": thresholds_mode, "note": threshold_note},
        "train_only_cv_benchmark": cv_summary,
        "untouched_test_full_metrics": full_holdout_metrics,
        "untouched_test_ui20_metrics": ui_holdout_metrics,
        "comparison_vs_v4_baseline": comparison_vs_v4,
        "generated_artifacts": {
            "thresholded_ridge": str(ridge_path),
            "continuous_regressor": str(cont_path),
            "metadata": str(meta_path),
        },
    }
    report_path = output_dir / f"training_summary_{version_tag}.json"
    report_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    summary["generated_artifacts"]["summary_report"] = str(report_path)
    return summary


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run leakage-free final Component 1 training pipeline on completed survey dataset."
    )
    parser.add_argument("--input", type=Path, required=True, help="Completed survey export (.xlsx or .csv).")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=COMPONENT1_DIR / "artifacts_candidate",
        help="Output folder for candidate artifacts (keeps active models/ V4 untouched until promotion).",
    )
    parser.add_argument("--version-tag", default="final_v5", help="Version tag for generated artifacts.")
    parser.add_argument("--test-size", type=float, default=0.20, help="Proportional test split fraction.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for reproducible splitting.")
    parser.add_argument(
        "--thresholds-mode",
        choices=["preserve-v4", "training-tertiles"],
        default="preserve-v4",
        help="Risk boundary mode (preserve V4 bounds or recompute strictly on training data).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    summary = run_final_training_workflow(
        input_path=args.input,
        output_dir=args.output_dir,
        version_tag=args.version_tag,
        test_size=args.test_size,
        random_state=args.random_state,
        thresholds_mode=args.thresholds_mode,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
