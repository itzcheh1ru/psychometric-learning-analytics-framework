"""
app/services/framework/status_service.py

Framework status aggregation service.

Aggregates readiness metadata from all four analytical component services
by importing them directly. Does NOT make HTTP requests to the application's
own API endpoints.

IMPORTANT:
- single_combined_model = False
- overall_score_available = False
- No combined scores, no cross-component risk classifications.
- Integration: Complementary Evidence only.

Status: Prototype – research data collection in progress.
"""

from typing import Any, Dict

from app.services.framework.registry import COMPONENT_REGISTRY
from app.services.cognitive_offloading.model_service import (
    CognitiveOffloadingModelService,
)
from app.services.sem_analysis.status_service import status_service as sem_status_svc
from app.services.longitudinal.analysis_service import LongitudinalAnalysisService
from app.services.retention.analysis_service import RetentionAnalysisService


class FrameworkStatusService:
    """
    Aggregates prototype readiness across all four analytical components.

    Reads status directly from component service modules.
    Never makes HTTP requests to the Flask application's own routes.
    """

    def get_status(self) -> Dict[str, Any]:
        """
        Return aggregated readiness status for the full framework.

        Each component section reflects only its own prototype state.
        There is no combined readiness score or overall risk metric.

        Returns:
            Dict[str, Any]: Structured status dictionary suitable for JSON serialization.
        """
        # Component 1: Cognitive Offloading (ML model)
        c1_svc = CognitiveOffloadingModelService()
        c1_ready = c1_svc.is_model_available()

        # Component 2: SEM Analysis
        c2_status = sem_status_svc.get_status()
        c2_ready = c2_status.get("sem_results_available", False)

        # Component 3: Longitudinal Analytics
        c3_svc = LongitudinalAnalysisService()
        c3_ready = c3_svc.is_analysis_available()

        # Component 4: Cognitive Retention
        c4_svc = RetentionAnalysisService()
        c4_ready = c4_svc.is_analysis_available()

        return {
            "project_id": "J26-DS-310",
            "framework": "Psychometric Learning Analytics Framework",
            "integration_principle": (
                "Complementary Evidence – outputs are interpreted together,"
                " not combined into a single score."
            ),
            "single_combined_model": False,
            "overall_score_available": False,
            "components": [
                {
                    "id": "c1",
                    "title": "Explainable Cognitive Offloading Risk Prediction",
                    "prototype_ready": True,
                    "analysis_ready": c1_ready,
                    "stage": "prototype_development",
                },
                {
                    "id": "c2",
                    "title": "Algorithmic Trust & Verification Analysis",
                    "prototype_ready": True,
                    "analysis_ready": c2_ready,
                    "stage": "prototype_development",
                },
                {
                    "id": "c3",
                    "title": "Longitudinal AI-Assisted Study Pattern Analytics",
                    "prototype_ready": True,
                    "analysis_ready": c3_ready,
                    "stage": "prototype_development",
                },
                {
                    "id": "c4",
                    "title": "Cognitive Engagement & Learning Retention Evaluation",
                    "prototype_ready": True,
                    "analysis_ready": c4_ready,
                    "stage": "prototype_development",
                },
            ],
            "all_prototypes_ready": True,
            "any_analysis_ready": any([c1_ready, c2_ready, c3_ready, c4_ready]),
        }


# Singleton service instance
framework_status_service = FrameworkStatusService()
