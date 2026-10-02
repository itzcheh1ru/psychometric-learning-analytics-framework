"""
app/routes/component4.py – Routes for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Endpoints:
  GET  /component4/                       – Interactive prototype UI
  GET  /api/component4/status             – Experimental pipeline status (JSON)
  GET  /api/component4/specification      – Research specification metadata (JSON)
  POST /api/component4/validate-session   – Experimental session prototype validation (JSON)

Status: Prototype – data collection in progress.
        No empirical retention results, mock essays, or simulated statistics.
"""

from flask import Blueprint, jsonify, render_template, request

from app.services.retention import (
    CONDITION_ORDERS,
    EXPERIMENTAL_CONDITIONS,
    LEARNING_OUTCOMES,
    NLP_FEATURES,
    RETENTION_SPECIFICATION,
    SESSION_STAGES,
    analysis_service,
    validate_experimental_session,
)

component4_bp = Blueprint("component4", __name__, url_prefix="/component4")
api_component4_bp = Blueprint("api_component4", __name__, url_prefix="/api/component4")


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@component4_bp.route("/")
def index():
    """
    Component 4 interactive prototype page.
    Renders controlled conditions, counterbalancing, session form, and NLP framework.
    """
    return render_template(
        "components/component4.html",
        conditions=sorted(list(EXPERIMENTAL_CONDITIONS)),
        condition_orders=sorted(list(CONDITION_ORDERS)),
        session_stages=list(SESSION_STAGES),
        outcomes=LEARNING_OUTCOMES,
        nlp_features=NLP_FEATURES,
        specification=RETENTION_SPECIFICATION,
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_component4_bp.route("/status", methods=["GET"])
def status():
    """
    Return the readiness status of the cognitive retention evaluation pipeline.

    Response:
        200 JSON – pipeline status metadata.
    """
    return jsonify(analysis_service.get_status()), 200


@api_component4_bp.route("/specification", methods=["GET"])
def specification():
    """
    Return the research specification metadata for Component 4.

    Response:
        200 JSON – conditions, outcomes, NLP features, and evaluation criteria.
    """
    return jsonify(RETENTION_SPECIFICATION), 200


@api_component4_bp.route("/validate-session", methods=["POST"])
def validate_session():
    """
    Validate a prototype experimental session record.

    Validates session metadata structure, counterbalancing order, and consent.
    Does NOT calculate learning retention or writing scores.
    Does NOT store or log participant submissions.

    Returns:
        200 JSON – validation success with analysis_ready = False
        400 JSON – validation errors
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "valid": False,
            "status": "invalid",
            "message": "Request body must be valid JSON.",
            "errors": ["No JSON body received."],
        }), 400

    result = validate_experimental_session(data)

    if not result.is_valid:
        return jsonify({
            "valid": False,
            "status": "invalid",
            "message": "Prototype experimental session validation failed.",
            "errors": result.errors,
        }), 400

    return jsonify({
        "valid": True,
        "status": "valid",
        "message": "Prototype experimental session validated successfully.",
        "analysis_ready": False,
        "research_stage": "experimental_data_collection",
        "persistence": False,
        "validated_session": result.sanitized,
    }), 200
