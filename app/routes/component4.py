"""
app/routes/component4.py – Routes for Component 4:
GenAI-Assisted Cognitive Engagement, Recall & Learning Retention.

Status: Module under development – data collection in progress.
"""

from flask import Blueprint, render_template

component4_bp = Blueprint("component4", __name__, url_prefix="/component4")


@component4_bp.route("/")
def index():
    """Component 4 detail page."""
    return render_template("components/component4.html")
