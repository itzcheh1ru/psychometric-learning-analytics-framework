"""
tests/test_component1_v4_scenarios.py
=====================================
Dedicated regression test execution for the 8 validated Version 4 scenarios:
1. Low-risk student profile (high verification, independent effort)
2. Medium-risk student profile (moderate usage, balanced delegation)
3. High-risk student profile (extreme delegation, direct copying, score clamping)
4. Empty input (validation guard preventing misleading assessments)
5. Inputs with missing optional values (median imputation and warning reporting)
6. Inputs with invalid text, NaNs or infinities (graceful coercion and clamping)
7. Out-of-range inputs (boundary clamping and warnings)
8. Borderline profiles near thresholds (probability distributions near 2.667 and 3.500)
"""

import pytest
import numpy as np

from app.services.cognitive_offloading.integration_service import get_predictor_v4


@pytest.fixture(scope="module")
def predictor():
    return get_predictor_v4()


def test_scenario_1_low_risk_profile(predictor):
    """Scenario 1: Low-Risk Student Profile."""
    p1 = {
        "ai_usage_freq": 1,
        "Q20_task_delegation_freq": 1,
        "Q1_direct_use_freq": 1,
        "Q22_effort_on_ai_answers": 5,
        "Q8_complete_without_ai": 5,
        "Q7_attempt_independently": 5,
        "Q2_verify_info": 5,
        "Q30_trust_accuracy": 2,
        "Q33_trust_appropriate_support": 2,
        "degree_field": "Natural & Applied Sciences"
    }
    r1 = predictor.predict(p1)
    assert r1["status"] == "success"
    assert r1["predicted_category"] == "Low"
    assert 1.0 <= r1["continuous_risk_score"] <= 2.667
    assert abs(sum(r1["probabilities"].values()) - 1.0) < 0.01
    assert len(r1["top_contributing_factors"]) > 0


def test_scenario_2_medium_risk_profile(predictor):
    """Scenario 2: Medium-Risk Student Profile."""
    p2 = {
        "ai_usage_freq": 2,
        "Q20_task_delegation_freq": 3,
        "Q1_direct_use_freq": 3,
        "Q22_effort_on_ai_answers": 3,
        "Q8_complete_without_ai": 3,
        "Q7_attempt_independently": 3,
        "Q2_verify_info": 3,
        "Q30_trust_accuracy": 3,
        "Q33_trust_appropriate_support": 3,
        "degree_field": "Computer Science / IT"
    }
    r2 = predictor.predict(p2)
    assert r2["status"] == "success"
    assert r2["predicted_category"] == "Medium"
    assert 2.667 < r2["continuous_risk_score"] <= 3.500
    assert abs(sum(r2["probabilities"].values()) - 1.0) < 0.01


def test_scenario_3_high_risk_clamping_profile(predictor):
    """Scenario 3: High-Risk Profile — Verifies construct clamping to [1.0, 5.0] while preserving raw estimate."""
    p3 = {
        "ai_usage_freq": 4,
        "Q20_task_delegation_freq": 5,
        "Q1_direct_use_freq": 5,
        "Q22_effort_on_ai_answers": 1,
        "Q8_complete_without_ai": 1,
        "Q7_attempt_independently": 1,
        "Q2_verify_info": 1,
        "Q30_trust_accuracy": 5,
        "Q33_trust_appropriate_support": 5,
        "tool_perplexity": 1.0,
        "tool_claude": 1.0,
        "tool_chatgpt": 1.0,
        "purpose_assignment_preparation": 1.0,
        "purpose_exam_preparation": 1.0,
        "delegate_writing_assignments": 1.0,
        "delegate_summarising_materials": 1.0,
        "delegate_programming_problems": 1.0,
        "delegate_mathematical_problems": 1.0,
        "faculty_Business_Economics": 1.0,
        "age_group": 1.0,
        "degree_field": "Business / Economics"
    }
    r3 = predictor.predict(p3)
    assert r3["status"] == "success"
    assert r3["predicted_category"] == "High"
    assert r3["continuous_risk_score"] == 5.0  # Clamped to upper Likert construct bound
    assert r3["raw_regression_score"] >= 5.0   # Raw unconstrained score preserved for audit
    assert abs(sum(r3["probabilities"].values()) - 1.0) < 0.01
    assert any("clamped" in w.lower() for w in r3["warnings"])


def test_scenario_4_empty_input_guard(predictor):
    """Scenario 4: Empty input prevents misleading default predictions."""
    r4 = predictor.predict({})
    assert r4["status"] == "validation_error"
    assert r4["error_type"] == "MissingRequiredInput"
    assert r4["predicted_category"] is None
    assert r4["continuous_risk_score"] is None


def test_scenario_5_missing_optional_values(predictor):
    """Scenario 5: Missing optional features use peer cohort medians and document warnings."""
    p5 = {
        "ai_usage_freq": 3,
        "Q20_task_delegation_freq": 4,
        "Q1_direct_use_freq": 2
    }
    r5 = predictor.predict(p5)
    assert r5["status"] == "success"
    assert r5["predicted_category"] in ["Low", "Medium", "High"]
    assert any("missing optional features" in w.lower() for w in r5["warnings"])


def test_scenario_6_dirty_text_and_nans(predictor):
    """Scenario 6: Text coercion, string Likert mappings, and NaN handling."""
    p6 = {
        "ai_usage_freq": "often",           # text mapping
        "Q20_task_delegation_freq": "rarely",# text mapping
        "Q1_direct_use_freq": np.nan,       # NaN imputation
        "Q22_effort_on_ai_answers": "invalid_string_xyz", # unparseable fallback
        "degree_field": "Engineering"
    }
    r6 = predictor.predict(p6)
    assert r6["status"] == "success"
    assert 1.0 <= r6["continuous_risk_score"] <= 5.0
    assert any("invalid text" in w.lower() or "unparseable" in w.lower() for w in r6["warnings"])


def test_scenario_7_out_of_range_clamping(predictor):
    """Scenario 7: Extreme numeric inputs are clamped to valid Likert bounds."""
    p7 = {
        "ai_usage_freq": 100.0,
        "Q20_task_delegation_freq": -20.0,
        "Q1_direct_use_freq": 5.0,
        "degree_field": "Computing_IT"
    }
    r7 = predictor.predict(p7)
    assert r7["status"] == "success"
    assert 1.0 <= r7["continuous_risk_score"] <= 5.0
    assert any("out-of-range" in w.lower() or "clamped" in w.lower() for w in r7["warnings"])


def test_scenario_8_borderline_profile(predictor):
    """Scenario 8: Borderline profiles near tertile cuts produce continuous smooth probabilities."""
    p8 = {
        "ai_usage_freq": 3,
        "Q20_task_delegation_freq": 3,
        "Q1_direct_use_freq": 3,
        "Q22_effort_on_ai_answers": 3,
        "Q8_complete_without_ai": 3,
        "Q7_attempt_independently": 3,
        "Q2_verify_info": 4,
        "Q30_trust_accuracy": 3,
        "degree_field": "Computing_IT"
    }
    r8 = predictor.predict(p8)
    assert r8["status"] == "success"
    assert r8["predicted_category"] in ["Low", "Medium"]
    assert abs(sum(r8["probabilities"].values()) - 1.0) < 0.01
    assert r8["probabilities"]["medium"] > 0.1
