"""
app/routes/component3.py – Routes for Component 3:
Longitudinal AI-Assisted Study Pattern Analytics.

Status: Module under development – data collection in progress.
"""

from flask import Blueprint, render_template

component3_bp = Blueprint("component3", __name__, url_prefix="/component3")


@component3_bp.route("/")
def index():
    """Component 3 detail page."""
    return render_template("components/component3.html")
