"""
tests/conftest.py – Global pytest fixtures for Psychometric Learning Analytics Framework.
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """Create a Flask test application instance."""
    flask_app = create_app()
    flask_app.config.update({"TESTING": True})
    return flask_app


@pytest.fixture
def client(app):
    """Provide a test client for the Flask application."""
    return app.test_client()
