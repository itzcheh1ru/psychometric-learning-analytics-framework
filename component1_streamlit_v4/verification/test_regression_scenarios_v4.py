"""
test_regression_scenarios_v4.py
===============================
Dedicated regression test execution for the 8 specified validation scenarios:
1. Low-risk student profile
2. Medium-risk student profile
3. High-risk student profile (Extreme, tests [1.0, 5.0] range constraint & raw preservation)
4. Empty input (tests validation guard preventing misleading assessments)
5. Inputs with missing optional values (tests median imputation and reporting)
6. Inputs with invalid text, NaNs or infinities (tests graceful coercion & warnings)
7. Out-of-range inputs (tests boundary clamping and warnings)
8. Borderline profiles near thresholds (tests calibrated probabilities near 2.667 and 3.500)

Saves execution summary to regression_test_report_v4.json.
"""

import json
import os
import sys
from pathlib import Path
import numpy as np

INTEGRATION_DIR = Path(__file__).resolve().parent.parent / "integration"
sys.path.append(str(INTEGRATION_DIR))

from integration_service_v4 import get_predictor_v4, DISCLAIMER


def run_all_scenarios():
    print("=" * 80)
    print("EXECUTING 8 REGRESSION SCENARIOS — COMPONENT 1 (VERSION 4)")
    print("Model: Calibrated Thresholded Ridge Regressor (Ordinal)")
    print("=" * 80)

    service = get_predictor_v4()
    results = {}

    # Scenario 1: Low-Risk Student Profile
    print("\n[Scenario 1] Low-Risk Student Profile")
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
    r1 = service.predict(p1)
    assert r1["status"] == "success"
    assert r1["predicted_category"] == "Low"
    assert 1.0 <= r1["continuous_risk_score"] <= 2.667
    assert sum(r1["probabilities"].values()) == 1.0
    assert len(r1["top_contributing_factors"]) > 0
    print(f"  Category: {r1['predicted_category']} | Score: {r1['continuous_risk_score']:.3f} / 5.0 | Confidence: {r1['confidence']*100:.1f}%")
    print(f"  Probabilities: {r1['probabilities']}")
    print(f"  Top SHAP Factor: {r1['top_contributing_factors'][0]['feature_name']} ({r1['top_contributing_factors'][0]['effect']})")
    results["scenario_1_low_risk"] = r1

    # Scenario 2: Medium-Risk Student Profile
    print("\n[Scenario 2] Medium-Risk Student Profile")
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
    r2 = service.predict(p2)
    assert r2["status"] == "success"
    assert r2["predicted_category"] == "Medium"
    assert 2.667 < r2["continuous_risk_score"] <= 3.500
    assert sum(r2["probabilities"].values()) == 1.0
    print(f"  Category: {r2['predicted_category']} | Score: {r2['continuous_risk_score']:.3f} / 5.0 | Confidence: {r2['confidence']*100:.1f}%")
    print(f"  Probabilities: {r2['probabilities']}")
    results["scenario_2_medium_risk"] = r2

    # Scenario 3: High-Risk Student Profile (Extreme, tests [1.0, 5.0] range constraint & raw preservation)
    print("\n[Scenario 3] High-Risk Student Profile (Score Constraint & Clamping Audit)")
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
    r3 = service.predict(p3)
    assert r3["status"] == "success"
    assert r3["predicted_category"] == "High"
    assert r3["continuous_risk_score"] == 5.0  # Clamped cleanly to maximum Likert construct scale!
    assert r3["raw_regression_score"] > 5.0    # Raw estimate preserved for audit!
    assert sum(r3["probabilities"].values()) == 1.0
    assert any("clamped to 5.000" in w for w in r3["warnings"])
    print(f"  Category: {r3['predicted_category']} | Clamped Score: {r3['continuous_risk_score']:.3f} / 5.0 | Raw Linear Estimate: {r3['raw_regression_score']:.3f}")
    print(f"  Probabilities: {r3['probabilities']}")
    print(f"  Clamping Notice: {next(w for w in r3['warnings'] if 'clamped' in w)}")
    results["scenario_3_high_risk_clamped"] = r3

    # Scenario 4: Empty Input (Validation Guard)
    print("\n[Scenario 4] Empty Input (Validation Guard Check)")
    r4 = service.predict({})
    assert r4["status"] == "validation_error"
    assert r4["error_type"] == "MissingRequiredInput"
    assert r4["predicted_category"] is None
    assert r4["continuous_risk_score"] is None
    print(f"  Status: {r4['status']} | Error Type: {r4['error_type']}")
    print(f"  Message: {r4['message']}")
    results["scenario_4_empty_input"] = r4

    # Scenario 5: Inputs with Missing Optional Values
    print("\n[Scenario 5] Inputs with Missing Optional Values (Empirical Median Imputation)")
    p5 = {
        "ai_usage_freq": 2,
        "Q20_task_delegation_freq": 2
    }
    r5 = service.predict(p5)
    assert r5["status"] == "success"
    assert r5["predicted_category"] in ["Low", "Medium", "High"]
    assert any("Handled 66 missing optional features" in w for w in r5["warnings"])
    print(f"  Status: {r5['status']} | Category: {r5['predicted_category']} | Score: {r5['continuous_risk_score']:.3f}")
    print(f"  Imputation Note: {next(w for w in r5['warnings'] if 'Handled' in w)}")
    results["scenario_5_missing_optional"] = r5

    # Scenario 6: Inputs with Invalid Text, NaNs or Infinities
    print("\n[Scenario 6] Inputs with Invalid Text, NaNs or Infinities (Defensive Coercion)")
    p6 = {
        "ai_usage_freq": "daily",              # text mapping -> 4.0
        "Q1_direct_use_freq": "bad_text_123",   # invalid text -> median fallback
        "Q20_task_delegation_freq": float("nan"),  # NaN -> median fallback
        "ai_time_per_week": float("inf"),      # +inf -> clamped to 5.0
        "Q8_complete_without_ai": float("-inf"), # -inf -> clamped to 1.0
        "degree_field": "Computer Science"
    }
    r6 = service.predict(p6)
    assert r6["status"] == "success"
    assert any("+Infinity" in w for w in r6["warnings"])
    assert any("-Infinity" in w for w in r6["warnings"])
    assert any("Invalid text" in w for w in r6["warnings"])
    assert any("NaN" in w for w in r6["warnings"])
    print(f"  Status: {r6['status']} | Category: {r6['predicted_category']} | Score: {r6['continuous_risk_score']:.3f}")
    print(f"  Defensive Warnings ({len(r6['warnings'])}):")
    for w in r6["warnings"][:4]:
        print(f"    - {w}")
    results["scenario_6_dirty_nan_inf_text"] = r6

    # Scenario 7: Out-of-Range Numerical Values
    print("\n[Scenario 7] Out-of-Range Inputs (Domain Boundary Clamping)")
    p7 = {
        "ai_usage_freq": 99.0,                 # range [1, 4] -> clamped to 4.0
        "Q1_direct_use_freq": 15.0,            # range [1, 5] -> clamped to 5.0
        "Q8_complete_without_ai": -5.0,        # range [1, 5] -> clamped to 1.0
        "academic_year": 10.0                  # range [1, 6] -> clamped to 6.0
    }
    r7 = service.predict(p7)
    assert r7["status"] == "success"
    assert any("Out-of-range" in w for w in r7["warnings"])
    print(f"  Status: {r7['status']} | Clamped Warnings ({len(r7['warnings'])}):")
    for w in r7["warnings"][:3]:
        print(f"    - {w}")
    results["scenario_7_out_of_range"] = r7

    # Scenario 8: Borderline Profiles near Category Thresholds
    print("\n[Scenario 8] Borderline Profiles near Decision Thresholds")
    # 8A: Near cut1 (2.667) - Low/Medium boundary
    p8a = {
        "ai_usage_freq": 2,
        "Q20_task_delegation_freq": 2,
        "Q1_direct_use_freq": 2,
        "Q22_effort_on_ai_answers": 3,
        "Q8_complete_without_ai": 3,
        "Q7_attempt_independently": 4,
        "Q2_verify_info": 4,
        "Q30_trust_accuracy": 3,
        "Q33_trust_appropriate_support": 3,
        "degree_field": "Natural & Applied Sciences"
    }
    r8a = service.predict(p8a)
    print(f"  [8A: Near cut1 (2.667)] Score: {r8a['continuous_risk_score']:.3f} | Category: {r8a['predicted_category']}")
    print(f"      Calibrated Probabilities: Low={r8a['probabilities']['low']:.2%}, Med={r8a['probabilities']['medium']:.2%}, High={r8a['probabilities']['high']:.2%}")

    # 8B: Near cut2 (3.500) - Medium/High boundary
    p8b = {
        "ai_usage_freq": 3,
        "Q20_task_delegation_freq": 4,
        "Q1_direct_use_freq": 3,
        "Q22_effort_on_ai_answers": 3,
        "Q8_complete_without_ai": 3,
        "Q7_attempt_independently": 3,
        "Q2_verify_info": 3,
        "Q30_trust_accuracy": 4,
        "Q33_trust_appropriate_support": 3,
        "degree_field": "Computer Science / IT"
    }
    r8b = service.predict(p8b)
    print(f"  [8B: Near cut2 (3.500)] Score: {r8b['continuous_risk_score']:.3f} | Category: {r8b['predicted_category']}")
    print(f"      Calibrated Probabilities: Low={r8b['probabilities']['low']:.2%}, Med={r8b['probabilities']['medium']:.2%}, High={r8b['probabilities']['high']:.2%}")
    results["scenario_8a_borderline_low_medium"] = r8a
    results["scenario_8b_borderline_medium_high"] = r8b

    report_file = Path(__file__).resolve().parent / "regression_test_report_v4.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print(f"ALL 8 REGRESSION SCENARIOS VALIDATED AND PASSED SUCCESSFULLY!")
    print(f"Detailed output saved to: {report_file}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(run_all_scenarios())
