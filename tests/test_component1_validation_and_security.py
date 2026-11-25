"""
tests/test_component1_validation_and_security.py
================================================
Regression, schema, security, and independent cohort evaluator tests for Component 1 (Version 4):
1. Canonical faculty dropdown mapping (Business_Economics, Humanities_Health_Other).
2. Exact 68-feature breakdown consistency & LinearSHAP additivity invariants.
3. Flask API payload validation and sanitized 500 error responses.
4. Blank independent cohort CSV template conformance (exact 27 headers, 0 fake rows).
5. Independent cohort evaluator fail-closed guards:
   - Duplicate study_id rejection
   - Missing required column / empty value rejection
   - Invalid ordinal / Likert range & non-numeric rejection
   - Unexpected / leakage column rejection
   - Missing reference-label (Q10-Q15) handling & rejection
   - Invalid categorical encodings (degree_field, tools_used, tasks_delegated)
   - PII column & email/student-ID study_id rejection
"""

import csv
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

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "component1_streamlit_v4" / "scripts"
TEMPLATE_CSV = (
    REPO_ROOT / "component1_streamlit_v4" / "progress_evaluation" / "independent_cohort_template.csv"
)
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
# 1. Faculty Slug Mapping, 68-Feature Breakdown & LinearSHAP Invariants       #
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


def test_mutually_exclusive_68_feature_breakdown():
    """Verify exact mutually exclusive partition: 17 direct + 22 engineered + 27 fixed + 2 hybrid = 68."""
    pred = get_predictor_v4()
    assert len(pred.feature_names) == 68

    direct_17 = {
        "age_group", "academic_year", "ai_usage_freq", "ai_time_per_week",
        "Q1_direct_use_freq", "Q20_task_delegation_freq", "Q22_effort_on_ai_answers",
        "Q2_verify_info", "Q3_compare_sources", "Q4_check_accuracy",
        "Q5_understand_reasoning", "Q6_modify_content",
        "Q7_attempt_independently", "Q8_complete_without_ai", "Q9_learning_assistant",
        "Q30_trust_accuracy", "Q33_trust_appropriate_support",
    }
    engineered_ui_22 = {
        "composite_verification", "composite_autonomy",
        "idx_delegation_intensity", "idx_passive_adoption",
        "count_tools_used", "count_tasks_delegated",
        "faculty_Business_Economics", "faculty_Computing_IT", "faculty_Engineering",
        "faculty_Humanities_Health_Other", "faculty_Natural_Applied_Sciences",
        "tool_chatgpt", "tool_google_gemini", "tool_microsoft_copilot",
        "tool_claude", "tool_perplexity",
        "delegate_writing_assignments", "delegate_explaining_concepts",
        "delegate_summarising_materials", "delegate_creating_presentations",
        "delegate_programming_problems", "delegate_mathematical_problems",
    }
    fully_imputed_27 = {
        "Q16_ai_improves_learning", "Q17_ai_confidence", "Q18_ai_efficiency", "Q19_negative_affect_warning",
        "Q23_pu_improves_understanding", "Q24_pu_complete_effectively", "Q25_pu_productivity",
        "Q26_pu_useful_for_goals", "Q27_pu_learn_difficult_topics",
        "Q28_trust_reliable_info", "Q29_trust_consistent", "Q31_trust_explanations", "Q32_trust_clear_explanations",
        "Q39_feel_capable", "Q40_feel_confident", "Q41_more_capable_after",
        "Q42_more_confident_after", "Q43_approach_challenging",
        "composite_tam", "composite_self_efficacy", "count_purposes",
        "purpose_understanding_concepts", "purpose_assignment_preparation", "purpose_exam_preparation",
        "purpose_writing_improvement", "purpose_summarising_content", "purpose_generating_ideas",
    }
    hybrid_2 = {"composite_trust", "idx_automation_bias"}

    assert len(direct_17) == 17
    assert len(engineered_ui_22) == 22
    assert len(fully_imputed_27) == 27
    assert len(hybrid_2) == 2
    combined = direct_17 | engineered_ui_22 | fully_imputed_27 | hybrid_2
    assert len(combined) == 68
    assert combined == set(pred.feature_names)


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
# 3. Blank Cohort CSV Template & Evaluator Safeguard Unit Tests (Test Fixture)#
# --------------------------------------------------------------------------- #

def test_independent_cohort_template_csv_schema_is_blank_and_exact():
    """Data collection CSV template must contain exact 27 headers and zero synthetic rows."""
    assert TEMPLATE_CSV.exists()
    with TEMPLATE_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 1
    assert rows[0] == ["study_id"] + UI_PREDICTOR_KEYS + SECTION_E_REFERENCE_KEYS


def _synthetic_test_fixture_cohort_df():
    """Software test fixture only; never real student data."""
    low_row = {
        "study_id": "FIXTURE_001",
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
        "study_id": "FIXTURE_002",
        **_sample_ui_payload(degree_field="Computing_IT"),
        "tools_used": "ChatGPT;Google Gemini",
        "tasks_delegated": "Explaining concepts;Summarising materials",
        **{k: 3 for k in SECTION_E_REFERENCE_KEYS},
    }
    high_row = {
        "study_id": "FIXTURE_003",
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
    df = _synthetic_test_fixture_cohort_df()
    assert len(UI_PREDICTOR_KEYS) == 20
    report = evaluate_cohort_dataframe(df)
    assert report["n_evaluated"] == 3
    assert report["zero_target_leakage_verified"] is True
    assert report["metrics"]["accuracy"] == 1.0
    assert report["metrics"]["high_risk_recall"] == 1.0
    assert len(report["metrics"]["confusion_matrix"]) == 3


def test_independent_cohort_evaluator_rejects_pii_and_email_ids():
    """Direct PII columns and email/registration-like study IDs must fail cleanly."""
    df_col = _synthetic_test_fixture_cohort_df()
    df_col["student_id"] = "IT99999999"
    with pytest.raises(ValueError, match="Privacy check failed"):
        evaluate_cohort_dataframe(df_col)

    df_id = _synthetic_test_fixture_cohort_df()
    df_id.loc[0, "study_id"] = "student@sliit.lk"
    with pytest.raises(ValueError, match="Privacy check failed"):
        evaluate_cohort_dataframe(df_id)


def test_independent_cohort_evaluator_rejects_duplicate_study_ids():
    """Duplicate participant study_id rows must be rejected fail-closed."""
    df = _synthetic_test_fixture_cohort_df()
    df.loc[1, "study_id"] = "FIXTURE_001"
    with pytest.raises(ValueError, match="Duplicate participant identifiers"):
        evaluate_cohort_dataframe(df)


def test_independent_cohort_evaluator_rejects_invalid_likert_and_categorical_values():
    """Out-of-range Likert values, non-numeric entries, and invalid categoricals must fail."""
    df_bad_likert = _synthetic_test_fixture_cohort_df()
    df_bad_likert.loc[0, "Q2_verify_info"] = 6
    with pytest.raises(ValueError, match="Invalid ordinal/Likert"):
        evaluate_cohort_dataframe(df_bad_likert)

    df_bad_deg = _synthetic_test_fixture_cohort_df()
    df_bad_deg.loc[0, "degree_field"] = "UnknownFaculty"
    with pytest.raises(ValueError, match="Invalid degree_field"):
        evaluate_cohort_dataframe(df_bad_deg)

    df_bad_tool = _synthetic_test_fixture_cohort_df()
    df_bad_tool.loc[0, "tools_used"] = "ChatGPT;MadeUpAI"
    with pytest.raises(ValueError, match="Invalid tools_used"):
        evaluate_cohort_dataframe(df_bad_tool)


def test_independent_cohort_evaluator_rejects_unexpected_or_missing_reference_cols():
    """Unexpected columns, leakage columns, and missing Q10-Q15 columns must raise ValueError."""
    df_extra = _synthetic_test_fixture_cohort_df()
    df_extra["unexpected_note"] = "foo"
    with pytest.raises(ValueError, match="Unexpected columns"):
        evaluate_cohort_dataframe(df_extra)

    df_leak = _synthetic_test_fixture_cohort_df()
    df_leak["Q37_important_part"] = 5
    with pytest.raises(ValueError, match="Leakage protection triggered"):
        evaluate_cohort_dataframe(df_leak)

    df_no_ref = _synthetic_test_fixture_cohort_df().drop(columns=["Q15_reduces_thinking"])
    with pytest.raises(ValueError, match="missing required columns"):
        evaluate_cohort_dataframe(df_no_ref)


def test_independent_cohort_evaluator_handles_partial_missing_responses_safely():
    """Partial missing numeric UI input is imputed safely; incomplete Q10-Q15 row is excluded."""
    df = _synthetic_test_fixture_cohort_df()
    df.loc[0, "Q3_compare_sources"] = np.nan
    df.loc[1, "Q10_rely_memory"] = np.nan
    report = evaluate_cohort_dataframe(df)
    assert report["n_submitted"] == 3
    assert report["n_evaluated"] == 2
    assert report["n_dropped_incomplete_reference"] == 1
    assert report["missing_reference_cells"] == 1
