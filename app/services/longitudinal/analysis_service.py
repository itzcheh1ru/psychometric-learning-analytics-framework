"""
app/services/longitudinal/analysis_service.py

Service interface for Component 3: Longitudinal AI-Assisted Study Pattern Analytics.

IMPORTANT:
This service strictly prevents the generation or display of simulated
longitudinal findings, artificial time-series trends, or mock participant
histories. All analytical methods raise LongitudinalAnalysisNotAvailableError
until the multi-week research dataset is fully collected and validated.

Status: Prototype – longitudinal data collection in progress.
"""

from typing import Any, Dict


class LongitudinalAnalysisNotAvailableError(RuntimeError):
    """
    Raised when longitudinal trends or analyses are requested
    before empirical multi-week research data has been collected and validated.
    """


class LongitudinalAnalysisService:
    """
    Service interface for future longitudinal analysis of multi-week study records.
    """

    COMPONENT_NAME: str = "Longitudinal AI-Assisted Study Pattern Analytics"
    STAGE: str = "prototype_development"
    DATA_COLLECTION_STATUS: str = "in_progress"

    def is_analysis_available(self) -> bool:
        """
        Return whether longitudinal analytical findings are ready.

        Returns:
            bool: Always False during data collection and prototype development.
        """
        return False

    def get_status(self) -> Dict[str, Any]:
        """
        Return the current readiness status of the longitudinal analysis pipeline.

        Returns:
            Dict[str, Any]: Structured status dictionary suitable for JSON serialization.
        """
        return {
            "component": self.COMPONENT_NAME,
            "stage": self.STAGE,
            "longitudinal_data_collection": self.DATA_COLLECTION_STATUS,
            "dataset_ready": False,
            "trend_analysis_available": False,
            "prompt_analysis_available": False,
            "study_pattern_results_available": False,
        }

    def get_trends(self) -> Dict[str, Any]:
        """
        Retrieve empirical longitudinal trends once available.

        Raises:
            LongitudinalAnalysisNotAvailableError: Always, until multi-week data is collected.
        """
        raise LongitudinalAnalysisNotAvailableError(
            "Longitudinal analysis is not available until the required "
            "multi-week research dataset has been collected and validated."
        )


# Singleton service instance
analysis_service = LongitudinalAnalysisService()
