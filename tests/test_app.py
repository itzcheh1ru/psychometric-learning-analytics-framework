"""
tests/test_app.py – Smoke tests for the Flask application scaffold.

Psychometric Learning Analytics Framework (J26-DS-310)
These tests verify that the application factory can create an app instance
and that core routes return the expected HTTP status codes.

No analytical logic is tested here.  Model and analytics tests will be
added in later features once research data collection is complete.
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


# --------------------------------------------------------------------------- #
# Application Factory Tests                                                    #
# --------------------------------------------------------------------------- #

def test_create_app_returns_flask_instance(app):
    """The application factory must return a Flask application instance."""
    from flask import Flask
    assert isinstance(app, Flask)


def test_create_app_has_testing_config(app):
    """TESTING flag should be set on the test application."""
    assert app.config["TESTING"] is True


# --------------------------------------------------------------------------- #
# Route Smoke Tests                                                            #
# --------------------------------------------------------------------------- #

def test_homepage_returns_200(client):
    """GET / must return HTTP 200 OK."""
    response = client.get("/")
    assert response.status_code == 200


def test_dashboard_returns_200(client):
    """GET /dashboard must return HTTP 200 OK."""
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_component1_returns_200(client):
    """GET /component1/ must return HTTP 200 OK."""
    response = client.get("/component1/")
    assert response.status_code == 200


def test_component2_returns_200(client):
    """GET /component2/ must return HTTP 200 OK."""
    response = client.get("/component2/")
    assert response.status_code == 200


def test_component3_returns_200(client):
    """GET /component3/ must return HTTP 200 OK."""
    response = client.get("/component3/")
    assert response.status_code == 200


def test_component4_returns_200(client):
    """GET /component4/ must return HTTP 200 OK."""
    response = client.get("/component4/")
    assert response.status_code == 200


def test_homepage_contains_project_title(client):
    """Homepage HTML must contain the project title."""
    response = client.get("/")
    assert b"Psychometric Learning Analytics Framework" in response.data


def test_homepage_contains_project_id(client):
    """Homepage HTML must contain the project ID J26-DS-310."""
    response = client.get("/")
    assert b"J26-DS-310" in response.data


def test_dashboard_contains_all_component_names(client):
    """Dashboard must list all four research module names."""
    response = client.get("/dashboard")
    assert b"Cognitive Offloading" in response.data
    assert b"Algorithmic Trust" in response.data
    assert b"Longitudinal" in response.data
    assert b"Learning Retention" in response.data


def test_dashboard_shows_module_under_development(client):
    """Dashboard cards must indicate that modules are under development."""
    response = client.get("/dashboard")
    assert b"under development" in response.data


def test_unknown_route_returns_404(client):
    """An undefined route must return HTTP 404 Not Found."""
    response = client.get("/nonexistent-page")
    assert response.status_code == 404
