"""
test_ui_pages_and_navigation_v4.py
==================================
Automated validation of the redesigned beginner-friendly UI state flow,
unselected initial state rules, required input validation, and predictor integration.

Tests:
1. Blank initial questionnaire state and required fields completeness.
2. Prevention of empty submissions and rejection of missing required inputs.
3. Successful prediction and LinearSHAP enrichment for valid student profiles.
4. Execution of all benchmark evaluation presets.
5. Continuous score bounds [1.0, 5.0] and raw score preservation audit.
6. Isolation of UI-only degree fields from the 68-feature model schema.
7. Granular required vs. optional questionnaire field validation.
"""

import sys
import unittest
from pathlib import Path

INTEGRATION_DIR = Path(__file__).resolve().parent.parent / "integration"
sys.path.append(str(INTEGRATION_DIR))

from integration_service_v4 import get_predictor_v4, FEATURE_HUMAN_LABELS, FEATURE_PLAIN_EXPLANATIONS
from app_ui_v4 import (
    PRESETS_DATA,
    BLANK_ANSWERS,
    DEFAULT_ANSWERS,
    SAMPLE_STUDENT_PROFILE,
    get_model_inputs,
    get_missing_required_fields,
    UI_ONLY_KEYS
)

class TestUIPagesAndNavigationV4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictor = get_predictor_v4()

    def test_01_blank_initial_state_and_keys(self):
        """Verify initial answers start completely unselected with no pre-checked defaults."""
        expected_keys = [
            "degree_field", "specific_degree_programme", "other_academic_field",
            "academic_year", "age_group", "ai_usage_freq",
            "ai_time_per_week", "tools_used", "Q20_task_delegation_freq",
            "tasks_delegated", "Q1_direct_use_freq", "Q22_effort_on_ai_answers",
            "Q2_verify_info", "Q3_compare_sources", "Q4_check_accuracy",
            "Q5_understand_reasoning", "Q6_modify_content",
            "Q7_attempt_independently", "Q8_complete_without_ai",
            "Q9_learning_assistant", "Q30_trust_accuracy", "Q33_trust_appropriate_support"
        ]
        for key in expected_keys:
            self.assertIn(key, BLANK_ANSWERS, f"Missing key in BLANK_ANSWERS: {key}")
            self.assertIn(key, DEFAULT_ANSWERS, f"Missing key in DEFAULT_ANSWERS: {key}")

        # Check that no answers are pre-selected
        self.assertIsNone(BLANK_ANSWERS["degree_field"])
        self.assertIsNone(BLANK_ANSWERS["academic_year"])
        self.assertIsNone(BLANK_ANSWERS["age_group"])
        self.assertIsNone(BLANK_ANSWERS["ai_usage_freq"])
        self.assertIsNone(BLANK_ANSWERS["ai_time_per_week"])
        self.assertEqual(BLANK_ANSWERS["tools_used"], [])
        self.assertIsNone(BLANK_ANSWERS["Q20_task_delegation_freq"])
        self.assertEqual(BLANK_ANSWERS["tasks_delegated"], [])
        self.assertIsNone(BLANK_ANSWERS["Q1_direct_use_freq"])
        self.assertIsNone(BLANK_ANSWERS["Q22_effort_on_ai_answers"])

        for k in ["Q2_verify_info", "Q3_compare_sources", "Q4_check_accuracy", "Q5_understand_reasoning", "Q6_modify_content"]:
            self.assertIsNone(BLANK_ANSWERS[k], f"{k} should initially be None")

        for k in ["Q7_attempt_independently", "Q8_complete_without_ai", "Q9_learning_assistant", "Q30_trust_accuracy", "Q33_trust_appropriate_support"]:
            self.assertIsNone(BLANK_ANSWERS[k], f"{k} should initially be None")

        # Verify get_missing_required_fields flags all 19 required fields on blank state
        missing = get_missing_required_fields(BLANK_ANSWERS)
        self.assertEqual(len(missing), 19, f"Expected 19 missing fields on blank state, got {len(missing)}: {missing}")
        print("  ✓ Checkpoint 1: Initial answers are genuinely blank with 19 required questions unselected.")

    def test_02_empty_submission_rejection(self):
        """Verify that an empty or unselected questionnaire submission is blocked and rejected."""
        model_inputs = get_model_inputs(BLANK_ANSWERS)
        res = self.predictor.predict(model_inputs, top_factors_count=5)
        self.assertEqual(res["status"], "validation_error")
        self.assertEqual(res["error_type"], "MissingRequiredInput")
        self.assertIsNone(res["continuous_risk_score"])
        self.assertIsNone(res["predicted_category"])
        print("  ✓ Checkpoint 2: Empty questionnaire submission successfully rejected with validation_error.")

    def test_03_sample_profile_prediction(self):
        """Verify sample student profile has zero missing fields and predicts successfully."""
        missing = get_missing_required_fields(SAMPLE_STUDENT_PROFILE)
        self.assertEqual(len(missing), 0, f"Sample profile has missing required fields: {missing}")

        model_inputs = get_model_inputs(SAMPLE_STUDENT_PROFILE)
        res = self.predictor.predict(model_inputs, top_factors_count=5)
        self.assertEqual(res["status"], "success")
        self.assertIn(res["predicted_category"], ["Low", "Medium", "High"])
        self.assertTrue(1.0 <= res["continuous_risk_score"] <= 5.0)
        self.assertEqual(len(res["top_contributing_factors"]), 5)
        for f in res["top_contributing_factors"]:
            self.assertIn("human_label", f)
            self.assertIn("plain_explanation", f)
            self.assertTrue(len(f["human_label"]) > 0)
            self.assertTrue(len(f["plain_explanation"]) > 0)
        print("  ✓ Checkpoint 3: Complete student profile prediction succeeded with full LinearSHAP enrichment.")

    def test_04_all_presets_execution(self):
        """Verify every benchmark preset executes cleanly without runtime exceptions."""
        for preset_name, preset_payload in PRESETS_DATA.items():
            model_inputs = get_model_inputs(preset_payload)
            res = self.predictor.predict(model_inputs, top_factors_count=5)
            if preset_name == "Simulate Incomplete / Empty Input":
                self.assertEqual(res["status"], "validation_error")
                self.assertEqual(res["error_type"], "MissingRequiredInput")
            else:
                self.assertEqual(res["status"], "success")
                self.assertIn(res["predicted_category"], ["Low", "Medium", "High"])
                self.assertTrue(1.0 <= res["continuous_risk_score"] <= 5.0)
            print(f"  ✓ Preset '{preset_name}': status={res['status']}")

    def test_05_score_range_and_clamping_audit(self):
        """Verify extreme high-risk profile clamps score to 5.000 while preserving raw estimate."""
        extreme_res = self.predictor.predict(get_model_inputs(PRESETS_DATA["High-Risk Student Profile (Extreme)"]))
        self.assertEqual(extreme_res["status"], "success")
        self.assertEqual(extreme_res["predicted_category"], "High")
        self.assertEqual(extreme_res["continuous_risk_score"], 5.0)
        self.assertGreater(extreme_res["raw_regression_score"], 5.0)
        self.assertTrue(any("clamped to 5.000" in w for w in extreme_res["warnings"]))
        print(f"  ✓ Checkpoint 5: Clamping audit verified (clamped: {extreme_res['continuous_risk_score']}, raw: {extreme_res['raw_regression_score']:.3f}).")

    def test_06_academic_field_and_specific_degree_isolation(self):
        """Verify that specific_degree_programme and other_academic_field are preserved in UI state but isolated from model inference."""
        simulated_state = dict(SAMPLE_STUDENT_PROFILE)
        simulated_state["degree_field"] = "Other"
        simulated_state["other_academic_field"] = "Law & Legal Studies"
        simulated_state["specific_degree_programme"] = "Bachelor of Laws (LL.B)"

        self.assertEqual(simulated_state["degree_field"], "Other")
        self.assertEqual(simulated_state["other_academic_field"], "Law & Legal Studies")
        self.assertEqual(simulated_state["specific_degree_programme"], "Bachelor of Laws (LL.B)")

        filtered_payload = get_model_inputs(simulated_state)
        self.assertNotIn("specific_degree_programme", filtered_payload)
        self.assertNotIn("other_academic_field", filtered_payload)
        self.assertIn("degree_field", filtered_payload)

        res = self.predictor.predict(filtered_payload, top_factors_count=5)
        self.assertEqual(res["status"], "success")
        unrecognized_warnings = [
            w for w in res.get("warnings", [])
            if "specific_degree_programme" in w or "other_academic_field" in w
        ]
        self.assertEqual(len(unrecognized_warnings), 0, f"Unrecognized warnings leaked to model: {unrecognized_warnings}")
        print("  ✓ Checkpoint 6: Academic Field and Specific Degree Programme successfully isolated from model payload.")

    def test_07_required_vs_optional_field_validation(self):
        """Verify required fields trigger validation warnings while optional fields do not."""
        # Baseline complete profile
        test_profile = dict(SAMPLE_STUDENT_PROFILE)
        self.assertEqual(len(get_missing_required_fields(test_profile)), 0)

        # Optional fields set to empty/blank -> still valid
        test_profile["specific_degree_programme"] = ""
        test_profile["other_academic_field"] = ""
        test_profile["tasks_delegated"] = []
        self.assertEqual(len(get_missing_required_fields(test_profile)), 0, "Optional fields should not trigger missing required fields.")

        # Omitting each required field triggers a detection
        required_checks = [
            ("degree_field", None),
            ("academic_year", None),
            ("age_group", None),
            ("ai_usage_freq", None),
            ("ai_time_per_week", None),
            ("tools_used", []),
            ("Q20_task_delegation_freq", None),
            ("Q1_direct_use_freq", None),
            ("Q22_effort_on_ai_answers", None),
            ("Q2_verify_info", None),
            ("Q3_compare_sources", None),
            ("Q4_check_accuracy", None),
            ("Q5_understand_reasoning", None),
            ("Q6_modify_content", None),
            ("Q7_attempt_independently", None),
            ("Q8_complete_without_ai", None),
            ("Q9_learning_assistant", None),
            ("Q30_trust_accuracy", None),
            ("Q33_trust_appropriate_support", None),
        ]

        for req_field, blank_val in required_checks:
            mutated = dict(test_profile)
            mutated[req_field] = blank_val
            missing = get_missing_required_fields(mutated)
            self.assertGreaterEqual(len(missing), 1, f"Failed to detect missing required field: {req_field}")
        print("  ✓ Checkpoint 7: Granular required vs. optional validation logic verified across all 19 required questions.")

if __name__ == "__main__":
    unittest.main()
