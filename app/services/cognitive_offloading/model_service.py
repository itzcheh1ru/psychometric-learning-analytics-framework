"""
app/services/cognitive_offloading/model_service.py

Service layer for Component 1:
Explainable Cognitive Offloading Risk Prediction (Version 4).

Connects the Flask application to the Calibrated Thresholded Ridge
Regressor pipeline and LinearSHAP explainability engine.

Status: Model Integrated — Version 4 Performance Experiments.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("CognitiveOffloadingModelService")


class ModelNotAvailableError(RuntimeError):
    """
    Raised when prediction is requested but the model artifact could not be loaded.
    """


class CognitiveOffloadingModelService:
    """
    Interface for the trained Cognitive Offloading Risk Prediction model (Version 4).
    Uses the Calibrated Thresholded Ridge Regressor with exact LinearSHAP explanations.
    """

    COMPONENT_NAME = "Explainable Cognitive Offloading Risk Prediction"
    STAGE = "model_integrated"
    DATA_COLLECTION_STATUS = "completed"

    def __init__(self) -> None:
        self._predictor = None
        self._load_predictor()

    def _load_predictor(self) -> None:
        try:
            from app.services.cognitive_offloading.integration_service import (
                get_predictor_v4,
            )
            self._predictor = get_predictor_v4()
            logger.info("Component 1 Version 4 predictor successfully loaded.")
        except Exception as e:
            logger.warning("Component 1 model could not be loaded: %s", e)
            self._predictor = None

    def is_model_available(self) -> bool:
        """Return True if the trained model artifact is loaded."""
        return self._predictor is not None and getattr(self._predictor, "model", None) is not None

    def get_status(self) -> dict:
        """Return the current readiness status of the model service."""
        available = self.is_model_available()
        meta = getattr(self._predictor, "metadata", {}) if self._predictor else {}
        return {
            "component": self.COMPONENT_NAME,
            "stage": self.STAGE if available else "prototype_development",
            "data_collection": self.DATA_COLLECTION_STATUS if available else "in_progress",
            "model_trained": available,
            "prediction_available": available,
            "explainability_available": available,
            "champion_model": meta.get("champion_model", "Calibrated Thresholded Ridge Regressor (Ordinal)"),
            "features_count": len(getattr(self._predictor, "feature_names", [])) if available else 0,
            "version": "v4_performance_experiments",
        }

    def predict(self, features: dict, top_factors_count: int = 5) -> dict:
        """
        Execute risk prediction using the Version 4 Ridge pipeline.
        """
        if not self.is_model_available():
            raise ModelNotAvailableError(
                "The Cognitive Offloading Risk Prediction model is not currently available."
            )
        return self._predictor.predict(features, top_factors_count=top_factors_count)

    def explain(self, features: dict, top_factors_count: int = 5) -> dict:
        """
        Return the exact LinearSHAP explanation from the Version 4 pipeline.
        """
        res = self.predict(features, top_factors_count=top_factors_count)
        return {
            "status": res.get("status"),
            "top_contributing_factors": res.get("top_contributing_factors", []),
            "disclaimer": res.get("disclaimer"),
        }


# Module-level singleton
model_service = CognitiveOffloadingModelService()
