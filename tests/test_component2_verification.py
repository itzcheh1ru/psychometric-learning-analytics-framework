"""
tests/test_component2_verification.py

Comprehensive test suite for Phase 4:
AI-Generated Answer Verification Performance Assessment & Empirical Validation.
Component 2: Explainable SEM-Informed AI Trust and Verification Assessment Framework.

Coverage:
1. Scenario bank integrity & error topology (8 scenarios, 24 testable claims, controls).
2. Answer-key security & sanitized scenario masking.
3. Multidimensional verification performance metrics (Accuracy, Precision, Recall, Specificity, F1).
4. Binary confusion matrix (TP, TN, FP, FN) calculation and edge cases.
5. Explanation rubric grading (0, 1, 2 point rubric criteria).
6. Metacognitive calibration analysis & 4-quadrant classification (Q1, Q2, Q3, Q4).
7. Discrepancy Index computation (Delta_calib = VB_norm - Task_Accuracy).
8. Empirical validation protocol & correlation statistics (Pearson r, Fisher's z CI, Spearman rho).
9. Privacy-preserving informed consent filtering for pilot evaluation storage.
10. UI and API routes (/component2/verification-task, /api/component2/verification-scenarios,
    /api/component2/evaluate-verification, /api/component2/combined-report, /api/component2/validation-protocol).
"""

import json
import pytest
from pathlib import Path

from app import create_app
from app.services.sem_analysis.verification_task_service import (
    VERIFICATION_SCENARIOS,
    get_sanitized_verification_scenarios,
    get_scenario_by_id,
    evaluate_student_verification,
    grade_explanation_rubric,
    generate_task_performance_feedback,
)
from app.services.sem_analysis.calibration_service import (
    compute_verification_calibration,
)
from app.services.sem_analysis.validation_protocol import (
    VALIDATION_PROTOCOL_SPEC,
    compute_sample_correlation,
    save_pilot_evaluation_record,
)
from app.services.sem_analysis.combined_report_service import (
    generate_combined_csv_report,
)
from app.services.sem_analysis.scoring_service import calculate_individual_scores


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def _get_dummy_survey_scores(vb_mean=4.0, at_mean=3.5, ad_mean=2.8):
    """Helper to generate mock survey construct scores for calibration testing."""
    return {
        "construct_scores": {
            "AT": {"mean_score": at_mean, "percentile_rank": 60.0, "z_score": 0.25},
            "VB": {"mean_score": vb_mean, "percentile_rank": 70.0, "z_score": 0.50},
            "PU": {"mean_score": 3.8, "percentile_rank": 55.0, "z_score": 0.10},
            "AD": {"mean_score": ad_mean, "percentile_rank": 40.0, "z_score": -0.20},
            "LC": {"mean_score": 3.9, "percentile_rank": 65.0, "z_score": 0.35},
        }
    }


# =========================================================================== #
# 1. Scenario Bank Integrity & Masking Tests                                 #
# =========================================================================== #

def test_verification_scenario_bank_integrity():
    """Verify scenario bank contains 8 scenarios with 24 claims covering 4 domains."""
    assert len(VERIFICATION_SCENARIOS) == 8

    total_claims = 0
    domains = set()
    has_control_scenarios = False

    for s in VERIFICATION_SCENARIOS:
        assert "id" in s
        assert "domain" in s
        assert "topic" in s
        assert "academic_question" in s
        assert "simulated_ai_response" in s
        assert "claims" in s
        assert len(s["claims"]) >= 2

        domains.add(s["domain"])
        total_claims += len(s["claims"])

        # Check if control scenario (all claims correct)
        all_correct = all(c["ground_truth"] == "CORRECT" for c in s["claims"])
        if all_correct:
            has_control_scenarios = True

        for c in s["claims"]:
            assert "claim_id" in c
            assert "statement" in c
            assert c["ground_truth"] in ["CORRECT", "INCORRECT", "UNSUPPORTED"]
            assert "expert_explanation" in c
            assert "reference_citation" in c
            assert len(c["reference_citation"]) > 5

    assert total_claims == 24
    assert len(domains) >= 4
    assert has_control_scenarios is True  # SCEN_03 and SCEN_07


def test_sanitized_scenarios_security():
    """Verify that get_sanitized_verification_scenarios masks ground truth and explanations."""
    sanitized = get_sanitized_verification_scenarios()
    assert len(sanitized) == 8

    for s in sanitized:
        assert "simulated_ai_response" in s
        for c in s["claims"]:
            assert "statement" in c
            assert "ground_truth" not in c
            assert "expert_explanation" not in c
            assert "reference_citation" not in c
            assert "rubric_keywords" not in c


# =========================================================================== #
# 2. Multidimensional Verification Grading Tests                              #
# =========================================================================== #

def test_evaluate_student_verification_perfect_score():
    """A student who classifies all 24 claims correctly receives 100% accuracy and F1."""
    perfect_submissions = []
    for s in VERIFICATION_SCENARIOS:
        claim_subs = []
        for c in s["claims"]:
            claim_subs.append({
                "claim_id": c["claim_id"],
                "selected_verdict": c["ground_truth"],
                "justification": f"Detailed mathematical proof and empirical calculation matching {c['ground_truth']}.",
                "verification_method": "Scratchpad Calculation",
            })
        perfect_submissions.append({
            "scenario_id": s["id"],
            "claims": claim_subs,
        })

    eval_result = evaluate_student_verification(perfect_submissions, student_id="PERFECT_STUDENT")
    summary = eval_result["summary"]
    cm = eval_result["confusion_matrix"]

    assert eval_result["success"] is True
    assert summary["accuracy"] == 1.0
    assert summary["accuracy_pct"] == 100.0
    assert summary["recall"] == 1.0
    assert summary["precision"] == 1.0
    assert summary["specificity"] == 1.0
    assert summary["f1_score"] == 1.0
    assert cm["false_negatives"] == 0
    assert cm["false_positives"] == 0
    assert cm["true_positives"] > 0
    assert cm["true_negatives"] > 0
    assert summary["rubric_points_earned"] > 0


def test_evaluate_student_verification_with_confusion():
    """Verify confusion matrix when a student misses errors (FN) and raises false alarms (FP)."""
    flawed_submissions = []
    for s in VERIFICATION_SCENARIOS:
        claim_subs = []
        for c in s["claims"]:
            # Invert verdict: if ground truth is CORRECT, student claims ERRONEOUS (FP)
            # if ground truth is flawed, student claims CORRECT (FN)
            inverted = "ERRONEOUS" if c["ground_truth"] == "CORRECT" else "CORRECT"
            claim_subs.append({
                "claim_id": c["claim_id"],
                "selected_verdict": inverted,
                "justification": "I guessed this without checking.",
                "verification_method": "Intuitive Reading",
            })
        flawed_submissions.append({
            "scenario_id": s["id"],
            "claims": claim_subs,
        })

    eval_result = evaluate_student_verification(flawed_submissions, student_id="CONFUSED_STUDENT")
    summary = eval_result["summary"]
    cm = eval_result["confusion_matrix"]

    assert summary["accuracy"] == 0.0
    assert summary["recall"] == 0.0
    assert cm["true_positives"] == 0
    assert cm["true_negatives"] == 0
    assert cm["false_positives"] > 0
    assert cm["false_negatives"] > 0


def test_explanation_rubric_scoring_levels():
    """Verify explanation rubric grades 0 for blank/trivial, 1 for partial, 2 for thorough rationale."""
    claim = VERIFICATION_SCENARIOS[0]["claims"][1]  # SCEN_01_C2 (integral of 1/2 e^{2x} error)

    # Level 0: Blank or trivial
    score_0, _ = grade_explanation_rubric("", claim, is_correct_verdict=True)
    assert score_0 == 0

    score_0b, _ = grade_explanation_rubric("it is wrong", claim, is_correct_verdict=True)
    assert score_0b == 0

    # Level 1: Plausible explanation without detailed keywords
    score_1, _ = grade_explanation_rubric("The integration step has a missing factor of two.", claim, is_correct_verdict=True)
    assert score_1 >= 1

    # Level 2: Includes exact mathematical derivation and rubric keywords (e.g. 1/4)
    score_2, _ = grade_explanation_rubric("The integral of 1/2 e^{2x} dx requires dividing by 2 again, yielding 1/4 e^{2x}, not 1/2.", claim, is_correct_verdict=True)
    assert score_2 == 2


# =========================================================================== #
# 3. Metacognitive Calibration Analysis Tests                                 #
# =========================================================================== #

def test_metacognitive_calibration_quadrants():
    """Verify calibration engine correctly identifies all 4 calibration quadrants."""
    mock_summary_high = {"summary": {"accuracy": 0.85, "recall": 0.80, "precision": 0.90, "rubric_pct": 75.0}}
    mock_summary_low = {"summary": {"accuracy": 0.40, "recall": 0.35, "precision": 0.45, "rubric_pct": 30.0}}

    # Q1: High VB (4.2 >= 3.80) & High Accuracy (0.85 >= 0.70) => Calibrated Discerning
    calib_q1 = compute_verification_calibration(
        construct_scores=_get_dummy_survey_scores(vb_mean=4.2)["construct_scores"],
        task_performance=mock_summary_high,
    )
    assert calib_q1["calibration_zone"]["zone_id"] == "CALIB_Q1"
    assert "Calibrated" in calib_q1["calibration_zone"]["zone_title"]

    # Q2: High VB (4.5 >= 3.80) & Low Accuracy (0.40 < 0.70) => Verification Illusion (Inflated Confidence)
    calib_q2 = compute_verification_calibration(
        construct_scores=_get_dummy_survey_scores(vb_mean=4.5)["construct_scores"],
        task_performance=mock_summary_low,
    )
    assert calib_q2["calibration_zone"]["zone_id"] == "CALIB_Q2"
    assert "Illusion" in calib_q2["calibration_zone"]["zone_title"] or "Inflated" in calib_q2["calibration_zone"]["zone_title"]
    assert calib_q2["metrics"]["discrepancy_index_delta"] > 0.15

    # Q3: Low VB (3.0 < 3.80) & High Accuracy (0.85 >= 0.70) => Cautious Skeptic
    calib_q3 = compute_verification_calibration(
        construct_scores=_get_dummy_survey_scores(vb_mean=3.0)["construct_scores"],
        task_performance=mock_summary_high,
    )
    assert calib_q3["calibration_zone"]["zone_id"] == "CALIB_Q3"
    assert "Cautious" in calib_q3["calibration_zone"]["zone_title"]

    # Q4: Low VB (2.5 < 3.80) & Low Accuracy (0.40 < 0.70) => Vulnerable Verifier
    calib_q4 = compute_verification_calibration(
        construct_scores=_get_dummy_survey_scores(vb_mean=2.5)["construct_scores"],
        task_performance=mock_summary_low,
    )
    assert calib_q4["calibration_zone"]["zone_id"] == "CALIB_Q4"
    assert "Vulnerable" in calib_q4["calibration_zone"]["zone_title"]


def test_discrepancy_index_formula():
    """Verify exact formula: Delta = (VB - 1.0)/4.0 - Task_Accuracy."""
    vb_mean = 4.0
    task_acc = 0.75
    expected_vb_norm = (4.0 - 1.0) / 4.0  # 0.75
    expected_delta = round(expected_vb_norm - task_acc, 3)  # 0.000

    calib = compute_verification_calibration(
        construct_scores=_get_dummy_survey_scores(vb_mean=vb_mean)["construct_scores"],
        task_performance={"summary": {"accuracy": task_acc, "recall": 0.75, "precision": 0.75, "rubric_pct": 70.0}},
    )
    m = calib["metrics"]
    assert m["normalized_vb_minmax"] == pytest.approx(expected_vb_norm, abs=1e-3)
    assert m["discrepancy_index_delta"] == pytest.approx(expected_delta, abs=1e-3)


# =========================================================================== #
# 4. Empirical Validation Protocol & Privacy Storage Tests                   #
# =========================================================================== #

def test_compute_sample_correlation_statistics():
    """Verify Pearson r, Fisher's z 95% CI, and Spearman rho computations."""
    x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    y = [1.2, 1.9, 3.1, 3.8, 5.2, 5.9, 7.1, 8.0, 9.2, 9.9]

    stats = compute_sample_correlation(x, y)
    assert stats["n"] == 10
    assert stats["pearson_r"] > 0.95
    assert stats["spearman_rho"] > 0.95
    assert stats["pearson_r_ci95"][0] < stats["pearson_r"] < stats["pearson_r_ci95"][1]
    assert stats["degrees_of_freedom"] == 8


def test_save_pilot_evaluation_consent_filtering(tmp_path):
    """Verify pilot data storage only persists when explicit informed consent is granted."""
    dummy_record = {
        "student_id": "TEST_CONSENT_001",
        "summary": {"accuracy": 0.80},
        "calibration": {"zone": "CALIB_Q1"},
        "claim_evaluations": [{"claim_id": "SCEN_01_C1"}],
    }

    # Case 1: No consent -> in-memory only, no disk file written
    res_no_consent = save_pilot_evaluation_record(dummy_record, consent_given=False)
    assert res_no_consent["saved"] is False
    assert "in-memory only" in res_no_consent["reason"]

    # Case 2: Explicit consent -> writes sanitized file
    res_consent = save_pilot_evaluation_record(dummy_record, consent_given=True)
    assert res_consent["saved"] is True
    assert "filepath" in res_consent
    filepath = Path(res_consent["filepath"])
    assert filepath.exists()

    # Clean up test artifact
    try:
        filepath.unlink()
    except Exception:
        pass


# =========================================================================== #
# 5. Combined Report CSV Export Tests                                         #
# =========================================================================== #

def test_generate_combined_csv_report():
    """Verify combined CSV report format includes all required sections and RFC 4180 headers."""
    scoring = _get_dummy_survey_scores()
    task_eval = {
        "summary": {
            "total_claims_evaluated": 24,
            "correct_classifications": 20,
            "accuracy": 0.833,
            "recall": 0.800,
            "precision": 0.850,
            "specificity": 0.875,
            "f1_score": 0.824,
            "rubric_points_earned": 36,
            "rubric_points_possible": 48,
            "rubric_pct": 75.0,
        },
        "confusion_matrix": {"true_positives": 12, "true_negatives": 8, "false_positives": 2, "false_negatives": 2},
        "claim_evaluations": [
            {
                "claim_id": "SCEN_01_C1",
                "statement": "Let u = x...",
                "student_verdict": "CORRECT",
                "ground_truth": "CORRECT",
                "is_correct_classification": True,
                "rubric_score": 2,
                "expert_explanation": "Correct parts step.",
                "reference_citation": "Stewart (2020)",
            }
        ],
        "performance_feedback": [
            {
                "id": "FB_01",
                "category": "Accuracy",
                "priority": "HIGH",
                "title": "Maintain Rigorous Step Verification",
                "diagnostic": "Solid discernment.",
                "action_strategy": "Continue checking intermediate steps.",
            }
        ],
    }
    calib = compute_verification_calibration(scoring["construct_scores"], task_eval)

    csv_text = generate_combined_csv_report(
        scoring_result=scoring,
        verification_eval=task_eval,
        calibration_result=calib,
        student_meta={"student_id": "STUDENT_COMBO_TEST"},
    )

    assert "COMBINED PSYCHOMETRIC & VERIFICATION PERFORMANCE ASSESSMENT REPORT" in csv_text
    assert "SECTION 1: SELF-REPORTED PSYCHOMETRIC CONSTRUCT SCORES" in csv_text
    assert "SECTION 2: DEMONSTRATED VERIFICATION TASK PERFORMANCE" in csv_text
    assert "SECTION 3: METACOGNITIVE CALIBRATION MATRIX" in csv_text
    assert "SECTION 4: SCENARIO-BY-SCENARIO CLAIM EVALUATION AUDIT" in csv_text
    assert "SECTION 5: DUAL-TIER EDUCATIONAL RECOMMENDATIONS" in csv_text
    assert "SECTION 6: SCIENTIFIC & METHODOLOGICAL DISCLAIMERS" in csv_text
    assert "STUDENT_COMBO_TEST" in csv_text


# =========================================================================== #
# 6. UI & Flask API Integration Route Tests                                   #
# =========================================================================== #

def test_verification_task_ui_route(client):
    """GET /component2/verification-task renders the practical verification interface."""
    res = client.get("/component2/verification-task")
    assert res.status_code == 200
    assert b"AI-Generated Answer Verification Performance Assessment" in res.data
    assert b"Scenario 1: Academic Problem Prompt" in res.data
    assert b"Simulated AI-Generated Output" in res.data
    assert b"Informed Research Consent" in res.data
    assert b"component2_verification.js" in res.data


def test_api_verification_scenarios_endpoint(client):
    """GET /api/component2/verification-scenarios returns 8 sanitized scenarios."""
    res = client.get("/api/component2/verification-scenarios")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["count"] == 8
    assert len(data["scenarios"]) == 8
    # Security: ground truth must be masked
    first_claim = data["scenarios"][0]["claims"][0]
    assert "ground_truth" not in first_claim


def test_api_evaluate_verification_endpoint(client):
    """POST /api/component2/evaluate-verification processes submissions and returns full metrics."""
    # Build minimal valid submission for 1 scenario
    submissions = [
        {
            "scenario_id": "SCEN_01",
            "claims": [
                {
                    "claim_id": "SCEN_01_C1",
                    "selected_verdict": "CORRECT",
                    "verification_method": "Scratchpad Calculation",
                    "justification": "Step 1 correctly identifies u and du.",
                },
                {
                    "claim_id": "SCEN_01_C2",
                    "selected_verdict": "ERRONEOUS",
                    "verification_method": "Scratchpad Calculation",
                    "justification": "Step 4 dropped the 1/2 factor inside the integral, should be 1/4.",
                },
                {
                    "claim_id": "SCEN_01_C3",
                    "selected_verdict": "ERRONEOUS",
                    "verification_method": "Scratchpad Calculation",
                    "justification": "Final answer carries forward the Step 4 error.",
                },
            ],
        }
    ]

    payload = {
        "submissions": submissions,
        "student_id": "API_TEST_STUDENT",
        "consent_research_data": False,
        "scoring_result": _get_dummy_survey_scores(vb_mean=4.1),
    }

    res = client.post("/api/component2/evaluate-verification", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["student_id"] == "API_TEST_STUDENT"
    assert "verification_evaluation" in data
    assert "calibration" in data
    assert data["verification_evaluation"]["summary"]["accuracy"] == 1.0  # All 3 classified correctly
    assert data["calibration"]["calibration_zone"]["zone_id"] in ["CALIB_Q1", "CALIB_Q2", "CALIB_Q3", "CALIB_Q4"]


def test_api_combined_report_export_endpoints(client):
    """POST /api/component2/combined-report exports CSV and JSON reports."""
    dummy_eval = {
        "summary": {
            "total_claims_evaluated": 3,
            "correct_classifications": 3,
            "accuracy": 1.0,
            "recall": 1.0,
            "precision": 1.0,
            "specificity": 1.0,
            "f1_score": 1.0,
            "rubric_points_earned": 6,
            "rubric_points_possible": 6,
            "rubric_pct": 100.0,
        },
        "confusion_matrix": {"true_positives": 2, "true_negatives": 1, "false_positives": 0, "false_negatives": 0},
        "claim_evaluations": [],
        "performance_feedback": [],
    }

    # 1. CSV export
    res_csv = client.post("/api/component2/combined-report", json={
        "format": "csv",
        "scoring_result": _get_dummy_survey_scores(),
        "verification_eval": dummy_eval,
        "calibration_result": None,
        "student_meta": {"student_id": "CSV_TEST_STUDENT"},
    })
    assert res_csv.status_code == 200
    assert res_csv.mimetype == "text/csv"
    assert b"COMBINED PSYCHOMETRIC & VERIFICATION PERFORMANCE ASSESSMENT REPORT" in res_csv.data

    # 2. JSON export
    res_json = client.post("/api/component2/combined-report", json={
        "format": "json",
        "scoring_result": _get_dummy_survey_scores(),
        "verification_eval": dummy_eval,
        "calibration_result": None,
        "student_meta": {"student_id": "JSON_TEST_STUDENT"},
    })
    assert res_json.status_code == 200
    assert res_json.mimetype == "application/json"
    json_data = res_json.get_json()
    assert json_data["meta"]["student_id"] == "JSON_TEST_STUDENT"

    # 3. Bad request on missing verification_eval
    res_bad = client.post("/api/component2/combined-report", json={"format": "csv"})
    assert res_bad.status_code == 400


def test_api_validation_protocol_endpoint(client):
    """GET /api/component2/validation-protocol returns protocol specification."""
    res = client.get("/api/component2/validation-protocol")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "protocol" in data
    assert data["protocol"]["project_id"] == "J26-DS-310"
    assert len(data["protocol"]["protocol_phases"]) >= 4
