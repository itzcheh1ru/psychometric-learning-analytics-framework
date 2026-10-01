"""
tests/test_app.py – Tests for the Psychometric Learning Analytics Framework.

Feature 001: Application factory + route smoke tests.
Feature 002: /project route, dashboard content, component titles.
Feature 003: Component 1 interactive prototype workflow:
  - GET /component1/ returns 200 and required page content
  - GET /api/component1/status returns 200, model_trained=false, prediction_available=false
  - POST /api/component1/validate-input:
      - valid input returns 200
      - missing required field returns 400
      - invalid category returns 400
      - malformed participant reference returns 400
      - valid response does NOT contain prediction probability or risk category
  - Component 1 page contains:
      - Target Leakage Protection
      - Available after model training
      - Clear statement that model/analytics are not currently available
  - Model service predict() raises ModelNotAvailableError
  - No regression on Feature 001 / Feature 002 tests
"""

import json
import pytest
from app import create_app
from app.services.cognitive_offloading.model_service import (
    CognitiveOffloadingModelService,
    ModelNotAvailableError,
)
from app.services.sem_analysis import (
    SemResultsNotAvailableError,
    SemResultService,
    result_service,
    status_service,
)
from app.services.longitudinal import (
    LongitudinalAnalysisNotAvailableError,
    LongitudinalAnalysisService,
    analysis_service,
)


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
# Valid payload fixture for Component 1 API tests                             #
# --------------------------------------------------------------------------- #

@pytest.fixture
def valid_payload():
    """Return a valid prototype behavioural input payload."""
    return {
        "participant_reference":  "P0001",
        "genai_usage_frequency":  "Often",
        "weekly_genai_usage":     "4-7 hours",
        "academic_purpose":       "Concept explanation",
        "verification_frequency": "Often",
        "independent_learning":   "High",
        "academic_year":          "Year 4",
    }


@pytest.fixture
def valid_weekly_payload():
    """Return a valid prototype weekly study record payload."""
    return {
        "participant_reference": "P0001",
        "study_week": "Week 2",
        "ai_study_hours": 5.5,
        "independent_study_hours": 8.0,
        "academic_period": "Regular study week",
        "learning_activity": "Concept learning",
        "prompt_count": 12,
        "prompt_purpose": "Concept explanation",
    }


# =========================================================================== #
# Feature 001: Application Factory & Baseline Smoke Tests                    #
# =========================================================================== #

def test_create_app_returns_flask_instance(app):
    from flask import Flask
    assert isinstance(app, Flask)


def test_create_app_has_testing_config(app):
    assert app.config["TESTING"] is True


def test_homepage_returns_200(client):
    assert client.get("/").status_code == 200


def test_dashboard_returns_200(client):
    assert client.get("/dashboard").status_code == 200


def test_component1_returns_200(client):
    assert client.get("/component1/").status_code == 200


def test_component2_returns_200(client):
    assert client.get("/component2/").status_code == 200


def test_component3_returns_200(client):
    assert client.get("/component3/").status_code == 200


def test_component4_returns_200(client):
    assert client.get("/component4/").status_code == 200


def test_unknown_route_returns_404(client):
    assert client.get("/nonexistent-page").status_code == 404


def test_homepage_contains_project_title(client):
    response = client.get("/")
    assert b"Psychometric Learning Analytics Framework" in response.data


def test_homepage_contains_project_id(client):
    response = client.get("/")
    assert b"J26-DS-310" in response.data


# =========================================================================== #
# Feature 002: Dashboard Content & Project Page                               #
# =========================================================================== #

def test_dashboard_contains_all_four_module_names(client):
    data = client.get("/dashboard").data
    assert b"Cognitive Offloading" in data
    assert b"Algorithmic Trust" in data
    assert b"Longitudinal" in data
    assert b"Learning Retention" in data


def test_dashboard_contains_prototype_status(client):
    data = client.get("/dashboard").data
    assert b"data collection" in data.lower() or b"Data Collection" in data


def test_dashboard_shows_open_module_links(client):
    data = client.get("/dashboard").data
    assert b"Open Module" in data


def test_dashboard_no_fake_analytical_values(client):
    data = client.get("/dashboard").data
    assert b"accuracy: 9" not in data.lower()
    assert b"risk: 7" not in data.lower()
    assert b"p-value" not in data.lower()


def test_component2_contains_correct_title(client):
    data = client.get("/component2/").data
    assert b"Algorithmic Trust" in data


def test_component3_contains_correct_title(client):
    data = client.get("/component3/").data
    assert b"Longitudinal" in data


def test_component4_contains_correct_title(client):
    data = client.get("/component4/").data
    assert b"Learning Retention" in data


def test_components_2_to_4_show_empty_analytics_state(client):
    for url in ["/component2/", "/component3/", "/component4/"]:
        data = client.get(url).data
        assert b"not yet available" in data, f"{url} missing empty-state message"


def test_project_page_returns_200(client):
    assert client.get("/project").status_code == 200


def test_project_page_contains_project_id(client):
    data = client.get("/project").data
    assert b"J26-DS-310" in data


def test_project_page_contains_prototype_note(client):
    data = client.get("/project").data
    assert b"Prototype" in data or b"prototype" in data


def test_project_page_no_personal_contact_info(client):
    data = client.get("/project").data
    assert b"@gmail" not in data
    assert b"@sliit.lk" not in data


def test_all_sidebar_routes_are_reachable(client):
    for route in ["/", "/dashboard", "/component1/", "/component2/", "/component3/", "/component4/", "/project"]:
        assert client.get(route).status_code == 200, f"{route} returned non-200"


# =========================================================================== #
# Feature 003: Component 1 Interactive Prototype Workflow                    #
# =========================================================================== #

# 1. Page title & structure
def test_component1_page_contains_correct_title(client):
    """Component 1 page must display its full research title."""
    data = client.get("/component1/").data
    assert b"Explainable Cognitive Offloading Risk Prediction" in data


def test_component1_page_contains_target_leakage_protection(client):
    """Component 1 page must have the Target Leakage Protection panel."""
    data = client.get("/component1/").data
    assert b"Target Leakage Protection" in data
    assert b"TARGET ITEMS" in data or b"TARGET ITEMS \xe2\x89\xa0" in data or b"TARGET ITEMS &#x2260;" in data or b"TARGET ITEMS &ne;" in data


def test_component1_page_contains_available_after_model_training(client):
    """Component 1 page must display 'Available after model training' in planned output cards."""
    data = client.get("/component1/").data
    assert b"Available after model training" in data


def test_component1_page_clearly_states_model_not_currently_available(client):
    """Component 1 page must state that the prediction model is not currently trained/available."""
    data = client.get("/component1/").data
    # Notice banner and/or workflow step mentions this
    assert b"does not generate research predictions" in data or b"Model Development Pending" in data


def test_component1_page_has_validate_button_not_predict_button(client):
    """Component 1 submit button must say 'Validate Prototype Input', NOT 'Predict Risk'."""
    data = client.get("/component1/").data
    assert b"Validate Prototype Input" in data
    assert b"Predict Risk" not in data


def test_component1_page_does_not_contain_target_questions_in_form(client):
    """Form should not ask cognitive-offloading target questions directly."""
    data = client.get("/component1/").data
    # The target scale items should NOT be form field labels
    assert b"how often do you rely entirely on AI to think for you" not in data.lower()


# 2. Status API
def test_component1_status_api_returns_200(client):
    """GET /api/component1/status must return HTTP 200."""
    response = client.get("/api/component1/status")
    assert response.status_code == 200


def test_component1_status_api_reports_model_not_trained(client):
    """Status API must report model_trained = False."""
    response = client.get("/api/component1/status")
    body = response.get_json()
    assert body["model_trained"] is False


def test_component1_status_api_reports_prediction_unavailable(client):
    """Status API must report prediction_available = False."""
    response = client.get("/api/component1/status")
    body = response.get_json()
    assert body["prediction_available"] is False


def test_component1_status_api_reports_explainability_unavailable(client):
    """Status API must report explainability_available = False."""
    response = client.get("/api/component1/status")
    body = response.get_json()
    assert body["explainability_available"] is False


def test_component1_status_api_reports_data_collection_in_progress(client):
    """Status API must report data_collection = 'in_progress'."""
    response = client.get("/api/component1/status")
    body = response.get_json()
    assert body["data_collection"] == "in_progress"


# 3. Input Validation API
def test_validate_input_with_valid_payload_returns_200(client, valid_payload):
    """POST /api/component1/validate-input with valid data must return HTTP 200."""
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "valid"
    assert body["model_ready"] is False


def test_validate_input_response_does_not_contain_prediction_probability(client, valid_payload):
    """Validation response must NOT contain any prediction probability value."""
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    body = response.get_json()
    assert "probability" not in body
    assert "risk_probability" not in body
    assert "prediction" not in body


def test_validate_input_response_does_not_contain_risk_classification(client, valid_payload):
    """Validation response must NOT contain any risk classification category."""
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    body = response.get_json()
    assert "risk_category" not in body
    assert "risk_classification" not in body
    assert "risk_level" not in body


def test_validate_input_missing_required_field_returns_400(client, valid_payload):
    """Missing a required field must return HTTP 400 with descriptive error."""
    del valid_payload["genai_usage_frequency"]
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] == "invalid"
    assert any("genai_usage_frequency" in err for err in body["errors"])


def test_validate_input_invalid_category_returns_400(client, valid_payload):
    """Submitting an unrecognised category value must return HTTP 400."""
    valid_payload["weekly_genai_usage"] = "100 hours per day"  # Not in allowed set
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] == "invalid"
    assert any("weekly_genai_usage" in err for err in body["errors"])


def test_validate_input_malformed_participant_reference_returns_400(client, valid_payload):
    """Participant reference with invalid characters (e.g. email or spaces) must return 400."""
    valid_payload["participant_reference"] = "student@sliit.lk"  # Not allowed
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] == "invalid"
    assert any("Participant reference" in err for err in body["errors"])


def test_validate_input_too_long_participant_reference_returns_400(client, valid_payload):
    """Participant reference exceeding 20 chars must return 400."""
    valid_payload["participant_reference"] = "P" * 25
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_validate_input_non_json_request_returns_400(client):
    """Sending non-JSON request body must return HTTP 400."""
    response = client.post(
        "/api/component1/validate-input",
        data="not json",
        content_type="text/plain",
    )
    assert response.status_code == 400


def test_validate_input_optional_year_can_be_omitted(client, valid_payload):
    """Academic year is optional — omitting it should still return 200."""
    del valid_payload["academic_year"]
    response = client.post(
        "/api/component1/validate-input",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert response.status_code == 200


# 4. Model Service Unit Tests
def test_model_service_predict_raises_model_not_available_error():
    """model_service.predict() must raise ModelNotAvailableError during prototype stage."""
    svc = CognitiveOffloadingModelService()
    with pytest.raises(ModelNotAvailableError) as exc_info:
        svc.predict({"sample": "feature"})
    assert "has not been trained yet" in str(exc_info.value)


def test_model_service_explain_raises_model_not_available_error():
    """model_service.explain() must raise ModelNotAvailableError during prototype stage."""
    svc = CognitiveOffloadingModelService()
    with pytest.raises(ModelNotAvailableError) as exc_info:
        svc.explain({"sample": "feature"})
    assert "SHAP explanation is not available" in str(exc_info.value)


def test_model_service_is_model_available_returns_false():
    """model_service.is_model_available() must return False during prototype stage."""
    svc = CognitiveOffloadingModelService()
    assert svc.is_model_available() is False


# =========================================================================== #
# Feature 004: Component 2 SEM Analysis Prototype Workflow                  #
# =========================================================================== #

# 1. UI route and page content
def test_component2_page_returns_200(client):
    """GET /component2/ must return HTTP 200."""
    response = client.get("/component2/")
    assert response.status_code == 200


def test_component2_page_contains_algorithmic_trust(client):
    """Component 2 page must contain 'Algorithmic Trust'."""
    data = client.get("/component2/").data
    assert b"Algorithmic Trust" in data


def test_component2_page_contains_perceived_usefulness(client):
    """Component 2 page must contain 'Perceived Usefulness'."""
    data = client.get("/component2/").data
    assert b"Perceived Usefulness" in data


def test_component2_page_contains_verification_behaviour(client):
    """Component 2 page must contain 'Verification Behaviour'."""
    data = client.get("/component2/").data
    assert b"Verification Behaviour" in data


def test_component2_page_contains_ai_dependence(client):
    """Component 2 page must contain 'AI Dependence'."""
    data = client.get("/component2/").data
    assert b"AI Dependence" in data


def test_component2_page_contains_learning_confidence(client):
    """Component 2 page must contain 'Learning Confidence'."""
    data = client.get("/component2/").data
    assert b"Learning Confidence" in data


def test_component2_page_contains_cfa(client):
    """Component 2 page must contain 'Confirmatory Factor Analysis'."""
    data = client.get("/component2/").data
    assert b"Confirmatory Factor Analysis" in data


def test_component2_page_contains_sem(client):
    """Component 2 page must contain 'Structural Equation Modelling'."""
    data = client.get("/component2/").data
    assert b"Structural Equation Modelling" in data


def test_component2_page_contains_pending_sem_estimation(client):
    """Component 2 page must display 'Pending SEM estimation' for uncomputed metrics."""
    data = client.get("/component2/").data
    assert b"Pending SEM estimation" in data


def test_component2_page_identifies_planned_relationships(client):
    """Component 2 page must clearly label the structural model as planned relationships to be tested."""
    data = client.get("/component2/").data
    assert b"PLANNED RELATIONSHIPS TO BE TESTED" in data or b"planned relationships to be tested" in data.lower()
    # Must NOT label the conceptual model as empirical SEM results
    assert b"confirmed relationships" not in data.lower()


# 2. Status API
def test_component2_status_api_returns_200(client):
    """GET /api/component2/status must return HTTP 200."""
    response = client.get("/api/component2/status")
    assert response.status_code == 200


def test_component2_status_api_reports_measurement_model_not_estimated(client):
    """Status API must report measurement_model_estimated = False."""
    response = client.get("/api/component2/status")
    body = response.get_json()
    assert body["measurement_model_estimated"] is False


def test_component2_status_api_reports_structural_model_not_estimated(client):
    """Status API must report structural_model_estimated = False."""
    response = client.get("/api/component2/status")
    body = response.get_json()
    assert body["structural_model_estimated"] is False


def test_component2_status_api_reports_sem_results_unavailable(client):
    """Status API must report sem_results_available = False."""
    response = client.get("/api/component2/status")
    body = response.get_json()
    assert body["sem_results_available"] is False
    assert body["mediation_results_available"] is False


# 3. Specification API
def test_component2_specification_api_returns_200(client):
    """GET /api/component2/specification must return HTTP 200."""
    response = client.get("/api/component2/specification")
    assert response.status_code == 200


def test_component2_specification_contains_approved_constructs(client):
    """Specification API must return exactly the five approved constructs."""
    response = client.get("/api/component2/specification")
    body = response.get_json()
    assert "constructs" in body
    codes = [c["code"] for c in body["constructs"]]
    assert set(codes) == {"AT", "PU", "VB", "AD", "LC"}
    assert len(codes) == 5


# 4. Result Service Unit Tests
def test_sem_result_service_raises_sem_results_not_available_error():
    """result_service.get_results() must raise SemResultsNotAvailableError during prototype stage."""
    svc = SemResultService()
    with pytest.raises(SemResultsNotAvailableError) as exc_info:
        svc.get_results()
    assert "not available until validated research data has been analysed" in str(exc_info.value)


def test_sem_result_service_results_available_returns_false():
    """result_service.results_available() must return False during prototype stage."""
    svc = SemResultService()
    assert svc.results_available() is False


# 5. Research Integrity: No fake numerical analytical results in APIs
def test_component2_apis_do_not_contain_fake_results(client):
    """Status and specification APIs must not contain fabricated statistical findings."""
    status_data = client.get("/api/component2/status").get_json()
    spec_data = client.get("/api/component2/specification").get_json()

    for payload in [status_data, spec_data]:
        payload_str = json.dumps(payload).lower()
        assert "cfi" not in payload_str
        assert "rmsea" not in payload_str
        assert "p-value" not in payload_str
        assert "path_coefficient" not in payload_str
        assert "significant" not in payload_str


# =========================================================================== #
# Feature 005: Component 3 Longitudinal Analytics Prototype Workflow        #
# =========================================================================== #

# 1. UI route and page content
def test_component3_page_returns_200(client):
    """GET /component3/ must return HTTP 200."""
    response = client.get("/component3/")
    assert response.status_code == 200


def test_component3_page_contains_title(client):
    """Component 3 page must contain 'Longitudinal AI-Assisted Study Pattern Analytics'."""
    data = client.get("/component3/").data
    assert b"Longitudinal AI-Assisted Study Pattern Analytics" in data


def test_component3_page_contains_prototype_record(client):
    """Component 3 page must contain 'Prototype record'."""
    data = client.get("/component3/").data
    assert b"Prototype record" in data or b"prototype record" in data.lower()


def test_component3_page_contains_available_after_longitudinal_data_collection(client):
    """Component 3 page must display 'Available after longitudinal data collection'."""
    data = client.get("/component3/").data
    assert b"Available after longitudinal data collection" in data


# 2. Status API
def test_component3_status_api_returns_200(client):
    """GET /api/component3/status must return HTTP 200."""
    response = client.get("/api/component3/status")
    assert response.status_code == 200


def test_component3_status_api_reports_dataset_not_ready(client):
    """Status API must report dataset_ready = False."""
    body = client.get("/api/component3/status").get_json()
    assert body["dataset_ready"] is False


def test_component3_status_api_reports_trend_analysis_unavailable(client):
    """Status API must report trend_analysis_available = False."""
    body = client.get("/api/component3/status").get_json()
    assert body["trend_analysis_available"] is False


def test_component3_status_api_reports_prompt_analysis_unavailable(client):
    """Status API must report prompt_analysis_available = False."""
    body = client.get("/api/component3/status").get_json()
    assert body["prompt_analysis_available"] is False


def test_component3_status_api_reports_study_pattern_results_unavailable(client):
    """Status API must report study_pattern_results_available = False."""
    body = client.get("/api/component3/status").get_json()
    assert body["study_pattern_results_available"] is False


# 3. Specification API
def test_component3_specification_api_returns_200(client):
    """GET /api/component3/specification must return HTTP 200."""
    response = client.get("/api/component3/specification")
    assert response.status_code == 200


def test_component3_specification_identifies_duration(client):
    """Specification must identify planned duration as 4-6 weeks."""
    body = client.get("/api/component3/specification").get_json()
    assert "collection" in body
    assert "4-6 weeks" in body["collection"]["planned_duration"]


def test_component3_specification_includes_ai_study_share(client):
    """Specification must include 'AI Study Share' indicator."""
    body = client.get("/api/component3/specification").get_json()
    assert "AI Study Share" in body["indicators"]


def test_component3_specification_includes_independent_study_share(client):
    """Specification must include 'Independent Study Share' indicator."""
    body = client.get("/api/component3/specification").get_json()
    assert "Independent Study Share" in body["indicators"]


def test_component3_specification_includes_prompt_frequency(client):
    """Specification must include 'Prompt Frequency' indicator."""
    body = client.get("/api/component3/specification").get_json()
    assert "Prompt Frequency" in body["indicators"]


# 4. Weekly Record Validation API
def test_validate_weekly_record_valid_returns_200(client, valid_weekly_payload):
    """POST /api/component3/validate-weekly-record with valid payload returns HTTP 200."""
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "valid"
    assert body["analysis_ready"] is False
    assert body["persistence"] is False


def test_validate_weekly_record_missing_participant_id_returns_400(client, valid_weekly_payload):
    """Missing participant reference ID returns HTTP 400."""
    del valid_weekly_payload["participant_reference"]
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] == "invalid"
    assert any("participant_reference" in err for err in body["errors"])


def test_validate_weekly_record_malformed_participant_id_returns_400(client, valid_weekly_payload):
    """Malformed participant ID (e.g. email or invalid characters) returns HTTP 400."""
    valid_weekly_payload["participant_reference"] = "student@sliit.lk"
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("Participant reference" in err for err in body["errors"])


def test_validate_weekly_record_invalid_week_returns_400(client, valid_weekly_payload):
    """Invalid study week returns HTTP 400."""
    valid_weekly_payload["study_week"] = "Week 10"  # Allowed is Week 1-6
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("study week" in err for err in body["errors"])


def test_validate_weekly_record_negative_ai_hours_returns_400(client, valid_weekly_payload):
    """Negative AI-assisted study hours returns HTTP 400."""
    valid_weekly_payload["ai_study_hours"] = -2.5
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("cannot be negative" in err for err in body["errors"])


def test_validate_weekly_record_excessive_study_hours_returns_400(client, valid_weekly_payload):
    """Excessive study hours (>168 hrs/week) returns HTTP 400."""
    valid_weekly_payload["ai_study_hours"] = 200.0
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("cannot exceed" in err for err in body["errors"])


def test_validate_weekly_record_negative_independent_hours_returns_400(client, valid_weekly_payload):
    """Negative independent study hours returns HTTP 400."""
    valid_weekly_payload["independent_study_hours"] = -1.0
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("cannot be negative" in err for err in body["errors"])


def test_validate_weekly_record_invalid_academic_period_returns_400(client, valid_weekly_payload):
    """Invalid academic period returns HTTP 400."""
    valid_weekly_payload["academic_period"] = "Summer vacation holiday"
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("academic period" in err for err in body["errors"])


def test_validate_weekly_record_invalid_learning_activity_returns_400(client, valid_weekly_payload):
    """Invalid learning activity returns HTTP 400."""
    valid_weekly_payload["learning_activity"] = "Playing video games"
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("learning activity" in err for err in body["errors"])


def test_validate_weekly_record_negative_prompt_count_returns_400(client, valid_weekly_payload):
    """Negative prompt count returns HTTP 400."""
    valid_weekly_payload["prompt_count"] = -5
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("cannot be negative" in err for err in body["errors"])


def test_validate_weekly_record_non_integer_prompt_count_returns_400(client, valid_weekly_payload):
    """Float/non-integer prompt count returns HTTP 400."""
    valid_weekly_payload["prompt_count"] = 4.7
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("integer" in err for err in body["errors"])


def test_validate_weekly_record_invalid_prompt_purpose_returns_400(client, valid_weekly_payload):
    """Invalid prompt purpose returns HTTP 400."""
    valid_weekly_payload["prompt_purpose"] = "Unauthorised purpose"
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("prompt purpose" in err for err in body["errors"])


def test_validate_weekly_record_rejects_unknown_fields(client, valid_weekly_payload):
    """Submitting unexpected/unknown fields must return HTTP 400."""
    valid_weekly_payload["extra_field"] = "unexpected_value"
    valid_weekly_payload["user_real_name"] = "Alice"
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert any("Unknown fields are not permitted" in err for err in body["errors"])


def test_validate_weekly_record_response_does_not_contain_trend_result(client, valid_weekly_payload):
    """Validation response must NOT contain any trend analysis result."""
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    body = response.get_json()
    payload_str = json.dumps(body).lower()
    assert "trend_result" not in payload_str
    assert "trend" not in payload_str
    assert "slope" not in payload_str


def test_validate_weekly_record_response_does_not_contain_study_pattern_classification(client, valid_weekly_payload):
    """Validation response must NOT contain any study-pattern classification."""
    response = client.post(
        "/api/component3/validate-weekly-record",
        data=json.dumps(valid_weekly_payload),
        content_type="application/json",
    )
    body = response.get_json()
    payload_str = json.dumps(body).lower()
    assert "study_pattern_classification" not in payload_str
    assert "classification" not in payload_str
    assert "cluster" not in payload_str


# 5. Longitudinal Analysis Service Unit Tests
def test_longitudinal_analysis_service_raises_not_available_error():
    """analysis_service.get_trends() must raise LongitudinalAnalysisNotAvailableError."""
    svc = LongitudinalAnalysisService()
    with pytest.raises(LongitudinalAnalysisNotAvailableError) as exc_info:
        svc.get_trends()
    assert "not available until the required multi-week research dataset has been collected" in str(exc_info.value)


def test_longitudinal_analysis_service_is_analysis_available_returns_false():
    """analysis_service.is_analysis_available() must return False."""
    svc = LongitudinalAnalysisService()
    assert svc.is_analysis_available() is False
