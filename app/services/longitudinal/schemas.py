"""
app/services/longitudinal/schemas.py

Schema definitions and allowed categorical values for Component 3:
Longitudinal AI-Assisted Study Pattern Analytics.

Defines:
- Study week definitions (4-6 weeks collection design)
- Academic period categories
- Learning activity categories
- Academic prompt purpose categories
- Indicator metadata
- Specification metadata

Status: Prototype – longitudinal data collection in progress.
        No fabricated trends or study pattern findings.
"""

import re
from typing import Any, Dict, List, Set

# --------------------------------------------------------------------------- #
# Allowed Categories                                                          #
# --------------------------------------------------------------------------- #

ALLOWED_WEEKS: Set[str] = {
    "Week 1",
    "Week 2",
    "Week 3",
    "Week 4",
    "Week 5",
    "Week 6",
}

ACADEMIC_PERIODS: Set[str] = {
    "Regular study week",
    "Assignment period",
    "Examination preparation",
    "Project / coursework period",
    "Other academic period",
}

LEARNING_ACTIVITIES: Set[str] = {
    "Concept learning",
    "Coding / debugging",
    "Assignment work",
    "Reading / research",
    "Writing",
    "Revision / exam preparation",
    "Other academic activity",
}

PROMPT_PURPOSES: Set[str] = {
    "Concept explanation",
    "Coding / debugging",
    "Summarisation",
    "Assignment support",
    "Writing support",
    "Exam revision",
    "Other academic purpose",
}

# --------------------------------------------------------------------------- #
# Participant Reference Constraints                                           #
# --------------------------------------------------------------------------- #

PARTICIPANT_REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9\-]{1,20}$")
MAX_PARTICIPANT_REF_LENGTH = 20

# Weekly hour bounds (0 to 168 hours in a week)
MIN_STUDY_HOURS = 0.0
MAX_STUDY_HOURS = 168.0

# Prompt count bounds
MIN_PROMPT_COUNT = 0
MAX_PROMPT_COUNT = 2000

# Strict list of accepted fields in weekly record submission
ACCEPTED_FIELDS: Set[str] = {
    "participant_reference",
    "study_week",
    "ai_study_hours",
    "independent_study_hours",
    "academic_period",
    "learning_activity",
    "prompt_count",
    "prompt_purpose",
}

# --------------------------------------------------------------------------- #
# Specification & Indicator Metadata                                          #
# --------------------------------------------------------------------------- #

LONGITUDINAL_SPECIFICATION: Dict[str, Any] = {
    "collection": {
        "structure": "weekly",
        "planned_duration": "4-6 weeks",
    },
    "indicators": [
        "AI Study Share",
        "Independent Study Share",
        "Prompt Frequency",
        "Prompt Purpose",
        "Study Pattern Shift",
    ],
    "analysis_methods": [
        "Longitudinal trend analysis",
        "Percentage change analysis",
        "Study pattern evolution",
        "Prompt behaviour analysis",
    ],
    "results_status": "pending",
}

BEHAVIOURAL_INDICATORS: List[Dict[str, str]] = [
    {
        "name": "AI Study Share",
        "concept": "Proportion of total recorded study time involving GenAI-assisted study.",
        "status": "Calculated after validated multi-week data collection",
    },
    {
        "name": "Independent Study Share",
        "concept": "Proportion of recorded study time completed independently without AI.",
        "status": "Calculated after validated multi-week data collection",
    },
    {
        "name": "Prompt Frequency",
        "concept": "Number of academic GenAI prompts/interactions within a study period.",
        "status": "Calculated after validated multi-week data collection",
    },
    {
        "name": "Prompt Purpose",
        "concept": "Distribution of GenAI interactions across academic purposes.",
        "status": "Calculated after validated multi-week data collection",
    },
    {
        "name": "Study Pattern Shift",
        "concept": "A future longitudinal indicator describing changes in study behaviour across repeated weekly observations.",
        "status": "Calculated after validated multi-week data collection",
    },
]
