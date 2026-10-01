"""
app/routes/component2.py – Routes for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).

Endpoints:
  GET /component2/                  – Interactive research prototype UI
  GET /api/component2/status        – Model readiness status (JSON)
  GET /api/component2/specification – Research model specification metadata (JSON)

Status: Prototype – data collection in progress.
        No empirical SEM results or fabricated statistics.
"""

from flask import Blueprint, jsonify, render_template

from app.services.sem_analysis import (
    CONSTRUCTS,
    MODEL_SPECIFICATION,
    PLANNED_MEASUREMENT_METRICS,
    PLANNED_MODEL_FIT_METRICS,
    PLANNED_STRUCTURAL_METRICS,
    status_service,
)

component2_bp = Blueprint("component2", __name__, url_prefix="/component2")
api_component2_bp = Blueprint("api_component2", __name__, url_prefix="/api/component2")


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@component2_bp.route("/")
def index():
    """
    Component 2 interactive research prototype page.
    Renders research model specification, CFA/SEM workflows, and planned metrics.
    """
    return render_template(
        "components/component2.html",
        constructs=CONSTRUCTS,
        specification=MODEL_SPECIFICATION,
        measurement_metrics=PLANNED_MEASUREMENT_METRICS,
        structural_metrics=PLANNED_STRUCTURAL_METRICS,
        model_fit_metrics=PLANNED_MODEL_FIT_METRICS,
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_component2_bp.route("/status", methods=["GET"])
def status():
    """
    Return the current readiness status of the SEM analysis pipeline.

    Response:
        200 JSON – readiness metadata indicating data collection in progress.
    """
    return jsonify(status_service.get_status()), 200


@api_component2_bp.route("/specification", methods=["GET"])
def specification():
    """
    Return the research model specification metadata.

    Response:
        200 JSON – construct definitions and planned analytical model design.
    """
    return jsonify(MODEL_SPECIFICATION), 200
