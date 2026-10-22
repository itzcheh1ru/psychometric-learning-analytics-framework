"""
app/__init__.py – Flask application factory and lifecycle handlers.

Psychometric Learning Analytics Framework (J26-DS-310)
Prototype status: data collection in progress.
"""

import os
from flask import Flask, jsonify, render_template, request

from app.config import CONFIG_MAP, DevelopmentConfig


def create_app(config_name: str | None = None) -> Flask:
    """
    Create and configure the Flask application instance.

    Args:
        config_name: Optional configuration name ('development', 'testing', 'production').

    Returns:
        Flask: Configured application instance.
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development").lower()
    config_class = CONFIG_MAP.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)

    # ------------------------------------------------------------------ #
    # Register blueprints                                                  #
    # ------------------------------------------------------------------ #
    from app.routes.main import main_bp
    from app.routes.component1 import component1_bp, api_component1_bp
    from app.routes.component2 import component2_bp, api_component2_bp
    from app.routes.component3 import component3_bp, api_component3_bp
    from app.routes.component4 import component4_bp, api_component4_bp
    from app.routes.framework import framework_bp, api_framework_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(framework_bp)
    app.register_blueprint(api_framework_bp)
    app.register_blueprint(component1_bp)
    app.register_blueprint(api_component1_bp)
    app.register_blueprint(component2_bp)
    app.register_blueprint(api_component2_bp)
    app.register_blueprint(component3_bp)
    app.register_blueprint(api_component3_bp)
    app.register_blueprint(component4_bp)
    app.register_blueprint(api_component4_bp)

    # ------------------------------------------------------------------ #
    # Security and cache headers                                         #
    # ------------------------------------------------------------------ #
    @app.after_request
    def apply_security_and_cache_headers(response):
        """Apply security headers and prevent stale API response caching."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Prevent browser/proxy caching for prototype API status and spec endpoints
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"

        return response

    # ------------------------------------------------------------------ #
    # Error handlers                                                     #
    # ------------------------------------------------------------------ #
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found for both web and API requests."""
        if request.path.startswith("/api/") or (
            request.accept_mimetypes.best == "application/json"
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({
                "status": "error",
                "message": "The requested API resource was not found.",
            }), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 Internal Server Error without exposing stack traces."""
        if request.path.startswith("/api/") or (
            request.accept_mimetypes.best == "application/json"
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({
                "status": "error",
                "message": "An internal server error occurred while processing the request.",
            }), 500
        return render_template("errors/500.html"), 500

    return app


def __getattr__(name: str):
    """
    Support WSGI servers looking for 'app' attribute on package (e.g. gunicorn app:app).
    """
    if name == "app":
        return create_app()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
