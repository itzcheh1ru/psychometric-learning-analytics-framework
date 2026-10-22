"""
app/routes/main.py – Core routes: homepage, dashboard, project, and health check.

Psychometric Learning Analytics Framework (J26-DS-310)
"""

from flask import Blueprint, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Homepage – project overview."""
    return render_template("index.html")


@main_bp.route("/dashboard", strict_slashes=False)
def dashboard():
    """Research analytics overview dashboard."""
    return render_template("dashboard.html")


@main_bp.route("/project", strict_slashes=False)
def project():
    """Project information page."""
    return render_template("project.html")


@main_bp.route("/health", methods=["GET"])
def health():
    """
    Lightweight health check endpoint for hosting and deployment monitoring.

    Returns:
        200 JSON – basic application identity and status.
    """
    return jsonify({
        "status": "ok",
        "application": "Psychometric Learning Analytics Framework",
        "project_id": "J26-DS-310",
    }), 200
