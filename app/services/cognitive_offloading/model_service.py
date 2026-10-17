"""
app/services/cognitive_offloading/model_service.py

Stub service for the future trained Cognitive Offloading Risk
Prediction model integration.

IMPORTANT:
This service intentionally does NOT contain a trained model,
fake predictions, or fabricated risk values.

Prediction functionality will become available only after:
  1. Research data collection is complete.
  2. Survey constructs are validated.
  3. The dataset is preprocessed and prepared.
  4. The machine-learning model is trained and evaluated.
  5. The model file is reviewed and approved for integration.

Status: Prototype — model development pending.
"""

from __future__ import annotations


# --------------------------------------------------------------------------- #
# Domain exception                                                             #
# --------------------------------------------------------------------------- #

class ModelNotAvailableError(RuntimeError):
    """
    Raised when prediction is requested before the model has been
    trained and integrated.
    """


# --------------------------------------------------------------------------- #
# Model service stub                                                           #
# --------------------------------------------------------------------------- #

class CognitiveOffloadingModelService:
    """
    Interface for the future trained Cognitive Offloading Risk
    Prediction model.

    All prediction methods raise ModelNotAvailableError until a
    validated, trained model is integrated.  This prevents any
    accidental fabrication of research results during the prototype
    development stage.
    """

    # Research/prototype status metadata ------------------------------------ #
    COMPONENT_NAME = "Explainable Cognitive Offloading Risk Prediction"
    STAGE = "prototype_development"
    DATA_COLLECTION_STATUS = "in_progress"

    # ------------------------------------------------------------------ #
    # Status query — safe to call at any stage                           #
    # ------------------------------------------------------------------ #

    def is_model_available(self) -> bool:
        """
        Return False until a trained model is loaded.

        Returns:
            bool: Always False during prototype development.
        """
        return False

    def get_status(self) -> dict:
        """
        Return the current readiness status of the model service.

        Returns:
            dict: Status information suitable for JSON serialization.
        """
        return {
            "component":                self.COMPONENT_NAME,
            "stage":                    self.STAGE,
            "data_collection":          self.DATA_COLLECTION_STATUS,
            "model_trained":            False,
            "prediction_available":     False,
            "explainability_available": False,
        }

    # ------------------------------------------------------------------ #
    # Prediction — raises until model is trained                         #
    # ------------------------------------------------------------------ #

    def predict(self, features: dict) -> dict:
        """
        Placeholder for the future risk prediction call.

        Args:
            features: Preprocessed feature dictionary.

        Raises:
            ModelNotAvailableError: Always, until model is integrated.
        """
        raise ModelNotAvailableError(
            "The Cognitive Offloading Risk Prediction model has not been "
            "trained yet. Prediction will be enabled after research data "
            "collection, validation, preprocessing, and model training "
            "are completed."
        )

    def explain(self, features: dict) -> dict:
        """
        Placeholder for the future SHAP explanation call.

        Args:
            features: Preprocessed feature dictionary.

        Raises:
            ModelNotAvailableError: Always, until model is integrated.
        """
        raise ModelNotAvailableError(
            "SHAP explanation is not available. The prediction model has "
            "not been trained yet."
        )


# --------------------------------------------------------------------------- #
# Module-level singleton (safe to import)                                      #
# --------------------------------------------------------------------------- #

model_service = CognitiveOffloadingModelService()
