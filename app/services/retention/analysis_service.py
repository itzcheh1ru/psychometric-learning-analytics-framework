"""
app/services/retention/analysis_service.py

Service interface for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

IMPORTANT:
Empirical analysis remains unavailable until actual study data is collected
and validated. The recall summary is a clearly labeled demonstration only;
it calculates averages from the processed prototype dataset and must not be
presented as real participant evidence.

Status: Prototype – experimental data collection in progress.
"""

import csv
import os
from typing import Any, Dict


class RetentionAnalysisNotAvailableError(RuntimeError):
    """
    Raised when experimental retention or cognitive engagement results
    are requested before empirical data has been collected and validated.
    """


class RetentionAnalysisService:
    """
    Service interface for future cognitive engagement and retention evaluation.
    """

    COMPONENT_NAME: str = (
        "GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation"
    )
    STAGE: str = "prototype_development"
    DATA_COLLECTION_STATUS: str = "in_progress"

    def is_analysis_available(self) -> bool:
        """
        Return whether experimental analytical findings are ready.

        Returns:
            bool: Always False during experimental data collection and prototype development.
        """
        return False

    def get_status(self) -> Dict[str, Any]:
        """
        Return the current readiness status of the experimental evaluation pipeline.

        Returns:
            Dict[str, Any]: Structured status dictionary suitable for JSON serialization.
        """
        return {
            "component": self.COMPONENT_NAME,
            "stage": self.STAGE,
            "experimental_data_collection": self.DATA_COLLECTION_STATUS,
            "dataset_ready": False,
            "nlp_analysis_available": False,
            "recall_analysis_available": False,
            "paired_analysis_available": False,
            "final_results_available": False,
        }

    def get_research_recommendations(self) -> list[Dict[str, str]]:
        """Build research-readiness guidance from availability flags and prototype metrics."""
        status = self.get_status()
        recommendations = []

        if not status["dataset_ready"]:
            recommendations.append({
                "category": "Data readiness",
                "title": "Collect and validate the approved participant dataset",
                "detail": "Current recall summaries and model metrics are prototype outputs. Do not use them as evidence for condition effects or student-level decisions.",
            })

        if not status["paired_analysis_available"]:
            recommendations.append({
                "category": "Study protocol",
                "title": "Finalize paired scoring and assessment procedures",
                "detail": "Confirm the same-task pairing, immediate and delayed test timing, approved rubric criteria, and rater blinding before collecting outcomes.",
            })

        delayed_metrics = self.get_delayed_recall_model_metrics()
        genai_metrics = delayed_metrics.get("genai", {})
        genai_r2 = genai_metrics.get("r2")
        if isinstance(genai_r2, (int, float)) and genai_r2 < 0.2:
            recommendations.append({
                "category": "Model validation",
                "title": "Review the GenAI delayed-recall model before interpretation",
                "detail": f"Its current prototype test R² is {genai_r2:.3f}. Compare against a mean baseline and reevaluate with participant-level validation on real data before using predictions.",
            })
        else:
            recommendations.append({
                "category": "Model validation",
                "title": "Revalidate recall models on real participant data",
                "detail": "Report MAE, RMSE, and R² against a simple baseline using participant-level train/test separation; current prototype metrics are not research evidence.",
            })

        return recommendations

    def get_results(self) -> Dict[str, Any]:
        """
        Retrieve empirical experimental results once available.

        Raises:
            RetentionAnalysisNotAvailableError: Always, until experimental results are validated.
        """
        raise RetentionAnalysisNotAvailableError(
            "Cognitive engagement and retention analysis is not available "
            "until the controlled experimental dataset has been collected "
            "and validated."
        )

    def get_model_metrics(self) -> Dict[str, Any]:
        """Return the trained machine learning model metrics."""
        from app.services.retention.model_engine import get_model_metrics
        return get_model_metrics() or {}

    def get_feature_importances(self) -> Dict[str, Any]:
        """Return the feature importance rankings for cognitive retention risk."""
        from app.services.retention.model_engine import get_feature_importances
        return get_feature_importances() or {}

    def get_immediate_recall_model_metrics(self) -> Dict[str, Any]:
        """Return evaluation metrics for the immediate-recall prototype models."""
        from app.services.retention.model_engine import get_immediate_recall_model_metrics
        return get_immediate_recall_model_metrics()

    def predict_immediate_recall(self, condition: str, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict an immediate recall score using a prototype-trained regressor."""
        from app.services.retention.model_engine import predict_immediate_recall
        return predict_immediate_recall(condition, input_features)

    def get_delayed_recall_model_metrics(self) -> Dict[str, Any]:
        """Return evaluation metrics for the delayed-recall prototype models."""
        from app.services.retention.model_engine import get_delayed_recall_model_metrics
        return get_delayed_recall_model_metrics()

    def predict_delayed_recall(self, condition: str, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict delayed recall with a condition-specific prototype regressor."""
        from app.services.retention.model_engine import predict_delayed_recall
        return predict_delayed_recall(condition, input_features)

    def get_recall_summary(self) -> Dict[str, Any]:
        """Return immediate and delayed recall averages from the prototype dataset."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        dataset_paths = [
            os.path.join(base_dir, "data", "processed", "component4_master_dataset_300_v2.csv"),
            os.path.join(base_dir, "data", "processed", "component4_master_dataset_300.csv"),
        ]
        dataset_path = next((path for path in dataset_paths if os.path.exists(path)), None)

        unavailable = {
            "brain_immediate_avg": 0.0,
            "genai_immediate_avg": 0.0,
            "immediate_difference": 0.0,
            "brain_delayed_avg": 0.0,
            "genai_delayed_avg": 0.0,
            "delayed_difference": 0.0,
            "sample_size": 0,
            "status": "dataset_not_found",
            "note": "Processed prototype recall dataset is not available.",
        }
        if dataset_path is None:
            return unavailable

        fields = (
            "brain_immediate_score",
            "genai_immediate_score",
            "brain_delayed_recall_score",
            "genai_delayed_recall_score",
        )
        scores = {field: [] for field in fields}

        with open(dataset_path, "r", encoding="utf-8", newline="") as csv_file:
            for row in csv.DictReader(csv_file):
                for field in fields:
                    try:
                        scores[field].append(float(row[field]))
                    except (KeyError, TypeError, ValueError):
                        continue

        def average(field: str) -> float:
            values = scores[field]
            return round(sum(values) / len(values), 2) if values else 0.0

        brain_immediate = average("brain_immediate_score")
        genai_immediate = average("genai_immediate_score")
        brain_delayed = average("brain_delayed_recall_score")
        genai_delayed = average("genai_delayed_recall_score")

        return {
            "brain_immediate_avg": brain_immediate,
            "genai_immediate_avg": genai_immediate,
            "immediate_difference": round(genai_immediate - brain_immediate, 2),
            "brain_delayed_avg": brain_delayed,
            "genai_delayed_avg": genai_delayed,
            "delayed_difference": round(genai_delayed - brain_delayed, 2),
            "sample_size": min(len(scores[field]) for field in fields),
            "status": "prototype_estimate",
            "note": "Demo averages calculated from the processed prototype dataset; these are not real participant research findings.",
        }

    def predict_retention_risk(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict cognitive retention risk using the trained Random Forest ensemble pipeline."""
        from app.services.retention.model_engine import predict_retention_risk
        return predict_retention_risk(input_data)


# Singleton service instance
analysis_service = RetentionAnalysisService()
