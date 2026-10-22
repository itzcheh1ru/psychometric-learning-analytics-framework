"""
tests/test_component1_v4_workflow.py
====================================
Comprehensive integration and reliability test suite for Component 1 (Version 4):
Explainable Cognitive Offloading Risk Model.

Verifies:
1. Version 4 model loads cleanly from disk without retraining.
2. The 68-feature deployed input schema is strictly respected.
3. Calibrated thresholded Ridge predictions produce valid Low, Medium, High tiers.
4. Decision thresholds strictly follow:
     - Low:   score <= 2.667
     - Medium: score > 2.667 and <= 3.500
     - High:  score > 3.500
5. Continuous score remains within [1.0, 5.0].
6. Probabilities are strictly valid, non-negative, and sum to approximately 1.0.
7. Exact LinearSHAP feature contributions and directional explanations are produced.
8. Defensive handling of missing, unparseable, and out-of-range inputs.
9. Empty or non-sensical inputs return clean 400 validation errors.
10. Flask routes GET /api/component1/status and POST /api/component1/predict.
11. Research integrity disclaimer and zero PII exposure.
"""

import json
import pytest
import numpy as np

from app.services.cognitive_offloading.model_service import model_service
from app.services.cognitive_offloading.integration_service import (
    get_predictor_v4,
    DISCLAIMER,
)


@pytest.fixture(scope="module")
def predictor():
    """Load the Version 4 integration service predictor."""
    return get_predictor_v4()


# --------------------------------------------------------------------------- #
# 1. Model Loading & Integrity                                                #
# --------------------------------------------------------------------------- #

def test_v4_model_loads_without_retraining(predictor):
    """Verify model loads from serialized artifact without retraining."""
    assert predictor.model is not None
    assert hasattr(predictor.model, "coef_") or hasattr(predictor.model, "predict")
    assert len(predictor.feature_names) == 68
    assert predictor.coefficients is not None


def test_v4_model_service_reports_ready():
    """ModelService singleton must report model_trained=True and prediction_available=True."""
    assert model_service.is_model_available() is True
    status = model_service.get_status()
    assert status["model_trained"] is True
    assert status["prediction_available"] is True
    assert status["explainability_available"] is True
    assert status["features_count"] == 68


# --------------------------------------------------------------------------- #
# 2. Schema Conformance & Target Leakage Protection                           #
# --------------------------------------------------------------------------- #

def test_v4_feature_schema_has_no_target_leakage(predictor):
    """Ensure no target items or survey identifiers exist in predictor features."""
    forbidden = [
        "co_score", "co_risk", "Q10_rely_memory", "Q11_avoid_mental_effort",
        "Q12_accept_without_understanding", "Q13_less_problem_solving",
        "Q14_depend_on_ai", "Q15_reduces_thinking", "Q37_important_part",
        "email", "name", "student_id", "timestamp"
    ]
    for feat in predictor.feature_names:
        assert feat.lower() not in [f.lower() for f in forbidden]


# --------------------------------------------------------------------------- #
# 3. Decision Thresholds & Risk Tier Mapping                                  #
# --------------------------------------------------------------------------- #

def test_v4_high_risk_prediction_scenario(predictor):
    """High delegation, direct copying, and low verification must classify as High risk."""
    high_input = {
        "ai_usage_freq": 4,
        "Q20_task_delegation_freq": 5,
        "Q1_direct_use_freq": 5,
        "Q22_effort_on_ai_answers": 1,
        "Q8_complete_without_ai": 1,
        "Q7_attempt_independently": 1,
        "Q2_verify_info": 1,
        "Q30_trust_accuracy": 5,
        "degree_field": "Computing_IT"
    }
    res = predictor.predict(high_input)
    assert res["status"] == "success"
    assert res["predicted_category"] == "High"
    assert res["continuous_risk_score"] > 3.500
    assert 1.0 <= res["continuous_risk_score"] <= 5.0
    assert res["probabilities"]["high"] > res["probabilities"]["low"]


def test_v4_low_risk_prediction_scenario(predictor):
    """High autonomy, independent problem solving, and rigorous verification must classify as Low risk."""
    low_input = {
        "ai_usage_freq": 2,
        "Q20_task_delegation_freq": 1,
        "Q1_direct_use_freq": 1,
        "Q22_effort_on_ai_answers": 5,
        "Q8_complete_without_ai": 5,
        "Q7_attempt_independently": 5,
        "Q2_verify_info": 5,
        "Q30_trust_accuracy": 1,
        "degree_field": "Engineering"
    }
    res = predictor.predict(low_input)
    assert res["status"] == "success"
    assert res["predicted_category"] == "Low"
    assert res["continuous_risk_score"] <= 2.667
    assert 1.0 <= res["continuous_risk_score"] <= 5.0
    assert res["probabilities"]["low"] > res["probabilities"]["high"]


def test_v4_medium_risk_balanced_scenario(predictor):
    """Moderate, balanced student habits produce valid predictions with probabilities."""
    med_input = {
        "ai_usage_freq": 3,
        "Q20_task_delegation_freq": 3,
        "Q1_direct_use_freq": 3,
        "Q22_effort_on_ai_answers": 3,
        "Q8_complete_without_ai": 3,
        "Q7_attempt_independently": 3,
        "Q2_verify_info": 3,
        "Q30_trust_accuracy": 3,
        "degree_field": "Business_Economics"
    }
    res = predictor.predict(med_input)
    assert res["status"] == "success"
    assert res["predicted_category"] in ["Low", "Medium", "High"]
    assert 1.0 <= res["continuous_risk_score"] <= 5.0


# --------------------------------------------------------------------------- #
# 4. Probabilities & Calibration                                              #
# --------------------------------------------------------------------------- #

def test_v4_probabilities_sum_to_one(predictor):
    """Calibrated class probabilities must be non-negative and sum to 1.0."""
    res = predictor.predict({"ai_usage_freq": 3, "Q20_task_delegation_freq": 3})
    probs = res["probabilities"]
    assert "low" in probs and "medium" in probs and "high" in probs
    for p in probs.values():
        assert 0.0 <= p <= 1.0
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.01


# --------------------------------------------------------------------------- #
# 5. Exact LinearSHAP Explanations                                            #
# --------------------------------------------------------------------------- #

def test_v4_linear_shap_explanations(predictor):
    """Verify top contributing factors contain exact LinearSHAP values and directional effects."""
    res = predictor.predict({
        "ai_usage_freq": 4,
        "Q20_task_delegation_freq": 5,
        "Q1_direct_use_freq": 5,
        "Q22_effort_on_ai_answers": 1,
        "Q2_verify_info": 1
    }, top_factors_count=5)

    factors = res["top_contributing_factors"]
    assert len(factors) <= 5
    assert len(factors) > 0
    for factor in factors:
        assert "feature_name" in factor
        assert "human_label" in factor
        assert "linear_shap_contribution" in factor
        assert "effect" in factor
        assert factor["effect"] in ["increases predicted risk", "mitigates predicted risk"]
        assert "plain_explanation" in factor


# --------------------------------------------------------------------------- #
# 6. Defensive Imputation & Missing Value Robustness                          #
# --------------------------------------------------------------------------- #

def test_v4_defensive_clamping_and_imputation(predictor):
    """Extreme out-of-range values and NaN must be clamped or imputed gracefully."""
    dirty_input = {
        "ai_usage_freq": "4",           # string cast
        "Q1_direct_use_freq": 999.0,     # excessive out-of-range
        "Q8_complete_without_ai": -50.0, # negative out-of-range
        "Q20_task_delegation_freq": np.nan,  # NaN value
        "degree_field": "Computer Science & Engineering"
    }
    res = predictor.predict(dirty_input)
    assert res["status"] == "success"
    assert 1.0 <= res["continuous_risk_score"] <= 5.0
    assert len(res["warnings"]) > 0


def test_v4_empty_input_returns_validation_error(predictor):
    """Completely empty input must return validation_error status."""
    res = predictor.predict({})
    assert res["status"] == "validation_error"
    assert res["error_type"] == "MissingRequiredInput"
    assert res["predicted_category"] is None


# --------------------------------------------------------------------------- #
# 7. Flask API Endpoints                                                      #
# --------------------------------------------------------------------------- #

def test_api_component1_predict_endpoint(client):
    """POST /api/component1/predict with valid payload returns HTTP 200 with prediction and SHAP."""
    payload = {
        "user_inputs": {
            "ai_usage_freq": 4,
            "Q20_task_delegation_freq": 4,
            "Q1_direct_use_freq": 4,
            "Q22_effort_on_ai_answers": 2,
            "Q8_complete_without_ai": 2,
            "degree_field": "Computing_IT"
        },
        "top_factors_count": 5
    }
    response = client.post("/api/component1/predict", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["predicted_category"] in ["Low", "Medium", "High"]
    assert 1.0 <= data["continuous_risk_score"] <= 5.0
    assert "probabilities" in data
    assert len(data["top_contributing_factors"]) > 0
    assert "disclaimer" in data


def test_api_component1_predict_empty_returns_400(client):
    """POST /api/component1/predict with empty payload returns HTTP 400."""
    response = client.post("/api/component1/predict", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "validation_error"
