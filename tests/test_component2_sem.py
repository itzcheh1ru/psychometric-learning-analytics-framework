"""
tests/test_component2_sem.py

Comprehensive test suite for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).

Tests:
1. UI route and template rendering
2. API specification and status contracts
3. Dataset ingestion, column mapping, and Likert scale validation
4. Reverse-coding of AD4 into AD4_R
5. Confirmatory Factor Analysis (CFA) pipeline, factor loadings, CR, AVE, HTMT
6. Structural Equation Modeling (SEM) pipeline, direct paths, mediation, and model fit
7. Demonstration benchmark dataset loading
8. Export endpoints (CSV and JSON)
"""

import io
import json
import pytest
import pandas as pd
import numpy as np

from app import create_app
from app.services.sem_analysis.dataset_service import validate_and_prepare_dataset
from app.services.sem_analysis.cfa_service import run_cfa_analysis
from app.services.sem_analysis.sem_service import run_sem_analysis


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_survey_df():
    """Generates a valid, complete 35-respondent synthetic dataset for unit testing."""
    np.random.seed(42)
    n = 35
    data = {
        "participant_id": [f"TEST-{i:03d}" for i in range(n)],
        "T1": np.random.choice([3, 4, 5], size=n),
        "T2": np.random.choice([3, 4, 5], size=n),
        "T3": np.random.choice([3, 4, 5], size=n),
        "T4": np.random.choice([3, 4, 5], size=n),
        "PU1": np.random.choice([3, 4, 5], size=n),
        "PU2": np.random.choice([3, 4, 5], size=n),
        "PU3": np.random.choice([3, 4, 5], size=n),
        "PU4": np.random.choice([3, 4, 5], size=n),
        "V1": np.random.choice([2, 3, 4], size=n),
        "V2": np.random.choice([2, 3, 4], size=n),
        "V3": np.random.choice([2, 3, 4], size=n),
        "AD1": np.random.choice([2, 3, 4], size=n),
        "AD2": np.random.choice([2, 3, 4], size=n),
        "AD3": np.random.choice([2, 3, 4], size=n),
        "AD4": np.random.choice([1, 2, 3], size=n),  # Autonomy item
        "LC1": np.random.choice([3, 4, 5], size=n),
        "LC2": np.random.choice([3, 4, 5], size=n),
        "LC3": np.random.choice([3, 4, 5], size=n),
        "LC4": np.random.choice([3, 4, 5], size=n),
    }
    return pd.DataFrame(data)


# --------------------------------------------------------------------------- #
# 1. UI Route Tests                                                           #
# --------------------------------------------------------------------------- #

def test_component2_page_status(client):
    """GET /component2/ returns 200 and loads successfully without template undefined errors."""
    response = client.get("/component2/")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Algorithmic Trust" in html
    assert "Perceived Usefulness" in html
    assert "Verification Behaviour" in html
    assert "AI Dependence" in html
    assert "Learning Confidence" in html
    # Verify questionnaire items are rendered properly
    assert "AT1" in html
    assert "VB1" in html
    assert "PU1" in html
    assert "AD1" in html
    assert "LC5" in html


def test_component2_page_contains_required_sections(client):
    """Component 2 page contains all primary dashboard sections."""
    html = client.get("/component2/").data.decode()
    assert "Survey Data Management" in html
    assert "Psychometric Constructs" in html
    assert "not yet available" in html
    assert "PLANNED RELATIONSHIPS TO BE TESTED" in html


# --------------------------------------------------------------------------- #
# 2. Specification & Status API Tests                                         #
# --------------------------------------------------------------------------- #

def test_specification_endpoint_returns_approved_items(client):
    """GET /api/component2/specification returns all 19 survey items and 12 hypotheses."""
    response = client.get("/api/component2/specification")
    assert response.status_code == 200
    data = response.get_json()
    assert "items" in data
    assert len(data["items"]) == 19
    assert "T1" in data["items"]
    assert "AD4" in data["items"]
    assert data["items"]["AD4"]["reverse_coded"] is True
    assert "hypotheses" in data
    assert len(data["hypotheses"]) == 12


def test_status_endpoint(client):
    """GET /api/component2/status returns expected metadata."""
    response = client.get("/api/component2/status")
    assert response.status_code == 200
    data = response.get_json()
    assert "stage" in data
    assert data["measurement_model_estimated"] is False


# --------------------------------------------------------------------------- #
# 3. Dataset Validation & Reverse Coding Tests                                #
# --------------------------------------------------------------------------- #

def test_dataset_validation_success(sample_survey_df):
    """validate_and_prepare_dataset successfully processes valid survey data and applies reverse coding."""
    result = validate_and_prepare_dataset(sample_survey_df)
    assert result["success"] is True
    assert result["valid_rows"] == len(sample_survey_df)
    assert result["reverse_coded_applied"] is True
    cleaned_df = result["cleaned_data"]
    assert "AD4_R" in cleaned_df.columns
    # Check that AD4_R = 6 - AD4
    for _, row in cleaned_df.iterrows():
        assert row["AD4_R"] == (6.0 - row["AD4"])


def test_dataset_validation_rejects_out_of_bounds_likert(sample_survey_df):
    """Dataset validation rejects values outside the 1-5 Likert range."""
    invalid_df = sample_survey_df.copy()
    invalid_df.loc[0, "T1"] = 7  # Out of range
    with pytest.raises(ValueError, match="Likert scale validation failed"):
        validate_and_prepare_dataset(invalid_df)


def test_dataset_validation_rejects_empty():
    """Dataset validation rejects empty datasets."""
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError, match="The uploaded dataset is empty"):
        validate_and_prepare_dataset(empty_df)


def test_dataset_upload_endpoint_csv(client, sample_survey_df):
    """POST /api/component2/upload accepts valid CSV files."""
    csv_bytes = sample_survey_df.to_csv(index=False).encode("utf-8")
    data = {
        "file": (io.BytesIO(csv_bytes), "test_survey.csv")
    }
    response = client.post("/api/component2/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json["success"] is True
    assert res_json["rows"] == len(sample_survey_df)
    assert res_json["all_items_mapped"] is True


# --------------------------------------------------------------------------- #
# 4. CFA and SEM Analysis Tests                                               #
# --------------------------------------------------------------------------- #

def test_cfa_service_execution(sample_survey_df):
    """run_cfa_analysis computes factor loadings, CR, AVE, and fit indices."""
    prep = validate_and_prepare_dataset(sample_survey_df)
    cfa_res = run_cfa_analysis(prep["cleaned_data"])
    assert cfa_res["success"] is True
    assert "loadings" in cfa_res
    assert "AT" in cfa_res["loadings"]
    assert len(cfa_res["loadings"]["AT"]) == 4
    assert "construct_validity" in cfa_res
    assert "AT" in cfa_res["construct_validity"]
    at_val = cfa_res["construct_validity"]["AT"]
    assert "composite_reliability" in at_val
    assert "ave" in at_val
    assert "cronbach_alpha" in at_val
    assert "model_fit" in cfa_res
    assert "cfi" in cfa_res["model_fit"]


def test_sem_service_execution(sample_survey_df):
    """run_sem_analysis computes structural paths, mediation, and hypothesis testing."""
    prep = validate_and_prepare_dataset(sample_survey_df)
    sem_res = run_sem_analysis(prep["cleaned_data"], n_bootstraps=50)
    assert sem_res["success"] is True
    assert "direct_paths" in sem_res
    assert len(sem_res["direct_paths"]) == 8
    assert "indirect_effects" in sem_res
    assert len(sem_res["indirect_effects"]) == 4
    assert "hypotheses_evaluation" in sem_res
    assert len(sem_res["hypotheses_evaluation"]) == 12
    assert "model_fit" in sem_res


def test_analyze_endpoint_with_synthetic_demo(client):
    """POST /api/component2/analyze with use_demo=true returns full analysis."""
    response = client.post("/api/component2/analyze", data={"use_demo": "true"})
    assert response.status_code == 200
    res = response.get_json()
    assert res["success"] is True
    assert res["is_demo"] is True
    assert "cfa_results" in res
    assert "sem_results" in res
    assert "charts" in res
    assert "loadings" in res["charts"]
    assert "path_diagram" in res["charts"]
    assert "apa_summary" in res
    assert "csv_report" in res


def test_load_demo_endpoint(client):
    """POST /api/component2/load-demo loads and evaluates the benchmark dataset."""
    response = client.post("/api/component2/load-demo")
    assert response.status_code == 200
    res = response.get_json()
    assert res["success"] is True
    assert res["is_demo"] is True
    assert res["dataset_summary"]["valid_rows"] == 250


# --------------------------------------------------------------------------- #
# 5. Export Endpoint Tests                                                    #
# --------------------------------------------------------------------------- #

def test_export_endpoint_csv(client):
    """POST /api/component2/export returns formatted CSV file."""
    sample_csv = "Item,Mean,StdDev\nT1,3.5,0.8\n"
    response = client.post("/api/component2/export", json={"format": "csv", "csv_content": sample_csv})
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"T1,3.5,0.8" in response.data


def test_export_endpoint_json(client):
    """POST /api/component2/export returns formatted JSON file."""
    response = client.post("/api/component2/export", json={"format": "json", "sample_key": "sample_val"})
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    res_data = response.get_json()
    assert res_data["sample_key"] == "sample_val"


# --------------------------------------------------------------------------- #
# 6. Preprocessing & Individual Scoring Tests (Phase 2 Implementation)        #
# --------------------------------------------------------------------------- #

from pathlib import Path
from app.services.sem_analysis.dataset_service import clean_likert_cell, filter_informed_consent
from app.services.sem_analysis.scoring_service import calculate_individual_scores


def test_consent_filtering():
    """Consent filtering excludes participants who did not consent."""
    df_raw = pd.DataFrame({
        "ID": [1, 2, 3],
        "Consent": ["I agree to participate", "I do not agree to participate", "I agree to participate"],
        "T1": [4, 2, 5],
    })
    filtered, excluded = filter_informed_consent(df_raw)
    assert len(filtered) == 2
    assert excluded == 1
    assert 2 not in filtered["ID"].values


def test_likert_cell_cleaning_text_and_unicode():
    """Likert cell cleaning converts text strings and handles Unicode non-breaking spaces."""
    assert clean_likert_cell("Strongly agree") == 5.0
    assert clean_likert_cell("Agree") == 4.0
    assert clean_likert_cell("Neutral") == 3.0
    assert clean_likert_cell("Neither agree nor disagree") == 3.0
    assert clean_likert_cell("Disagree") == 2.0
    assert clean_likert_cell("Strongly disagree") == 1.0
    assert clean_likert_cell("Strongly Disagree\xa0") == 1.0  # Unicode non-breaking space
    assert clean_likert_cell("  Agree  ") == 4.0
    assert clean_likert_cell(4) == 4.0
    assert clean_likert_cell(7) == 7.0  # Preserved out-of-range number for validator
    assert np.isnan(clean_likert_cell(np.nan))
    assert np.isnan(clean_likert_cell("Not a rating"))


def test_empirical_26_item_dataset_preparation():
    """Empirical 26-item dataset maps all 26 indicators and preserves standard polarity on AD4."""
    clean_path = "data/processed/component2_survey_clean.csv"
    assert pd.Series(Path(clean_path).exists()).iloc[0] is True or Path(clean_path).exists()
    df_clean = pd.read_csv(clean_path)
    res = validate_and_prepare_dataset(df_clean)
    assert res["success"] is True
    assert res["valid_rows"] == 375
    assert res["all_items_mapped"] is True
    assert len(res["mapping"]) == 26
    # In empirical survey, AD4 is standard polarity (not reverse coded)
    assert res["reverse_coded_applied"] is False


def test_individual_scoring_engine():
    """Individual scoring engine calculates unweighted composites, weighted averages, and cohort norms."""
    # Test sample with known response vector (all 4s)
    sample_responses = {f"AT{i}": 4 for i in range(1, 7)}
    sample_responses.update({f"VB{i}": 5 for i in range(1, 6)})
    sample_responses.update({f"PU{i}": 4 for i in range(1, 6)})
    sample_responses.update({f"AD{i}": 2 for i in range(1, 6)})
    sample_responses.update({f"LC{i}": 4 for i in range(1, 6)})

    result = calculate_individual_scores(sample_responses)
    assert result["success"] is True
    assert result["is_complete"] is True
    assert result["items_answered"] == 26

    scores = result["construct_scores"]
    assert "AT" in scores and "VB" in scores and "AD" in scores and "PU" in scores and "LC" in scores

    # Unweighted mean score
    assert scores["AT"]["mean_score"] == 4.0
    assert scores["VB"]["mean_score"] == 5.0
    assert scores["AD"]["mean_score"] == 2.0

    # Norm-referenced z-score and percentile
    assert scores["VB"]["z_score"] > 1.0  # Above cohort mean (3.71)
    assert scores["VB"]["percentile_rank"] > 80.0
    assert scores["VB"]["band_code"] == "HIGH"

    assert scores["AD"]["z_score"] < -1.0  # Below cohort mean (3.09)
    assert scores["AD"]["band_code"] == "LOW"

    # Scientific notes and caveats are present
    assert "primary_metric" in result["scientific_notes"]
    assert "measurement_boundary" in result["scientific_notes"]


# --------------------------------------------------------------------------- #
# 7. Phase 3: Personalized Student Assessment & Behavioural Interpretation    #
# --------------------------------------------------------------------------- #

from app.services.sem_analysis.profile_service import evaluate_behavioral_profile
from app.services.sem_analysis.recommendation_service import generate_recommendations
from app.services.sem_analysis.student_report_service import generate_student_csv_report
from app.services.sem_analysis.visualization_service import (
    generate_student_radar_chart,
    generate_student_quadrant_chart,
)


def _get_valid_26_responses(at=4.0, vb=4.0, pu=4.0, ad=3.0, lc=4.0):
    """Helper to generate a complete 26-item response dict."""
    resp = {}
    for i in range(1, 7):
        resp[f"AT{i}"] = float(at)
    for i in range(1, 6):
        resp[f"VB{i}"] = float(vb)
        resp[f"PU{i}"] = float(pu)
        resp[f"AD{i}"] = float(ad)
        resp[f"LC{i}"] = float(lc)
    return resp


def test_student_assessment_ui_renders(client):
    """GET /component2/assessment returns 200 and renders the 26-item assessment UI."""
    response = client.get("/component2/assessment")
    assert response.status_code == 200
    assert b"Personalized AI Trust &amp; Verification Assessment" in response.data
    assert b"Algorithmic Trust" in response.data
    assert b"Verification Behaviour" in response.data
    assert b"Perceived Usefulness" in response.data
    assert b"AI Dependence" in response.data
    assert b"Learning Confidence" in response.data
    assert b"Start Assessment" in response.data
    assert b"AT1" in response.data
    assert b"VB5" in response.data
    assert b"LC5" in response.data


def test_questionnaire_api_endpoint(client):
    """GET /api/component2/questionnaire returns 26 validated items grouped by construct."""
    response = client.get("/api/component2/questionnaire")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["total_items"] == 26
    assert len(data["scale"]) == 5
    assert "AT" in data["constructs"]
    assert "VB" in data["constructs"]
    assert "PU" in data["constructs"]
    assert "AD" in data["constructs"]
    assert "LC" in data["constructs"]
    assert len(data["constructs"]["AT"]["items"]) == 6
    assert len(data["constructs"]["VB"]["items"]) == 5


def test_assess_api_complete_success(client):
    """POST /api/component2/assess processes 26 responses and returns scores, profile, recommendations, and charts."""
    sample_responses = _get_valid_26_responses(at=4.0, vb=4.5, pu=4.0, ad=2.5, lc=4.2)
    payload = {
        "responses": sample_responses,
        "student_id": "STUDENT_TEST_101",
    }
    response = client.post("/api/component2/assess", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["student_id"] == "STUDENT_TEST_101"

    # 1. Scoring results
    assert "scoring" in data
    assert "construct_scores" in data["scoring"]
    assert data["scoring"]["construct_scores"]["AT"]["mean_score"] == 4.0
    assert data["scoring"]["construct_scores"]["VB"]["mean_score"] == 4.5
    assert "percentile_rank" in data["scoring"]["construct_scores"]["AT"]
    assert "quartile_band" in data["scoring"]["construct_scores"]["AT"]

    # 2. Profile results
    assert "profile" in data
    assert data["profile"]["quadrant_id"] in ["Q1", "Q2", "Q3", "Q4"]
    assert "profile_title" in data["profile"]
    assert "sem_structural_insights" in data["profile"]
    assert "dependence_context" in data["profile"]
    assert "confidence_context" in data["profile"]

    # 3. Recommendations
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 3
    for rec in data["recommendations"]:
        assert "id" in rec
        assert "title" in rec
        assert "priority" in rec
        assert "evidence_trace" in rec
        assert "rationale" in rec
        assert len(rec["action_steps"]) == 3

    # 4. Interactive Charts
    assert "charts" in data
    assert "radar" in data["charts"]
    assert "quadrant" in data["charts"]
    assert "data" in data["charts"]["radar"]
    assert "data" in data["charts"]["quadrant"]

    # 5. Non-diagnostic disclaimer
    assert "disclaimer" in data


def test_assess_api_validation_rejects_missing_items(client):
    """POST /api/component2/assess rejects incomplete questionnaire submissions with 400 Bad Request."""
    incomplete_responses = {"AT1": 4.0, "AT2": 3.0}
    response = client.post("/api/component2/assess", json={"responses": incomplete_responses})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "missing_items" in data
    assert len(data["missing_items"]) == 24


def test_assess_api_validation_rejects_out_of_bounds_values(client):
    """POST /api/component2/assess rejects Likert responses outside 1-5 with 400 Bad Request."""
    bad_responses = _get_valid_26_responses()
    bad_responses["AT1"] = 7.0  # Invalid Likert rating
    response = client.post("/api/component2/assess", json={"responses": bad_responses})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "invalid_items" in data
    assert "AT1" in data["invalid_items"]


def test_recommendation_traceability_vulnerable_overtruster():
    """Vulnerable Over-Truster profile triggers traceable verification and calibration recommendations."""
    # High Trust (4.5), Low Verification (2.0), High Dependence (4.2)
    resp = _get_valid_26_responses(at=4.5, vb=2.0, pu=4.0, ad=4.2, lc=3.0)
    resp["VB1"] = 1.0  # Explicitly low verification rating
    resp["VB2"] = 2.0
    resp["AD2"] = 5.0  # Explicitly high dependence rating
    resp["AD5"] = 4.0

    scores = calculate_individual_scores(resp)
    profile = evaluate_behavioral_profile(scores["construct_scores"])
    recs = generate_recommendations(scores["construct_scores"], resp)

    # Must be classified as Q2 (High Trust, Low Verification)
    assert profile["quadrant_id"] == "Q2"
    assert "Over-Truster" in profile["profile_title"]

    # Must generate at least 3 recommendations
    assert len(recs) >= 3

    # Check that verification and trust rules were triggered
    rec_ids = [r["id"] for r in recs]
    assert "REC_VB_TRIANGULATION" in rec_ids
    assert "REC_AT_CALIBRATION" in rec_ids
    assert "REC_AD_AUTONOMY" in rec_ids

    # Check evidence traceability
    vb_rec = next(r for r in recs if r["id"] == "REC_VB_TRIANGULATION")
    assert "VB2" in vb_rec["evidence_trace"] or "VB1" in vb_rec["evidence_trace"]
    assert "beta = -0.014" in vb_rec["rationale"] or "structural" in vb_rec["rationale"]

    ad_rec = next(r for r in recs if r["id"] == "REC_AD_AUTONOMY")
    assert "AD2" in ad_rec["evidence_trace"] or "AD5" in ad_rec["evidence_trace"] or "percentile" in ad_rec["evidence_trace"]


def test_student_report_export_endpoints(client):
    """POST /api/component2/student-report generates valid RFC 4180 CSV and JSON exports."""
    resp = _get_valid_26_responses()
    scores = calculate_individual_scores(resp)
    profile = evaluate_behavioral_profile(scores["construct_scores"])
    recs = generate_recommendations(scores["construct_scores"], resp)

    # 1. Export as CSV
    csv_payload = {
        "format": "csv",
        "scoring_result": scores,
        "profile_result": profile,
        "recommendations": recs,
        "student_meta": {"student_id": "TEST_STUDENT_CSV"},
    }
    res_csv = client.post("/api/component2/student-report", json=csv_payload)
    assert res_csv.status_code == 200
    assert res_csv.mimetype == "text/csv"
    assert b"INDIVIDUAL STUDENT PSYCHOMETRIC ASSESSMENT REPORT" in res_csv.data
    assert b"TEST_STUDENT_CSV" in res_csv.data
    assert b"SECTION 1: PERSONAL CONSTRUCT SCORES & COHORT NORMS" in res_csv.data
    assert b"SECTION 2: EXPLAINABLE BEHAVIOURAL INTERPRETATION" in res_csv.data
    assert b"SECTION 3: TRACEABLE EDUCATIONAL RECOMMENDATIONS" in res_csv.data

    # 2. Export as JSON
    json_payload = {
        "format": "json",
        "scoring_result": scores,
        "profile_result": profile,
        "recommendations": recs,
        "student_meta": {"student_id": "TEST_STUDENT_JSON"},
    }
    res_json = client.post("/api/component2/student-report", json=json_payload)
    assert res_json.status_code == 200
    assert res_json.mimetype == "application/json"
    json_data = res_json.get_json()
    assert json_data["scoring"]["construct_scores"]["AT"]["mean_score"] == 4.0
    assert json_data["profile"]["quadrant_id"] in ["Q1", "Q2", "Q3", "Q4"]
    assert len(json_data["recommendations"]) >= 3
    assert json_data["meta"]["student_id"] == "TEST_STUDENT_JSON"

    # 3. Bad request on missing payload
    res_bad = client.post("/api/component2/student-report", json={})
    assert res_bad.status_code == 400


