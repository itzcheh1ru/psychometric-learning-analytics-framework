"""
app/routes/component1.py – Routes for Component 1:
Explainable Cognitive Offloading Risk Prediction (Version 4).

Endpoints:
  GET  /component1/                  – Interactive assessment UI page
  GET  /api/component1/status        – Model readiness status (JSON)
  POST /api/component1/validate-input – Prototype input validation (JSON)
  POST /api/component1/predict       – Deployed ML prediction & LinearSHAP explanation (JSON)

Status: Model Integrated — Version 4 Performance Experiments.
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
api_component1_bp = Blueprint("api_component1", __name__, url_prefix="/api/component1")


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@component1_bp.route("", strict_slashes=False)
@component1_bp.route("/", strict_slashes=False)
def index():
    """
    Component 1 interactive assessment page.
    Passes schema and metadata to template for rendering questionnaire and results.
    """
    status_info = model_service.get_status()
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
        model_status=status_info,
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_component1_bp.route("/status", methods=["GET"])
def status():
    """
    Return the current model readiness status for Component 1.

    Response:
        200 JSON – component, stage, model_trained, prediction_available,
                   explainability_available, champion_model, features_count
    """
    return jsonify(model_service.get_status()), 200


@api_component1_bp.route("/validate-input", methods=["POST"])
def validate_input():
    """
    Validate a prototype behavioural input submission.
    Preserved for schema verification and backwards compatibility.

    Returns:
        200 JSON – validation success
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
        "model_ready":    model_service.is_model_available(),
        "research_stage": "model_integrated",
        "validated_input": result.sanitized,
    }), 200


@api_component1_bp.route("/predict", methods=["POST"])
def predict():
    """
    Execute cognitive offloading risk prediction and LinearSHAP explanation.

    Accepts:
        JSON body with student habit responses (Likert scales 1-5, tools, academic field).
        Accepts raw survey variables, composite indices, or partial inputs with safe median imputation.

    Returns:
        200 JSON – prediction, continuous_risk_score, probabilities, top_contributing_factors
        400 JSON – validation error (e.g. empty or unparseable input)
        500 JSON – inference execution error
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "validation_error",
            "error_type": "MissingRequiredInput",
            "message": "Validation Error: Request body must be valid JSON.",
            "predicted_category": None,
            "continuous_risk_score": None,
            "confidence": None,
            "probabilities": None,
            "top_contributing_factors": [],
            "warnings": ["No JSON body received."],
            "warnings_count": 1,
        }), 400

    try:
        top_factors = data.get("top_factors_count", 5)
        # Support both direct flat payload or {"user_inputs": {...}} wrapper
        inputs = data.get("user_inputs", data)
        result = model_service.predict(inputs, top_factors_count=top_factors)

        status_code = 400 if result.get("status") == "validation_error" else 200
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Inference execution error: {str(e)}",
        }), 500
