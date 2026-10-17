"""
app/services/cognitive_offloading/__init__.py

Service package for Component 1:
Explainable Cognitive Offloading Risk Prediction.

Exports the model service singleton and key validation utilities
for use by the route layer.

Status: Prototype — data collection in progress.
        DO NOT add prediction logic until research data is available
        and the model has been properly trained and evaluated.
"""

from app.services.cognitive_offloading.model_service import (
    CognitiveOffloadingModelService,
    ModelNotAvailableError,
    model_service,
)
from app.services.cognitive_offloading.validation import validate_prototype_input

__all__ = [
    "CognitiveOffloadingModelService",
    "ModelNotAvailableError",
    "model_service",
    "validate_prototype_input",
]
