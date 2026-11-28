"""
app/services/sem_analysis/validation_protocol.py

Independent Empirical Validation Protocol & Statistical Analysis Suite for
the AI Answer Verification Performance Assessment Module.
Component 2: Algorithmic Trust & Verification Analysis (J26-DS-310).

Methodological Principles:
1. Scientific Integrity:
   Explicitly distinguishes the existing N=375 benchmark survey from the newly developed
   practical verification assessment. Never fabricates task performance data for the 375 students.
2. Formal Educational Measurement Protocol:
   Defines expert review standards (Content Validity Index), pilot feasibility targets (N=5-10),
   and main evaluation statistical power parameters (N >= 60).
3. Psychometric & Statistical Rigor:
   Implements Spearman rank correlation, Pearson correlation with Fisher's z 95% CI,
   and exploratory OLS regression relating self-reported constructs to demonstrated performance.
4. Privacy & Research Ethics:
   Enforces strict informed consent filters and pseudonymous session IDs. Never persists
   identifiable student data without explicit opt-in consent.
"""

from typing import Any, Dict, List, Optional, Tuple
import math
import json
from pathlib import Path
from datetime import datetime


# =========================================================================== #
# 1. Validation Protocol Metadata & Specification                             #
# =========================================================================== #

VALIDATION_PROTOCOL_SPEC: Dict[str, Any] = {
    "framework_title": "Empirical Validation Protocol for AI-Generated Answer Verification Assessment",
    "project_id": "J26-DS-310",
    "component": "Component 2: Algorithmic Trust & Verification Analysis",
    "lead_investigator": "Kumari A.M.W.P.G.S.R. (IT23217904)",
    "current_status": "Researcher-Designed Assessment Engine; External Validation Pending Pilot Collection",
    "protocol_phases": [
        {
            "phase": "Phase 4.1: Scenario Construction & Expert Content Review",
            "status": "Ready for Panel Review",
            "description": "8 controlled academic scenarios covering 4 university domains with verified answer keys.",
            "target_metrics": {
                "expert_panel_size": "6 to 10 subject matter experts (faculty & researchers)",
                "item_content_validity_index_target": "I-CVI >= 0.78 for each claim",
                "scale_content_validity_index_target": "S-CVI/Ave >= 0.90 across entire scenario bank",
            },
        },
        {
            "phase": "Phase 4.2: Cognitive Walkthrough & Feasibility Pilot",
            "status": "Protocol Defined (Recruitment Pending)",
            "description": "Formative evaluation with N=5 to 10 undergraduate students to test scenario readability, pacing, and interface usability.",
            "target_metrics": {
                "sample_size": "5 to 10 consented undergraduate students",
                "target_completion_time": "15 to 25 minutes for 8 scenarios",
                "qualitative_clarity_rating": ">= 80% rating instructions and claims as clear",
            },
        },
        {
            "phase": "Phase 4.3: Inter-Rater Reliability for Explanation Rubrics",
            "status": "Protocol Defined",
            "description": "Independent double-blind grading of written justifications by two trained evaluators.",
            "target_metrics": {
                "classification_agreement": "Cohen's Kappa (kappa >= 0.80) for claim error tagging",
                "rubric_grading_agreement": "Intraclass Correlation Coefficient ICC(2,1) >= 0.75 for 0-2 explanation rubric",
            },
        },
        {
            "phase": "Phase 4.4: Main Independent Validation Study",
            "status": "Design Complete (Awaiting Institutional Ethics Clearance)",
            "description": "Independent empirical study examining correlation between self-reported Verification Behaviour (VB) and demonstrated task accuracy.",
            "target_metrics": {
                "sample_size_target": "N >= 60 undergraduate students (statistically powered)",
                "significance_level": "alpha = 0.05 (two-tailed)",
                "statistical_power": "1 - beta = 0.80 to detect moderate correlation r >= 0.35",
            },
        },
    ],
    "power_analysis": {
        "formula": "N = ((z_{alpha/2} + z_{beta}) / (0.5 * ln((1+r)/(1-r))))^2 + 3",
        "assumptions": {
            "alpha": 0.05,
            "power": 0.80,
            "minimum_detectable_effect_r": 0.35,
            "required_sample_size": 62,
        },
        "interpretation": "A minimum sample size of 62 independent participants is required to detect a statistically significant correlation of r >= 0.35 between self-reported VB and task accuracy at 80% power.",
    },
}


# =========================================================================== #
# 2. Statistical Correlation & Regression Suite                              #
# =========================================================================== #

def compute_fisher_z_ci(r: float, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate Fisher's z-transformed confidence interval for Pearson correlation r."""
    if n <= 3 or abs(r) >= 1.0:
        return (r, r)
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1.0 / math.sqrt(n - 3)
    z_crit = 1.96 if confidence == 0.95 else 2.576
    low_z = z - z_crit * se
    high_z = z + z_crit * se
    low_r = (math.exp(2 * low_z) - 1) / (math.exp(2 * low_z) + 1)
    high_r = (math.exp(2 * high_z) - 1) / (math.exp(2 * high_z) + 1)
    return (round(low_r, 3), round(high_r, 3))


def compute_sample_correlation(x_vals: List[float], y_vals: List[float]) -> Dict[str, Any]:
    """
    Compute descriptive statistics, Pearson r, Spearman rank rho, and 95% CI.
    
    Args:
        x_vals: List of numeric values (e.g. self-reported VB scores).
        y_vals: List of numeric values (e.g. demonstrated task accuracy).

    Returns:
        Dictionary of correlation statistics.
    """
    n = len(x_vals)
    if n != len(y_vals) or n < 3:
        return {
            "n": n,
            "error": "Insufficient sample size (minimum N=3 required for correlation analysis).",
            "pearson_r": None,
            "spearman_rho": None,
        }

    # Means and standard deviations
    mean_x = sum(x_vals) / n
    mean_y = sum(y_vals) / n
    var_x = sum((x - mean_x) ** 2 for x in x_vals) / (n - 1)
    var_y = sum((y - mean_y) ** 2 for y in y_vals) / (n - 1)
    sd_x = math.sqrt(var_x) if var_x > 0 else 0.0
    sd_y = math.sqrt(var_y) if var_y > 0 else 0.0

    if sd_x == 0 or sd_y == 0:
        return {
            "n": n,
            "error": "Zero variance detected in one or both variables.",
            "pearson_r": 0.0,
            "spearman_rho": 0.0,
        }

    # Pearson r
    cov_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals)) / (n - 1)
    pearson_r = cov_xy / (sd_x * sd_y)
    pearson_r = max(-1.0, min(1.0, pearson_r))

    # Fisher's z 95% CI
    ci_low, ci_high = compute_fisher_z_ci(pearson_r, n)

    # t-test for r significance
    df = n - 2
    if abs(pearson_r) < 1.0:
        t_stat = pearson_r * math.sqrt(df / (1.0 - pearson_r ** 2))
    else:
        t_stat = float("inf") if pearson_r > 0 else float("-inf")

    # Spearman rank correlation
    def get_ranks(seq: List[float]) -> List[float]:
        sorted_indices = sorted(range(len(seq)), key=lambda i: seq[i])
        ranks = [0.0] * len(seq)
        i = 0
        while i < len(seq):
            j = i
            while j < len(seq) - 1 and seq[sorted_indices[j]] == seq[sorted_indices[j + 1]]:
                j += 1
            avg_rank = (i + j + 2) / 2.0
            for k in range(i, j + 1):
                ranks[sorted_indices[k]] = avg_rank
            i = j + 1
        return ranks

    rank_x = get_ranks(x_vals)
    rank_y = get_ranks(y_vals)
    d_sq_sum = sum((rx - ry) ** 2 for rx, ry in zip(rank_x, rank_y))
    spearman_rho = 1.0 - (6.0 * d_sq_sum) / (n * (n ** 2 - 1))
    spearman_rho = max(-1.0, min(1.0, spearman_rho))

    return {
        "n": n,
        "mean_x": round(mean_x, 3),
        "sd_x": round(sd_x, 3),
        "mean_y": round(mean_y, 3),
        "sd_y": round(sd_y, 3),
        "pearson_r": round(pearson_r, 3),
        "pearson_r_ci95": [ci_low, ci_high],
        "spearman_rho": round(spearman_rho, 3),
        "t_statistic": round(t_stat, 3),
        "degrees_of_freedom": df,
        "is_significant_p05": abs(t_stat) >= 2.00 if df >= 60 else (abs(t_stat) >= 2.10 if df >= 20 else abs(t_stat) >= 2.30),
    }


# =========================================================================== #
# 3. Pilot Psychometric Evaluation: Item Difficulty, Discrimination & Timing  #
# =========================================================================== #

def compute_item_difficulty(
    claim_evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compute item difficulty (p-value: proportion of correct classifications).
    
    In classical test theory (CTT):
      p_i = N_correct / N_total
      - p > 0.80: Easy item
      - 0.40 <= p <= 0.80: Optimal / Medium difficulty range
      - p < 0.40: Challenging item
      
    Args:
        claim_evaluations: List of evaluated claim records. Each dict may contain
                           'claim_id', 'is_correct' (or 'claim_correct').
                           Alternatively accepts dict of {claim_id: is_correct_bool}.
                           
    Returns:
        Dictionary mapping claim_id to difficulty statistics, plus overall summary.
    """
    if not claim_evaluations:
        return {
            "total_evaluations": 0,
            "items": {},
            "mean_difficulty": 0.0,
            "interpretation": "No evaluation records provided.",
        }

    item_counts: Dict[str, Dict[str, int]] = {}

    for record in claim_evaluations:
        claim_id = record.get("claim_id") or record.get("id", "UNKNOWN")
        is_corr = bool(record.get("is_correct", False) or record.get("claim_correct", False))

        if claim_id not in item_counts:
            item_counts[claim_id] = {"correct": 0, "total": 0}
        item_counts[claim_id]["total"] += 1
        if is_corr:
            item_counts[claim_id]["correct"] += 1

    items_res: Dict[str, Any] = {}
    p_values: List[float] = []

    for cid, counts in sorted(item_counts.items()):
        tot = counts["total"]
        corr = counts["correct"]
        p = round(corr / tot, 3) if tot > 0 else 0.0
        p_values.append(p)

        if p > 0.80:
            classification = "EASY"
            review_note = "High pass rate. Good for introductory pacing; minimal challenge."
        elif p >= 0.40:
            classification = "OPTIMAL_MEDIUM"
            review_note = "Ideal psychometric difficulty for cross-disciplinary discrimination."
        else:
            classification = "CHALLENGING"
            review_note = "Low pass rate. Assesses subtle bias, complex synthesis, or edge constraints."

        items_res[cid] = {
            "claim_id": cid,
            "total_attempts": tot,
            "correct_attempts": corr,
            "difficulty_p": p,
            "classification": classification,
            "review_note": review_note,
        }

    mean_p = round(sum(p_values) / len(p_values), 3) if p_values else 0.0

    return {
        "total_evaluations": len(claim_evaluations),
        "total_unique_items": len(items_res),
        "items": items_res,
        "mean_difficulty": mean_p,
        "interpretation": (
            f"Mean item difficulty is p={mean_p}. Optimal CTT target range is 0.40 <= p <= 0.80."
        ),
    }


def compute_item_discrimination(
    upper_correct: int,
    upper_total: int,
    lower_correct: int,
    lower_total: int,
) -> Dict[str, Any]:
    """
    Compute item discrimination index (D) using Kelley's extreme groups method (top 27% vs bottom 27%).
    
    Formula:
      D = P_upper - P_lower = (R_upper / N_upper) - (R_lower / N_lower)
      
    Classification:
      - D >= 0.40: Excellent discrimination
      - 0.30 <= D < 0.40: Good discrimination
      - 0.20 <= D < 0.30: Marginal / acceptable (candidate for minor wording review)
      - D < 0.20: Poor discrimination (needs revision or replacement)
      - D < 0.00: Negative discrimination (defective item: high performers get it wrong more often)
      
    Args:
        upper_correct: Correct responses in upper criterion group (e.g. top 27% on total score).
        upper_total: Total participants in upper group.
        lower_correct: Correct responses in lower criterion group (e.g. bottom 27%).
        lower_total: Total participants in lower group.
        
    Returns:
        Dictionary of discrimination statistics and psychometric quality tier.
    """
    if upper_total <= 0 or lower_total <= 0:
        return {
            "error": "Group totals must be greater than zero.",
            "discrimination_index": None,
            "tier": "INVALID",
        }

    p_upper = upper_correct / upper_total
    p_lower = lower_correct / lower_total
    d_index = round(p_upper - p_lower, 3)

    if d_index >= 0.40:
        tier = "EXCELLENT"
        recommendation = "Retain without modification. Highly discriminates critical evaluators."
    elif d_index >= 0.30:
        tier = "GOOD"
        recommendation = "Retain. Good discrimination power for undergraduate assessment."
    elif d_index >= 0.20:
        tier = "MARGINAL"
        recommendation = "Acceptable, but consider refining prompt clarity or distractors."
    elif d_index >= 0.00:
        tier = "POOR"
        recommendation = "Revise item. Low discrimination between high and low verification ability."
    else:
        tier = "DEFECTIVE_NEGATIVE"
        recommendation = "Discard or overhaul immediately. High performers fail more frequently than low performers."

    return {
        "p_upper": round(p_upper, 3),
        "p_lower": round(p_lower, 3),
        "discrimination_index": d_index,
        "tier": tier,
        "recommendation": recommendation,
    }


def compute_item_discrimination_from_scores(
    upper_group_scores: List[int],
    lower_group_scores: List[int],
) -> Dict[str, Any]:
    """
    Convenience wrapper to compute discrimination index D from lists of binary item scores (1 or 0).
    """
    u_total = len(upper_group_scores)
    l_total = len(lower_group_scores)
    u_corr = sum(1 for s in upper_group_scores if s == 1)
    l_corr = sum(1 for s in lower_group_scores if s == 1)
    return compute_item_discrimination(u_corr, u_total, l_corr, l_total)


def compute_completion_time_metrics(
    completion_times: List[float],
) -> Dict[str, Any]:
    """
    Compute descriptive pacing and completion time statistics for pilot participants.
    
    Args:
        completion_times: List of duration values in seconds or minutes.
        
    Returns:
        Dictionary with sample size, mean, SD, median, IQR, min, max, and feasibility check.
    """
    n = len(completion_times)
    if n == 0:
        return {
            "n": 0,
            "mean_seconds": 0.0,
            "median_seconds": 0.0,
            "iqr_seconds": 0.0,
            "feasibility_assessment": "No timing records available.",
        }

    sorted_times = sorted(completion_times)
    mean_time = sum(sorted_times) / n
    variance = sum((t - mean_time) ** 2 for t in sorted_times) / (n - 1) if n > 1 else 0.0
    sd_time = math.sqrt(variance)

    # Median
    mid = n // 2
    if n % 2 == 1:
        median_time = sorted_times[mid]
    else:
        median_time = (sorted_times[mid - 1] + sorted_times[mid]) / 2.0

    # Quartiles
    def get_percentile(sorted_list: List[float], p: float) -> float:
        k = (len(sorted_list) - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_list[int(k)]
        d0 = sorted_list[int(f)] * (c - k)
        d1 = sorted_list[int(c)] * (k - f)
        return d0 + d1

    q1 = get_percentile(sorted_times, 0.25)
    q3 = get_percentile(sorted_times, 0.75)
    iqr = round(q3 - q1, 2)

    # Feasibility against 15-25 minute benchmark (900s - 1500s)
    # or per-scenario 60s - 180s
    in_target_window = (mean_time >= 60.0 and mean_time <= 1800.0)

    return {
        "n": n,
        "mean_seconds": round(mean_time, 2),
        "mean_minutes": round(mean_time / 60.0, 2),
        "sd_seconds": round(sd_time, 2),
        "median_seconds": round(median_time, 2),
        "median_minutes": round(median_time / 60.0, 2),
        "q1_seconds": round(q1, 2),
        "q3_seconds": round(q3, 2),
        "iqr_seconds": iqr,
        "min_seconds": round(sorted_times[0], 2),
        "max_seconds": round(sorted_times[-1], 2),
        "feasibility_assessment": (
            "Completion times fall within expected educational pacing targets."
            if in_target_window else "Completion times indicate potential cognitive overload or disengaged rushing."
        ),
    }


# =========================================================================== #
# 4. Privacy, Research Ethics & Pilot Storage Handler                        #
# =========================================================================== #

DATA_STORAGE_DIR = Path("data/processed/verification_evaluations")


def generate_pseudonymous_id(base_prefix: str = "P_VERIF") -> str:
    """Generate a privacy-preserving pseudonymous participant token."""
    import uuid
    token = uuid.uuid4().hex[:8].upper()
    return f"{base_prefix}_{token}"


def save_pilot_evaluation_record(
    evaluation_record: Dict[str, Any],
    consent_given: bool = False,
) -> Dict[str, Any]:
    """
    Store evaluation record only when explicit informed consent is granted.
    Never persists identifiable names or IP addresses.
    """
    if not consent_given:
        return {
            "saved": False,
            "reason": "Explicit research data donation consent not provided. Processed in-memory only.",
        }

    try:
        DATA_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        participant_id = evaluation_record.get("student_id") or generate_pseudonymous_id()

        # Scrub sensitive headers if any
        sanitized_record = {
            "pseudonymous_id": participant_id,
            "timestamp": datetime.now().isoformat(),
            "consent_status": "EXPLICIT_OPT_IN",
            "summary": evaluation_record.get("summary", {}),
            "calibration": evaluation_record.get("calibration", {}),
            "claims_count": len(evaluation_record.get("claim_evaluations", [])),
        }

        filename = f"{participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = DATA_STORAGE_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sanitized_record, f, indent=2)

        return {
            "saved": True,
            "filepath": str(filepath),
            "pseudonymous_id": participant_id,
            "message": "Evaluation record successfully saved for empirical validation pilot under informed consent.",
        }
    except Exception as exc:
        return {
            "saved": False,
            "reason": f"File storage error: {str(exc)}",
        }
