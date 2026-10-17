"""
app/services/retention/schemas.py

Schema definitions and categorical metadata for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Defines:
- Controlled experimental conditions (Brain-only vs. GenAI-assisted)
- Condition orders for counterbalancing
- Experimental session stages
- Task reference validation constraints
- Planned learning outcome measures
- Planned NLP features
- Planned statistical evaluation criteria
- Specification metadata

Status: Prototype – experimental data collection in progress.
        No fabricated experimental results or NLP metrics.
"""

import re
from typing import Any, Dict, List, Set

# --------------------------------------------------------------------------- #
# Experimental Conditions & Session Metadata                                  #
# --------------------------------------------------------------------------- #

EXPERIMENTAL_CONDITIONS: Set[str] = {
    "Brain-only writing",
    "GenAI-assisted writing",
}

CONDITION_ORDERS: Set[str] = {
    "Brain-only first",
    "GenAI-assisted first",
}

SESSION_STAGES: Set[str] = {
    "Writing task",
    "Immediate recall",
    "Ownership / cognitive effort",
    "Delayed recall",
}

# --------------------------------------------------------------------------- #
# Validation Constraints                                                      #
# --------------------------------------------------------------------------- #

PARTICIPANT_REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9\-_]{2,20}$")
TASK_REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9\-_]{2,20}$")
MIN_REF_LENGTH = 2
MAX_REF_LENGTH = 20

ACCEPTED_SESSION_FIELDS: Set[str] = {
    "participant_reference",
    "experimental_condition",
    "condition_order",
    "session_stage",
    "task_reference",
    "consent_confirmed",
}

LEARNING_OUTCOMES: List[Dict[str, str]] = [
    {
        "name": "Writing Quality",
        "description": "Evaluated through NLP linguistic metrics and independent human rubric assessment.",
        "status": "Pending experimental data",
    },
    {
        "name": "Immediate Recall",
        "description": "Content recall assessed immediately following the experimental writing condition.",
        "status": "Pending experimental data",
    },
    {
        "name": "Delayed Recall",
        "description": "Knowledge retention assessed following a defined longitudinal delay interval.",
        "status": "Pending experimental data",
    },
    {
        "name": "Ownership",
        "description": "Self-reported psychological ownership and perceived authorship of the written work.",
        "status": "Pending experimental data",
    },
    {
        "name": "Cognitive Effort",
        "description": "Self-reported cognitive load and mental effort invested during the writing task.",
        "status": "Pending experimental data",
    },
]

NLP_FEATURES: List[Dict[str, str]] = [
    {
        "name": "Word Count",
        "description": "Total writing volume and output length.",
        "status": "Prototype calculation available",
    },
    {
        "name": "Lexical Diversity",
        "description": "Unique-token ratio (TTR), root TTR, and words used once; lemmatization is not included.",
        "status": "Prototype calculation available",
    },
    {
        "name": "Readability Scores",
        "description": "Approximate Coleman-Liau readability index from text length and sentence count.",
        "status": "Prototype approximation available",
    },
    {
        "name": "Sentence Complexity",
        "description": "Sentence count and mean sentence length; syntactic parsing and clause analysis are not included.",
        "status": "Basic prototype metrics available",
    },
    {
        "name": "Repetition",
        "description": "Words used once are counted; n-gram redundancy analysis is not included.",
        "status": "Partial prototype metric available",
    },
    {
        "name": "Semantic Similarity",
        "description": "Cosine similarity against task reference materials using sentence embeddings.",
        "status": "Not implemented; requires reference text and embeddings",
    },
]

RUBRIC_CRITERIA: List[Dict[str, str]] = [
    {"key": "content_accuracy", "name": "Content accuracy"},
    {"key": "task_relevance", "name": "Task relevance"},
    {"key": "reasoning_support", "name": "Reasoning and support"},
    {"key": "clarity_organization", "name": "Clarity and organization"},
]

CONDITION_COMPARISON_MEASURES: List[Dict[str, str]] = [
    {"key": "immediate_recall_count", "label": "Immediate recall", "unit": "items", "kind": "count"},
    {"key": "delayed_recall_count", "label": "Delayed recall", "unit": "items", "kind": "count"},
    {"key": "ownership_rating", "label": "Ownership", "unit": "mean rating (1–5)", "kind": "rating"},
    {"key": "cognitive_effort_rating", "label": "Cognitive effort", "unit": "mean rating (1–5)", "kind": "rating"},
    {"key": "human_rubric_mean", "label": "Human rubric", "unit": "mean rating (1–5)", "kind": "rating"},
]

# --------------------------------------------------------------------------- #
# Research Specification Metadata                                             #
# --------------------------------------------------------------------------- #

RETENTION_SPECIFICATION: Dict[str, Any] = {
    "conditions": sorted(list(EXPERIMENTAL_CONDITIONS)),
    "condition_orders": sorted(list(CONDITION_ORDERS)),
    "session_stages": list(SESSION_STAGES),
    "outcomes": LEARNING_OUTCOMES,
    "nlp_features": NLP_FEATURES,
    "evaluation": [
        "Human rubric scoring",
        "Paired comparison",
        "Effect sizes",
        "Confidence intervals",
        "Inter-rater agreement",
    ],
    "results_status": "pending",
}
