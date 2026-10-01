"""
app/services/sem_analysis/__init__.py

Service package for Component 2:
Algorithmic Trust & Verification Analysis (SEM / CFA).

Exports schema metadata, status service, result service, and exceptions.

Status: Prototype – R/lavaan integration pending data collection.
        DO NOT add fake SEM coefficients or fit statistics.
"""

from app.services.sem_analysis.schemas import (
    CONSTRUCTS,
    MODEL_SPECIFICATION,
    PLANNED_MEASUREMENT_METRICS,
    PLANNED_STRUCTURAL_METRICS,
    PLANNED_MODEL_FIT_METRICS,
)
from app.services.sem_analysis.status_service import (
    SemStatusService,
    status_service,
)
from app.services.sem_analysis.result_service import (
    SemResultsNotAvailableError,
    SemResultService,
    result_service,
)

__all__ = [
    "CONSTRUCTS",
    "MODEL_SPECIFICATION",
    "PLANNED_MEASUREMENT_METRICS",
    "PLANNED_STRUCTURAL_METRICS",
    "PLANNED_MODEL_FIT_METRICS",
    "SemStatusService",
    "status_service",
    "SemResultsNotAvailableError",
    "SemResultService",
    "result_service",
]
