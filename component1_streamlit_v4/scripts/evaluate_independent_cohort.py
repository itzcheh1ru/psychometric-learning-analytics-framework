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

FORBIDDEN_PII_COLUMNS = {
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


def parse_multi_value(value: Any) -> List[str]:
    """Normalize semicolon/comma-separated strings or lists from CSV/JSON inputs."""
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


def validate_cohort_schema(df: pd.DataFrame, predictor_features: List[str]) -> Tuple[int, List[str]]:
    """
    Validate cohort columns strictly:
      - Reject direct PII fields (fail-closed privacy protection).
      - Require anonymous study_id, all 20 UI keys, and all 6 Section E items.
      - Verify zero leakage of Section E or ground-truth columns inside predictor schema.
    """
    lower_cols = {c.lower().strip(): c for c in df.columns}
    present_pii = [lower_cols[k] for k in FORBIDDEN_PII_COLUMNS if k in lower_cols]
    if present_pii:
        raise ValueError(
            f"Privacy check failed: remove direct PII columns before evaluation: {present_pii}"
        )

    for target_col in SECTION_E_REFERENCE_KEYS + ["co_score", "co_risk"]:
        if target_col in predictor_features:
            raise AssertionError(f"Target leakage detected inside predictor features: {target_col}")

    required = ["study_id"] + UI_PREDICTOR_KEYS + SECTION_E_REFERENCE_KEYS
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Cohort file missing required columns: {missing}")

    if df["study_id"].isna().any():
        raise ValueError("All rows must contain a non-empty anonymous study_id.")

    # Track completeness across numeric UI inputs + reference items
    warnings: List[str] = []
    numeric_ui = [
        k for k in UI_PREDICTOR_KEYS if k not in {"degree_field", "tools_used", "tasks_delegated"}
    ]
    missing_ui_cells = int(df[numeric_ui].isna().sum().sum())
    if missing_ui_cells > 0:
        warnings.append(
            f"Detected {missing_ui_cells} missing numeric UI responses across cohort (handled via reference medians)."
        )
    missing_ref = int(df[SECTION_E_REFERENCE_KEYS].isna().sum().sum())
    return missing_ref, warnings


def evaluate_cohort_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluate an independent anonymized cohort using deployed Component 1 V4 inference.
    Models, thresholds, medians, and weights remain strictly unmodified.
    """
    predictor = get_predictor_v4()
    missing_ref_cells, validation_warnings = validate_cohort_schema(df, predictor.feature_names)

    # Filter to rows with valid reference Section E items (Q10-Q15)
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

    if ((eval_ref < 1.0) | (eval_ref > 5.0)).any().any():
        raise ValueError("Reference items Q10-Q15 must strictly lie within Likert [1, 5].")

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
                payload[key] = "" if pd.isna(val) else str(val).strip()
            else:
                payload[key] = np.nan if pd.isna(val) else val

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
