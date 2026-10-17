"""
app/routes/main.py – Core routes: homepage, dashboard, and project information.

Psychometric Learning Analytics Framework (J26-DS-310)
"""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Homepage – project overview."""
    return render_template("index.html")


@main_bp.route("/dashboard")
def dashboard():
    """Research analytics overview dashboard."""
    return render_template("dashboard.html")


@main_bp.route("/project")
def project():
    """Project information page."""
    return render_template("project.html")
