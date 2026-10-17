"""
app/routes/framework.py – Routes for the Framework Integration layer.

Endpoints:
  GET  /framework/                       – Full architectural integration page
  GET  /api/framework/status             – Aggregated component readiness (JSON)
  GET  /api/framework/specification      – Framework specification metadata (JSON)

Status: Prototype – data collection in progress.
        No combined model, no overall score, no cross-component results.
"""

from flask import Blueprint, jsonify, render_template

from app.services.framework import (
    COMPONENT_REGISTRY,
    FRAMEWORK_SPECIFICATION,
    framework_status_service,
)

framework_bp = Blueprint("framework", __name__, url_prefix="/framework")
api_framework_bp = Blueprint("api_framework", __name__, url_prefix="/api/framework")


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@framework_bp.route("/")
def index():
    """
    Framework Integration architectural page.

    Renders integration architecture, data source mapping, method comparison,
    analytical independence section, and system readiness table.
    """
    return render_template(
        "framework.html",
        components=COMPONENT_REGISTRY,
        specification=FRAMEWORK_SPECIFICATION,
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_framework_bp.route("/status", methods=["GET"])
def status():
    """
    Return aggregated prototype readiness status for all four components.

    Does NOT return a combined model, overall risk score, or cross-component
    classification. integration_principle = 'Complementary Evidence'.

    Response:
        200 JSON – per-component readiness metadata.
    """
    return jsonify(framework_status_service.get_status()), 200


@api_framework_bp.route("/specification", methods=["GET"])
def specification():
    """
    Return the full framework specification metadata.

    Includes component roles, methods, data sources, and integration principle.
    single_combined_model = False, overall_score_available = False.

    Response:
        200 JSON – framework specification.
    """
    return jsonify(FRAMEWORK_SPECIFICATION), 200
