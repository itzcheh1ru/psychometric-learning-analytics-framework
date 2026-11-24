"""
app/services/sem_analysis/combined_report_service.py

Combined Psychometric & Verification Performance Assessment Report Generator.
Component 2: Algorithmic Trust & Verification Analysis (J26-DS-310).

Generates RFC 4180 CSV and structured JSON exports integrating:
1. Self-Reported Construct Scores & Cohort Benchmarks (N=375 Reference)
2. Objective Verification Task Performance (Accuracy, Precision, Recall, F1, Rubrics)
3. Calibration & Discrepancy Index (Delta = VB_norm - Task_Accuracy)
4. Dual-Tier Educational Recommendations
5. Transparent Scientific Disclaimers
"""

from typing import Any, Dict, List, Optional
import io
import csv
import json
from datetime import datetime


def generate_combined_csv_report(
    scoring_result: Optional[Dict[str, Any]],
    verification_eval: Dict[str, Any],
    calibration_result: Optional[Dict[str, Any]],
    student_meta: Optional[Dict[str, Any]] = None,
) -> str:
    """Format full combined assessment findings into an RFC 4180 CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Header & Institutional Metadata
    writer.writerow(["# COMBINED PSYCHOMETRIC & VERIFICATION PERFORMANCE ASSESSMENT REPORT"])
    writer.writerow(["# Component 2: Explainable SEM-Informed AI Trust and Verification Assessment Framework"])
    writer.writerow(["# Research Project: J26-DS-310 | Psychometric Learning Analytics Framework"])
    writer.writerow(["# Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    if student_meta:
        for k, v in student_meta.items():
            writer.writerow([f"# {k}", v])
    writer.writerow([])

    # 2. Section 1: Self-Reported Psychometric Constructs (if available)
    if scoring_result and "construct_scores" in scoring_result:
        writer.writerow(["--- SECTION 1: SELF-REPORTED PSYCHOMETRIC CONSTRUCT SCORES (N=375 REFERENCE COHORT) ---"])
        writer.writerow([
            "Construct Code", "Construct Name", "Mean Score (1-5)", "Factor Weighted",
            "Cohort Mean", "Cohort Median", "z-score", "Percentile Rank", "Quartile Band"
        ])
        for c_code, c in scoring_result["construct_scores"].items():
            writer.writerow([
                c_code,
                c.get("name"),
                c.get("mean_score"),
                c.get("weighted_score"),
                c.get("cohort_mean"),
                c.get("cohort_median"),
                c.get("z_score"),
                f"{c.get('percentile_rank')}%",
                c.get("quartile_band"),
            ])
        writer.writerow([])

    # 3. Section 2: Demonstrated Task Performance
    writer.writerow(["--- SECTION 2: DEMONSTRATED VERIFICATION TASK PERFORMANCE ---"])
    summary = verification_eval.get("summary", {})
    writer.writerow(["Metric", "Value", "Benchmark / Range", "Methodological Description"])
    writer.writerow(["Total Claims Evaluated", summary.get("total_claims_evaluated"), "24 Claims across 8 Scenarios", "Controlled academic evaluation items"])
    writer.writerow(["Correct Classifications", summary.get("correct_classifications"), f"{summary.get('total_claims_evaluated')} possible", "Exact matches with expert ground truth"])
    acc_val = summary.get('accuracy_pct')
    if acc_val is None:
        acc_val = round(float(summary.get('accuracy', 0.0)) * 100.0, 1)
    writer.writerow(["Task Classification Accuracy", f"{acc_val}%", ">= 70.0% Mastery Threshold", "Overall proportion of correct classifications"])
    writer.writerow(["Error Detection Recall (Sensitivity)", summary.get("recall"), "0.0 - 1.0 (Target >= 0.75)", "Ability to correctly catch flawed / unsupported claims"])
    writer.writerow(["Discrimination Precision", summary.get("precision"), "0.0 - 1.0 (Target >= 0.75)", "Proportion of flagged errors that were truly flawed"])
    writer.writerow(["False Error Accusations", verification_eval.get("confusion_matrix", {}).get("false_positives"), "Target: 0", "Accurate AI derivations mistakenly rejected"])
    writer.writerow(["Missed AI Errors", verification_eval.get("confusion_matrix", {}).get("false_negatives"), "Target: 0", "Erroneous AI derivations mistakenly accepted"])
    writer.writerow(["F1 Performance Composite", summary.get("f1_score"), "0.0 - 1.0", "Harmonic mean of precision and recall"])
    rub_val = summary.get('rubric_pct')
    if rub_val is None:
        rub_val = 0.0
    writer.writerow(["Explanation Rubric Score", f"{rub_val}%", "0 - 100% (2 pts per claim)", "Quality of written evidence-based justifications"])
    writer.writerow([])

    # 4. Section 3: Calibration & Discrepancy Analysis (if both are present)
    if calibration_result and "metrics" in calibration_result:
        writer.writerow(["--- SECTION 3: METACOGNITIVE CALIBRATION MATRIX ---"])
        c_metrics = calibration_result["metrics"]
        c_zone = calibration_result.get("calibration_zone", {})
        writer.writerow(["Calibration Dimension", "Observed Value", "Interpretation"])
        writer.writerow(["Self-Reported Verification Score (VB)", f"{c_metrics.get('self_reported_vb')}/5.0", f"{c_metrics.get('self_reported_vb_percentile', c_metrics.get('vb_percentile'))}th cohort percentile"])
        writer.writerow(["Normalized VB Index [0, 1]", c_metrics.get("normalized_vb"), "Rescaled: (VB - 1.0) / 4.0"])
        writer.writerow(["Demonstrated Task Accuracy [0, 1]", c_metrics.get("task_accuracy"), f"{c_metrics.get('task_accuracy_pct')}% on practical scenarios"])
        writer.writerow(["Discrepancy Index (Delta)", c_metrics.get("discrepancy_index_delta"), "Delta = Normalized_VB - Task_Accuracy (+ indicates overconfidence risk)"])
        writer.writerow(["Calibration Zone", c_zone.get("title", c_zone.get("zone_title")), c_zone.get("tagline")])
        writer.writerow(["Calibration Summary", calibration_result.get("alignment_summary"), ""])
        writer.writerow(["Trust & Dependence Context", calibration_result.get("trust_dependence_context", {}).get("risk_level"), calibration_result.get("trust_dependence_context", {}).get("narrative")])
        writer.writerow([])

    # 5. Section 4: Scenario-by-Scenario Claim Evaluation Audit
    claim_evals = verification_eval.get("claim_evaluations", [])
    if claim_evals:
        writer.writerow(["--- SECTION 4: SCENARIO-BY-SCENARIO CLAIM EVALUATION AUDIT ---"])
        writer.writerow(["Claim ID", "Statement", "Your Verdict", "Ground Truth", "Evaluation Result", "Rubric Score", "Expert Derivation", "Academic Citation"])
        for ce in claim_evals:
            stmt = ce.get("statement", ce.get("claim_text", ""))
            v_stu = ce.get("student_verdict", ce.get("student_choice", ""))
            v_gt = ce.get("ground_truth", "")
            is_cor = "Correct" if ce.get("is_correct_classification", ce.get("is_correct", False)) else "Incorrect"
            rub_sc = f"{ce.get('rubric_score', 0)}/2"
            exp = ce.get("expert_explanation", "")
            cit = ce.get("reference_citation", ce.get("reference_source", ""))
            writer.writerow([ce.get("claim_id"), stmt, v_stu, v_gt, is_cor, rub_sc, exp, cit])
        writer.writerow([])

    # 6. Section 5: Dual-Tier Educational Recommendations
    writer.writerow(["--- SECTION 5: DUAL-TIER EDUCATIONAL RECOMMENDATIONS ---"])
    writer.writerow(["Tier", "ID", "Title", "Priority", "Evidence Trigger", "Rationale", "Action Steps"])
    
    # Task Performance Feedback
    task_recs = verification_eval.get("performance_feedback", [])
    for r in task_recs:
        steps_str = " | ".join(r.get("action_steps", []))
        writer.writerow([
            "Demonstrated Task Performance",
            r.get("id"),
            r.get("title"),
            r.get("priority"),
            r.get("evidence_trace"),
            r.get("rationale"),
            steps_str,
        ])
    writer.writerow([])

    # 7. Section 6: Scientific & Research Disclaimers
    writer.writerow(["--- SECTION 6: SCIENTIFIC & METHODOLOGICAL DISCLAIMERS ---"])
    writer.writerow([
        "Validation Status",
        "The verification scenarios and answer keys are researcher-designed assessment instruments currently pending formal expert panel review and empirical pilot validation."
    ])
    writer.writerow([
        "Non-Diagnostic Notice",
        "Discrepancy indices and calibration zones reflect exploratory educational feedback, not clinical diagnostic classifications or permanent cognitive traits."
    ])
    writer.writerow([
        "Dataset Independence",
        "Performance data on practical tasks are evaluated independently and are never retroactively inserted into the baseline N=375 cross-sectional SEM survey dataset."
    ])

    return output.getvalue()
