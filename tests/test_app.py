"""
tests/test_app.py – Smoke and content tests for the Flask application.

Psychometric Learning Analytics Framework (J26-DS-310)

Feature 001: Application factory + route smoke tests.
Feature 002: /project route, dashboard content, component titles.
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
# Application Factory                                                          #
# --------------------------------------------------------------------------- #

def test_create_app_returns_flask_instance(app):
    """The application factory must return a Flask application instance."""
    from flask import Flask
    assert isinstance(app, Flask)


def test_create_app_has_testing_config(app):
    """TESTING flag must be set on the test application."""
    assert app.config["TESTING"] is True


# --------------------------------------------------------------------------- #
# Route Smoke Tests (Feature 001)                                              #
# --------------------------------------------------------------------------- #

def test_homepage_returns_200(client):
    """GET / must return HTTP 200 OK."""
    assert client.get("/").status_code == 200


def test_dashboard_returns_200(client):
    """GET /dashboard must return HTTP 200 OK."""
    assert client.get("/dashboard").status_code == 200


def test_component1_returns_200(client):
    """GET /component1/ must return HTTP 200 OK."""
    assert client.get("/component1/").status_code == 200


def test_component2_returns_200(client):
    """GET /component2/ must return HTTP 200 OK."""
    assert client.get("/component2/").status_code == 200


def test_component3_returns_200(client):
    """GET /component3/ must return HTTP 200 OK."""
    assert client.get("/component3/").status_code == 200


def test_component4_returns_200(client):
    """GET /component4/ must return HTTP 200 OK."""
    assert client.get("/component4/").status_code == 200


def test_unknown_route_returns_404(client):
    """An undefined route must return HTTP 404 Not Found."""
    assert client.get("/nonexistent-page").status_code == 404


# --------------------------------------------------------------------------- #
# Homepage Content                                                             #
# --------------------------------------------------------------------------- #

def test_homepage_contains_project_title(client):
    """Homepage HTML must contain the project title."""
    response = client.get("/")
    assert b"Psychometric Learning Analytics Framework" in response.data


def test_homepage_contains_project_id(client):
    """Homepage HTML must contain the project ID J26-DS-310."""
    response = client.get("/")
    assert b"J26-DS-310" in response.data


# --------------------------------------------------------------------------- #
# Dashboard Content (Feature 002)                                              #
# --------------------------------------------------------------------------- #

def test_dashboard_contains_all_four_module_names(client):
    """Dashboard must list all four research module names."""
    data = client.get("/dashboard").data
    assert b"Cognitive Offloading" in data
    assert b"Algorithmic Trust" in data
    assert b"Longitudinal" in data
    assert b"Learning Retention" in data


def test_dashboard_contains_prototype_status(client):
    """Dashboard must communicate prototype / data-collection status."""
    data = client.get("/dashboard").data
    # The banner and/or status badges must mention data collection
    assert b"data collection" in data.lower() or b"Data Collection" in data


def test_dashboard_shows_open_module_links(client):
    """Dashboard cards must include 'Open Module' call-to-action links."""
    data = client.get("/dashboard").data
    assert b"Open Module" in data


def test_dashboard_no_fake_analytical_values(client):
    """Dashboard must not contain fabricated accuracy or risk percentages."""
    data = client.get("/dashboard").data
    # These strings would indicate hard-coded fake research results
    assert b"accuracy: 9" not in data.lower()
    assert b"risk: 7" not in data.lower()
    assert b"p-value" not in data.lower()


# --------------------------------------------------------------------------- #
# Component Page Titles (Feature 002)                                          #
# --------------------------------------------------------------------------- #

def test_component1_contains_correct_title(client):
    """Component 1 page must contain its full research title."""
    data = client.get("/component1/").data
    assert b"Cognitive Offloading Risk Prediction" in data


def test_component2_contains_correct_title(client):
    """Component 2 page must contain its full research title."""
    data = client.get("/component2/").data
    assert b"Algorithmic Trust" in data


def test_component3_contains_correct_title(client):
    """Component 3 page must contain its full research title."""
    data = client.get("/component3/").data
    assert b"Longitudinal" in data


def test_component4_contains_correct_title(client):
    """Component 4 page must contain its full research title."""
    data = client.get("/component4/").data
    assert b"Learning Retention" in data


def test_component_pages_show_empty_analytics_state(client):
    """All component pages must show an analytics-unavailable empty state."""
    for url in ["/component1/", "/component2/", "/component3/", "/component4/"]:
        data = client.get(url).data
        assert b"not yet available" in data, f"{url} missing empty-state message"


# --------------------------------------------------------------------------- #
# Project Information Page (Feature 002)                                       #
# --------------------------------------------------------------------------- #

def test_project_page_returns_200(client):
    """GET /project must return HTTP 200 OK."""
    assert client.get("/project").status_code == 200


def test_project_page_contains_project_id(client):
    """Project page must display the project ID J26-DS-310."""
    data = client.get("/project").data
    assert b"J26-DS-310" in data


def test_project_page_contains_prototype_note(client):
    """Project page must include a prototype / data-collection statement."""
    data = client.get("/project").data
    assert (b"Prototype" in data or b"prototype" in data)


def test_project_page_no_personal_contact_info(client):
    """Project page must not contain personal email addresses."""
    data = client.get("/project").data
    assert b"@gmail" not in data
    assert b"@sliit.lk" not in data


# --------------------------------------------------------------------------- #
# Sidebar Navigation (route existence check)                                   #
# --------------------------------------------------------------------------- #

def test_all_sidebar_routes_are_reachable(client):
    """Every route linked from the sidebar must return HTTP 200."""
    sidebar_routes = [
        "/",
        "/dashboard",
        "/component1/",
        "/component2/",
        "/component3/",
        "/component4/",
        "/project",
    ]
    for route in sidebar_routes:
        response = client.get(route)
        assert response.status_code == 200, f"{route} returned {response.status_code}"
