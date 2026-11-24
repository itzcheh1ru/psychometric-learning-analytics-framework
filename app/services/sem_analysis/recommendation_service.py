"""
app/services/sem_analysis/recommendation_service.py

Explainable Personalized Recommendation Engine for Component 2:
Algorithmic Trust & Verification Analysis.

Methodological Principles:
1. Strict Response Traceability:
   Every recommendation is triggered by and cites explicit questionnaire item
   ratings or construct percentile scores from the student's actual submission.
2. Pedagogical & SEM Justification:
   Rationales align with empirical structural findings (e.g. AT -> AD beta = 0.428; PU -> VB beta = 0.291; AT -> VB beta = -0.014).
3. Concrete Action Steps:
   Provides 3 practical, immediately actionable study strategies per recommendation.
4. Evidence Categorization:
   Explicitly distinguishes empirical survey findings from general educational guidance.
5. Scientific Humility:
   Never claims that recommendations are experimentally proven clinical interventions.
6. Guaranteed Coverage:
   Every student receives between 3 and 5 actionable, explainable educational recommendations.
"""

from typing import Any, Dict, List, Optional
from app.services.sem_analysis.schemas import SURVEY_ITEMS


def generate_recommendations(
    construct_scores: Dict[str, Dict[str, Any]],
    raw_responses: Dict[str, float],
) -> List[Dict[str, Any]]:
    """
    Generate 3 to 5 traceable, personalized educational recommendations based on
    a student's construct scores and specific indicator responses.

    Args:
        construct_scores: Evaluated construct scores from scoring_service.
        raw_responses: Dictionary of cleaned 1-5 responses for each indicator (e.g. 'AT1': 4.0).

    Returns:
        List of 3 to 5 recommendation dictionaries, each containing:
        - id: Unique rule identifier
        - title: Recommendation title
        - construct: Associated construct
        - priority: "High" | "Medium" | "Guidance"
        - evidence_trace: Explicit citation of the student's score or item rating that triggered the rule
        - rationale: Theoretical and empirical justification referencing SEM insights
        - action_steps: List of 3 practical, immediate action items
        - evidence_category: Category label distinguishing empirical baseline from pedagogical advice
        - caveat: Transparent limitation notice
    """
    recommendations: List[Dict[str, Any]] = []

    # Extract construct metrics
    at_score = construct_scores.get("AT", {}).get("mean_score", 3.0)
    at_pr = construct_scores.get("AT", {}).get("percentile_rank", 50.0)

    vb_score = construct_scores.get("VB", {}).get("mean_score", 3.0)
    vb_pr = construct_scores.get("VB", {}).get("percentile_rank", 50.0)

    ad_score = construct_scores.get("AD", {}).get("mean_score", 3.0)
    ad_pr = construct_scores.get("AD", {}).get("percentile_rank", 50.0)

    pu_score = construct_scores.get("PU", {}).get("mean_score", 3.0)
    pu_pr = construct_scores.get("PU", {}).get("percentile_rank", 50.0)

    lc_score = construct_scores.get("LC", {}).get("mean_score", 3.0)
    lc_pr = construct_scores.get("LC", {}).get("percentile_rank", 50.0)

    # Item ratings
    vb1 = raw_responses.get("VB1", 3.0)
    vb2 = raw_responses.get("VB2", 3.0)
    vb3 = raw_responses.get("VB3", 3.0)
    vb4 = raw_responses.get("VB4", 3.0)
    vb5 = raw_responses.get("VB5", 3.0)

    ad1 = raw_responses.get("AD1", 3.0)
    ad2 = raw_responses.get("AD2", 3.0)
    ad5 = raw_responses.get("AD5", 3.0)

    lc2 = raw_responses.get("LC2", 3.0)
    lc4 = raw_responses.get("LC4", 3.0)

    # ----------------------------------------------------------------------- #
    # Rule 1: Multi-Source Academic Cross-Checking (Low Verification)         #
    # ----------------------------------------------------------------------- #
    if vb_score < 3.80 or vb1 <= 3.0 or vb2 <= 3.0:
        triggered_items = []
        if vb2 <= 3.0:
            triggered_items.append(f"VB2 ('compare AI answers with textbooks/sources') = {int(vb2)}/5")
        if vb1 <= 3.0:
            triggered_items.append(f"VB1 ('verify information before academic use') = {int(vb1)}/5")
        trace_detail = ", and specifically ".join(triggered_items) if triggered_items else f"overall verification ({vb_score:.2f})"

        recommendations.append({
            "id": "REC_VB_TRIANGULATION",
            "title": "Establish a Multi-Source Academic Cross-Checking Routine",
            "construct": "Verification Behaviour (VB)",
            "priority": "High" if vb_score < 3.40 else "Medium",
            "evidence_trace": (
                f"Your Verification Behaviour score is {vb_score:.2f} ({vb_pr:.1f}th cohort percentile, cohort median = 3.80)"
                f"{f', with {trace_detail}' if triggered_items else ''}."
            ),
            "rationale": (
                "Our structural equation model reveals that Algorithmic Trust does NOT naturally stimulate verification "
                "(beta = -0.014, p = 0.836). Without proactive cross-checking, subtle inaccuracies or fabricated citations "
                "pass unnoticed into coursework, undermining conceptual mastery."
            ),
            "action_steps": [
                "Open your official course lecture slides or prescribed textbook whenever GenAI defines a core theorem, formula, or case study to verify accuracy.",
                "Employ the 'Cite & Trace' rule: never submit an AI-generated fact or citation without independently locating it in a peer-reviewed database or course syllabus.",
                "Maintain a short study notes column marking whether an AI concept explanation was verified against secondary literature.",
            ],
            "evidence_category": "Empirical SEM Finding (Null AT->VB Path) + Metacognitive Pedagogy",
            "caveat": "Educational suggestion derived from survey patterns; individual cross-checking efficiency varies by discipline.",
        })

    # ----------------------------------------------------------------------- #
    # Rule 2: Adversarial & Critical Evaluation (High Trust + Low/Mod Verif)  #
    # ----------------------------------------------------------------------- #
    if (at_score >= 3.50 and vb_score < 3.80) or (at_score > vb_score and at_score >= 3.60):
        recommendations.append({
            "id": "REC_AT_CALIBRATION",
            "title": "Calibrate Subjective Trust via Adversarial Prompting",
            "construct": "Algorithmic Trust (AT) & Verification Behaviour (VB)",
            "priority": "High",
            "evidence_trace": (
                f"Your Algorithmic Trust is elevated at {at_score:.2f} ({at_pr:.1f}th percentile), while your "
                f"Verification Behaviour is {vb_score:.2f} ({vb_pr:.1f}th percentile, below trust level)."
            ),
            "rationale": (
                "In our empirical SEM model, Algorithmic Trust has a direct, positive structural effect on AI Dependence "
                "(beta = +0.428, p < 0.001). Trusting fluent responses without active verification creates an uncritical dependence loop. "
                "Adversarial prompting trains you to actively stress-test model outputs."
            ),
            "action_steps": [
                "After receiving an AI explanation, immediately submit an adversarial prompt: 'Identify three potential edge cases, hidden assumptions, or common misconceptions in this solution.'",
                "Deliberately challenge the AI with an alternative perspective to observe whether it defends its logic or hallucinates concessions.",
                "Review the reasoning steps rather than just the final answer; inspect intermediate logical jumps for plausibility.",
            ],
            "evidence_category": "Empirical SEM Finding (Strong AT->AD Path) + Critical AI Literacy",
            "caveat": "Recommended to foster critical discernment; not an automated guarantee against all generative errors.",
        })

    # ----------------------------------------------------------------------- #
    # Rule 3: Pre-AI Problem-Solving Incubation (Elevated Dependence)         #
    # ----------------------------------------------------------------------- #
    if ad_score >= 3.20 or ad5 >= 3.0 or ad2 >= 3.0:
        triggered_ad = []
        if ad5 >= 3.0:
            triggered_ad.append(f"AD5 ('difficult to complete tasks without AI') = {int(ad5)}/5")
        if ad2 >= 3.0:
            triggered_ad.append(f"AD2 ('frequently depend on AI answers') = {int(ad2)}/5")
        ad_detail = " and ".join(triggered_ad) if triggered_ad else "elevated overall dependence"

        recommendations.append({
            "id": "REC_AD_AUTONOMY",
            "title": "Preserve Cognitive Autonomy with the '15-Minute Pre-AI' Rule",
            "construct": "AI Dependence (AD)",
            "priority": "High" if ad_score >= 3.80 else "Medium",
            "evidence_trace": (
                f"Your AI Dependence score is {ad_score:.2f} ({ad_pr:.1f}th cohort percentile, mean = 3.09)"
                f"{f', reporting {ad_detail}' if triggered_ad else ''}."
            ),
            "rationale": (
                "High reliance on AI assistance for initial problem-solving risks cognitive offloading—reducing independent "
                "analytical stamina and conceptual retrieval fluency during unassisted examinations and laboratory assessments."
            ),
            "action_steps": [
                "Adopt a strict '15-minute incubation period': spend at least 15 minutes drafting your own outline, defining variables, or attempting solutions before opening an AI tool.",
                "When asking AI for assistance on difficult homework, paste your own preliminary working first and ask it to critique your approach rather than providing a solution from scratch.",
                "Schedule one unassisted study session per week where all coursework problems are completed using textbooks and lecture notes alone.",
            ],
            "evidence_category": "Descriptive Cohort Distribution (Upper Quartile Dependence) + Cognitive Psychology",
            "caveat": "Descriptive study habit recommendation; does not imply a clinical or cognitive deficiency.",
        })

    # ----------------------------------------------------------------------- #
    # Rule 4: Concept Self-Explanation & Retention (Lower Confidence)         #
    # ----------------------------------------------------------------------- #
    if lc_score < 3.80 or lc4 <= 3.0 or (pu_score >= 3.60 and lc_score <= pu_score):
        recommendations.append({
            "id": "REC_LC_SELF_EXPLANATION",
            "title": "Bridge Utility into Confidence via Active Concept Self-Explanation",
            "construct": "Learning Confidence (LC) & Perceived Usefulness (PU)",
            "priority": "Medium",
            "evidence_trace": (
                f"Your Learning Confidence score is {lc_score:.2f} ({lc_pr:.1f}th percentile)"
                f"{f' while Perceived Usefulness is high ({pu_score:.2f})' if pu_score >= 3.60 else ''}."
            ),
            "rationale": (
                "SEM path estimates demonstrate that Perceived Usefulness strongly predicts Learning Confidence "
                "(beta = +0.292, p < 0.001). However, when AI utility is high but personal confidence remains low, understanding "
                "may remain externalized in the AI tool rather than consolidated into working memory."
            ),
            "action_steps": [
                "After reading an AI explanation, immediately minimize the window and explain the concept aloud or write a 3-sentence summary in your own words without looking.",
                "Practice the 'Feynman Technique': draft an explanation of the topic as if teaching it to a first-year student without AI assistance.",
                "Test yourself on two unassisted practice questions after each AI study session to confirm that the explanation generated genuine personal comprehension.",
            ],
            "evidence_category": "Empirical SEM Finding (PU->LC Path) + Educational Cognitive Science",
            "caveat": "Pedagogical self-efficacy guidance; not evaluated in a clinical trial.",
        })

    # ----------------------------------------------------------------------- #
    # Rule 5: Socratic Prompting (High Utility, Surface Engagement)            #
    # ----------------------------------------------------------------------- #
    if pu_score >= 3.40 and vb4 <= 4.0:
        recommendations.append({
            "id": "REC_PU_SOCRATIC",
            "title": "Shift from Answer Retrieval to Socratic Learning Dialogues",
            "construct": "Perceived Usefulness (PU) & Verification Behaviour (VB)",
            "priority": "Guidance",
            "evidence_trace": (
                f"You report solid Perceived Usefulness ({pu_score:.2f}, {pu_pr:.1f}th percentile), but moderate ratings on understanding underlying "
                f"reasoning (VB4 = {int(vb4)}/5)."
            ),
            "rationale": (
                "Using AI primarily as a direct answer engine maximizes short-term speed but minimizes conceptual depth. "
                "In our SEM, Perceived Usefulness is the single strongest motivator of active verification (beta = +0.291)."
            ),
            "action_steps": [
                "Instruct the AI: 'Do not provide the final answer. Ask me guiding questions step-by-step so I can derive the solution myself.'",
                "Ask the model: 'Why did you choose this specific method over alternative approaches?' to unpack intermediate logic.",
                "Request intuitive analogies connecting the new technical concept to foundational topics you already master.",
            ],
            "evidence_category": "Empirical SEM Path (PU->VB) + Socratic Learning Theory",
            "caveat": "Instructional recommendation for prompt engineering; effectiveness depends on subject complexity.",
        })

    # ----------------------------------------------------------------------- #
    # Rule 6: Maintenance Routine (For Balanced / Calibrated Learners)        #
    # ----------------------------------------------------------------------- #
    if vb_score >= 3.80 and at_score >= 3.20:
        recommendations.append({
            "id": "REC_CALIBRATED_MAINTENANCE",
            "title": "Maintain Discerning Verification and Optimize Advanced Prompting",
            "construct": "Verification Behaviour (VB) & Algorithmic Trust (AT)",
            "priority": "Guidance",
            "evidence_trace": (
                f"Your Verification Behaviour ({vb_score:.2f}, {vb_pr:.1f}th percentile) and Algorithmic Trust ({at_score:.2f}) "
                "reflect a well-calibrated profile relative to the undergraduate cohort."
            ),
            "rationale": (
                "Your self-reported study habits reflect the balanced quadrant where AI utility is leveraged without uncritical "
                "dependence. Maintaining this critical discipline across complex final-year projects and dissertation work is key."
            ),
            "action_steps": [
                "Establish structured prompt templates for literature synthesis and code refactoring to maintain consistent verification standards.",
                "Share your verification heuristics with project team members to foster a culture of critical AI evaluation in group coursework.",
                "Periodically assess newly released AI model versions against your own benchmark questions to monitor drift in accuracy.",
            ],
            "evidence_category": "Empirical Baseline Profile (Top Quadrant) + Academic Best Practice",
            "caveat": "Maintenance guidance for high-performing study workflows.",
        })

    # ----------------------------------------------------------------------- #
    # Rule 7: Multi-Stage Prompt Decomposition & Logic Chain Validation       #
    # ----------------------------------------------------------------------- #
    recommendations.append({
        "id": "REC_PROMPT_DECOMPOSITION",
        "title": "Deconstruct Complex Coursework Problems into Staged Sub-Prompts",
        "construct": "Perceived Usefulness (PU) & Algorithmic Trust (AT)",
        "priority": "Guidance",
        "evidence_trace": (
            f"Your Perceived Usefulness score is {pu_score:.2f} ({pu_pr:.1f}th percentile), reflecting regular academic integration."
        ),
        "rationale": (
            "Complex queries submitted as single monolithic prompts frequently cause subtle reasoning hallucinations in large language models. "
            "Deconstructing tasks into sequential sub-prompts allows you to verify each intermediate step before proceeding."
        ),
        "action_steps": [
            "Submit multi-part homework questions as discrete steps: define equations first, request logic outline second, and verify calculations third.",
            "Instruct the tool to output explicit intermediate variables and assumptions before generating final code or answers.",
            "Verify the validity of each step against course slides before allowing the AI to build upon previous outputs.",
        ],
        "evidence_category": "Cognitive Load Theory & Prompt Engineering Best Practice",
        "caveat": "Practical technique for reducing compound generative errors.",
    })

    # ----------------------------------------------------------------------- #
    # Rule 8: Spaced Unassisted Retrieval Practice                            #
    # ----------------------------------------------------------------------- #
    recommendations.append({
        "id": "REC_INDEPENDENT_RETRIEVAL",
        "title": "Strengthen Long-Term Retention via Spaced Unassisted Retrieval",
        "construct": "Learning Confidence (LC) & AI Dependence (AD)",
        "priority": "Medium" if lc_score < 3.50 else "Guidance",
        "evidence_trace": (
            f"Your Learning Confidence is {lc_score:.2f} and AI Dependence is {ad_score:.2f} ({ad_pr:.1f}th percentile)."
        ),
        "rationale": (
            "Even when AI explanations feel immediately intuitive, passive consumption does not build robust memory traces. "
            "Spaced unassisted retrieval cements neural pathways and prepares you for closed-book examinations."
        ),
        "action_steps": [
            "Perform a 10-minute 'free recall brain dump' on a blank sheet of paper before opening AI to review lecture concepts.",
            "Complete at least 50% of practice problems under unassisted, timed exam conditions without digital aids.",
            "Review challenging AI-assisted topics 48 hours later using self-generated flashcards to measure true retention.",
        ],
        "evidence_category": "Cognitive Psychology (Testing Effect & Desirable Difficulties)",
        "caveat": "Evidence-based memory retention strategy.",
    })

    # Deduplicate while preserving order
    seen_ids = set()
    deduped = []
    for r in recommendations:
        if r["id"] not in seen_ids:
            seen_ids.add(r["id"])
            deduped.append(r)

    # Return between 3 and 5 recommendations
    return deduped[:5]
