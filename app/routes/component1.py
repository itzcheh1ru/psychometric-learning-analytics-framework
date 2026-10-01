"""
app/routes/component1.py – Routes for Component 1:
Explainable Cognitive Offloading Risk Prediction.

Status: Module under development – data collection in progress.
"""

from flask import Blueprint, render_template

component1_bp = Blueprint("component1", __name__, url_prefix="/component1")


@component1_bp.route("/")
def index():
    """Component 1 detail page."""
    return render_template("components/component1.html")
