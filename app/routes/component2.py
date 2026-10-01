"""
app/routes/component2.py – Routes for Component 2:
Algorithmic Trust & Verification Analysis.

Status: Module under development – data collection in progress.
"""

from flask import Blueprint, render_template

component2_bp = Blueprint("component2", __name__, url_prefix="/component2")


@component2_bp.route("/")
def index():
    """Component 2 detail page."""
    return render_template("components/component2.html")
