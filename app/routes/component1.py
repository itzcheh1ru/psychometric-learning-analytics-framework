"""
app/routes/component1.py – Routes for Component 1:
Explainable Cognitive Offloading Risk Prediction.

Endpoints:
  GET  /component1/                  – UI page
  GET  /api/component1/status        – Model readiness status (JSON)
  POST /api/component1/validate-input – Prototype input validation (JSON)

Status: Prototype — data collection in progress.
        No prediction logic is implemented here.
"""

from flask import Blueprint, render_template, request, jsonify

from app.services.cognitive_offloading import (
    model_service,
    validate_prototype_input,
)
from app.services.cognitive_offloading.schemas import (
    GENAI_USAGE_FREQUENCY,
    WEEKLY_GENAI_USAGE,
    ACADEMIC_PURPOSE,
    VERIFICATION_FREQUENCY,
    INDEPENDENT_LEARNING,
    ACADEMIC_YEAR,
)

component1_bp = Blueprint("component1", __name__, url_prefix="/component1")

# API blueprint lives under /api to keep UI and API routes separate
api_component1_bp = Blueprint("api_component1", __name__, url_prefix="/api/component1")


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@component1_bp.route("/")
def index():
    """
    Component 1 interactive prototype page.
    Passes allowed schema values to template for populating select fields.
    """
    return render_template(
        "components/component1.html",
        schema={
            "genai_usage_frequency": sorted(GENAI_USAGE_FREQUENCY),
            "weekly_genai_usage":    sorted(WEEKLY_GENAI_USAGE),
            "academic_purpose":      sorted(ACADEMIC_PURPOSE),
            "verification_frequency":sorted(VERIFICATION_FREQUENCY),
            "independent_learning":  sorted(INDEPENDENT_LEARNING),
            "academic_year":         sorted(ACADEMIC_YEAR),
        },
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_component1_bp.route("/status", methods=["GET"])
def status():
    """
    Return the current model readiness status for Component 1.

    Response:
        200 JSON – component, stage, data_collection, model_trained,
                   prediction_available, explainability_available
    """
    return jsonify(model_service.get_status()), 200


@api_component1_bp.route("/validate-input", methods=["POST"])
def validate_input():
    """
    Validate a prototype behavioural input submission.

    Accepts JSON body with prototype predictor fields.
    Does NOT perform any risk prediction.
    Does NOT store or log submitted values.

    Returns:
        200 JSON – validation success with model_ready = false
        400 JSON – validation errors
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "error",
            "message": "Request body must be valid JSON.",
            "errors": ["No JSON body received."],
        }), 400

    result = validate_prototype_input(data)

    if not result.is_valid:
        return jsonify({
            "status": "invalid",
            "message": "Prototype input validation failed.",
            "errors": result.errors,
        }), 400

    return jsonify({
        "status":         "valid",
        "message":        "Prototype input validated successfully.",
        "model_ready":    False,
        "research_stage": "data_collection",
        "next_stage":     "preprocessing_and_model_development",
        "validated_input": result.sanitized,
    }), 200
