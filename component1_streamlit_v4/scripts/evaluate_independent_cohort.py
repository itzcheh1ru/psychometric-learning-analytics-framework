"""
evaluate_independent_cohort.py
==============================
Standalone, leakage-guarded cohort validation utility for Component 1 (Version 4):
Explainable Cognitive Offloading Risk Prediction Model (J26-DS-310).

Evaluates deployed 20-input predictions against separately collected reference
Section E items (Q10_rely_memory .. Q15_reduces_thinking) from an independent
de-identified student sample WITHOUT retraining or modifying model artifacts.

Usage:
    .venv/bin/python component1_streamlit_v4/scripts/evaluate_independent_cohort.py \
        --input /path/to/anonymized_cohort.csv \
        --out-json /tmp/independent_validation_summary.json
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_fscore_support,
)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.cognitive_offloading.integration_service import (  # noqa: E402
    get_predictor_v4,
)

TARGET_MAP = {"Low": 0, "Medium": 1, "High": 2}
CLASS_NAMES = ["Low", "Medium", "High"]

UI_PREDICTOR_KEYS: List[str] = [
    "degree_field",
    "academic_year",
    "age_group",
    "ai_usage_freq",
    "ai_time_per_week",
    "tools_used",
    "Q20_task_delegation_freq",
    "tasks_delegated",
    "Q1_direct_use_freq",
    "Q22_effort_on_ai_answers",
    "Q2_verify_info",
    "Q3_compare_sources",
    "Q4_check_accuracy",
    "Q5_understand_reasoning",
    "Q6_modify_content",
    "Q7_attempt_independently",
    "Q8_complete_without_ai",
    "Q9_learning_assistant",
    "Q30_trust_accuracy",
    "Q33_trust_appropriate_support",
]

SECTION_E_REFERENCE_KEYS: List[str] = [
    "Q10_rely_memory",
    "Q11_avoid_mental_effort",
    "Q12_accept_without_understanding",
    "Q13_less_problem_solving",
    "Q14_depend_on_ai",
    "Q15_reduces_thinking",
]

ALLOWED_COLUMNS = {"study_id", *UI_PREDICTOR_KEYS, *SECTION_E_REFERENCE_KEYS}

VALID_DEGREE_FIELDS = {
    "Computing_IT",
    "Engineering",
    "Business_Economics",
    "Natural_Applied_Sciences",
    "Humanities_Health_Other",
}

VALID_TOOLS = {
    "ChatGPT",
    "Google Gemini",
    "Microsoft Copilot",
    "Claude",
    "Perplexity AI",
}

VALID_TASKS = {
    "Writing assignments",
    "Explaining concepts",
    "Summarising materials",
    "Creating presentations",
    "Programming problems",
    "Mathematical problems",
}

NUMERIC_UI_BOUNDS: Dict[str, Tuple[int, int]] = {
    "academic_year": (1, 6),
    "age_group": (1, 4),
    "ai_usage_freq": (1, 4),
    "ai_time_per_week": (1, 5),
    "Q20_task_delegation_freq": (1, 5),
    "Q1_direct_use_freq": (1, 5),
    "Q22_effort_on_ai_answers": (1, 5),
    "Q2_verify_info": (1, 5),
    "Q3_compare_sources": (1, 5),
    "Q4_check_accuracy": (1, 5),
    "Q5_understand_reasoning": (1, 5),
    "Q6_modify_content": (1, 5),
    "Q7_attempt_independently": (1, 5),
    "Q8_complete_without_ai": (1, 5),
    "Q9_learning_assistant": (1, 5),
    "Q30_trust_accuracy": (1, 5),
    "Q33_trust_appropriate_support": (1, 5),
}

FORBIDDEN_PII_TERMS = {
    "name",
    "full_name",
    "first_name",
    "last_name",
    "email",
    "student_id",
    "registration_no",
    "phone",
    "contact",
    "ip_address",
}

FORBIDDEN_LEAKAGE_COLUMNS = {
    "co_score",
    "co_risk",
    "q34_depend_study",
    "q35_hard_without_ai",
    "q36_rely_grades",
    "q37_important_part",
    "q38_feel_anxious",
}


def parse_multi_value(value: Any) -> List[str]:
    """Normalize semicolon/pipe/comma-separated strings or lists from CSV/JSON inputs."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "[]"}:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if str(v).strip()]
        except json.JSONDecodeError:
            pass
    sep = ";" if ";" in text else "|" if "|" in text else ","
    return [part.strip() for part in text.split(sep) if part.strip()]


def assign_reference_risk(co_score: float, cut1: float, cut2: float) -> str:
    """Apply approved Version 4 tertile thresholds to the reference co_score."""
    if co_score <= cut1:
        return "Low"
    if co_score <= cut2:
        return "Medium"
    return "High"


def compute_cronbach_alpha(items_df: pd.DataFrame) -> Optional[float]:
    """Compute Cronbach's alpha for the 6 reference Section E Likert items."""
    clean = items_df.dropna()
    if len(clean) < 2 or clean.shape[1] < 2:
        return None
    k = clean.shape[1]
    item_vars = float(clean.var(axis=0, ddof=1).sum())
    total_var = float(clean.sum(axis=1).var(ddof=1))
    if total_var <= 0.0:
        return None
    alpha = (k / (k - 1)) * (1.0 - item_vars / total_var)
    return round(float(alpha), 4)


def load_cohort_records(input_path: Path) -> pd.DataFrame:
    """Load an external anonymized cohort CSV or JSON records file."""
    if not input_path.exists():
        raise FileNotFoundError(f"Cohort file not found: {input_path}")
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(input_path)
    if suffix == ".json":
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "records" in payload:
            payload = payload["records"]
        if not isinstance(payload, list):
            raise ValueError("JSON cohort file must be a list of objects or {'records': [...]}.")
        return pd.DataFrame(payload)
    raise ValueError(f"Unsupported cohort file format: {suffix}. Use .csv or .json.")


def _validate_integer_range(
    df: pd.DataFrame, col: str, low: int, high: int, allow_missing: bool
) -> int:
    """Validate finite integer responses within [low, high]; return missing count."""
    missing_cnt = 0
    for idx, raw in df[col].items():
        if raw is None or (isinstance(raw, float) and math.isnan(raw)) or (
            isinstance(raw, str) and not raw.strip()
        ):
            if not allow_missing:
                raise ValueError(f"Missing required reference value in '{col}' (row index {idx}).")
            missing_cnt += 1
            continue
        if isinstance(raw, bool):
            raise ValueError(f"Invalid boolean value in numeric column '{col}' (row index {idx}).")
        try:
            num = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Non-numeric value {raw!r} in Likert/ordinal column '{col}' (row index {idx})."
            ) from exc
        if not math.isfinite(num) or not num.is_integer() or num < low or num > high:
            raise ValueError(
                f"Invalid ordinal/Likert value {raw!r} in '{col}' (row index {idx}); expected integer in [{low}, {high}]."
            )
    return missing_cnt


def validate_cohort_schema(df: pd.DataFrame, predictor_features: List[str]) -> Tuple[int, List[str]]:
    """
    Validate cohort records fail-closed:
      - Reject direct PII fields, email-like IDs, and duplicate study_id values.
      - Verify zero leakage of Section E or ground-truth columns inside predictor schema.
      - Reject unexpected columns and missing required predictor/reference columns.
      - Reject invalid ordinal/Likert numbers and unrecognized categorical encodings.
    """
    if len(df) == 0:
        raise ValueError("Cohort dataset contains zero rows.")

    lower_cols = {str(c).lower().strip(): str(c) for c in df.columns}
    present_pii = [
        orig
        for norm, orig in lower_cols.items()
        if norm in FORBIDDEN_PII_TERMS or any(term in norm for term in ("email", "phone", "student_id"))
    ]
    if present_pii:
        raise ValueError(
            f"Privacy check failed: remove direct PII columns before evaluation: {present_pii}"
        )

    present_leakage = [
        orig for norm, orig in lower_cols.items() if norm in FORBIDDEN_LEAKAGE_COLUMNS
    ]
    if present_leakage:
        raise ValueError(
            f"Leakage protection triggered: forbidden outcome/dependence columns present: {present_leakage}"
        )

    for target_col in SECTION_E_REFERENCE_KEYS + ["co_score", "co_risk"]:
        if target_col in predictor_features:
            raise AssertionError(f"Target leakage detected inside predictor features: {target_col}")

    required = ["study_id"] + UI_PREDICTOR_KEYS + SECTION_E_REFERENCE_KEYS
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Cohort file missing required columns: {missing}")

    unexpected = [str(col) for col in df.columns if col not in ALLOWED_COLUMNS]
    if unexpected:
        raise ValueError(
            f"Unexpected columns detected (remove extra fields or fix typos): {unexpected}"
        )

    if df["study_id"].isna().any():
        raise ValueError("All rows must contain a non-empty anonymous study_id.")

    normalized_ids: List[str] = []
    for idx, sid in df["study_id"].items():
        clean_id = str(sid).strip()
        if not clean_id or clean_id.lower() in {"nan", "none"}:
            raise ValueError(f"Empty study_id at row index {idx}.")
        if "@" in clean_id or re.search(r"\bit\d{6,}\b", clean_id.lower()):
            raise ValueError(
                f"Privacy check failed: study_id {clean_id!r} appears to contain an email or university student ID."
            )
        normalized_ids.append(clean_id)

    if len(set(normalized_ids)) != len(normalized_ids):
        seen = set()
        dups = sorted({s for s in normalized_ids if s in seen or seen.add(s)})
        raise ValueError(f"Duplicate participant identifiers (study_id) detected: {dups}")

    # Validate categorical encodings strictly
    for idx, deg in df["degree_field"].items():
        if pd.isna(deg) or str(deg).strip() not in VALID_DEGREE_FIELDS:
            raise ValueError(
                f"Invalid degree_field {deg!r} at row {idx}; expected one of {sorted(VALID_DEGREE_FIELDS)}."
            )

    for idx, raw_tools in df["tools_used"].items():
        parsed = parse_multi_value(raw_tools)
        invalid_tools = [item for item in parsed if item not in VALID_TOOLS]
        if invalid_tools:
            raise ValueError(
                f"Invalid tools_used entries {invalid_tools} at row {idx}; expected subset of {sorted(VALID_TOOLS)}."
            )

    for idx, raw_tasks in df["tasks_delegated"].items():
        parsed = parse_multi_value(raw_tasks)
        invalid_tasks = [item for item in parsed if item not in VALID_TASKS]
        if invalid_tasks:
            raise ValueError(
                f"Invalid tasks_delegated entries {invalid_tasks} at row {idx}; expected subset of {sorted(VALID_TASKS)}."
            )

    # Validate ordinal/Likert ranges for UI predictors (allow occasional missing -> median imputed with warning)
    warnings: List[str] = []
    missing_ui_cells = 0
    for col, (lo, hi) in NUMERIC_UI_BOUNDS.items():
        missing_ui_cells += _validate_integer_range(df, col, lo, hi, allow_missing=True)
    if missing_ui_cells > 0:
        warnings.append(
            f"Detected {missing_ui_cells} missing numeric UI responses across cohort (handled via reference medians)."
        )

    # Validate Section E reference values (allow incomplete rows to be explicitly excluded unless all invalid)
    missing_ref = 0
    for ref_col in SECTION_E_REFERENCE_KEYS:
        missing_ref += _validate_integer_range(df, ref_col, 1, 5, allow_missing=True)
    return missing_ref, warnings


def evaluate_cohort_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluate an independent anonymized cohort using deployed Component 1 V4 inference.
    Models, thresholds, medians, and weights remain strictly unmodified.
    """
    predictor = get_predictor_v4()
    missing_ref_cells, validation_warnings = validate_cohort_schema(df, predictor.feature_names)

    # Filter to rows with complete reference Section E items (Q10-Q15)
    ref_df = df[SECTION_E_REFERENCE_KEYS].apply(pd.to_numeric, errors="coerce")
    valid_mask = ref_df.notna().all(axis=1)
    dropped_rows = int((~valid_mask).sum())
    if dropped_rows > 0:
        validation_warnings.append(
            f"Excluded {dropped_rows} rows with incomplete reference items (Q10-Q15)."
        )

    eval_df = df.loc[valid_mask].copy()
    eval_ref = ref_df.loc[valid_mask].copy()
    if len(eval_df) == 0:
        raise ValueError("No rows have complete Section E reference items (Q10-Q15).")

    co_true = eval_ref.mean(axis=1).values.astype(float)
    y_true = np.array(
        [TARGET_MAP[assign_reference_risk(s, predictor.cut1, predictor.cut2)] for s in co_true],
        dtype=int,
    )

    y_pred: List[int] = []
    raw_pred: List[float] = []
    probs_list: List[List[float]] = []
    shap_driver_counts: Dict[str, int] = {}
    warning_rows = 0

    for _, row in eval_df.iterrows():
        payload: Dict[str, Any] = {}
        for key in UI_PREDICTOR_KEYS:
            val = row[key]
            if key in {"tools_used", "tasks_delegated"}:
                payload[key] = parse_multi_value(val)
            elif key == "degree_field":
                payload[key] = str(val).strip()
            else:
                payload[key] = (
                    np.nan
                    if pd.isna(val) or (isinstance(val, str) and not val.strip())
                    else int(float(val))
                )

        res = predictor.predict(payload, top_factors_count=5)
        if res.get("status") != "success":
            raise ValueError(f"Inference failed for study_id={row['study_id']}: {res.get('message')}")
        if res.get("warnings_count", 0) > 0:
            warning_rows += 1

        y_pred.append(TARGET_MAP[res["predicted_category"]])
        raw_pred.append(float(res["raw_regression_score"]))
        probs_list.append(
            [
                float(res["probabilities"]["low"]),
                float(res["probabilities"]["medium"]),
                float(res["probabilities"]["high"]),
            ]
        )
        for factor in res.get("top_contributing_factors", []):
            fname = factor["feature_name"]
            shap_driver_counts[fname] = shap_driver_counts.get(fname, 0) + 1

    y_pred_arr = np.asarray(y_pred, dtype=int)
    raw_pred_arr = np.asarray(raw_pred, dtype=float)
    probs_arr = np.asarray(probs_list, dtype=float)

    prec, rec, f1_c, sup = precision_recall_fscore_support(
        y_true, y_pred_arr, labels=[0, 1, 2], zero_division=0
    )
    macro_f1 = float(f1_score(y_true, y_pred_arr, labels=[0, 1, 2], average="macro", zero_division=0))
    weighted_f1 = float(
        f1_score(y_true, y_pred_arr, labels=[0, 1, 2], average="weighted", zero_division=0)
    )
    acc = float(accuracy_score(y_true, y_pred_arr))
    ll = float(log_loss(y_true, probs_arr, labels=[0, 1, 2]))
    rmse = float(np.sqrt(np.mean((co_true - raw_pred_arr) ** 2)))
    mae = float(np.mean(np.abs(co_true - raw_pred_arr)))
    pearson_r = (
        round(float(np.corrcoef(co_true, raw_pred_arr)[0, 1]), 4)
        if np.std(co_true) > 1e-12 and np.std(raw_pred_arr) > 1e-12
        else None
    )

    per_class = {
        cname: {
            "precision": round(float(prec[i]), 4),
            "recall": round(float(rec[i]), 4),
            "f1": round(float(f1_c[i]), 4),
            "support": int(sup[i]),
        }
        for i, cname in enumerate(CLASS_NAMES)
    }

    top_global_factors = sorted(
        shap_driver_counts.items(), key=lambda kv: kv[1], reverse=True
    )[:10]

    return {
        "n_submitted": int(len(df)),
        "n_evaluated": int(len(eval_df)),
        "n_dropped_incomplete_reference": dropped_rows,
        "missing_reference_cells": missing_ref_cells,
        "rows_with_imputation_or_clamping_warnings": warning_rows,
        "validation_warnings": validation_warnings,
        "reference_scale_cronbach_alpha": compute_cronbach_alpha(eval_ref),
        "thresholds_applied": {"cut1_low_max": predictor.cut1, "cut2_med_max": predictor.cut2},
        "zero_target_leakage_verified": True,
        "metrics": {
            "accuracy": round(acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "high_risk_recall": per_class["High"]["recall"],
            "log_loss": round(ll, 4),
            "continuous_rmse": round(rmse, 4),
            "continuous_mae": round(mae, 4),
            "continuous_pearson_r": pearson_r,
            "per_class": per_class,
            "confusion_matrix": confusion_matrix(y_true, y_pred_arr, labels=[0, 1, 2]).tolist(),
        },
        "top_shap_factor_frequencies": [
            {"feature_name": k, "top5_appearances": v} for k, v in top_global_factors
        ],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate deployed 20-input Component 1 model on an independent anonymized cohort."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to anonymized CSV or JSON file with 20 UI inputs + Q10..Q15 + study_id.",
    )
    parser.add_argument("--out-json", type=Path, default=None, help="Optional output JSON report.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    df = load_cohort_records(args.input)
    report = evaluate_cohort_dataframe(df)
    output_text = json.dumps(report, indent=2)
    print(output_text)
    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(output_text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
