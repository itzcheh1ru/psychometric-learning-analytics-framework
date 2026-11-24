"""
app/services/sem_analysis/calibration_service.py

Self-Report vs. Demonstrated Verification Performance Calibration Analysis.
Component 2: Algorithmic Trust & Verification Analysis (J26-DS-310).

Methodological Principles:
1. Non-Equivalence Principle:
   Self-reported questionnaire scores (Likert 1-5) and demonstrated verification
   performance (0-100% accuracy on controlled tasks) measure distinct cognitive facets:
   subjective perception / behavioral intention vs. demonstrated evaluative skill.
2. Scientific Calibration Normalization:
   Normalizes self-reported Verification Behaviour (VB) to [0, 1] via min-max scaling,
   and computes standardized z-scores relative to the N=375 empirical cohort.
   Exploratory discrepancy index: Delta_calib = VB_norm - Task_Accuracy.
3. Continuous Calibration Matrix:
   Characterizes students into four descriptive calibration zones using cohort medians:
   - Calibrated Discerning (High VB, High Performance)
   - Verification Illusion / Inflated Confidence (High VB, Lower Performance)
   - Cautious Skeptic (Lower VB, High Performance)
   - Vulnerable Under-Utilizer (Lower VB, Lower Performance)
4. Empirical Humility:
   Transparently documents limitations: cross-sectional survey scores do not predict
   demonstrated accuracy without independent validation data.
"""

from typing import Any, Dict, Optional
from app.services.sem_analysis.schemas import EMPIRICAL_COHORT_BENCHMARKS


def compute_verification_calibration(
    construct_scores: Dict[str, Dict[str, Any]],
    task_performance: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluate the alignment between self-reported Verification Behaviour and
    demonstrated performance on controlled verification tasks.

    Args:
        construct_scores: Scoring dictionary from scoring_service containing AT, VB, PU, AD, LC.
        task_performance: Evaluation dictionary from verification_task_service containing accuracy, precision, recall, etc.

    Returns:
        Structured calibration dictionary containing:
        - metrics: Normalized VB, Task Accuracy, Discrepancy Index (Delta), z-scores
        - calibration_zone: Quadrant ID and descriptive label
        - alignment_summary: Plain-language summary
        - detailed_interpretation: Multi-paragraph academic interpretation
        - trust_dependence_context: Analysis combining AT, AD, and demonstrated accuracy
        - limitations_and_assumptions: Transparent methodological notice
    """
    # 1. Extract Self-Reported Construct Scores
    vb_info = construct_scores.get("VB", {})
    vb_score = float(vb_info.get("mean_score", 3.0))
    vb_percentile = float(vb_info.get("percentile_rank", 50.0))
    vb_z = float(vb_info.get("z_score", 0.0))

    at_info = construct_scores.get("AT", {})
    at_score = float(at_info.get("mean_score", 3.0))

    ad_info = construct_scores.get("AD", {})
    ad_score = float(ad_info.get("mean_score", 3.0))

    # 2. Extract Demonstrated Task Performance
    summary = task_performance.get("summary", {})
    task_acc = float(summary.get("accuracy", 0.0))  # 0.0 to 1.0
    task_recall = float(summary.get("recall", 0.0))
    task_precision = float(summary.get("precision", 0.0))
    rubric_pct = float(summary.get("rubric_pct", 0.0))

    # 3. Methodologically Justified Normalization
    # Rescale self-reported VB from [1.0, 5.0] to [0.0, 1.0]
    vb_norm = max(0.0, min(1.0, (vb_score - 1.0) / 4.0))

    # Compute exploratory Discrepancy Index: Delta = VB_norm - Task_Accuracy
    # Positive delta => Self-reported verification exceeds demonstrated accuracy (Overconfidence risk)
    # Negative delta => Demonstrated accuracy exceeds self-reported verification (Underconfident/Cautious)
    delta_calib = round(vb_norm - task_acc, 3)

    # 4. Calibration Reference Boundaries
    # VB cohort median = 3.80 (empirical N=375 benchmark)
    # Task benchmark: 70% accuracy (standard university mastery threshold)
    vb_median = EMPIRICAL_COHORT_BENCHMARKS["constructs"]["VB"]["median"]
    is_high_vb = vb_score >= vb_median
    is_high_perf = task_acc >= 0.70

    # 5. Evaluate Calibration Zone
    if is_high_vb and is_high_perf:
        zone_id = "CALIB_Q1"
        zone_title = "Calibrated Discerning Verifier"
        tagline = "High self-reported verification habits backed by high demonstrated accuracy."
        alignment_summary = (
            f"Your self-reported verification habits (VB = {vb_score:.2f}, {vb_percentile:.1f}th percentile) "
            f"are well-aligned with your demonstrated verification performance ({task_acc:.1%} accuracy). "
            "You report active scrutiny and successfully catch simulated errors in practice."
        )
        interpretation = (
            "You exhibit genuine metacognitive calibration: your perceived verification practices match your "
            "objective problem-solving and fact-checking performance. You caught the majority of simulated AI errors, "
            "avoided false alarms on accurate mathematical steps, and provided sound academic reasoning. "
            "This combination ensures you can safely leverage the productivity benefits of Generative AI without "
            "falling prey to subtle conceptual hallucinations."
        )
    elif is_high_vb and not is_high_perf:
        zone_id = "CALIB_Q2"
        zone_title = "Verification Illusion (Inflated Self-Appraisal Gap)"
        tagline = "High self-reported verification, but lower-than-expected accuracy on controlled academic tasks."
        alignment_summary = (
            f"A notable calibration gap was observed: you reported high verification frequency (VB = {vb_score:.2f}, "
            f"above cohort median {vb_median}), yet achieved an accuracy of {task_acc:.1%} on the practical verification tasks. "
            f"Exploratory Discrepancy Index: Delta = +{delta_calib:.2f}."
        )
        interpretation = (
            "This profile suggests an 'illusion of verification'—a common cognitive pattern where learners believe they "
            "routinely cross-check AI outputs, but their verification routines fail to detect subtle calculation errors, "
            "distorted thermodynamic formulas, or fabricated citations in practice. In fluent, well-formatted AI outputs, "
            "superficial skimming often gives a false sense of correctness. Transitioning from superficial reading to "
            "step-by-step arithmetic re-derivation and explicit database citation searches is strongly recommended."
        )
    elif not is_high_vb and is_high_perf:
        zone_id = "CALIB_Q3"
        zone_title = "Cautious Skeptic (Latent Verifier)"
        tagline = "Modest self-reported verification habits combined with strong objective accuracy."
        alignment_summary = (
            f"Your demonstrated verification accuracy ({task_acc:.1%}) substantially exceeded your self-reported "
            f"verification habits (VB = {vb_score:.2f}, {vb_percentile:.1f}th percentile). "
            f"Exploratory Discrepancy Index: Delta = {delta_calib:.2f}."
        )
        interpretation = (
            "You demonstrated high critical acuity when challenged with specific academic scenarios, successfully identifying "
            "errors despite rating your routine verification habits modestly on the survey. This may indicate healthy intellectual "
            "humility or that you naturally apply strong critical reasoning during coursework without viewing it as a separate 'verification task'. "
            "Formalizing your intuitive scrutiny into a consistent, documented checklist will further strengthen your academic workflow."
        )
    else:  # not is_high_vb and not is_high_perf
        zone_id = "CALIB_Q4"
        zone_title = "Vulnerable / Disengaged Verifier"
        tagline = "Lower self-reported verification frequency and lower accuracy on controlled error tasks."
        alignment_summary = (
            f"Both self-reported verification (VB = {vb_score:.2f}, below median) and demonstrated verification "
            f"accuracy ({task_acc:.1%}) are in the lower distribution tier. "
            "This combination indicates vulnerability to adopting incorrect AI outputs."
        )
        interpretation = (
            "You report infrequent cross-checking of AI-generated answers and missed several simulated errors during the practical "
            "assessment. If combined with high trust in AI, this pattern creates substantial reliance risk, as errors and fabricated "
            "claims can pass unnoticed into assignments and exam preparation. Establishing a basic 'Cite & Trace' routine is critical."
        )

    # 6. Contextualize with Algorithmic Trust (AT) and AI Dependence (AD)
    if at_score >= 3.60 and ad_score >= 3.40 and task_acc < 0.70:
        trust_risk_level = "High Reliance Vulnerability"
        trust_context_narrative = (
            f"Critical Risk Combination: You exhibit high Algorithmic Trust (AT = {at_score:.2f}) and high AI Dependence (AD = {ad_score:.2f}), "
            f"paired with below-benchmark verification task performance ({task_acc:.1%}). In our empirical SEM model, AT strongly predicts "
            "habitual dependence (beta = +0.428), while trust alone does not stimulate verification (beta = -0.014). "
            "Relying heavily on AI assistance while failing to catch errors directly impairs academic retention and exam readiness."
        )
    elif at_score >= 3.60 and task_acc >= 0.70:
        trust_risk_level = "Calibrated Trust"
        trust_context_narrative = (
            f"Your elevated Algorithmic Trust (AT = {at_score:.2f}) is backed by demonstrated evaluative skill ({task_acc:.1%} accuracy). "
            "You trust AI outputs where appropriate while possessing the critical discernment needed to detect occasional errors."
        )
    elif at_score < 3.0 and task_acc < 0.70:
        trust_risk_level = "General Skepticism without Evaluative Precision"
        trust_context_narrative = (
            f"While you report low trust in AI (AT = {at_score:.2f}), your task accuracy ({task_acc:.1%}) indicates difficulty in distinguishing "
            "true errors from valid derivations. Developing specific domain criteria for checking will help you evaluate claims objectively."
        )
    else:
        trust_risk_level = "Moderate Autonomy"
        trust_context_narrative = (
            f"Your trust (AT = {at_score:.2f}) and dependence (AD = {ad_score:.2f}) levels fall within typical cohort ranges relative to "
            f"your task accuracy ({task_acc:.1%})."
        )

    return {
        "metrics": {
            "self_reported_vb": round(vb_score, 2),
            "self_reported_vb_mean": round(vb_score, 2),
            "self_reported_vb_percentile": round(vb_percentile, 1),
            "vb_percentile": round(vb_percentile, 1),
            "self_reported_vb_z": round(vb_z, 2),
            "normalized_vb": round(vb_norm, 3),
            "normalized_vb_minmax": round(vb_norm, 3),
            "task_accuracy": round(task_acc, 3),
            "task_accuracy_pct": round(task_acc * 100.0, 1),
            "task_recall": round(task_recall, 3),
            "task_precision": round(task_precision, 3),
            "rubric_pct": round(rubric_pct, 1),
            "discrepancy_index_delta": delta_calib,
        },
        "calibration_zone": {
            "id": zone_id,
            "zone_id": zone_id,
            "title": zone_title,
            "zone_title": zone_title,
            "tagline": tagline,
        },
        "alignment_summary": alignment_summary,
        "detailed_interpretation": interpretation,
        "trust_dependence_context": {
            "risk_level": trust_risk_level,
            "risk_category": trust_risk_level,
            "at_score": round(at_score, 2),
            "ad_score": round(ad_score, 2),
            "narrative": trust_context_narrative,
            "description": trust_context_narrative,
        },
        "boundaries_used": {
            "vb_median": vb_median,
            "task_benchmark": 0.70,
            "formula": "Delta_calib = ((VB - 1.0)/4.0) - Task_Accuracy",
        },
        "limitations_and_assumptions": (
            "Scientific Limitations Notice: The Discrepancy Index (Delta) is an exploratory research metric comparing "
            "self-reported behavioral intention against performance on 8 specific university scenarios. It is not an "
            "experimentally validated psychometric construct and must not be used as a clinical diagnostic label."
        ),
    }
