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
    """GET /component2/ returns 200 and loads successfully."""
    response = client.get("/component2/")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Algorithmic Trust" in html
    assert "Perceived Usefulness" in html
    assert "Verification Behaviour" in html
    assert "AI Dependence" in html
    assert "Learning Confidence" in html


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
