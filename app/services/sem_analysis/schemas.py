"""
app/services/sem_analysis/schemas.py

Research model specification and schema definitions for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).

This module defines:
- Latent construct definitions (AT, PU, VB, AD, LC)
- Validated 26-item research instrument items (exact undergraduate survey wording)
- Legacy 19-item synthetic items (for backwards compatibility with unit tests)
- Hypothesized structural relationships and mediation pathways (H1–H12)
- Empirical cohort benchmark parameters (N=375)
- Model evaluation criteria and psychometric threshold definitions
"""

from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# 1. Validated 26-Item Questionnaire Survey Instrument (Exact Wording)        #
# --------------------------------------------------------------------------- #

SURVEY_ITEMS_EMPIRICAL_26: Dict[str, Dict[str, Any]] = {
    # 1. Algorithmic Trust (AT) - 6 items
    "AT1": {
        "construct": "AT",
        "code": "AT1",
        "wording": "I believe Generative AI tools provide reliable information for my academic learning activities.",
        "reverse_coded": False,
    },
    "AT2": {
        "construct": "AT",
        "code": "AT2",
        "wording": "I trust Generative AI tools because they provide consistent responses when I use them for learning tasks.",
        "reverse_coded": False,
    },
    "AT3": {
        "construct": "AT",
        "code": "AT3",
        "wording": "I believe Generative AI-generated information is generally accurate for academic purposes.",
        "reverse_coded": False,
    },
    "AT4": {
        "construct": "AT",
        "code": "AT4",
        "wording": "I trust Generative AI responses when they provide explanations or solutions to academic problems.",
        "reverse_coded": False,
    },
    "AT5": {
        "construct": "AT",
        "code": "AT5",
        "wording": "I trust Generative AI tools more when they provide clear explanations for their answers.",
        "reverse_coded": False,
    },
    "AT6": {
        "construct": "AT",
        "code": "AT6",
        "wording": "I believe Generative AI tools can be trusted to provide appropriate support for my academic tasks.",
        "reverse_coded": False,
    },
    # 2. Verification Behaviour (VB) - 5 items
    "VB1": {
        "construct": "VB",
        "code": "VB1",
        "wording": "I verify information provided by Generative AI before using it in academic work.",
        "reverse_coded": False,
    },
    "VB2": {
        "construct": "VB",
        "code": "VB2",
        "wording": "I compare Generative AI-generated answers with textbooks, lecture materials, websites, or other reliable sources.",
        "reverse_coded": False,
    },
    "VB3": {
        "construct": "VB",
        "code": "VB3",
        "wording": "I check whether Generative AI responses are accurate before accepting them.",
        "reverse_coded": False,
    },
    "VB4": {
        "construct": "VB",
        "code": "VB4",
        "wording": "I try to understand the reasoning behind Generative AI-generated answers instead of only copying the output.",
        "reverse_coded": False,
    },
    "VB5": {
        "construct": "VB",
        "code": "VB5",
        "wording": "I modify or correct Generative AI-generated content after reviewing its accuracy.",
        "reverse_coded": False,
    },
    # 3. Perceived Usefulness (PU) - 5 items
    "PU1": {
        "construct": "PU",
        "code": "PU1",
        "wording": "Using Generative AI tools improves my understanding of academic concepts and learning materials.",
        "reverse_coded": False,
    },
    "PU2": {
        "construct": "PU",
        "code": "PU2",
        "wording": "Using Generative AI tools helps me complete academic tasks more effectively.",
        "reverse_coded": False,
    },
    "PU3": {
        "construct": "PU",
        "code": "PU3",
        "wording": "Generative AI tools increase my productivity when studying or preparing academic work.",
        "reverse_coded": False,
    },
    "PU4": {
        "construct": "PU",
        "code": "PU4",
        "wording": "I find Generative AI tools useful for achieving my academic learning goals.",
        "reverse_coded": False,
    },
    "PU5": {
        "construct": "PU",
        "code": "PU5",
        "wording": "Generative AI tools help me learn difficult topics by providing explanations and examples.",
        "reverse_coded": False,
    },
    # 4. AI Dependence (AD) - 5 items
    "AD1": {
        "construct": "AD",
        "code": "AD1",
        "wording": "I rely on Generative AI tools when I face difficulties in academic tasks.",
        "reverse_coded": False,
    },
    "AD2": {
        "construct": "AD",
        "code": "AD2",
        "wording": "I frequently depend on Generative AI-generated answers when completing academic work.",
        "reverse_coded": False,
    },
    "AD3": {
        "construct": "AD",
        "code": "AD3",
        "wording": "I use Generative AI assistance instead of solving some academic problems independently.",
        "reverse_coded": False,
    },
    "AD4": {
        "construct": "AD",
        "code": "AD4",
        "wording": "Generative AI tools have become an important part of my learning process.",
        "reverse_coded": False,  # Note: Standard polarity in validated 26-item survey (higher = greater reliance)
    },
    "AD5": {
        "construct": "AD",
        "code": "AD5",
        "wording": "I find it difficult to complete some academic tasks without assistance from Generative AI tools.",
        "reverse_coded": False,
    },
    # 5. Learning Confidence (LC) - 5 items
    "LC1": {
        "construct": "LC",
        "code": "LC1",
        "wording": "Using Generative AI tools make me feel more capable of learning new academic concepts.",
        "reverse_coded": False,
    },
    "LC2": {
        "construct": "LC",
        "code": "LC2",
        "wording": "Generative AI tools help me feel more confident when solving academic problems.",
        "reverse_coded": False,
    },
    "LC3": {
        "construct": "LC",
        "code": "LC3",
        "wording": "I feel more capable of completing academic tasks after receiving support from Generative AI tools.",
        "reverse_coded": False,
    },
    "LC4": {
        "construct": "LC",
        "code": "LC4",
        "wording": "I feel more confident in my ability to complete academic tasks after using Generative AI support.",
        "reverse_coded": False,
    },
    "LC5": {
        "construct": "LC",
        "code": "LC5",
        "wording": "Using Generative AI tools helps me approach challenging academic tasks with greater confidence.",
        "reverse_coded": False,
    },
}

# --------------------------------------------------------------------------- #
# 2. Legacy 19-Item Items (Preserved for Unit Test & Synthetic Demo Compat)   #
# --------------------------------------------------------------------------- #

SURVEY_ITEMS_LEGACY_19: Dict[str, Dict[str, Any]] = {
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
}

# Combined dictionary: primary 26 items plus legacy aliases
SURVEY_ITEMS: Dict[str, Dict[str, Any]] = {
    **SURVEY_ITEMS_EMPIRICAL_26,
    **SURVEY_ITEMS_LEGACY_19,
}

# --------------------------------------------------------------------------- #
# 3. Latent Construct Metadata                                                #
# --------------------------------------------------------------------------- #

CONSTRUCTS: List[Dict[str, Any]] = [
    {
        "code": "AT",
        "name": "Algorithmic Trust",
        "role": "Antecedent Construct",
        "items": ["AT1", "AT2", "AT3", "AT4", "AT5", "AT6"],
        "legacy_items": ["T1", "T2", "T3", "T4"],
        "description": (
            "Represents students' subjective confidence in the reliability, accuracy, "
            "and consistency of Generative AI outputs for academic tasks."
        ),
    },
    {
        "code": "PU",
        "name": "Perceived Usefulness",
        "role": "Antecedent Construct",
        "items": ["PU1", "PU2", "PU3", "PU4", "PU5"],
        "legacy_items": ["PU1", "PU2", "PU3", "PU4"],
        "description": (
            "Represents students' subjective appraisal of how effectively GenAI tools "
            "enhance productivity, conceptual comprehension, and academic workflow."
        ),
    },
    {
        "code": "VB",
        "name": "Verification Behaviour",
        "role": "Behavioural Mechanism (Mediator)",
        "items": ["VB1", "VB2", "VB3", "VB4", "VB5"],
        "legacy_items": ["V1", "V2", "V3"],
        "description": (
            "Represents self-reported behaviours used to cross-reference, evaluate, "
            "and critically scrutinize AI-generated content before academic adoption."
        ),
    },
    {
        "code": "AD",
        "name": "AI Dependence",
        "role": "Learning / Reliance Outcome",
        "items": ["AD1", "AD2", "AD3", "AD4", "AD5"],
        "legacy_items": ["AD1", "AD2", "AD3", "AD4"],
        "description": (
            "Represents self-reported academic reliance on Generative AI tools and perceived "
            "difficulty in completing coursework independently without AI intervention."
        ),
    },
    {
        "code": "LC",
        "name": "Learning Confidence",
        "role": "Learning / Reliance Outcome",
        "items": ["LC1", "LC2", "LC3", "LC4", "LC5"],
        "legacy_items": ["LC1", "LC2", "LC3", "LC4"],
        "description": (
            "Represents students' self-efficacy and confidence in understanding concepts "
            "and completing challenging academic tasks within AI-supported environments."
        ),
    },
]

# --------------------------------------------------------------------------- #
# 4. Research Hypotheses Specification                                        #
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
        "description": "Verification Behaviour negatively influences AI Dependence (hypothesized critical mitigating role).",
    },
    {
        "id": "H8",
        "path": "VB -> LC",
        "source": "VB",
        "target": "LC",
        "expected_direction": "+",
        "type": "Direct Structural Path",
        "description": "Verification Behaviour positively influences Learning Confidence through metacognitive review.",
    },
    {
        "id": "H9",
        "path": "AT -> VB -> AD",
        "source": "AT",
        "mediator": "VB",
        "target": "AD",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the structural relationship between Algorithmic Trust and AI Dependence.",
    },
    {
        "id": "H10",
        "path": "AT -> VB -> LC",
        "source": "AT",
        "mediator": "VB",
        "target": "LC",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the structural relationship between Algorithmic Trust and Learning Confidence.",
    },
    {
        "id": "H11",
        "path": "PU -> VB -> AD",
        "source": "PU",
        "mediator": "VB",
        "target": "AD",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the structural relationship between Perceived Usefulness and AI Dependence.",
    },
    {
        "id": "H12",
        "path": "PU -> VB -> LC",
        "source": "PU",
        "mediator": "VB",
        "target": "LC",
        "expected_direction": "Mediated",
        "type": "Indirect Mediation Path",
        "description": "Verification Behaviour mediates the structural relationship between Perceived Usefulness and Learning Confidence.",
    },
]

# --------------------------------------------------------------------------- #
# 5. Empirical Cohort Normative Parameters (N = 375 Consented Students)       #
# --------------------------------------------------------------------------- #

EMPIRICAL_COHORT_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "sample_size": 375,
    "constructs": {
        "AT": {
            "name": "Algorithmic Trust",
            "mean": 3.310,
            "sd": 0.742,
            "median": 3.333,
            "q1": 2.833,
            "q3": 3.833,
            "cronbach_alpha": 0.858,
            "composite_reliability": 0.858,
            "ave": 0.502,
            "sqrt_ave": 0.709,
            "factor_loadings": {
                "AT1": 0.635,
                "AT2": 0.772,
                "AT3": 0.743,
                "AT4": 0.682,
                "AT5": 0.724,
                "AT6": 0.688,
            },
        },
        "VB": {
            "name": "Verification Behaviour",
            "mean": 3.708,
            "sd": 0.672,
            "median": 3.800,
            "q1": 3.200,
            "q3": 4.200,
            "cronbach_alpha": 0.786,
            "composite_reliability": 0.787,
            "ave": 0.426,
            "sqrt_ave": 0.652,
            "factor_loadings": {
                "VB1": 0.611,
                "VB2": 0.610,
                "VB3": 0.624,
                "VB4": 0.692,
                "VB5": 0.718,
            },
        },
        "PU": {
            "name": "Perceived Usefulness",
            "mean": 3.777,
            "sd": 0.636,
            "median": 3.800,
            "q1": 3.400,
            "q3": 4.200,
            "cronbach_alpha": 0.748,
            "composite_reliability": 0.748,
            "ave": 0.373,
            "sqrt_ave": 0.611,
            "factor_loadings": {
                "PU1": 0.559,
                "PU2": 0.607,
                "PU3": 0.582,
                "PU4": 0.662,
                "PU5": 0.639,
            },
        },
        "AD": {
            "name": "AI Dependence",
            "mean": 3.091,
            "sd": 0.880,
            "median": 3.000,
            "q1": 2.400,
            "q3": 3.800,
            "cronbach_alpha": 0.868,
            "composite_reliability": 0.869,
            "ave": 0.570,
            "sqrt_ave": 0.755,
            "factor_loadings": {
                "AD1": 0.738,
                "AD2": 0.762,
                "AD3": 0.740,
                "AD4": 0.789,
                "AD5": 0.744,
            },
        },
        "LC": {
            "name": "Learning Confidence",
            "mean": 3.596,
            "sd": 0.677,
            "median": 3.600,
            "q1": 3.200,
            "q3": 4.000,
            "cronbach_alpha": 0.773,
            "composite_reliability": 0.773,
            "ave": 0.407,
            "sqrt_ave": 0.638,
            "factor_loadings": {
                "LC1": 0.605,
                "LC2": 0.704,
                "LC3": 0.655,
                "LC4": 0.636,
                "LC5": 0.583,
            },
        },
    },
    "model_fit": {
        "chi2": 354.316,
        "df": 290,
        "chi2_df": 1.222,
        "cfi": 0.979,
        "tli": 0.977,
        "rmsea": 0.024,
    },
}

# --------------------------------------------------------------------------- #
# 6. Research Model Specification (Metadata for APIs & UI)                     #
# --------------------------------------------------------------------------- #

MODEL_SPECIFICATION: Dict[str, Any] = {
    "constructs": [
        {"code": c["code"], "name": c["name"], "items": c.get("legacy_items", c["items"])} for c in CONSTRUCTS
    ],
    "items": {
        # Preserved 19 items for specification API contract compatibility
        "T1": SURVEY_ITEMS_LEGACY_19["T1"],
        "T2": SURVEY_ITEMS_LEGACY_19["T2"],
        "T3": SURVEY_ITEMS_LEGACY_19["T3"],
        "T4": SURVEY_ITEMS_LEGACY_19["T4"],
        "PU1": SURVEY_ITEMS_EMPIRICAL_26["PU1"],
        "PU2": SURVEY_ITEMS_EMPIRICAL_26["PU2"],
        "PU3": SURVEY_ITEMS_EMPIRICAL_26["PU3"],
        "PU4": SURVEY_ITEMS_EMPIRICAL_26["PU4"],
        "V1": SURVEY_ITEMS_LEGACY_19["V1"],
        "V2": SURVEY_ITEMS_LEGACY_19["V2"],
        "V3": SURVEY_ITEMS_LEGACY_19["V3"],
        "AD1": SURVEY_ITEMS_EMPIRICAL_26["AD1"],
        "AD2": SURVEY_ITEMS_EMPIRICAL_26["AD2"],
        "AD3": SURVEY_ITEMS_EMPIRICAL_26["AD3"],
        "AD4": {
            "construct": "AD",
            "code": "AD4",
            "wording": "I can independently analyze and solve coursework problems without using Generative AI.",
            "reverse_coded": True,
        },
        "LC1": SURVEY_ITEMS_EMPIRICAL_26["LC1"],
        "LC2": SURVEY_ITEMS_EMPIRICAL_26["LC2"],
        "LC3": SURVEY_ITEMS_EMPIRICAL_26["LC3"],
        "LC4": SURVEY_ITEMS_EMPIRICAL_26["LC4"],
    },
    "empirical_items_26": SURVEY_ITEMS_EMPIRICAL_26,
    "hypotheses": RESEARCH_HYPOTHESES,
    "analysis": {
        "measurement_model": "CFA (Confirmatory Factor Analysis)",
        "structural_model": "SEM (Structural Equation Modeling)",
        "mediator": "Verification Behaviour (VB)",
        "estimation_status": "ready",
        "estimator": "MLW / Maximum Likelihood Wishart (semopy / lavaan)",
    },
}

# --------------------------------------------------------------------------- #
# 7. Evaluation Metric Criteria Definitions                                   #
# --------------------------------------------------------------------------- #

PLANNED_MEASUREMENT_METRICS: List[Dict[str, str]] = [
    {
        "name": "Factor Loadings",
        "threshold": "λ ≥ 0.70 (acceptable ≥ 0.50 for established psychometric scales)",
        "status": "Calculated via CFA on survey data",
    },
    {
        "name": "Composite Reliability (CR)",
        "threshold": "CR ≥ 0.70",
        "status": "Calculated via CFA on survey data",
    },
    {
        "name": "Average Variance Extracted (AVE)",
        "threshold": "AVE ≥ 0.50 (if CR ≥ 0.70, AVE ≥ 0.40 acceptable per Fornell-Larcker, 1981)",
        "status": "Calculated via CFA on survey data",
    },
    {
        "name": "Heterotrait-Monotrait Ratio (HTMT)",
        "threshold": "HTMT < 0.85 / 0.90",
        "status": "Calculated via CFA on survey data",
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
        "threshold": "Bootstrapped mediation significance (95% bias-corrected percentile CI)",
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
