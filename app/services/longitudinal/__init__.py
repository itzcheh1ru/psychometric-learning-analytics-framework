"""
app/services/longitudinal/__init__.py

Service package for Component 3:
Longitudinal AI-Assisted Study Pattern Analytics.

Exports:
- LongitudinalAnalysisService, analysis_service
- LongitudinalAnalysisNotAvailableError
- validate_weekly_record
- Schemas and metadata (ALLOWED_WEEKS, ACADEMIC_PERIODS, LEARNING_ACTIVITIES,
  PROMPT_PURPOSES, LONGITUDINAL_SPECIFICATION, BEHAVIOURAL_INDICATORS)

Status: Prototype – longitudinal data collection in progress.
        DO NOT add fake trends, fake graphs, or fabricated longitudinal findings.
"""

from app.services.longitudinal.schemas import (
    ACADEMIC_PERIODS,
    ALLOWED_WEEKS,
    BEHAVIOURAL_INDICATORS,
    LEARNING_ACTIVITIES,
    LONGITUDINAL_SPECIFICATION,
    PROMPT_PURPOSES,
)
from app.services.longitudinal.validation import (
    ValidationResult,
    validate_weekly_record,
)
from app.services.longitudinal.analysis_service import (
    LongitudinalAnalysisNotAvailableError,
    LongitudinalAnalysisService,
    analysis_service,
)

__all__ = [
    "ACADEMIC_PERIODS",
    "ALLOWED_WEEKS",
    "BEHAVIOURAL_INDICATORS",
    "LEARNING_ACTIVITIES",
    "LONGITUDINAL_SPECIFICATION",
    "PROMPT_PURPOSES",
    "ValidationResult",
    "validate_weekly_record",
    "LongitudinalAnalysisNotAvailableError",
    "LongitudinalAnalysisService",
    "analysis_service",
]
