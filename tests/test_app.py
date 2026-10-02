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
Feature 007: Integrated four-component research dashboard:
  - GET /framework/ returns 200 with required headings and content
  - GET /api/framework/status returns 200 with correct structure
  - GET /api/framework/specification returns 200 with correct structure
  - Framework service layer imports, registry, and status aggregation
  - No combined model, no overall score, no fake findings in APIs
  - Dashboard upgraded with badges and integration principle notice
  - Sidebar contains Framework Integration link
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
from app.services.retention import (
    RetentionAnalysisNotAvailableError,
    RetentionAnalysisService,
    analysis_service as retention_analysis_service,
)
from app.services.framework import (
    COMPONENT_REGISTRY,
    FRAMEWORK_SPECIFICATION,
    FrameworkStatusService,
    framework_status_service,
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


@pytest.fixture
def valid_session_payload():
    """Return a valid prototype experimental session payload."""
    return {
        "participant_reference": "P0001",
        "experimental_condition": "Brain-only writing",
        "condition_order": "Brain-only first",
        "session_stage": "Writing task",
        "task_reference": "TASK01",
        "consent_confirmed": True,
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


# =========================================================================== #
# Feature 006: Component 4 Cognitive Engagement & Learning Retention         #
# =========================================================================== #

def test_component4_page_returns_200_and_content(client):
    """GET /component4/ returns 200 with required structure and empty-state disclaimer."""
    response = client.get("/component4/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Core condition references
    assert "Brain-Only Writing" in html
    assert "GenAI-Assisted Writing" in html
    assert "Better writing output does not automatically imply better learning" in html
    assert "Pending experimental data" in html or "Pending experimental evaluation" in html
    assert "Available after experimental analysis" in html
    assert "Counterbalanced condition order" in html or "counterbalanced" in html.lower()

    # Empty analytics state check for research integrity
    assert "NLP analytics not yet available" in html

    # Methodological architecture elements
    assert "Controlled Experimental Sessions" in html
    assert "Validate Experimental Session" in html


def test_component4_status_api(client):
    """GET /api/component4/status returns 200 with all availability flags False."""
    response = client.get("/api/component4/status")
    assert response.status_code == 200
    data = response.get_json()

    assert data["dataset_ready"] is False
    assert data["nlp_analysis_available"] is False
    assert data["recall_analysis_available"] is False
    assert data["paired_analysis_available"] is False
    assert data["final_results_available"] is False
    assert "prototype" in data["stage"].lower() or "in_progress" in data["experimental_data_collection"].lower()


def test_component4_specification_api(client):
    """GET /api/component4/specification returns 200 with experimental specifications."""
    response = client.get("/api/component4/specification")
    assert response.status_code == 200
    data = response.get_json()

    assert "Brain-only writing" in data["conditions"]
    assert "GenAI-assisted writing" in data["conditions"]
    assert "Brain-only first" in data["condition_orders"]
    assert "GenAI-assisted first" in data["condition_orders"]
    assert "Writing task" in data["session_stages"]
    assert "Immediate recall" in data["session_stages"]
    assert "Delayed recall" in data["session_stages"]

    outcome_names = [o["name"] for o in data["outcomes"]]
    assert "Immediate Recall" in outcome_names
    assert "Delayed Recall" in outcome_names
    assert "Ownership" in outcome_names
    assert "Cognitive Effort" in outcome_names

    nlp_names = [n["name"] for n in data["nlp_features"]]
    assert "Lexical Diversity" in nlp_names
    assert "Readability Scores" in nlp_names
    assert "Sentence Complexity" in nlp_names
    assert "Semantic Similarity" in nlp_names


def test_validate_session_valid_payload_returns_200(client, valid_session_payload):
    """Valid experimental session payload returns HTTP 200 and echo validated_session."""
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["valid"] is True
    validated = data["validated_session"]
    assert validated["participant_reference"] == "P0001"
    assert validated["experimental_condition"] == "Brain-only writing"
    assert validated["condition_order"] == "Brain-only first"
    assert validated["session_stage"] == "Writing task"
    assert validated["task_reference"] == "TASK01"
    assert validated["consent_confirmed"] is True


def test_validate_session_missing_required_fields_returns_400(client, valid_session_payload):
    """Missing any required field returns HTTP 400 with specific error."""
    required_keys = [
        "participant_reference",
        "experimental_condition",
        "condition_order",
        "session_stage",
        "task_reference",
        "consent_confirmed",
    ]
    for key in required_keys:
        payload = dict(valid_session_payload)
        del payload[key]
        response = client.post(
            "/api/component4/validate-session",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400, f"Expected 400 when '{key}' is missing"
        data = response.get_json()
        assert not data["valid"]
        assert any(key in err or "consent" in err.lower() for err in data["errors"])


def test_validate_session_malformed_participant_reference_returns_400(client, valid_session_payload):
    """Malformed participant reference returns HTTP 400."""
    invalid_refs = ["P@01", "P", "A" * 25, ""]
    for bad_ref in invalid_refs:
        payload = dict(valid_session_payload)
        payload["participant_reference"] = bad_ref
        response = client.post(
            "/api/component4/validate-session",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400, f"Expected 400 for bad participant_reference: '{bad_ref}'"
        data = response.get_json()
        assert not data["valid"]


def test_validate_session_invalid_experimental_condition_returns_400(client, valid_session_payload):
    """Invalid experimental condition returns HTTP 400."""
    valid_session_payload["experimental_condition"] = "Autonomous Agent Writing"
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any("experimental condition" in err.lower() for err in data["errors"])


def test_validate_session_invalid_condition_order_returns_400(client, valid_session_payload):
    """Invalid condition order returns HTTP 400."""
    valid_session_payload["condition_order"] = "Randomized Sequence"
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any("condition order" in err.lower() for err in data["errors"])


def test_validate_session_invalid_session_stage_returns_400(client, valid_session_payload):
    """Invalid session stage returns HTTP 400."""
    valid_session_payload["session_stage"] = "Post-experiment debrief"
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any("session stage" in err.lower() for err in data["errors"])


def test_validate_session_malformed_task_reference_returns_400(client, valid_session_payload):
    """Malformed task reference returns HTTP 400."""
    valid_session_payload["task_reference"] = "TASK#01"
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any("task reference" in err.lower() for err in data["errors"])


def test_validate_session_consent_not_confirmed_returns_400(client, valid_session_payload):
    """Consent confirmed = False returns HTTP 400."""
    valid_session_payload["consent_confirmed"] = False
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any("consent" in err.lower() for err in data["errors"])


def test_validate_session_consent_not_boolean_returns_400(client, valid_session_payload):
    """Non-boolean consent confirmed returns HTTP 400."""
    valid_session_payload["consent_confirmed"] = "True"
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any("boolean" in err.lower() for err in data["errors"])


def test_validate_session_rejects_unknown_fields(client, valid_session_payload):
    """Submitting unknown fields like essay text or student name returns HTTP 400."""
    valid_session_payload["essay_response_text"] = "This is a student written essay sample..."
    valid_session_payload["student_real_name"] = "Alice Smith"
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any("unknown fields" in err.lower() for err in data["errors"])


def test_validate_session_empty_payload_returns_400(client):
    """Empty JSON body returns HTTP 400."""
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert not data["valid"]


def test_validate_session_response_does_not_contain_recall_or_retention_scores(client, valid_session_payload):
    """Validation response must NOT contain any simulated recall, retention, or effect-size metrics."""
    response = client.post(
        "/api/component4/validate-session",
        data=json.dumps(valid_session_payload),
        content_type="application/json",
    )
    body = response.get_json()
    payload_str = json.dumps(body).lower()

    assert "recall_score" not in payload_str
    assert "retention_score" not in payload_str
    assert "ownership_score" not in payload_str
    assert "cognitive_effort_score" not in payload_str
    assert "p_value" not in payload_str
    assert "effect_size" not in payload_str
    assert "cohen" not in payload_str
    assert "superiority" not in payload_str


def test_retention_analysis_service_raises_not_available_error():
    """RetentionAnalysisService.get_results() must raise RetentionAnalysisNotAvailableError."""
    svc = RetentionAnalysisService()
    with pytest.raises(RetentionAnalysisNotAvailableError) as exc_info:
        svc.get_results()
    assert "not available until the controlled experimental dataset has been collected" in str(exc_info.value)


def test_retention_analysis_service_is_analysis_available_returns_false():
    """RetentionAnalysisService.is_analysis_available() must return False."""
    svc = RetentionAnalysisService()
    assert svc.is_analysis_available() is False


def test_component4_no_fabricated_findings_in_apis(client):
    """Component 4 status and specification endpoints contain no fabricated p-values or effect sizes."""
    for endpoint in ["/api/component4/status", "/api/component4/specification"]:
        response = client.get(endpoint)
        assert response.status_code == 200
        text = json.dumps(response.get_json()).lower()
        assert "p_value" not in text
        assert "p-value" not in text
        assert "p <" not in text
        assert "effect_size" not in text
        assert "cohen" not in text
        assert "hedges" not in text
        assert "eta_squared" not in text


# ===========================================================================
# Feature 007 – Integrated Four-Component Research Dashboard
# ===========================================================================

# --------------------------------------------------------------------------- #
# Test 1 – GET /framework/ returns 200                                        #
# --------------------------------------------------------------------------- #

def test_framework_page_returns_200(client):
    """GET /framework/ must return HTTP 200."""
    response = client.get("/framework/")
    assert response.status_code == 200


# --------------------------------------------------------------------------- #
# Test 2 – /framework/ contains page title                                    #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_title(client):
    """GET /framework/ must contain the framework title text."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Psychometric Learning Analytics Framework" in html


# --------------------------------------------------------------------------- #
# Test 3 – /framework/ contains integration architecture heading              #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_integration_architecture_heading(client):
    """GET /framework/ must contain 'Integration Architecture' heading."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Integration Architecture" in html


# --------------------------------------------------------------------------- #
# Test 4 – /framework/ contains data source mapping                          #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_data_source_mapping(client):
    """GET /framework/ must contain a data source mapping section."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Data Source Mapping" in html


# --------------------------------------------------------------------------- #
# Test 5 – /framework/ contains method comparison matrix                     #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_method_comparison_matrix(client):
    """GET /framework/ must contain a method comparison matrix section."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Method Comparison" in html


# --------------------------------------------------------------------------- #
# Test 6 – /framework/ contains analytical independence section               #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_analytical_independence(client):
    """GET /framework/ must contain the analytical independence section."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Analytical Independence" in html


# --------------------------------------------------------------------------- #
# Test 7 – /framework/ contains integration principle notice                  #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_integration_principle(client):
    """GET /framework/ must contain integration principle text."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Complementary Evidence" in html


# --------------------------------------------------------------------------- #
# Test 8 – /framework/ contains system readiness section                     #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_system_readiness(client):
    """GET /framework/ must contain 'System Readiness' section."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "System Readiness" in html


# --------------------------------------------------------------------------- #
# Test 9 – /framework/ contains Framework at a Glance section                #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_framework_at_a_glance(client):
    """GET /framework/ must contain 'Framework at a Glance' section."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Framework at a Glance" in html


# --------------------------------------------------------------------------- #
# Test 10 – /framework/ contains Integrated Insights empty state              #
# --------------------------------------------------------------------------- #

def test_framework_page_contains_integrated_insights_empty_state(client):
    """GET /framework/ must contain the Integrated Insights empty state."""
    response = client.get("/framework/")
    html = response.data.decode()
    assert "Integrated Insights" in html
    assert "No Integrated Insights Available Yet" in html


# --------------------------------------------------------------------------- #
# Test 11 – GET /api/framework/status returns 200                            #
# --------------------------------------------------------------------------- #

def test_framework_status_api_returns_200(client):
    """GET /api/framework/status must return HTTP 200."""
    response = client.get("/api/framework/status")
    assert response.status_code == 200


# --------------------------------------------------------------------------- #
# Test 12 – /api/framework/status response structure                         #
# --------------------------------------------------------------------------- #

def test_framework_status_api_structure(client):
    """GET /api/framework/status must return required top-level keys."""
    response = client.get("/api/framework/status")
    data = response.get_json()
    assert "components" in data
    assert "single_combined_model" in data
    assert "overall_score_available" in data
    assert "integration_principle" in data


# --------------------------------------------------------------------------- #
# Test 13 – single_combined_model is False                                   #
# --------------------------------------------------------------------------- #

def test_framework_status_api_single_combined_model_is_false(client):
    """GET /api/framework/status must return single_combined_model = False."""
    response = client.get("/api/framework/status")
    data = response.get_json()
    assert data["single_combined_model"] is False


# --------------------------------------------------------------------------- #
# Test 14 – overall_score_available is False                                 #
# --------------------------------------------------------------------------- #

def test_framework_status_api_overall_score_available_is_false(client):
    """GET /api/framework/status must return overall_score_available = False."""
    response = client.get("/api/framework/status")
    data = response.get_json()
    assert data["overall_score_available"] is False


# --------------------------------------------------------------------------- #
# Test 15 – /api/framework/status contains 4 components                     #
# --------------------------------------------------------------------------- #

def test_framework_status_api_has_four_components(client):
    """GET /api/framework/status must list exactly four components."""
    response = client.get("/api/framework/status")
    data = response.get_json()
    assert len(data["components"]) == 4


# --------------------------------------------------------------------------- #
# Test 16 – each component has prototype_ready = True                        #
# --------------------------------------------------------------------------- #

def test_framework_status_api_all_prototypes_ready(client):
    """GET /api/framework/status – all components must have prototype_ready=True."""
    response = client.get("/api/framework/status")
    data = response.get_json()
    for comp in data["components"]:
        assert comp["prototype_ready"] is True, (
            f"prototype_ready should be True for {comp.get('id')}"
        )


# --------------------------------------------------------------------------- #
# Test 17 – each component has analysis_ready = False                        #
# --------------------------------------------------------------------------- #

def test_framework_status_api_all_analysis_not_ready(client):
    """GET /api/framework/status – all components must have analysis_ready=False."""
    response = client.get("/api/framework/status")
    data = response.get_json()
    for comp in data["components"]:
        assert comp["analysis_ready"] is False, (
            f"analysis_ready should be False for {comp.get('id')}"
        )


# --------------------------------------------------------------------------- #
# Test 18 – GET /api/framework/specification returns 200                     #
# --------------------------------------------------------------------------- #

def test_framework_specification_api_returns_200(client):
    """GET /api/framework/specification must return HTTP 200."""
    response = client.get("/api/framework/specification")
    assert response.status_code == 200


# --------------------------------------------------------------------------- #
# Test 19 – /api/framework/specification structure                           #
# --------------------------------------------------------------------------- #

def test_framework_specification_api_structure(client):
    """GET /api/framework/specification must contain required keys."""
    response = client.get("/api/framework/specification")
    data = response.get_json()
    assert "components" in data
    assert "integration_principle" in data
    assert "single_combined_model" in data
    assert "overall_score_available" in data


# --------------------------------------------------------------------------- #
# Test 20 – specification single_combined_model is False                     #
# --------------------------------------------------------------------------- #

def test_framework_specification_single_combined_model_is_false(client):
    """GET /api/framework/specification must return single_combined_model = False."""
    response = client.get("/api/framework/specification")
    data = response.get_json()
    assert data["single_combined_model"] is False


# --------------------------------------------------------------------------- #
# Test 21 – specification overall_score_available is False                   #
# --------------------------------------------------------------------------- #

def test_framework_specification_overall_score_available_is_false(client):
    """GET /api/framework/specification must return overall_score_available = False."""
    response = client.get("/api/framework/specification")
    data = response.get_json()
    assert data["overall_score_available"] is False


# --------------------------------------------------------------------------- #
# Test 22 – COMPONENT_REGISTRY contains 4 entries                            #
# --------------------------------------------------------------------------- #

def test_component_registry_has_four_entries():
    """COMPONENT_REGISTRY must contain exactly four components."""
    assert len(COMPONENT_REGISTRY) == 4


# --------------------------------------------------------------------------- #
# Test 23 – COMPONENT_REGISTRY has required fields                           #
# --------------------------------------------------------------------------- #

def test_component_registry_entries_have_required_fields():
    """Each COMPONENT_REGISTRY entry must have required metadata fields."""
    required_fields = [
        "id", "number", "title", "short_title", "role",
        "methods", "data_source", "route",
        "prototype_ready", "analysis_ready", "stage",
    ]
    for comp in COMPONENT_REGISTRY:
        for field in required_fields:
            assert field in comp, (
                f"Missing field '{field}' in registry entry for {comp.get('id')}"
            )


# --------------------------------------------------------------------------- #
# Test 24 – all registry entries have prototype_ready = True                 #
# --------------------------------------------------------------------------- #

def test_component_registry_prototype_ready_is_true():
    """All COMPONENT_REGISTRY entries must have prototype_ready=True."""
    for comp in COMPONENT_REGISTRY:
        assert comp["prototype_ready"] is True, (
            f"prototype_ready should be True for {comp.get('id')}"
        )


# --------------------------------------------------------------------------- #
# Test 25 – all registry entries have analysis_ready = False                 #
# --------------------------------------------------------------------------- #

def test_component_registry_analysis_ready_is_false():
    """All COMPONENT_REGISTRY entries must have analysis_ready=False."""
    for comp in COMPONENT_REGISTRY:
        assert comp["analysis_ready"] is False, (
            f"analysis_ready should be False for {comp.get('id')}"
        )


# --------------------------------------------------------------------------- #
# Test 26 – FrameworkStatusService.get_status() does not combine scores      #
# --------------------------------------------------------------------------- #

def test_framework_status_service_no_combined_score():
    """FrameworkStatusService.get_status() must not contain combined_score or overall_risk."""
    svc = FrameworkStatusService()
    status = svc.get_status()
    status_str = json.dumps(status).lower()
    assert "combined_score" not in status_str
    assert "overall_risk" not in status_str
    assert "aggregated_score" not in status_str


# --------------------------------------------------------------------------- #
# Test 27 – Framework APIs contain no fabricated findings                    #
# --------------------------------------------------------------------------- #

def test_framework_apis_contain_no_fabricated_findings(client):
    """Framework status and specification endpoints contain no fabricated p-values or effect sizes."""
    for endpoint in ["/api/framework/status", "/api/framework/specification"]:
        response = client.get(endpoint)
        assert response.status_code == 200
        text = json.dumps(response.get_json()).lower()
        assert "p_value" not in text
        assert "p-value" not in text
        assert "effect_size" not in text
        assert "cohen" not in text
        assert "predicted_risk" not in text
        assert "overall_risk_level" not in text


# --------------------------------------------------------------------------- #
# Test 28 – Dashboard page contains badges and integration principle          #
# --------------------------------------------------------------------------- #

def test_dashboard_page_contains_badges_and_integration_principle(client):
    """GET /dashboard must contain J26-DS-310 badge, prototype badge, and integration principle."""
    response = client.get("/dashboard")
    html = response.data.decode()
    assert "J26-DS-310" in html
    assert "Research Prototype" in html
    assert "Data Collection" in html
    assert "Complementary Evidence" in html
