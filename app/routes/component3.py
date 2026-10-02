"""
app/routes/component3.py – Routes for Component 3:
Longitudinal AI-Assisted Study Pattern Analytics.

Endpoints:
  GET  /component3/                           – Interactive prototype UI
  GET  /api/component3/status                 – Pipeline readiness status (JSON)
  GET  /api/component3/specification          – Longitudinal specification metadata (JSON)
  POST /api/component3/validate-weekly-record – Weekly record prototype validation (JSON)

Status: Prototype – data collection in progress.
        No empirical trend results or participant data persistence.
"""

from flask import Blueprint, jsonify, render_template, request

from app.services.longitudinal import (
    ACADEMIC_PERIODS,
    ALLOWED_WEEKS,
    BEHAVIOURAL_INDICATORS,
    LEARNING_ACTIVITIES,
    LONGITUDINAL_SPECIFICATION,
    PROMPT_PURPOSES,
    analysis_service,
    validate_weekly_record,
)

component3_bp = Blueprint("component3", __name__, url_prefix="/component3")
api_component3_bp = Blueprint("api_component3", __name__, url_prefix="/api/component3")


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@component3_bp.route("/")
def index():
    """
    Component 3 interactive prototype page.
    Supplies schema dropdown values and indicator definitions to template.
    """
    return render_template(
        "components/component3.html",
        allowed_weeks=sorted(list(ALLOWED_WEEKS)),
        academic_periods=sorted(list(ACADEMIC_PERIODS)),
        learning_activities=sorted(list(LEARNING_ACTIVITIES)),
        prompt_purposes=sorted(list(PROMPT_PURPOSES)),
        indicators=BEHAVIOURAL_INDICATORS,
        specification=LONGITUDINAL_SPECIFICATION,
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_component3_bp.route("/status", methods=["GET"])
def status():
    """
    Return the readiness status of the longitudinal analysis pipeline.

    Response:
        200 JSON – pipeline status metadata.
    """
    return jsonify(analysis_service.get_status()), 200


@api_component3_bp.route("/specification", methods=["GET"])
def specification():
    """
    Return the longitudinal research specification metadata.

    Response:
        200 JSON – collection structure, indicators, and analysis methods.
    """
    return jsonify(LONGITUDINAL_SPECIFICATION), 200


@api_component3_bp.route("/validate-weekly-record", methods=["POST"])
def validate_record():
    """
    Validate a prototype weekly study record.

    Validates record structure, ranges, and categories.
    Does NOT calculate trends or study-pattern classifications.
    Does NOT store the record in any database or log.

    Returns:
        200 JSON – validation success with analysis_ready = False
        400 JSON – validation errors
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "invalid",
            "message": "Request body must be valid JSON.",
            "errors": ["No JSON body received."],
        }), 400

    result = validate_weekly_record(data)

    if not result.is_valid:
        return jsonify({
            "status": "invalid",
            "message": "Weekly prototype record validation failed.",
            "errors": result.errors,
        }), 400

    return jsonify({
        "status": "valid",
        "message": "Weekly prototype record validated successfully.",
        "analysis_ready": False,
        "research_stage": "longitudinal_data_collection",
        "persistence": False,
        "validated_record": result.sanitized,
    }), 200
