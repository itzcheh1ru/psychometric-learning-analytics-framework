"""
app/services/sem_analysis/schemas.py

Research model specification and schema definitions for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).

This file defines:
- Latent construct metadata (AT, PU, VB, AD, LC)
- Questionnaire survey items with exact academic wording (T1–T4, PU1–PU4, V1–V3, AD1–AD4, LC1–LC4)
- Hypothesized structural relationships and mediation pathways
- Planned evaluation metric thresholds
- Reverse-coding definitions
"""

from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# Survey Item Definitions & Exact Questionnaire Wording                       #
# --------------------------------------------------------------------------- #

SURVEY_ITEMS: Dict[str, Dict[str, Any]] = {
    # 1. Algorithmic Trust (AT)
    "T1": {
        "construct": "AT",
        "code": "T1",
        "wording": "I trust the accuracy and reliability of AI-generated responses for my learning tasks.",
        "reverse_coded": False,
    },
    "T2": {
        "construct": "AT",
        "code": "T2",
        "wording": "I believe Generative AI provides dependable information for my academic studies.",
        "reverse_coded": False,
    },
    "T3": {
        "construct": "AT",
        "code": "T3",
        "wording": "I feel confident relying on GenAI explanations when learning challenging topics.",
        "reverse_coded": False,
    },
    "T4": {
        "construct": "AT",
        "code": "T4",
        "wording": "Overall, I consider Generative AI systems to be trustworthy academic learning tools.",
        "reverse_coded": False,
    },
    # 2. Perceived Usefulness (PU)
    "PU1": {
        "construct": "PU",
        "code": "PU1",
        "wording": "Using Generative AI enhances my academic productivity and study speed.",
        "reverse_coded": False,
    },
    "PU2": {
        "construct": "PU",
        "code": "PU2",
        "wording": "Using Generative AI helps me comprehend difficult concepts more effectively.",
        "reverse_coded": False,
    },
    "PU3": {
        "construct": "PU",
        "code": "PU3",
        "wording": "Using Generative AI improves the overall quality of my academic coursework.",
        "reverse_coded": False,
    },
    "PU4": {
        "construct": "PU",
        "code": "PU4",
        "wording": "Overall, I find Generative AI useful in supporting my university studies.",
        "reverse_coded": False,
    },
    # 3. Verification Behaviour (VB)
    "V1": {
        "construct": "VB",
        "code": "V1",
        "wording": "I cross-check GenAI-generated answers with academic textbooks, slides, or verified papers.",
        "reverse_coded": False,
    },
    "V2": {
        "construct": "VB",
        "code": "V2",
        "wording": "I critically inspect code, reasoning, or references provided by GenAI before accepting them.",
        "reverse_coded": False,
    },
    "V3": {
        "construct": "VB",
        "code": "V3",
        "wording": "I compare multiple AI prompts or search engine sources to confirm accuracy.",
        "reverse_coded": False,
    },
    # 4. Autonomy / AI Dependence (AD)
    "AD1": {
        "construct": "AD",
        "code": "AD1",
        "wording": "I feel dependent on Generative AI to complete my regular university coursework.",
        "reverse_coded": False,
    },
    "AD2": {
        "construct": "AD",
        "code": "AD2",
        "wording": "I hesitate to start academic problem-solving without first consulting Generative AI.",
        "reverse_coded": False,
    },
    "AD3": {
        "construct": "AD",
        "code": "AD3",
        "wording": "I find it difficult to complete assignments without assistance from Generative AI tools.",
        "reverse_coded": False,
    },
    "AD4": {
        "construct": "AD",
        "code": "AD4",
        "wording": "I can independently analyze and solve coursework problems without using Generative AI.",
        "reverse_coded": True,  # Autonomy item in dependence scale -> Reverse-coded AD4_R = (6 - score)
    },
    # 5. Learning Control / Metacognition (LC)
    "LC1": {
        "construct": "LC",
        "code": "LC1",
        "wording": "I maintain active cognitive control over my own learning processes and strategies.",
        "reverse_coded": False,
    },
    "LC2": {
        "construct": "LC",
        "code": "LC2",
        "wording": "I critically reflect on my understanding rather than passively accepting GenAI answers.",
        "reverse_coded": False,
    },
    "LC3": {
        "construct": "LC",
        "code": "LC3",
        "wording": "I consciously set my own learning goals and monitor my progress independently.",
        "reverse_coded": False,
    },
    "LC4": {
        "construct": "LC",
        "code": "LC4",
        "wording": "I am confident in my own ability to master subject concepts without constant GenAI intervention.",
        "reverse_coded": False,
    },
}

# --------------------------------------------------------------------------- #
# Latent Construct Metadata                                                   #
# --------------------------------------------------------------------------- #

CONSTRUCTS: List[Dict[str, Any]] = [
    {
        "code": "AT",
        "name": "Algorithmic Trust",
        "role": "Antecedent Construct",
        "items": ["T1", "T2", "T3", "T4"],
        "description": (
            "Represents students' trust in the reliability, consistency "
            "and usefulness of Generative AI outputs for academic support."
        ),
    },
    {
        "code": "PU",
        "name": "Perceived Usefulness",
        "role": "Antecedent Construct",
        "items": ["PU1", "PU2", "PU3", "PU4"],
        "description": (
            "Represents students' perceptions of the usefulness of "
            "Generative AI for supporting academic learning activities."
        ),
    },
    {
        "code": "VB",
        "name": "Verification Behaviour",
        "role": "Behavioural Mechanism (Mediator)",
        "items": ["V1", "V2", "V3"],
        "description": (
            "Represents behaviours used to verify, review, compare or "
            "critically evaluate AI-generated academic information."
        ),
    },
    {
        "code": "AD",
        "name": "AI Dependence",
        "role": "Learning / Reliance Outcome",
        "items": ["AD1", "AD2", "AD3", "AD4"],
        "description": (
            "Represents reliance on Generative AI during academic "
            "learning and task completion."
        ),
    },
    {
        "code": "LC",
        "name": "Learning Confidence",
        "role": "Learning / Reliance Outcome",
        "items": ["LC1", "LC2", "LC3", "LC4"],
        "description": (
            "Represents students' confidence in understanding and "
            "completing learning activities within GenAI-assisted learning contexts."
        ),
    },
]

# --------------------------------------------------------------------------- #
# Research Hypotheses Specification                                           #
# --------------------------------------------------------------------------- #

RESEARCH_HYPOTHESES: List[Dict[str, Any]] = [
    {
        "id": "H1",
        "path": "AT -> VB",
        "source": "AT",
        "target": "VB",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Algorithmic Trust positively influences Verification Behaviour.",
    },
    {
        "id": "H2",
        "path": "PU -> VB",
        "source": "PU",
        "target": "VB",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Perceived Usefulness positively influences Verification Behaviour.",
    },
    {
        "id": "H3",
        "path": "AT -> AD",
        "source": "AT",
        "target": "AD",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Algorithmic Trust positively influences AI Dependence.",
    },
    {
        "id": "H4",
        "path": "PU -> AD",
        "source": "PU",
        "target": "AD",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Perceived Usefulness positively influences AI Dependence.",
    },
    {
        "id": "H5",
        "path": "AT -> LC",
        "source": "AT",
        "target": "LC",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Algorithmic Trust positively influences Learning Confidence.",
    },
    {
        "id": "H6",
        "path": "PU -> LC",
        "source": "PU",
        "target": "LC",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Perceived Usefulness positively influences Learning Confidence.",
    },
    {
        "id": "H7",
        "path": "VB -> AD",
        "source": "VB",
        "target": "AD",
        "expected_direction": "-",
        "type": "Direct Structural Path",
        "description": "Verification Behaviour negatively influences AI Dependence (mitigating excessive reliance).",
    },
    {
        "id": "H8",
        "path": "VB -> LC",
        "source": "VB",
        "target": "LC",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Verification Behaviour positively influences Learning Confidence through cognitive verification.",
    },
    {
        "id": "H9",
        "path": "AT -> VB -> AD",
        "source": "AT",
        "mediator": "VB",
        "target": "AD",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the relationship between Algorithmic Trust and AI Dependence.",
    },
    {
        "id": "H10",
        "path": "AT -> VB -> LC",
        "source": "AT",
        "mediator": "VB",
        "target": "LC",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the relationship between Algorithmic Trust and Learning Confidence.",
    },
    {
        "id": "H11",
        "path": "PU -> VB -> AD",
        "source": "PU",
        "mediator": "VB",
        "target": "AD",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the relationship between Perceived Usefulness and AI Dependence.",
    },
    {
        "id": "H12",
        "path": "PU -> VB -> LC",
        "source": "PU",
        "mediator": "VB",
        "target": "LC",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the relationship between Perceived Usefulness and Learning Confidence.",
    },
]

# --------------------------------------------------------------------------- #
# Research Model Specification (Metadata Only)                                #
# --------------------------------------------------------------------------- #

MODEL_SPECIFICATION: Dict[str, Any] = {
    "constructs": [
        {"code": c["code"], "name": c["name"]} for c in CONSTRUCTS
    ],
    "items": SURVEY_ITEMS,
    "hypotheses": RESEARCH_HYPOTHESES,
    "analysis": {
        "measurement_model": "CFA",
        "structural_model": "SEM",
        "mediator": "Verification Behaviour (VB)",
        "estimation_status": "ready",
        "estimator": "MLW / ML",
    },
}

# --------------------------------------------------------------------------- #
# Planned Evaluation Metric Definitions                                       #
# --------------------------------------------------------------------------- #

PLANNED_MEASUREMENT_METRICS: List[Dict[str, str]] = [
    {
        "name": "Factor Loadings",
        "threshold": "λ ≥ 0.70",
        "status": "Calculated via CFA on uploaded data",
    },
    {
        "name": "Composite Reliability (CR)",
        "threshold": "CR ≥ 0.70",
        "status": "Calculated via CFA on uploaded data",
    },
    {
        "name": "Average Variance Extracted (AVE)",
        "threshold": "AVE ≥ 0.50",
        "status": "Calculated via CFA on uploaded data",
    },
    {
        "name": "Heterotrait-Monotrait Ratio (HTMT)",
        "threshold": "HTMT < 0.85 / 0.90",
        "status": "Calculated via CFA on uploaded data",
    },
    {
        "name": "Internal Consistency (Cronbach's α)",
        "threshold": "α ≥ 0.70",
        "status": "Calculated on survey items",
    },
]

PLANNED_STRUCTURAL_METRICS: List[Dict[str, str]] = [
    {
        "name": "Path Coefficients (β)",
        "threshold": "Standardised estimates with p-values",
        "status": "Estimated via SEM",
    },
    {
        "name": "Direct Effects",
        "threshold": "Direct antecedent-to-outcome pathways",
        "status": "Estimated via SEM",
    },
    {
        "name": "Indirect Effects",
        "threshold": "Mediated pathways via Verification Behaviour",
        "status": "Estimated via SEM",
    },
    {
        "name": "Mediation Effects",
        "threshold": "Bootstrapped mediation significance (bias-corrected CI)",
        "status": "Estimated via SEM",
    },
]

PLANNED_MODEL_FIT_METRICS: List[Dict[str, str]] = [
    {
        "name": "Chi-square / df (χ²/df)",
        "threshold": "χ²/df ≤ 3.0",
        "status": "Calculated via SEM",
    },
    {
        "name": "Comparative Fit Index (CFI)",
        "threshold": "CFI ≥ 0.90 (ideally ≥ 0.95)",
        "status": "Calculated via SEM",
    },
    {
        "name": "Tucker-Lewis Index (TLI)",
        "threshold": "TLI ≥ 0.90 (ideally ≥ 0.95)",
        "status": "Calculated via SEM",
    },
    {
        "name": "Root Mean Square Error of Approximation (RMSEA)",
        "threshold": "RMSEA ≤ 0.08 (ideally ≤ 0.05)",
        "status": "Calculated via SEM",
    },
    {
        "name": "Standardized Root Mean Square Residual (SRMR)",
        "threshold": "SRMR ≤ 0.08",
        "status": "Calculated via SEM",
    },
]
