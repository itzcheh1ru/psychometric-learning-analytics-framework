"""
tests/test_component1_validation_and_security.py
================================================
Focused regression tests for Component 1 (Version 4) covering:
1. Canonical faculty dropdown mapping fix (Business_Economics, Humanities_Health_Other).
2. Exact LinearSHAP additivity (base_value + sum(contribs) == raw_regression_score).
3. Flask API payload type validation and sanitized 500 error responses.
4. Independent cohort validator unit tests (leakage checks, PII rejection, metrics).
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from app.services.cognitive_offloading.integration_service import (
    classify_meta_faculty,
    get_predictor_v4,
)

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "component1_streamlit_v4" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from evaluate_independent_cohort import (  # noqa: E402
    SECTION_E_REFERENCE_KEYS,
    UI_PREDICTOR_KEYS,
    evaluate_cohort_dataframe,
)


def _sample_ui_payload(**overrides):
    base = {
        "degree_field": "Computing_IT",
        "academic_year": 3,
        "age_group": 2,
        "ai_usage_freq": 3,
        "ai_time_per_week": 3,
        "tools_used": ["ChatGPT"],
        "Q20_task_delegation_freq": 3,
        "tasks_delegated": ["Explaining concepts"],
        "Q1_direct_use_freq": 3,
        "Q22_effort_on_ai_answers": 3,
        "Q2_verify_info": 3,
        "Q3_compare_sources": 3,
        "Q4_check_accuracy": 3,
        "Q5_understand_reasoning": 3,
        "Q6_modify_content": 3,
        "Q7_attempt_independently": 3,
        "Q8_complete_without_ai": 3,
        "Q9_learning_assistant": 3,
        "Q30_trust_accuracy": 3,
        "Q33_trust_appropriate_support": 3,
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- #
# 1. Faculty Slug Mapping & Exact LinearSHAP Invariants                       #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "raw_value,expected_faculty,expected_col",
    [
        ("Computing_IT", "Computing_IT", "faculty_Computing_IT"),
        ("Engineering", "Engineering", "faculty_Engineering"),
        ("Business_Economics", "Business_Economics", "faculty_Business_Economics"),
        ("Natural_Applied_Sciences", "Natural_Applied_Sciences", "faculty_Natural_Applied_Sciences"),
        ("Humanities_Health_Other", "Humanities_Health_Other", "faculty_Humanities_Health_Other"),
        ("Arts / Humanities", "Humanities_Health_Other", "faculty_Humanities_Health_Other"),
        ("B.A. Economics", "Business_Economics", "faculty_Business_Economics"),
        ("BSc IT", "Computing_IT", "faculty_Computing_IT"),
    ],
)
def test_faculty_mapping_avoids_substring_collisions(raw_value, expected_faculty, expected_col):
    """All UI dropdown values and natural free-text labels must resolve to exact faculty cols."""
    assert classify_meta_faculty(raw_value) == expected_faculty
    pred = get_predictor_v4()
    df_row, _ = pred.transform_inputs(_sample_ui_payload(degree_field=raw_value), [])
    assert float(df_row[expected_col].iloc[0]) == 1.0


def test_linear_shap_exact_additivity():
    """Sum of LinearSHAP contributions plus expected baseline must equal raw regression score."""
    pred = get_predictor_v4()
    payload = _sample_ui_payload(degree_field="Business_Economics", Q20_task_delegation_freq=5)
    df_row, _ = pred.transform_inputs(payload, [])
    res = pred.predict(payload, top_factors_count=68)

    x_vals = df_row.iloc[0].values.astype(float)
    x_means = np.array([pred.background_means.get(f, 0.0) for f in pred.feature_names], dtype=float)
    base_val = float(pred.intercept + np.dot(pred.coefficients, x_means))
    exact_sum = float((pred.coefficients * (x_vals - x_means)).sum())

    assert abs((base_val + exact_sum) - float(pred.model.predict(df_row)[0])) < 1e-9
    returned_sum = sum(item["linear_shap_contribution"] for item in res["top_contributing_factors"])
    assert abs((base_val + returned_sum) - res["raw_regression_score"]) < 0.01


# --------------------------------------------------------------------------- #
# 2. Component 1 Route Security & Validation Hardening                        #
# --------------------------------------------------------------------------- #

def test_api_predict_rejects_non_object_json_cleanly(client):
    """List or scalar JSON payloads must return HTTP 400 rather than 500 AttributeError."""
    for body in ([1, 2, 3], "plain-string", 42):
        resp = client.post("/api/component1/predict", json=body)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["status"] == "validation_error"
        assert data["error_type"] == "MissingRequiredInput"


def test_api_predict_rejects_invalid_user_inputs_and_top_factors(client):
    """Non-dict user_inputs or malformed top_factors_count must fail cleanly with HTTP 400."""
    bad_inputs = client.post("/api/component1/predict", json={"user_inputs": ["not", "a", "dict"]})
    assert bad_inputs.status_code == 400
    assert bad_inputs.get_json()["status"] == "validation_error"

    bad_count = client.post(
        "/api/component1/predict",
        json={"user_inputs": _sample_ui_payload(), "top_factors_count": True},
    )
    assert bad_count.status_code == 400
    assert bad_count.get_json()["error_type"] == "InvalidParameter"


def test_api_validate_input_rejects_json_list_with_400(client):
    """Legacy /validate-input endpoint must reject non-dict JSON cleanly with 400."""
    resp = client.post("/api/component1/validate-input", json=["invalid"])
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_api_predict_hides_internal_exception_details(client):
    """Unexpected backend inference failures must not leak internal exception strings."""
    with patch(
        "app.routes.component1.model_service.predict",
        side_effect=RuntimeError("SECRET_INTERNAL_TRACE_TOKEN"),
    ):
        resp = client.post("/api/component1/predict", json={"user_inputs": _sample_ui_payload()})
        assert resp.status_code == 500
        payload = resp.get_json()
        assert payload["status"] == "error"
        assert "SECRET_INTERNAL_TRACE_TOKEN" not in json.dumps(payload)


def test_xss_like_input_strings_are_not_reflected_or_stored(client):
    """Script tags inside categorical/unknown keys must not trigger errors or echo raw values."""
    payload = _sample_ui_payload(degree_field="<script>alert(1)</script>")
    resp = client.post("/api/component1/predict", json=payload)
    assert resp.status_code == 200
    body_text = resp.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in body_text


# --------------------------------------------------------------------------- #
# 3. Independent Cohort Validation Utility Tests                              #
# --------------------------------------------------------------------------- #

def _synthetic_cohort_df():
    low_row = {
        "study_id": "STU_001",
        **_sample_ui_payload(
            degree_field="Engineering",
            ai_usage_freq=1,
            Q20_task_delegation_freq=1,
            Q1_direct_use_freq=1,
            Q22_effort_on_ai_answers=5,
            Q2_verify_info=5,
            Q7_attempt_independently=5,
            Q8_complete_without_ai=5,
            Q30_trust_accuracy=1,
        ),
        "tools_used": "ChatGPT",
        "tasks_delegated": "Explaining concepts",
        **{k: 1 for k in SECTION_E_REFERENCE_KEYS},
    }
    med_row = {
        "study_id": "STU_002",
        **_sample_ui_payload(degree_field="Computing_IT"),
        "tools_used": "ChatGPT;Google Gemini",
        "tasks_delegated": "Explaining concepts;Summarising materials",
        **{k: 3 for k in SECTION_E_REFERENCE_KEYS},
    }
    high_row = {
        "study_id": "STU_003",
        **_sample_ui_payload(
            degree_field="Business_Economics",
            ai_usage_freq=4,
            Q20_task_delegation_freq=5,
            Q1_direct_use_freq=5,
            Q22_effort_on_ai_answers=1,
            Q2_verify_info=1,
            Q7_attempt_independently=1,
            Q8_complete_without_ai=1,
            Q30_trust_accuracy=5,
            Q33_trust_appropriate_support=5,
        ),
        "tools_used": "ChatGPT;Claude;Perplexity AI",
        "tasks_delegated": "Writing assignments;Programming problems",
        **{k: 5 for k in SECTION_E_REFERENCE_KEYS},
    }
    return pd.DataFrame([low_row, med_row, high_row])


def test_independent_cohort_evaluator_runs_on_clean_anonymized_schema():
    """Evaluator computes accuracy, High-Risk recall, RMSE, and verifies zero leakage."""
    df = _synthetic_cohort_df()
    assert len(UI_PREDICTOR_KEYS) == 20
    report = evaluate_cohort_dataframe(df)
    assert report["n_evaluated"] == 3
    assert report["zero_target_leakage_verified"] is True
    assert report["metrics"]["accuracy"] == 1.0
    assert report["metrics"]["high_risk_recall"] == 1.0
    assert len(report["metrics"]["confusion_matrix"]) == 3


def test_independent_cohort_evaluator_rejects_pii_columns():
    """Direct PII columns (student_id, email) must fail privacy validation cleanly."""
    df = _synthetic_cohort_df()
    df["student_id"] = "IT99999999"
    with pytest.raises(ValueError, match="Privacy check failed"):
        evaluate_cohort_dataframe(df)
