"""
app/services/sem_analysis/schemas.py

Research model specification and schema definitions for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).

This file defines:
- Latent construct metadata (AT, PU, VB, AD, LC)
- Research model specification (structural relationships to test)
- Planned measurement model metrics
- Planned structural model metrics
- Planned model-fit evaluation metrics

Status: Prototype – research data collection in progress.
        No empirical SEM results or fabricated statistics are included.
"""

from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# Latent Construct Metadata                                                   #
# --------------------------------------------------------------------------- #

CONSTRUCTS: List[Dict[str, str]] = [
    {
        "code": "AT",
        "name": "Algorithmic Trust",
        "role": "Antecedent Construct",
        "description": (
            "Represents students' trust in the reliability, consistency "
            "and usefulness of Generative AI outputs for academic support."
        ),
    },
    {
        "code": "PU",
        "name": "Perceived Usefulness",
        "role": "Antecedent Construct",
        "description": (
            "Represents students' perceptions of the usefulness of "
            "Generative AI for supporting academic learning activities."
        ),
    },
    {
        "code": "VB",
        "name": "Verification Behaviour",
        "role": "Behavioural Mechanism (Mediator)",
        "description": (
            "Represents behaviours used to verify, review, compare or "
            "critically evaluate AI-generated academic information."
        ),
    },
    {
        "code": "AD",
        "name": "AI Dependence",
        "role": "Learning / Reliance Outcome",
        "description": (
            "Represents reliance on Generative AI during academic "
            "learning and task completion."
        ),
    },
    {
        "code": "LC",
        "name": "Learning Confidence",
        "role": "Learning / Reliance Outcome",
        "description": (
            "Represents students' confidence in understanding and "
            "completing learning activities within GenAI-assisted learning contexts."
        ),
    },
]

# --------------------------------------------------------------------------- #
# Research Model Specification (Metadata Only)                                #
# --------------------------------------------------------------------------- #

MODEL_SPECIFICATION: Dict[str, Any] = {
    "constructs": [
        {"code": c["code"], "name": c["name"]} for c in CONSTRUCTS
    ],
    "analysis": {
        "measurement_model": "CFA",
        "structural_model": "SEM",
        "mediation": "Verification Behaviour",
        "estimation_status": "pending",
    },
}

# --------------------------------------------------------------------------- #
# Planned Evaluation Metric Definitions (All Pending)                         #
# --------------------------------------------------------------------------- #

PLANNED_MEASUREMENT_METRICS: List[Dict[str, str]] = [
    {
        "name": "Factor Loadings",
        "threshold": "λ ≥ 0.70",
        "status": "Pending validated survey data",
    },
    {
        "name": "Composite Reliability (CR)",
        "threshold": "CR ≥ 0.70",
        "status": "Pending validated survey data",
    },
    {
        "name": "Average Variance Extracted (AVE)",
        "threshold": "AVE ≥ 0.50",
        "status": "Pending validated survey data",
    },
    {
        "name": "Heterotrait-Monotrait Ratio (HTMT)",
        "threshold": "HTMT < 0.85 / 0.90",
        "status": "Pending validated survey data",
    },
    {
        "name": "Internal Consistency (Cronbach's α)",
        "threshold": "α ≥ 0.70",
        "status": "Pending validated survey data",
    },
]

PLANNED_STRUCTURAL_METRICS: List[Dict[str, str]] = [
    {
        "name": "Path Coefficients (β)",
        "threshold": "Standardised estimates with p-values",
        "status": "Pending SEM estimation",
    },
    {
        "name": "Direct Effects",
        "threshold": "Direct antecedent-to-outcome pathways",
        "status": "Pending SEM estimation",
    },
    {
        "name": "Indirect Effects",
        "threshold": "Mediated pathways via Verification Behaviour",
        "status": "Pending SEM estimation",
    },
    {
        "name": "Mediation Effects",
        "threshold": "Bootstrapped mediation significance (5000 resamples)",
        "status": "Pending SEM estimation",
    },
]

PLANNED_MODEL_FIT_METRICS: List[Dict[str, str]] = [
    {
        "name": "Chi-square / df (χ²/df)",
        "threshold": "χ²/df ≤ 3.0",
        "status": "Pending SEM estimation",
    },
    {
        "name": "Comparative Fit Index (CFI)",
        "threshold": "CFI ≥ 0.90 (ideally ≥ 0.95)",
        "status": "Pending SEM estimation",
    },
    {
        "name": "Tucker-Lewis Index (TLI)",
        "threshold": "TLI ≥ 0.90 (ideally ≥ 0.95)",
        "status": "Pending SEM estimation",
    },
    {
        "name": "Root Mean Square Error of Approximation (RMSEA)",
        "threshold": "RMSEA ≤ 0.08 (ideally ≤ 0.05)",
        "status": "Pending SEM estimation",
    },
    {
        "name": "Standardized Root Mean Square Residual (SRMR)",
        "threshold": "SRMR ≤ 0.08",
        "status": "Pending SEM estimation",
    },
]
