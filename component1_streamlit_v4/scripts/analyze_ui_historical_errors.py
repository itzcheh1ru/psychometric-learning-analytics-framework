"""
analyze_ui_historical_errors.py
===============================
Reproducible, strictly read-only evaluation comparing the deployed 20-input UI
payload against the full 68-feature Version 4 Calibrated Thresholded Ridge Regressor
on the historical stratified 75-student holdout split (test_size=75, random_state=42).

Does NOT retrain, recalibrate, or modify any model weights or research datasets.
Pass --dataset-path pointing to an external de-identified cleaned_dataset_v4.csv.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.cognitive_offloading.integration_service import get_predictor_v4  # noqa: E402

TARGET_MAP = {"Low": 0, "Medium": 1, "High": 2}
INV_TARGET_MAP = {0: "Low", 1: "Medium", 2: "High"}
CLASS_NAMES = ["Low", "Medium", "High"]

FACULTY_COL_TO_UI = {
    "faculty_Business_Economics": "Business_Economics",
    "faculty_Computing_IT": "Computing_IT",
    "faculty_Engineering": "Engineering",
    "faculty_Humanities_Health_Other": "Humanities_Health_Other",
    "faculty_Natural_Applied_Sciences": "Natural_Applied_Sciences",
}

TOOL_COL_TO_UI = {
    "tool_chatgpt": "ChatGPT",
    "tool_google_gemini": "Google Gemini",
    "tool_microsoft_copilot": "Microsoft Copilot",
    "tool_claude": "Claude",
    "tool_perplexity": "Perplexity AI",
}

DELEGATE_COL_TO_UI = {
    "delegate_writing_assignments": "Writing assignments",
    "delegate_explaining_concepts": "Explaining concepts",
    "delegate_summarising_materials": "Summarising materials",
    "delegate_creating_presentations": "Creating presentations",
    "delegate_programming_problems": "Programming problems",
    "delegate_mathematical_problems": "Mathematical problems",
}

NUMERIC_UI_KEYS = [
    "academic_year",
    "age_group",
    "ai_usage_freq",
    "ai_time_per_week",
    "Q20_task_delegation_freq",
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


def row_to_ui_payload(row: pd.Series) -> Dict[str, Any]:
    """Convert one 68-feature dataset row strictly into the 20-input UI JSON payload."""
    payload: Dict[str, Any] = {}
    for key in NUMERIC_UI_KEYS:
        val = float(row[key])
        payload[key] = int(round(val)) if val.is_integer() else val

    payload["degree_field"] = next(
        (ui_val for col, ui_val in FACULTY_COL_TO_UI.items() if float(row[col]) >= 0.5),
        "Humanities_Health_Other",
    )
    payload["tools_used"] = [
        label for col, label in TOOL_COL_TO_UI.items() if float(row[col]) >= 0.5
    ]
    payload["tasks_delegated"] = [
        label for col, label in DELEGATE_COL_TO_UI.items() if float(row[col]) >= 0.5
    ]
    return payload


def score_to_probs(scores: np.ndarray, cut1: float, cut2: float, sigma: float) -> np.ndarray:
    """Compute Gaussian residual cumulative probabilities matching Version 4 inference."""
    probs = []
    for score in scores:
        p_low = float(norm.cdf((cut1 - score) / sigma))
        p_mid = float(norm.cdf((cut2 - score) / sigma) - p_low)
        p_high = float(1.0 - norm.cdf((cut2 - score) / sigma))
        arr = np.clip([p_low, p_mid, p_high], 1e-6, 1.0)
        probs.append(arr / arr.sum())
    return np.asarray(probs, dtype=float)


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    probs: np.ndarray,
    co_true: np.ndarray,
    raw_scores: np.ndarray,
) -> Dict[str, Any]:
    """Compute overall, per-class, calibration, and continuous score diagnostics."""
    prec, rec, f1_c, sup = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1, 2], zero_division=0
    )
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    per_class = {}
    for idx, cname in enumerate(CLASS_NAMES):
        per_class[cname] = {
            "precision": round(float(prec[idx]), 4),
            "recall": round(float(rec[idx]), 4),
            "f1": round(float(f1_c[idx]), 4),
            "support": int(sup[idx]),
        }

    conf = probs.max(axis=1)
    correct = (y_pred == y_true).astype(float)
    y_onehot = np.eye(3)[y_true]
    brier = float(np.mean(np.sum((probs - y_onehot) ** 2, axis=1)))

    bins = np.linspace(0.3, 1.0, 8)
    ece = 0.0
    calibration_bins = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (conf >= lo) & (conf < hi if hi < 1.0 else conf <= hi)
        if mask.sum() > 0:
            mean_c = float(conf[mask].mean())
            emp_a = float(correct[mask].mean())
            ece += (float(mask.sum()) / len(conf)) * abs(emp_a - mean_c)
            calibration_bins.append(
                {
                    "range": f"[{lo:.1f}, {hi:.1f}]",
                    "count": int(mask.sum()),
                    "mean_confidence": round(mean_c, 4),
                    "empirical_accuracy": round(emp_a, 4),
                }
            )

    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "macro_precision": round(float(macro_p), 4),
        "weighted_precision": round(float(weighted_p), 4),
        "macro_recall": round(float(macro_r), 4),
        "weighted_recall": round(float(weighted_r), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "roc_auc_ovr_macro": round(
            float(roc_auc_score(y_true, probs, multi_class="ovr", average="macro")), 4
        ),
        "log_loss": round(float(log_loss(y_true, probs, labels=[0, 1, 2])), 4),
        "brier_score": round(brier, 4),
        "ece_top_label": round(ece, 4),
        "rmse_raw_score": round(float(np.sqrt(np.mean((co_true - raw_scores) ** 2))), 4),
        "mae_raw_score": round(float(np.mean(np.abs(co_true - raw_scores))), 4),
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist(),
        "calibration_bins": calibration_bins,
    }


def analyze_historical_errors(df: pd.DataFrame) -> Dict[str, Any]:
    """Run full 68-feature vs 20-input UI comparison on the stratified N=75 split."""
    predictor = get_predictor_v4()
    feature_cols = predictor.feature_names

    missing_cols = [c for c in feature_cols + ["co_score", "co_risk"] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols[:5]}")

    X = df[feature_cols].copy()
    y = df["co_risk"].map(TARGET_MAP).values
    co_scores = df["co_score"].values

    _, X_test, _, y_test, _, co_test = train_test_split(
        X, y, co_scores, test_size=75, stratify=y, random_state=42
    )

    raw_68 = predictor.model.predict(X_test)
    y_pred_68 = np.array(
        [0 if s <= predictor.cut1 else (1 if s <= predictor.cut2 else 2) for s in raw_68]
    )
    prob_68 = score_to_probs(raw_68, predictor.cut1, predictor.cut2, predictor.residual_std)

    ui_preds: List[int] = []
    ui_raw_scores: List[float] = []
    ui_probs: List[List[float]] = []
    ui_rows: List[pd.Series] = []
    for _, row in X_test.iterrows():
        payload = row_to_ui_payload(row)
        res = predictor.predict(payload, top_factors_count=5)
        df_row, _ = predictor.transform_inputs(payload, [])
        ui_rows.append(df_row.iloc[0])
        ui_preds.append(TARGET_MAP[res["predicted_category"]])
        ui_raw_scores.append(float(res["raw_regression_score"]))
        ui_probs.append(
            [
                float(res["probabilities"]["low"]),
                float(res["probabilities"]["medium"]),
                float(res["probabilities"]["high"]),
            ]
        )

    y_pred_ui = np.asarray(ui_preds, dtype=int)
    raw_ui = np.asarray(ui_raw_scores, dtype=float)
    prob_ui = np.asarray(ui_probs, dtype=float)
    X_ui = pd.DataFrame(ui_rows, index=X_test.index)

    full_metrics = compute_classification_metrics(y_test, y_pred_68, prob_68, co_test, raw_68)
    ui_metrics = compute_classification_metrics(y_test, y_pred_ui, prob_ui, co_test, raw_ui)

    # Agreement and imputation impact
    agreement = float(np.mean(y_pred_ui == y_pred_68))
    coefs = predictor.coefficients
    delta_X = X_ui.values - X_test.values
    score_shift = delta_X * coefs
    top_imputed_shifts = []
    for fi in np.argsort(np.mean(np.abs(score_shift), axis=0))[::-1][:12]:
        top_imputed_shifts.append(
            {
                "feature": feature_cols[fi],
                "coef": round(float(coefs[fi]), 4),
                "mean_abs_shift": round(float(np.mean(np.abs(score_shift[:, fi]))), 4),
                "mean_signed_shift_all": round(float(np.mean(score_shift[:, fi])), 4),
                "mean_signed_shift_true_high": round(
                    float(np.mean(score_shift[y_test == 2, fi])), 4
                ),
            }
        )

    # Boundary & High-Risk miss diagnostics
    mis_mask = y_pred_ui != y_test
    ui_near_cut = (np.abs(raw_ui - predictor.cut1) <= 0.25) | (
        np.abs(raw_ui - predictor.cut2) <= 0.25
    )
    true_near_cut = (np.abs(co_test - predictor.cut1) <= 0.25) | (
        np.abs(co_test - predictor.cut2) <= 0.25
    )

    high_risk_cases = []
    for idx in np.where(y_test == 2)[0]:
        high_risk_cases.append(
            {
                "holdout_row": int(idx),
                "true_co_score": round(float(co_test[idx]), 3),
                "pred_68_score": round(float(raw_68[idx]), 3),
                "pred_68_class": INV_TARGET_MAP[int(y_pred_68[idx])],
                "pred_ui_score": round(float(raw_ui[idx]), 3),
                "pred_ui_class": INV_TARGET_MAP[int(y_pred_ui[idx])],
                "gap_to_high_cutoff": round(float(raw_ui[idx] - predictor.cut2), 3),
                "hit": bool(y_pred_ui[idx] == 2),
            }
        )

    # LinearSHAP explanation overlap
    x_means = np.array([predictor.background_means.get(f, 0.0) for f in feature_cols])
    shap_68 = (X_test.values - x_means) * coefs
    shap_ui = (X_ui.values - x_means) * coefs
    top3_overlap = []
    top5_overlap = []
    imputed_in_top5 = 0
    for i in range(len(X_test)):
        s3_68 = set(np.argsort(np.abs(shap_68[i]))[::-1][:3])
        s3_ui = set(np.argsort(np.abs(shap_ui[i]))[::-1][:3])
        s5_68 = set(np.argsort(np.abs(shap_68[i]))[::-1][:5])
        s5_ui = set(np.argsort(np.abs(shap_ui[i]))[::-1][:5])
        top3_overlap.append(len(s3_68 & s3_ui) / 3.0)
        top5_overlap.append(len(s5_68 & s5_ui) / 5.0)
        for fi in s5_ui:
            if (
                abs(float(X_ui.iloc[i, fi]) - float(predictor.default_features[feature_cols[fi]]))
                < 1e-12
                and abs(float(X_test.iloc[i, fi]) - float(X_ui.iloc[i, fi])) > 1e-6
            ):
                imputed_in_top5 += 1

    return {
        "holdout_n": int(len(X_test)),
        "full_68_metrics": full_metrics,
        "ui_20_metrics": ui_metrics,
        "agreement_vs_full_68": {
            "class_agreement": round(agreement, 4),
            "exact_matches": int((y_pred_ui == y_pred_68).sum()),
            "score_mae": round(float(np.mean(np.abs(raw_ui - raw_68))), 4),
            "score_pearson_r": round(float(np.corrcoef(raw_ui, raw_68)[0, 1]), 4),
            "agreement_matrix": confusion_matrix(
                y_pred_68, y_pred_ui, labels=[0, 1, 2]
            ).tolist(),
        },
        "boundary_diagnostics": {
            "total_ui_misclassifications": int(mis_mask.sum()),
            "errors_pred_within_0_25_of_cutoff": int((mis_mask & ui_near_cut).sum()),
            "errors_true_within_0_25_of_cutoff": int((mis_mask & true_near_cut).sum()),
            "shrinkage_by_true_class": {
                cname: round(float((raw_ui[y_test == i] - raw_68[y_test == i]).mean()), 4)
                for i, cname in enumerate(CLASS_NAMES)
            },
        },
        "high_risk_breakdown": high_risk_cases,
        "top_imputed_feature_shifts": top_imputed_shifts,
        "explanation_fidelity": {
            "top3_factor_overlap": round(float(np.mean(top3_overlap)), 4),
            "top5_factor_overlap": round(float(np.mean(top5_overlap)), 4),
            "imputed_mismatch_in_ui_top5": int(imputed_in_top5),
            "total_ui_top5_slots": int(len(X_test) * 5),
        },
    }


def resolve_default_dataset() -> Optional[Path]:
    """Locate cleaned_dataset_v4.csv in the optional local data directory."""
    candidate = REPO_ROOT / "data" / "cleaned_dataset_v4.csv"
    return candidate if candidate.exists() else None


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze historical 75-student 20-input UI errors.")
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=None,
        help="Path to external de-identified cleaned_dataset_v4.csv.",
    )
    parser.add_argument("--out-json", type=Path, default=None, help="Optional JSON output path.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    csv_path = args.dataset_path or resolve_default_dataset()
    if csv_path is None or not csv_path.exists():
        print(
            "Dataset CSV not found. Provide --dataset-path /path/to/cleaned_dataset_v4.csv",
            file=sys.stderr,
        )
        return 1

    df = pd.read_csv(csv_path)
    results = analyze_historical_errors(df)
    summary_text = json.dumps(results, indent=2)
    print(summary_text)
    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(summary_text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
