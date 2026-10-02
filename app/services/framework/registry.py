"""
app/services/framework/registry.py

Component registry metadata for the Psychometric Learning Analytics Framework.

Provides structured metadata for all four analytical components including:
- Component identity (id, title, role)
- Analytical method description
- Prototype readiness state
- Analysis readiness state (False until data collection and analysis complete)
- Route endpoints for UI navigation

IMPORTANT:
- single_combined_model = False
- overall_score_available = False
- No cross-component classification rules exist or will be added here.
- Integration principle: Complementary Evidence (not mathematical aggregation).

Status: Prototype – research data collection in progress.
"""

from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# Component Registry                                                           #
# --------------------------------------------------------------------------- #

COMPONENT_REGISTRY: List[Dict[str, Any]] = [
    {
        "id": "c1",
        "number": 1,
        "title": "Explainable Cognitive Offloading Risk Prediction",
        "short_title": "Cognitive Offloading",
        "role": (
            "Predicts individual cognitive-offloading risk using GenAI usage"
            " behaviour, verification practices, and independent-learning strategies."
        ),
        "methods": ["Logistic Regression", "Random Forest", "XGBoost", "SHAP"],
        "data_source": "Psychometric behaviour survey",
        "route": "/component1/",
        "api_status_route": "/api/component1/status",
        "prototype_ready": True,
        "analysis_ready": False,
        "stage": "prototype_development",
        "color_token": "c1",
        "owner": "IT23426580",
    },
    {
        "id": "c2",
        "number": 2,
        "title": "Algorithmic Trust & Verification Analysis",
        "short_title": "Trust & Verification",
        "role": (
            "Models psychological relationships between algorithmic trust, perceived"
            " usefulness, verification behaviour, AI dependence, and learning confidence."
        ),
        "methods": ["CFA", "SEM", "R/lavaan", "Psychometrics"],
        "data_source": "Likert-scale psychometric survey",
        "route": "/component2/",
        "api_status_route": "/api/component2/status",
        "prototype_ready": True,
        "analysis_ready": False,
        "stage": "prototype_development",
        "color_token": "c2",
        "owner": "IT23217904",
    },
    {
        "id": "c3",
        "number": 3,
        "title": "Longitudinal AI-Assisted Study Pattern Analytics",
        "short_title": "Study Patterns",
        "role": (
            "Analyses how AI-assisted and independent study behaviours and academic"
            " prompt patterns evolve over time throughout the research period."
        ),
        "methods": ["Longitudinal Analytics", "Time-Series", "Trend Analysis", "Pandas"],
        "data_source": "Weekly self-report study diaries",
        "route": "/component3/",
        "api_status_route": "/api/component3/status",
        "prototype_ready": True,
        "analysis_ready": False,
        "stage": "prototype_development",
        "color_token": "c3",
        "owner": "IT23426344",
    },
    {
        "id": "c4",
        "number": 4,
        "title": "Cognitive Engagement & Learning Retention Evaluation",
        "short_title": "Engagement & Retention",
        "role": (
            "Evaluates AI-assisted vs. brain-only writing through NLP linguistic"
            " analysis, recall assessment, and statistical comparison of learning conditions."
        ),
        "methods": ["NLP", "NLTK", "spaCy", "Statistical Analysis", "SciPy"],
        "data_source": "Controlled writing experiments",
        "route": "/component4/",
        "api_status_route": "/api/component4/status",
        "prototype_ready": True,
        "analysis_ready": False,
        "stage": "prototype_development",
        "color_token": "c4",
        "owner": "IT23165220",
    },
]

# --------------------------------------------------------------------------- #
# Framework Specification                                                      #
# --------------------------------------------------------------------------- #

FRAMEWORK_SPECIFICATION: Dict[str, Any] = {
    "project_id": "J26-DS-310",
    "title": "Psychometric Learning Analytics Framework",
    "integration_principle": (
        "Complementary Evidence: each component produces independent analytical"
        " findings that are interpreted together for a holistic understanding."
        " Outputs are NOT mathematically combined into a single score or prediction."
    ),
    "single_combined_model": False,
    "overall_score_available": False,
    "components": [
        {
            "id": c["id"],
            "number": c["number"],
            "title": c["title"],
            "role": c["role"],
            "methods": c["methods"],
            "data_source": c["data_source"],
            "prototype_ready": c["prototype_ready"],
            "analysis_ready": c["analysis_ready"],
            "owner": c["owner"],
        }
        for c in COMPONENT_REGISTRY
    ],
}
