"""
app/services/sem_analysis/profile_service.py

Explainable Behavioural Interpretation Service for Component 2:
Algorithmic Trust & Verification Analysis.

Methodological Principles:
1. Continuous Profiles over Rigid Diagnoses:
   Characterizes self-reported behavioural tendencies along continuous
   dimensions rather than assigning clinical or psychological risk labels.
2. SEM-Informed Contextual Interpretation:
   Interprets the interaction of Algorithmic Trust (AT) and Verification Behaviour (VB)
   in light of the empirical SEM structural paths (e.g. AT -> AD beta = 0.428; PU -> VB beta = 0.291).
3. Descriptive Reference Conventions:
   The four-quadrant trust-verification boundaries use empirical cohort medians
   (AT median = 3.33, VB median = 3.80) as descriptive conventions, not clinically validated cutoffs.
4. Multidimensional Contextualization:
   Integrates AI Dependence (AD), Perceived Usefulness (PU), and Learning Confidence (LC)
   as complementary contextual dimensions.
"""

from typing import Any, Dict, List, Optional
from app.services.sem_analysis.schemas import EMPIRICAL_COHORT_BENCHMARKS


def evaluate_behavioral_profile(
    construct_scores: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate an explainable, continuous behavioural interpretation for an individual student.

    Args:
        construct_scores: Output from scoring_service.calculate_individual_scores,
                          containing mean_score, percentile_rank, quartile_band, etc. for
                          AT, VB, PU, AD, and LC.

    Returns:
        Structured interpretation dictionary containing:
        - quadrant_id: "Q1" | "Q2" | "Q3" | "Q4"
        - profile_title: Concise descriptive label
        - summary: High-level plain-language summary of the self-reported profile
        - detailed_interpretation: Multi-paragraph explainable narrative
        - sem_structural_insights: Academic alignment with validated structural equation model paths
        - dependence_context: Analysis of the student's AI Dependence level
        - confidence_context: Analysis of Learning Confidence in relation to Perceived Usefulness
        - boundaries_used: Transparently documented median reference boundaries
        - non_diagnostic_notice: Explicit scientific disclaimer
    """
    # Extract unweighted construct means
    at_score = construct_scores.get("AT", {}).get("mean_score", 3.0)
    vb_score = construct_scores.get("VB", {}).get("mean_score", 3.0)
    ad_score = construct_scores.get("AD", {}).get("mean_score", 3.0)
    pu_score = construct_scores.get("PU", {}).get("mean_score", 3.0)
    lc_score = construct_scores.get("LC", {}).get("mean_score", 3.0)

    # Empirical cohort median reference conventions
    benchmarks = EMPIRICAL_COHORT_BENCHMARKS.get("constructs", {})
    at_median = benchmarks.get("AT", {}).get("median", 3.33)
    vb_median = benchmarks.get("VB", {}).get("median", 3.80)
    ad_median = benchmarks.get("AD", {}).get("median", 3.20)
    pu_median = benchmarks.get("PU", {}).get("median", 3.80)
    lc_median = benchmarks.get("LC", {}).get("median", 3.60)

    is_high_at = at_score >= at_median
    is_high_vb = vb_score >= vb_median
    is_high_ad = ad_score >= ad_median
    is_high_pu = pu_score >= pu_median
    is_high_lc = lc_score >= lc_median

    # 1. Determine Trust-Verification Quadrant (Descriptive Convention)
    if is_high_at and is_high_vb:
        quadrant_id = "Q1"
        profile_title = "Calibrated & Discerning AI Learner"
        tagline = "Balanced high trust paired with active verification routines."
        summary = (
            f"Your responses indicate relatively high confidence in Generative AI tools (AT = {at_score:.2f}) "
            f"combined with above-average verification practices (VB = {vb_score:.2f}). "
            "You leverage AI utility while actively cross-referencing information against verified academic sources."
        )
        detailed_interpretation = (
            "You report a well-calibrated study strategy where trust in AI output is tempered by proactive scrutiny. "
            "You do not passively accept generated answers; instead, you inspect reasoning, check factual accuracy, "
            "and compare outputs against course lecture materials or textbooks. This combination preserves academic "
            "agency while allowing you to benefit from the efficiency gains of Generative AI."
        )
        sem_insight = (
            "In our empirical structural model, Algorithmic Trust strongly predicts AI Dependence (beta = +0.428), "
            "while Trust alone does not stimulate verification (beta = -0.014). Your profile successfully avoids the "
            "dependence vulnerability because your active verification habits provide an empirical counterweight, "
            "allowing you to benefit from Perceived Usefulness without uncritical reliance."
        )

    elif is_high_at and not is_high_vb:
        quadrant_id = "Q2"
        profile_title = "Vulnerable Over-Truster (High Reliance Risk)"
        tagline = "High algorithmic trust with lower-than-average verification frequency."
        summary = (
            f"Your responses indicate high confidence in Generative AI outputs (AT = {at_score:.2f}) "
            f"paired with below-median verification habits (VB = {vb_score:.2f}). "
            "This self-reported pattern suggests a tendency to accept AI responses at face value without systematic cross-checking."
        )
        detailed_interpretation = (
            "You place substantial faith in the dependability and accuracy of GenAI explanations, but report "
            "infrequent comparison of these answers against authoritative textbooks, papers, or course materials. "
            "While this enables rapid coursework completion, it leaves you vulnerable to subtle conceptual hallucinations, "
            "incorrect reasoning chains, and fabricated citations that can undermine deep conceptual understanding."
        )
        sem_insight = (
            "Empirical SEM analysis reveals that Algorithmic Trust has a strong direct effect on AI Dependence (beta = +0.428, p < 0.001), "
            "yet does NOT stimulate Verification Behaviour (beta = -0.014, p = 0.836). In the absence of rigorous verification, "
            "high trust directly accelerates habitual dependence, as confirmed by our structural path estimates."
        )

    elif not is_high_at and is_high_vb:
        quadrant_id = "Q3"
        profile_title = "Vigilant Skeptical Learner"
        tagline = "Critical scrutiny with cautious, low subjective trust."
        summary = (
            f"Your responses indicate cautious, lower-than-average trust in AI tools (AT = {at_score:.2f}) "
            f"coupled with high active verification behaviour (VB = {vb_score:.2f}). "
            "You maintain strong critical distance and independently scrutinize AI responses."
        )
        detailed_interpretation = (
            "You approach Generative AI with a skeptical mindset, maintaining rigorous verification habits. "
            "You frequently cross-check statements, inspect proofs, and verify claims across textbooks and lecture slides. "
            "This safeguards your independent problem-solving skills and minimizes error adoption. However, overly low trust "
            "might lead you to spend excessive time verifying routine conceptual explanations where AI is dependable."
        )
        sem_insight = (
            "Our structural model confirms that Verification Behaviour is driven primarily by Perceived Usefulness (beta = +0.291, p < 0.001) "
            "rather than blind trust. Your profile exemplifies this: you recognize where tools can assist, yet maintain the active verification "
            "essential for cognitive retention."
        )

    else:  # not is_high_at and not is_high_vb
        quadrant_id = "Q4"
        profile_title = "Disengaged / Under-Utilizing Learner"
        tagline = "Low trust and low verification, suggesting minimal AI academic integration."
        summary = (
            f"Your responses indicate both low subjective trust in Generative AI (AT = {at_score:.2f}) "
            f"and low engagement in verification practices (VB = {vb_score:.2f}). "
            "This pattern reflects limited integration of AI tools into your academic study routines."
        )
        detailed_interpretation = (
            "You currently make limited use of Generative AI for academic tasks and rarely verify outputs, likely because "
            "you prefer traditional learning methods or doubt the utility of conversational AI in your discipline. "
            "While this completely protects you from AI dependence, developing structured verification literacy and learning "
            "how to prompt for conceptual explanations could expand your study toolkit."
        )
        sem_insight = (
            "The SEM baseline shows that Perceived Usefulness is the critical engine for both Verification (beta = +0.291) "
            "and Learning Confidence (beta = +0.292). In your profile, low perceived utility correlates with minimal verification engagement."
        )

    # 2. Contextualize AI Dependence (AD)
    if ad_score > 3.80:
        dependence_level = "High"
        dependence_text = (
            f"Your reported AI Dependence (AD = {ad_score:.2f}, > 75th percentile) is notably higher than the cohort average (mean = 3.09). "
            "You report relying on AI when facing academic difficulties and finding it challenging to complete assignments without AI support. "
            "Pairing this dependence with rigorous verification and scheduled independent problem-solving is strongly advised."
        )
    elif ad_score < 2.60:
        dependence_level = "Low"
        dependence_text = (
            f"Your reported AI Dependence (AD = {ad_score:.2f}, < 25th percentile) indicates high problem-solving autonomy. "
            "You complete academic tasks independently and treat AI as an optional resource rather than a necessary crutch."
        )
    else:
        dependence_level = "Moderate"
        dependence_text = (
            f"Your reported AI Dependence (AD = {ad_score:.2f}) falls within the typical cohort interquartile range (2.60 - 3.80). "
            "You use AI assistance regularly for challenging work while maintaining standard independent coursework completion."
        )

    # 3. Contextualize Learning Confidence (LC) & Perceived Usefulness (PU)
    if is_high_pu and not is_high_lc:
        confidence_text = (
            f"You perceive Generative AI as highly useful (PU = {pu_score:.2f}, above median), yet report lower self-reported "
            f"learning confidence (LC = {lc_score:.2f}, below median). This discrepancy suggests that while AI tools help you complete tasks, "
            "you may feel that conceptual mastery remains externalized in the AI rather than fully integrated into your own memory."
        )
    elif is_high_pu and is_high_lc:
        confidence_text = (
            f"Both Perceived Usefulness (PU = {pu_score:.2f}) and Learning Confidence (LC = {lc_score:.2f}) are elevated. "
            "In our SEM model, PU directly stimulates Learning Confidence (beta = +0.292, p < 0.001). You appear to successfully "
            "translate AI assistance into genuine personal confidence and academic capability."
        )
    elif not is_high_pu and is_high_lc:
        confidence_text = (
            f"You report high personal learning confidence (LC = {lc_score:.2f}) despite low reliance on AI usefulness (PU = {pu_score:.2f}). "
            "This points to strong intrinsic academic self-efficacy built upon independent study strategies."
        )
    else:
        confidence_text = (
            f"Both Perceived Usefulness (PU = {pu_score:.2f}) and Learning Confidence (LC = {lc_score:.2f}) are below cohort medians. "
            "Engaging with structured, step-by-step AI explanations for difficult topics may help build learning confidence."
        )

    return {
        "quadrant_id": quadrant_id,
        "profile_title": profile_title,
        "tagline": tagline,
        "summary": summary,
        "detailed_interpretation": detailed_interpretation,
        "sem_structural_insights": sem_insight,
        "dependence_context": {
            "level": dependence_level,
            "score": round(ad_score, 2),
            "text": dependence_text,
        },
        "confidence_context": {
            "score": round(lc_score, 2),
            "pu_score": round(pu_score, 2),
            "text": confidence_text,
        },
        "boundaries_used": {
            "at_median": at_median,
            "vb_median": vb_median,
            "ad_median": ad_median,
            "pu_median": pu_median,
            "lc_median": lc_median,
            "note": "Reference boundaries derived from the median scores of N=375 undergraduate participants.",
        },
        "non_diagnostic_notice": (
            "Descriptive Research Notice: This profile reflects self-reported behavioural tendencies relative to an empirical "
            "undergraduate student reference distribution. It is not an experimental outcome, psychometric diagnostic assessment, "
            "or indicator of cognitive deficit."
        ),
    }
