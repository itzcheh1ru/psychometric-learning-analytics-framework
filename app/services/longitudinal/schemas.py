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

WORKLOAD_PRESSURES: Set[str] = {
    "Low",
    "Moderate",
    "High",
}

LEARNING_ACTIVITIES: Set[str] = {
    "Concept learning",
    "Coding / debugging",
    "Assignment work",
    "Reading / research",
    "Writing",
    "Revision / exam preparation",
    "Presentation",
    "The semester just started",
    "Other academic activity",
}

PROMPT_PURPOSES: Set[str] = {
    "Concept explanation",
    "Coding / debugging",
    "Summarisation",
    "Assignment support",
    "Writing support",
    "Exam revision",
    "Research/information seeking",
    "Presentation preparation",
    "No prompts this week",
    "Other academic purpose",
}

STUDY_METHODS: Set[str] = {
    "AI-guided learning (asking GenAI to explain/teach concepts)",
    "Deep research",
    "Flashcards/active recall",
    "Group discussion/peer study",
    "Note-making/summarising",
    "Practice problems/past papers",
    "Reading textbooks/notes",
    "Video creation",
    "Watching video lectures/tutorials",
    "Didn't use any yet",
}

PRODUCTIVITY_RATINGS: List[str] = [
    "Very unproductive",
    "Somewhat unproductive",
    "Neutral",
    "Somewhat productive",
    "Very productive",
]

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
    "learning_activity",
    "prompt_count",
    "prompt_purpose",
    "study_methods",
    "perceived_productivity",
    "workload_pressure",
    "prompt_detail",
}

REQUIRED_FIELDS: Set[str] = {
    "participant_reference",
    "study_week",
    "ai_study_hours",
    "independent_study_hours",
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
        "Study Method Distribution",
        "Perceived Productivity",
        "Self-Reported Prompt Detail",
        "Study Pattern Shift",
    ],
    "analysis_methods": [
        "Weekly descriptive trend visualisation",
        "Within-participant percentage-point change in study-share allocation",
        "Weekly prompt-purpose, study-method, and productivity distributions",
        "Descriptive comparison of AI use by self-reported workload pressure",
    ],
    "results_status": "pending",
}

BEHAVIOURAL_INDICATORS: List[Dict[str, str]] = [
    {
        "name": "AI Study Share",
        "concept": "Proportion of total recorded study time involving GenAI-assisted study.",
        "status": "Weekly descriptive measure; excludes records without valid positive study-hour totals",
    },
    {
        "name": "Independent Study Share",
        "concept": "Proportion of recorded study time completed independently without AI.",
        "status": "Weekly descriptive measure",
    },
    {
        "name": "Prompt Frequency",
        "concept": "Number of academic GenAI prompts/interactions within a study period.",
        "status": "Weekly average and total; sample size reported",
    },
    {
        "name": "Prompt Purpose",
        "concept": "Distribution of GenAI interactions across academic purposes.",
        "status": "Weekly category counts; categories may overlap",
    },
    {
        "name": "Study Method Distribution",
        "concept": "Weekly distribution of self-reported study methods; multiple methods may be selected.",
        "status": "Descriptive weekly comparison",
    },
    {
        "name": "Perceived Productivity",
        "concept": "Weekly self-reported perceived productivity category.",
        "status": "Descriptive ordinal distribution; not an objective productivity measure",
    },
    {
        "name": "Self-Reported Prompt Detail",
        "concept": "Weekly 1–5 self-rating of prompt detail and specificity.",
        "status": "Descriptive self-report; not an independently measured complexity score",
    },
    {
        "name": "Study Pattern Shift",
        "concept": "Average absolute percentage-point change in AI-assisted and independent study shares between a participant's current and previous available week.",
        "status": "Descriptive indicator; not a validated psychometric scale",
    },
    {
        "name": "Workload Comparison",
        "concept": "Weekly average AI-assisted study hours and academic prompt counts grouped by self-reported workload/deadline pressure.",
        "status": "Descriptive association; not a causal or composite spike score",
    },
]
