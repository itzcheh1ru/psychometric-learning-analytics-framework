"""
app/services/cognitive_offloading/schemas.py

Allowed prototype input categories and expected schema for
Component 1: Explainable Cognitive Offloading Risk Prediction.

These definitions govern frontend form options and backend validation.
They represent PREDICTOR variables only — cognitive-offloading target
items are intentionally excluded to prevent data leakage.

Status: Prototype — research data collection in progress.
"""

import re

# --------------------------------------------------------------------------- #
# Allowed category sets                                                        #
# --------------------------------------------------------------------------- #

GENAI_USAGE_FREQUENCY = {
    "Never",
    "Rarely",
    "Sometimes",
    "Often",
    "Very Frequently",
}

WEEKLY_GENAI_USAGE = {
    "Less than 1 hour",
    "1-3 hours",
    "4-7 hours",
    "8-14 hours",
    "15+ hours",
}

ACADEMIC_PURPOSE = {
    "Concept explanation",
    "Coding / debugging",
    "Assignment support",
    "Summarisation",
    "Writing support",
    "Exam preparation",
    "Other academic use",
}

VERIFICATION_FREQUENCY = {
    "Never",
    "Rarely",
    "Sometimes",
    "Often",
    "Always",
}

INDEPENDENT_LEARNING = {
    "Very Low",
    "Low",
    "Moderate",
    "High",
    "Very High",
}

ACADEMIC_YEAR = {
    "Year 1",
    "Year 2",
    "Year 3",
    "Year 4",
    "Other",
}

# --------------------------------------------------------------------------- #
# Required and optional field definitions                                      #
# --------------------------------------------------------------------------- #

REQUIRED_FIELDS = [
    "participant_reference",
    "genai_usage_frequency",
    "weekly_genai_usage",
    "academic_purpose",
    "verification_frequency",
    "independent_learning",
]

OPTIONAL_FIELDS = [
    "academic_year",
]

# Participant reference: alphanumeric + hyphens, max 20 chars.
# Must NOT contain personal information such as names or email addresses.
PARTICIPANT_REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9\-]{1,20}$")
MAX_PARTICIPANT_REF_LENGTH = 20

# --------------------------------------------------------------------------- #
# Field → allowed values mapping (used by validation layer)                   #
# --------------------------------------------------------------------------- #

FIELD_ALLOWED_VALUES: dict[str, set[str]] = {
    "genai_usage_frequency": GENAI_USAGE_FREQUENCY,
    "weekly_genai_usage":    WEEKLY_GENAI_USAGE,
    "academic_purpose":      ACADEMIC_PURPOSE,
    "verification_frequency":VERIFICATION_FREQUENCY,
    "independent_learning":  INDEPENDENT_LEARNING,
    "academic_year":         ACADEMIC_YEAR,
}
