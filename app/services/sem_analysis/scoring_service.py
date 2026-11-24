"""
app/services/sem_analysis/scoring_service.py

Individual psychometric construct scoring engine for Component 2:
Algorithmic Trust & Verification Analysis.

Methodological Principles:
1. Core Metric: Unweighted Mean Construct Score (1.0 to 5.0 scale).
   Scientifically preferred for direct interpretability and scale preservation.
2. Sensitivity Metric: Factor-Loading-Weighted Average.
   Weighted by standardized CFA loadings (lambda). Documented as an exploratory
   composite heuristic, explicitly distinguished from latent factor scores.
3. Norm-Referenced Benchmarking:
   Grounds individual student scores against the empirical undergraduate
   reference distribution (N = 375). Computes z-scores, T-scores, and percentile ranks.
4. Non-Diagnostic Classifications:
   Uses empirical quartile bands (Lower 25%, Middle 50%, Upper 25%) instead of
   arbitrary clinical or psychological risk thresholds.
5. Epistemological Boundary:
   Self-reported ratings reflect perceived habits, not direct objective performance.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from app.services.sem_analysis.schemas import (
    CONSTRUCTS,
    EMPIRICAL_COHORT_BENCHMARKS,
    SURVEY_ITEMS,
    SURVEY_ITEMS_EMPIRICAL_26,
)
from app.services.sem_analysis.dataset_service import clean_likert_cell


def calculate_individual_scores(
    responses: Dict[str, Any],
    clean_csv_path: Optional[str] = "data/processed/component2_survey_clean.csv",
) -> Dict[str, Any]:
    """
    Calculate individual construct scores and norm-referenced cohort comparisons.

    Args:
        responses: Dictionary mapping item codes (e.g. 'AT1', 'VB1', ...) to
                   Likert responses (integers 1-5 or string labels 'Agree', etc.)
        clean_csv_path: Path to the processed cohort dataset for empirical percentile calculation.

    Returns:
        Structured dictionary containing:
        - raw_item_scores: cleaned 1-5 integer ratings for all submitted items
        - construct_scores: dictionary per construct with:
            - mean_score: primary unweighted composite (1.0 - 5.0)
            - weighted_score: factor-loading weighted composite
            - cohort_mean, cohort_sd, cohort_median, cohort_q1, cohort_q3
            - z_score: standard deviations from cohort mean
            - t_score: standardized score (Mean=50, SD=10)
            - percentile_rank: empirical percentile relative to N=375 cohort
            - quartile_band: Lower 25%, Middle 50%, or Upper 25%
        - completion_summary: items answered, items missing, validity status
        - scientific_notes: methodological explanation of formulas and caveats
    """
    # 1. Clean and normalize input responses
    normalized_responses: Dict[str, float] = {}
    for raw_key, raw_val in responses.items():
        clean_key = str(raw_key).replace("-", "_").strip().upper()
        # Handle cases like "item_at1" or "at_1"
        for standard_code in SURVEY_ITEMS.keys():
            if clean_key == standard_code.upper() or clean_key.endswith(standard_code.upper()):
                clean_key = standard_code
                break

        val = clean_likert_cell(raw_val)
        if not np.isnan(val):
            normalized_responses[clean_key] = val

    # 2. Load empirical cohort data if available for exact rank calculation
    cohort_df = None
    try:
        import os
        if clean_csv_path and os.path.exists(clean_csv_path):
            cohort_df = pd.read_csv(clean_csv_path)
    except Exception:
        cohort_df = None

    # 3. Compute scores per construct
    construct_scores: Dict[str, Dict[str, Any]] = {}
    total_expected_items = 0
    total_answered_items = 0

    benchmarks = EMPIRICAL_COHORT_BENCHMARKS.get("constructs", {})

    for c in CONSTRUCTS:
        c_code = c["code"]
        c_name = c["name"]
        item_keys = c["items"]
        total_expected_items += len(item_keys)

        # Extract answered items for this construct
        c_answered = {
            it: normalized_responses[it]
            for it in item_keys
            if it in normalized_responses
        }
        total_answered_items += len(c_answered)

        if not c_answered:
            construct_scores[c_code] = {
                "code": c_code,
                "name": c_name,
                "items_count": len(item_keys),
                "items_answered": 0,
                "mean_score": None,
                "weighted_score": None,
                "z_score": None,
                "t_score": None,
                "percentile_rank": None,
                "quartile_band": "No Data",
                "status": "Incomplete",
            }
            continue

        # A. Unweighted Mean Score (Primary Metric)
        mean_score = float(np.mean(list(c_answered.values())))

        # B. Factor-Loading Weighted Average (Sensitivity / Alternative Metric)
        c_bench = benchmarks.get(c_code, {})
        c_loadings = c_bench.get("factor_loadings", {})

        weighted_numerator = 0.0
        weighted_denominator = 0.0
        for it, val in c_answered.items():
            lambda_i = float(c_loadings.get(it, 1.0))
            weighted_numerator += lambda_i * val
            weighted_denominator += lambda_i

        weighted_score = (
            float(weighted_numerator / weighted_denominator)
            if weighted_denominator > 0 else mean_score
        )

        # C. Norm-Referenced Benchmarking against N=375 Cohort
        cohort_mean = float(c_bench.get("mean", 3.0))
        cohort_sd = float(c_bench.get("sd", 0.7))
        cohort_med = float(c_bench.get("median", 3.0))
        cohort_q1 = float(c_bench.get("q1", 2.5))
        cohort_q3 = float(c_bench.get("q3", 3.8))

        # Standardized z-score and T-score
        z_score = float((mean_score - cohort_mean) / cohort_sd) if cohort_sd > 0 else 0.0
        t_score = float(50.0 + (10.0 * z_score))

        # Empirical Percentile Rank
        if cohort_df is not None:
            active_cols = [it for it in item_keys if it in cohort_df.columns]
            if active_cols:
                cohort_comp = cohort_df[active_cols].mean(axis=1)
                percentile = float((cohort_comp <= mean_score).mean() * 100.0)
            else:
                percentile = float(stats.norm.cdf(z_score) * 100.0)
        else:
            percentile = float(stats.norm.cdf(z_score) * 100.0)

        # D. Non-Arbitrary Quartile Band (Empirically grounded)
        if mean_score < cohort_q1:
            quartile_band = "Lower Quartile (< 25th percentile)"
            band_code = "LOW"
        elif mean_score > cohort_q3:
            quartile_band = "Upper Quartile (> 75th percentile)"
            band_code = "HIGH"
        else:
            quartile_band = "Interquartile Range (25th - 75th percentile)"
            band_code = "MODERATE"

        construct_scores[c_code] = {
            "code": c_code,
            "name": c_name,
            "items_count": len(item_keys),
            "items_answered": len(c_answered),
            "mean_score": round(mean_score, 2),
            "weighted_score": round(weighted_score, 2),
            "cohort_mean": round(cohort_mean, 2),
            "cohort_sd": round(cohort_sd, 2),
            "cohort_median": round(cohort_med, 2),
            "cohort_q1": round(cohort_q1, 2),
            "cohort_q3": round(cohort_q3, 2),
            "z_score": round(z_score, 2),
            "t_score": round(t_score, 1),
            "percentile_rank": round(percentile, 1),
            "quartile_band": quartile_band,
            "band_code": band_code,
            "is_complete": len(c_answered) == len(item_keys),
        }

    is_all_complete = total_answered_items == total_expected_items

    return {
        "success": True,
        "is_complete": is_all_complete,
        "items_expected": total_expected_items,
        "items_answered": total_answered_items,
        "raw_responses": normalized_responses,
        "construct_scores": construct_scores,
        "scientific_notes": {
            "primary_metric": (
                "Unweighted Mean Construct Score: S_c = (1/K) * sum(x_k). "
                "Maintains direct fidelity to the original 1-5 Likert response scale."
            ),
            "weighted_metric_caveat": (
                "Factor-Loading Weighted Average: S_weighted = sum(lambda_k * x_k) / sum(lambda_k). "
                "Serves as an exploratory reliability-weighted composite. "
                "Explicitly not equivalent to latent variable scores estimated in SEM."
            ),
            "norm_reference_framework": (
                f"Norm-referenced against N={EMPIRICAL_COHORT_BENCHMARKS.get('sample_size', 375)} "
                "undergraduate students. Z-scores and T-scores indicate relative cohort position, "
                "not clinical or psychological deficit diagnoses."
            ),
            "measurement_boundary": (
                "Ratings reflect self-reported student perceptions and habits. "
                "They do not capture automated telemetry of verification actions or objective academic performance."
            ),
        },
    }
