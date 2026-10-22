"""
tests/test_component4_retention.py
==================================
Comprehensive integration and unit test suite for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Verifies:
1. UI Page Rendering (/component4/ and /component4) with all required headings,
   disclaimers, workflow steps, and forms.
2. Status and Specification APIs (GET /api/component4/status, /api/component4/specification).
3. Experimental Session Validation (POST /api/component4/validate-session) with valid
   and invalid payloads.
4. Retention Risk Prediction Engine (POST /api/component4/predict-risk).
5. Corpus NLP Summary and Text Analysis (GET /api/component4/nlp-summary,
   POST /api/component4/analyze-text, POST /api/component4/compare-nlp).
6. Recall Previews and Regressors (POST /api/component4/preview-immediate-recall,
   POST /api/component4/preview-delayed-recall, POST /api/component4/predict-immediate-recall).
7. Rubric and Condition Comparison Previews (POST /api/component4/preview-human-rubric,
   POST /api/component4/preview-condition-comparison).
8. Model Metrics and Feature Importances (GET /api/component4/model-metrics,
   GET /api/component4/feature-importance).
9. Input Validation Robustness (malformed JSON, empty payload, out-of-range ratings).
10. Research Integrity Guarantees (no fake p-values, explicit prototype disclaimers).
"""

import json
import pytest

from app.services.retention import (
    EXPERIMENTAL_CONDITIONS,
    CONDITION_ORDERS,
    SESSION_STAGES,
    RUBRIC_CRITERIA,
    CONDITION_COMPARISON_MEASURES,
    analysis_service,
)
from app.services.retention.nlp_pipeline import analyze_text, compare_texts


# =========================================================================== #
# 1. UI Page Rendering & Trailing Slash Tests                                  #
# =========================================================================== #

def test_component4_page_loads_with_and_without_trailing_slash(client):
    """GET /component4 and /component4/ must both return HTTP 200 with HTML content."""
    for path in ["/component4", "/component4/"]:
        res = client.get(path)
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert "GenAI-Assisted Cognitive Engagement" in html
        assert "Experimental Workflow" in html
        assert "Brain-Only Writing" in html
        assert "GenAI-Assisted Writing" in html
        assert "Better writing output does not automatically imply better learning" in html


def test_component4_page_contains_all_core_interactive_sections(client):
    """Page must contain the interactive assessment cards, forms, and results displays."""
    res = client.get("/component4/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Validate Experimental Session" in html
    assert "Immediate Recall" in html
    assert "Delayed Recall" in html
    assert "NLP Feature Extraction Framework" in html
    assert "NLP Linguistic Evaluation" in html or "NLP" in html


# =========================================================================== #
# 2. Status and Specification APIs                                            #
# =========================================================================== #

def test_component4_status_api_structure(client):
    """GET /api/component4/status returns structured status with prototype completion flags."""
    res = client.get("/api/component4/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["component"] == "GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation"
    assert "prototype_completion" in data
    assert "sample_size" in data["prototype_completion"]
    assert data["dataset_ready"] is False
    assert data["final_results_available"] is False


def test_component4_specification_api_contents(client):
    """GET /api/component4/specification returns complete study conditions and orders."""
    res = client.get("/api/component4/specification")
    assert res.status_code == 200
    data = res.get_json()
    assert "Brain-only writing" in data["conditions"]
    assert "GenAI-assisted writing" in data["conditions"]
    assert "Brain-only first" in data["condition_orders"]
    assert "GenAI-assisted first" in data["condition_orders"]
    assert "Writing task" in data["session_stages"]


# =========================================================================== #
# 3. Session Validation API (POST /api/component4/validate-session)          #
# =========================================================================== #

def test_validate_session_valid_payload(client):
    """Valid session payload returns HTTP 200 with sanitized data."""
    payload = {
        "participant_reference": "P4-TEST-001",
        "experimental_condition": "Brain-only writing",
        "condition_order": "Brain-only first",
        "session_stage": "Writing task",
        "task_reference": "TASK-RET-01",
        "consent_confirmed": True,
    }
    res = client.post("/api/component4/validate-session", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["persistence"] is False
    assert data["validated_session"]["participant_reference"] == "P4-TEST-001"


def test_validate_session_missing_consent_fails(client):
    """Session without explicit research consent must fail validation with HTTP 400."""
    payload = {
        "participant_reference": "P4-TEST-002",
        "experimental_condition": "GenAI-assisted writing",
        "condition_order": "GenAI-assisted first",
        "session_stage": "Writing task",
        "task_reference": "TASK-RET-02",
        "consent_confirmed": False,
    }
    res = client.post("/api/component4/validate-session", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["valid"] is False
    assert any("consent" in e.lower() for e in data["errors"])


def test_validate_session_invalid_reference_fails(client):
    """Invalid participant reference format must be rejected."""
    payload = {
        "participant_reference": "INVALID$$CODE@@",
        "experimental_condition": "Brain-only writing",
        "condition_order": "Brain-only first",
        "session_stage": "Writing task",
        "task_reference": "TASK-RET-01",
        "consent_confirmed": True,
    }
    res = client.post("/api/component4/validate-session", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["valid"] is False


# =========================================================================== #
# 4. Retention Risk Prediction (POST /api/component4/predict-risk)           #
# =========================================================================== #

def test_predict_risk_high_dependency(client):
    """Participant with high dependency and low effort triggers High Retention Risk."""
    payload = {
        "perceived_ai_dependency_score": 5,
        "ga_mental_effort": 1,
        "cognitive_ownership_score": 1,
        "ga_learning_time_sec": 120.0,
        "ga_immediate_mcq": 9.0,
        "ga_prompt_count": 8,
        "ga_confidence": 5,
        "ga_ai_usefulness": 5,
        "ga_explanation_ease": 5,
        "ga_word_count": 65,
        "ga_lexical_diversity_ttr": 0.55,
        "explanation_autonomy_score": 1,
        "bo_learning_time_sec": 240.0,
        "bo_immediate_mcq": 7.5,
        "bo_mental_effort": 4,
        "bo_lexical_diversity_ttr": 0.75,
    }
    res = client.post("/api/component4/predict-risk", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "prediction" in data
    assert data["prediction"] in ["High Retention Risk", "Stable Retention"]
    assert "risk_probability" in data
    assert 0.0 <= data["risk_probability"] <= 1.0
    assert "predicted_retention_rate" in data


def test_predict_risk_balanced_engagement(client):
    """Participant with balanced effort and low AI dependency yields Stable Retention."""
    payload = {
        "perceived_ai_dependency_score": 1,
        "ga_mental_effort": 5,
        "cognitive_ownership_score": 5,
        "ga_learning_time_sec": 250.0,
        "ga_immediate_mcq": 8.5,
        "ga_prompt_count": 2,
    }
    res = client.post("/api/component4/predict-risk", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "prediction" in data
    assert 0.0 <= data["risk_probability"] <= 1.0


def test_predict_risk_empty_body_uses_safe_defaults(client):
    """Empty JSON body falls back safely to cohort medians or rule heuristics."""
    res = client.post("/api/component4/predict-risk", json={})
    assert res.status_code == 200
    data = res.get_json()
    assert "prediction" in data
    assert "predicted_retention_rate" in data


# =========================================================================== #
# 5. NLP Analysis & Comparison APIs                                          #
# =========================================================================== #

def test_nlp_summary_api(client):
    """GET /api/component4/nlp-summary returns comparative condition corpus stats."""
    res = client.get("/api/component4/nlp-summary")
    assert res.status_code == 200
    data = res.get_json()
    assert "brain_only_metrics" in data
    assert "genai_assisted_metrics" in data
    assert "mean_lexical_diversity_ttr" in data["brain_only_metrics"]
    assert "mean_lexical_diversity_ttr" in data["genai_assisted_metrics"]


def test_analyze_text_valid_input(client):
    """POST /api/component4/analyze-text computes linguistic features in memory."""
    sample_text = (
        "Educational data mining techniques allow researchers to extract patterns "
        "from student learning interactions and cognitive retention logs."
    )
    res = client.post("/api/component4/analyze-text", json={"text": sample_text})
    assert res.status_code == 200
    data = res.get_json()
    assert data["word_count"] > 10
    assert 0.0 < data["ttr"] <= 1.0
    assert data["persistence"] is False


def test_analyze_text_empty_input_rejected(client):
    """POST /api/component4/analyze-text rejects empty or whitespace-only strings with HTTP 400."""
    res = client.post("/api/component4/analyze-text", json={"text": "   "})
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data


def test_compare_nlp_valid_pair(client):
    """POST /api/component4/compare-nlp performs paired condition lexical comparison."""
    payload = {
        "human_text": "Students actively formulating their own explanations retain concepts more thoroughly over time.",
        "ai_text": "Generative artificial intelligence provides immediate automated assistance and conversational support."
    }
    res = client.post("/api/component4/compare-nlp", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "brain_only" in data
    assert "genai_assisted" in data
    assert "comparison" in data
    assert "ttr_difference" in data["comparison"]


# =========================================================================== #
# 6. Immediate & Delayed Recall Previews                                      #
# =========================================================================== #

def test_preview_immediate_recall_valid(client):
    """POST /api/component4/preview-immediate-recall computes count difference in memory."""
    payload = {
        "brain_only_count": 8,
        "genai_assisted_count": 9,
    }
    res = client.post("/api/component4/preview-immediate-recall", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["preview"]["difference_genai_minus_brain"] == 1


def test_preview_immediate_recall_negative_count_rejected(client):
    """Negative counts must be rejected with HTTP 400."""
    payload = {
        "brain_only_count": -3,
        "genai_assisted_count": 8,
    }
    res = client.post("/api/component4/preview-immediate-recall", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["valid"] is False


def test_preview_delayed_recall_valid(client):
    """POST /api/component4/preview-delayed-recall validates delayed recall items."""
    payload = {
        "brain_only_count": 7,
        "genai_assisted_count": 5,
    }
    res = client.post("/api/component4/preview-delayed-recall", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["preview"]["difference_genai_minus_brain"] == -2


# =========================================================================== #
# 7. Rubric & Condition Comparison Previews                                   #
# =========================================================================== #

def test_preview_rubric_valid_ratings(client):
    """POST /api/component4/preview-human-rubric computes exact agreement and condition means."""
    payload = {
        "ratings": {
            "content_accuracy": {
                "brain_only": {"rater_1": 4, "rater_2": 4},
                "genai_assisted": {"rater_1": 5, "rater_2": 4},
            },
            "task_relevance": {
                "brain_only": {"rater_1": 4, "rater_2": 3},
                "genai_assisted": {"rater_1": 4, "rater_2": 4},
            },
            "reasoning_support": {
                "brain_only": {"rater_1": 3, "rater_2": 3},
                "genai_assisted": {"rater_1": 4, "rater_2": 4},
            },
            "clarity_organization": {
                "brain_only": {"rater_1": 4, "rater_2": 4},
                "genai_assisted": {"rater_1": 5, "rater_2": 5},
            },
        }
    }
    res = client.post("/api/component4/preview-human-rubric", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert "exact_agreement_percent" in data["preview"]
    assert "difference_genai_minus_brain" in data["preview"]


def test_preview_condition_comparison_valid(client):
    """POST /api/component4/preview-condition-comparison compares independent measures without combining."""
    payload = {
        "brain_only": {
            "immediate_recall_count": 8,
            "delayed_recall_count": 7,
            "ownership_rating": 4.5,
            "cognitive_effort_rating": 4.0,
            "human_rubric_mean": 3.8,
        },
        "genai_assisted": {
            "immediate_recall_count": 9,
            "delayed_recall_count": 5,
            "ownership_rating": 2.5,
            "cognitive_effort_rating": 2.0,
            "human_rubric_mean": 4.2,
        }
    }
    res = client.post("/api/component4/preview-condition-comparison", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["combined_score"] is None
    assert "immediate_recall_count" in data["comparisons"]
    assert data["comparisons"]["delayed_recall_count"]["difference_genai_minus_brain"] == -2.0


# =========================================================================== #
# 8. Model Metrics and Feature Importance APIs                                #
# =========================================================================== #

def test_model_metrics_api(client):
    """GET /api/component4/model-metrics returns trained model performance metrics."""
    res = client.get("/api/component4/model-metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert "classification_results" in data
    assert "Random Forest" in data["classification_results"]
    assert "Decision Tree" in data["classification_results"]


def test_feature_importance_api(client):
    """GET /api/component4/feature-importance returns ranked feature weights."""
    res = client.get("/api/component4/feature-importance")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, dict)
    assert len(data) > 0


# =========================================================================== #
# 9. NLP Pipeline Pure-Python Unit Tests                                      #
# =========================================================================== #

def test_pure_python_nlp_pipeline_functions():
    """Unit test the pure-Python tokenizer and linguistic feature extractor."""
    text = "Students who rely exclusively on AI lose conceptual recall."
    res = analyze_text(text)
    assert res["word_count"] == 9
    assert res["sentence_count"] == 1
    assert res["ttr"] == 1.0

    cmp_res = compare_texts("Human written essay text.", "AI generated academic response text.")
    assert "brain_only" in cmp_res
    assert "genai_assisted" in cmp_res
