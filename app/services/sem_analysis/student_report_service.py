"""
app/services/sem_analysis/student_report_service.py

Exportable Student Assessment Report Generator for Component 2:
Algorithmic Trust & Verification Analysis.

Generates structured CSV, JSON, and printable narrative summaries of an individual student's
assessment results, construct scores, norm-referenced comparisons, and recommendations.
"""

from typing import Any, Dict, List, Optional
import io
import csv
import json
from datetime import datetime


def generate_student_csv_report(
    scoring_result: Dict[str, Any],
    profile_result: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
    student_meta: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Format individual student assessment findings into an RFC 4180 CSV string.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Header & Metadata
    writer.writerow(["# INDIVIDUAL STUDENT PSYCHOMETRIC ASSESSMENT REPORT"])
    writer.writerow(["# Component 2: Algorithmic Trust & Verification Assessment Framework"])
    writer.writerow(["# Research Project: J26-DS-310 | Psychometric Learning Analytics Framework"])
    writer.writerow(["# Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    if student_meta:
        for k, v in student_meta.items():
            writer.writerow([f"# {k}", v])
    writer.writerow([])

    # 2. Construct Scores Summary
    writer.writerow(["--- SECTION 1: PERSONAL CONSTRUCT SCORES & COHORT NORMS (N=375) ---"])
    writer.writerow([
        "Construct Code", "Construct Name", "Mean Score (1-5)", "Factor Weighted",
        "Cohort Mean", "Cohort Median", "z-score", "T-score", "Percentile Rank", "Quartile Band"
    ])
    scores = scoring_result.get("construct_scores", {})
    for c_code, c in scores.items():
        writer.writerow([
            c_code,
            c.get("name"),
            c.get("mean_score"),
            c.get("weighted_score"),
            c.get("cohort_mean"),
            c.get("cohort_median"),
            c.get("z_score"),
            c.get("t_score"),
            f"{c.get('percentile_rank')}%",
            c.get("quartile_band"),
        ])
    writer.writerow([])

    # 3. Behavioural Profile
    writer.writerow(["--- SECTION 2: EXPLAINABLE BEHAVIOURAL INTERPRETATION ---"])
    writer.writerow(["Profile Title", profile_result.get("profile_title")])
    writer.writerow(["Quadrant", profile_result.get("quadrant_id")])
    writer.writerow(["Summary", profile_result.get("summary")])
    writer.writerow(["SEM Insight", profile_result.get("sem_structural_insights")])
    writer.writerow(["AI Dependence Context", profile_result.get("dependence_context", {}).get("text")])
    writer.writerow(["Confidence Context", profile_result.get("confidence_context", {}).get("text")])
    writer.writerow([])

    # 4. Personalized Recommendations
    writer.writerow(["--- SECTION 3: TRACEABLE EDUCATIONAL RECOMMENDATIONS ---"])
    writer.writerow(["#", "Title", "Construct", "Priority", "Evidence Trigger", "Rationale", "Action Steps"])
    for idx, rec in enumerate(recommendations, start=1):
        steps_str = " | ".join(rec.get("action_steps", []))
        writer.writerow([
            idx,
            rec.get("title"),
            rec.get("construct"),
            rec.get("priority"),
            rec.get("evidence_trace"),
            rec.get("rationale"),
            steps_str,
        ])
    writer.writerow([])

    # 5. Scientific Caveat
    writer.writerow(["--- SECTION 4: SCIENTIFIC & METHODOLOGICAL DISCLAIMERS ---"])
    writer.writerow([
        "Disclaimer",
        "Scores reflect self-reported student ratings on a 5-point Likert scale relative to an empirical undergraduate reference cohort (N=375). They indicate descriptive behavioral tendencies, not objective task performance or clinical risk diagnoses."
    ])

    return output.getvalue()
