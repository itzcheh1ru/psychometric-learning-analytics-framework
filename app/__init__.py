"""
app/__init__.py – Flask application factory.

Psychometric Learning Analytics Framework (J26-DS-310)
Prototype status: data collection in progress.
"""

from flask import Flask


def create_app() -> Flask:
    """
    Create and configure the Flask application instance.

    Returns:
        Flask: Configured application instance.
    """
    app = Flask(__name__)

    # ------------------------------------------------------------------ #
    # Register blueprints                                                  #
    # ------------------------------------------------------------------ #
    from app.routes.main import main_bp
    from app.routes.component1 import component1_bp, api_component1_bp
    from app.routes.component2 import component2_bp, api_component2_bp
    from app.routes.component3 import component3_bp
    from app.routes.component4 import component4_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(component1_bp)
    app.register_blueprint(api_component1_bp)
    app.register_blueprint(component2_bp)
    app.register_blueprint(api_component2_bp)
    app.register_blueprint(component3_bp)
    app.register_blueprint(component4_bp)

    return app
