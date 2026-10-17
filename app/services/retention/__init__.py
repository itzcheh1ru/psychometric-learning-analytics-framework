"""
app/services/retention/__init__.py

Service package for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Exports:
- Schemas and metadata (EXPERIMENTAL_CONDITIONS, CONDITION_ORDERS,
  SESSION_STAGES, RETENTION_SPECIFICATION, LEARNING_OUTCOMES, NLP_FEATURES)
- ValidationResult, validate_experimental_session
- RetentionAnalysisNotAvailableError, RetentionAnalysisService, analysis_service

Status: Prototype – experimental data collection in progress.
        DO NOT add fake essays, synthetic recall scores, or fabricated NLP metrics.
"""

from app.services.retention.schemas import (
    CONDITION_ORDERS,
    CONDITION_COMPARISON_MEASURES,
    EXPERIMENTAL_CONDITIONS,
    LEARNING_OUTCOMES,
    NLP_FEATURES,
    RUBRIC_CRITERIA,
    RETENTION_SPECIFICATION,
    SESSION_STAGES,
)
from app.services.retention.validation import (
    ValidationResult,
    validate_experimental_session,
    validate_immediate_recall_counts,
    validate_ownership_effort_ratings,
    validate_rubric_ratings,
    validate_condition_comparison,
)
from app.services.retention.analysis_service import (
    RetentionAnalysisNotAvailableError,
    RetentionAnalysisService,
    analysis_service,
)

__all__ = [
    "EXPERIMENTAL_CONDITIONS",
    "CONDITION_ORDERS",
    "CONDITION_COMPARISON_MEASURES",
    "SESSION_STAGES",
    "RETENTION_SPECIFICATION",
    "LEARNING_OUTCOMES",
    "NLP_FEATURES",
    "RUBRIC_CRITERIA",
    "ValidationResult",
    "validate_experimental_session",
    "validate_immediate_recall_counts",
    "validate_ownership_effort_ratings",
    "validate_rubric_ratings",
    "validate_condition_comparison",
    "RetentionAnalysisNotAvailableError",
    "RetentionAnalysisService",
    "analysis_service",
]
