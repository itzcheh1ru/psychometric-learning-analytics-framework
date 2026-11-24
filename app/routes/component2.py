"""
app/routes/component2.py – Routes for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).

Endpoints:
  GET/POST /component2/               – Interactive research prototype dashboard UI
  GET      /api/component2/status     – Model readiness status (JSON)
  GET      /api/component2/specification – Research model specification metadata (JSON)
  POST     /api/component2/upload     – Validate uploaded CSV or Excel survey data
  POST     /api/component2/analyze-cfa – Execute CFA analysis on dataset
  POST     /api/component2/analyze-sem – Execute full SEM & bootstrap mediation
  POST     /api/component2/analyze    – Complete end-to-end CFA + SEM pipeline
  POST     /api/component2/load-demo  – Load validated benchmark synthetic dataset (N=250)
  POST     /api/component2/export     – Export analytical findings (CSV or JSON)
"""

from pathlib import Path
import json
from datetime import datetime
import pandas as pd
from flask import Blueprint, jsonify, render_template, request, Response

from app.services.sem_analysis import (
    CONSTRUCTS,
    MODEL_SPECIFICATION,
    PLANNED_MEASUREMENT_METRICS,
    PLANNED_MODEL_FIT_METRICS,
    PLANNED_STRUCTURAL_METRICS,
    SURVEY_ITEMS,
    SURVEY_ITEMS_EMPIRICAL_26,
    RESEARCH_HYPOTHESES,
    EMPIRICAL_COHORT_BENCHMARKS,
    status_service,
    validate_dataset,
    validate_and_prepare_dataset,
    run_cfa_analysis,
    run_sem_analysis,
    generate_loadings_chart,
    generate_htmt_heatmap,
    generate_path_diagram,
    generate_effects_comparison_chart,
    generate_student_radar_chart,
    generate_student_quadrant_chart,
    generate_results_csv,
    generate_apa_summary,
    calculate_individual_scores,
    evaluate_behavioral_profile,
    generate_recommendations,
    generate_student_csv_report,
    VERIFICATION_SCENARIOS,
    get_sanitized_verification_scenarios,
    get_scenario_by_id,
    evaluate_student_verification,
    compute_verification_calibration,
    VALIDATION_PROTOCOL_SPEC,
    save_pilot_evaluation_record,
    generate_combined_csv_report,
)

component2_bp = Blueprint("component2", __name__, url_prefix="/component2")
api_component2_bp = Blueprint("api_component2", __name__, url_prefix="/api/component2")

DEMO_DATASET_PATH = Path("data/demo/component2_survey_synthetic.csv")


def execute_pipeline(file_storage_or_df, is_demo=False, custom_mapping=None):
    """Helper to run the full CFA and SEM analysis pipeline."""
    prep = validate_and_prepare_dataset(file_storage_or_df, custom_mapping=custom_mapping)
    cleaned_df = prep["cleaned_data"]
    sample_size = prep["valid_rows"]

    cfa_results = run_cfa_analysis(cleaned_df)
    sem_results = run_sem_analysis(cleaned_df, n_bootstraps=300)

    loadings_chart = generate_loadings_chart(cfa_results)
    htmt_heatmap = generate_htmt_heatmap(cfa_results)
    path_diagram = generate_path_diagram(sem_results)
    effects_chart = generate_effects_comparison_chart(sem_results)

    apa_text = generate_apa_summary(cfa_results, sem_results, sample_size)
    csv_report = generate_results_csv(cfa_results, sem_results, prep["descriptive_statistics"])

    return {
        "success": True,
        "is_demo": is_demo,
        "dataset_summary": {k: v for k, v in prep.items() if k != "cleaned_data"},
        "cfa_results": cfa_results,
        "sem_results": sem_results,
        "charts": {
            "loadings": loadings_chart,
            "htmt": htmt_heatmap,
            "path_diagram": path_diagram,
            "effects_chart": effects_chart,
        },
        "apa_summary": apa_text,
        "csv_report": csv_report,
        "message": "CFA and SEM statistical models successfully estimated from empirical data.",
    }


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@component2_bp.route("", methods=["GET", "POST"], strict_slashes=False)
@component2_bp.route("/", methods=["GET", "POST"], strict_slashes=False)
def index():
    """
    Component 2 interactive research prototype and analysis dashboard page.
    Renders initial awaiting-data interface by default (preserving research integrity
    and contract tests). When requested via demo=1 or file upload POST, renders
    the full empirical analysis directly in the template.
    """
    is_analyzed = False
    analysis_data = None
    upload_error = None

    # Check if demonstration dataset analysis is requested via query param
    demo_param = request.args.get("demo", "").lower() in ("1", "true", "yes")

    if demo_param and DEMO_DATASET_PATH.exists():
        try:
            df = pd.read_csv(DEMO_DATASET_PATH)
            analysis_data = execute_pipeline(df, is_demo=True)
            is_analyzed = True
        except Exception as exc:
            upload_error = f"Error computing demonstration analysis: {str(exc)}"

    elif request.method == "POST":
        # Form submission upload
        if "file" in request.files and request.files["file"].filename:
            try:
                uploaded_file = request.files["file"]
                analysis_data = execute_pipeline(uploaded_file, is_demo=False)
                is_analyzed = True
            except Exception as exc:
                upload_error = f"Error processing uploaded file: {str(exc)}"
        elif request.form.get("use_demo") == "true" and DEMO_DATASET_PATH.exists():
            try:
                df = pd.read_csv(DEMO_DATASET_PATH)
                analysis_data = execute_pipeline(df, is_demo=True)
                is_analyzed = True
            except Exception as exc:
                upload_error = f"Error computing demonstration analysis: {str(exc)}"

    return render_template(
        "components/component2.html",
        constructs=CONSTRUCTS,
        items=SURVEY_ITEMS_EMPIRICAL_26,
        hypotheses=RESEARCH_HYPOTHESES,
        specification=MODEL_SPECIFICATION,
        measurement_metrics=PLANNED_MEASUREMENT_METRICS,
        structural_metrics=PLANNED_STRUCTURAL_METRICS,
        model_fit_metrics=PLANNED_MODEL_FIT_METRICS,
        is_analyzed=is_analyzed,
        analysis_data=analysis_data,
        upload_error=upload_error,
    )


@component2_bp.route("/assessment", methods=["GET"])
def student_assessment():
    """
    Component 2 Personalized Student Assessment Interface.
    Presents the validated 26-item questionnaire, real-time progress tracking,
    and renders the explainable behavioural profile & recommendations.
    """
    # Group empirical items by construct for structured UI rendering
    grouped_items = {}
    for c in CONSTRUCTS:
        code = c["code"]
        grouped_items[code] = {
            "code": code,
            "name": c["name"],
            "description": c["description"],
            "items": [],
        }

    # Item dimension subtitles for clean UX
    dimensions = {
        "AT1": "Information Reliability", "AT2": "Output Consistency", "AT3": "Factual Accuracy",
        "AT4": "Explanation Quality", "AT5": "Problem Solving", "AT6": "Coursework Advice",
        "VB1": "Academic Scrutiny", "VB2": "Source Triangulation", "VB3": "Fact Checking",
        "VB4": "Logic Inspection", "VB5": "Cross-Referencing",
        "PU1": "Learning Efficiency", "PU2": "Concept Clarity", "PU3": "Study Productivity",
        "PU4": "Academic Performance", "PU5": "Study Scaffolding",
        "AD1": "Task Reliance", "AD2": "Frequent Dependence", "AD3": "Assisted Solving",
        "AD4": "Process Integration", "AD5": "Unassisted Difficulty",
        "LC1": "Learning Capability", "LC2": "Problem Self-Efficacy", "LC3": "Task Mastery",
        "LC4": "Academic Retention", "LC5": "Complex Concepts",
    }

    for item_code, item_data in SURVEY_ITEMS_EMPIRICAL_26.items():
        c = item_data["construct"]
        if c in grouped_items:
            grouped_items[c]["items"].append({
                "code": item_code,
                "text": item_data.get("wording") or item_data.get("text", ""),
                "construct": c,
                "dimension": dimensions.get(item_code, "Psychometric Indicator"),
            })

    return render_template(
        "components/component2_assessment.html",
        constructs=CONSTRUCTS,
        grouped_items=grouped_items,
        items=SURVEY_ITEMS_EMPIRICAL_26,
        benchmarks=EMPIRICAL_COHORT_BENCHMARKS,
    )


@component2_bp.route("/verification-task", methods=["GET"])
def verification_task():
    """
    Component 2 Practical AI Verification Performance Assessment Interface.
    Renders controlled academic evaluation scenarios with claim-level
    classification controls and evidence justification fields.
    """
    scenarios = get_sanitized_verification_scenarios()
    return render_template(
        "components/component2_verification.html",
        scenarios=scenarios,
        total_scenarios=len(scenarios),
        protocol_spec=VALIDATION_PROTOCOL_SPEC,
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_component2_bp.route("/status", methods=["GET"])
def status():
    """Return the current readiness status of the SEM analysis pipeline."""
    return jsonify(status_service.get_status()), 200


@api_component2_bp.route("/specification", methods=["GET"])
def specification():
    """Return the research model specification metadata."""
    return jsonify(MODEL_SPECIFICATION), 200


@api_component2_bp.route("/upload", methods=["POST"])
def upload_dataset_route():
    """Validate an uploaded CSV or Excel survey dataset and return full analysis."""
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "Please select a dataset file."
        }), 400

    uploaded_file = request.files["file"]
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({
            "success": False,
            "error": "Please select a dataset file."
        }), 400

    try:
        payload = execute_pipeline(uploaded_file, is_demo=False)
        # Include top-level fields for backwards-compatibility with simple validation clients
        payload["rows"] = payload["dataset_summary"]["rows"]
        payload["valid_rows"] = payload["dataset_summary"]["valid_rows"]
        payload["columns"] = payload["dataset_summary"]["columns"]
        payload["all_items_mapped"] = payload["dataset_summary"]["all_items_mapped"]
        payload["missing_values"] = payload["dataset_summary"]["missing_values"]
        payload["duplicate_rows"] = payload["dataset_summary"]["duplicate_rows"]
        payload["sensitive_columns_detected"] = payload["dataset_summary"]["sensitive_columns_detected"]
        return jsonify(payload), 200

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"Validation and analysis error: {str(exc)}"
        }), 500


@api_component2_bp.route("/analyze", methods=["POST"])
def analyze_full_pipeline():
    """Execute full CFA and SEM analysis on uploaded file or benchmark dataset."""
    is_demo = False
    custom_mapping = None

    if "custom_mapping" in request.form:
        try:
            custom_mapping = json.loads(request.form["custom_mapping"])
        except Exception:
            custom_mapping = None

    if "file" in request.files and request.files["file"].filename:
        file_storage = request.files["file"]
        is_demo = False
    elif request.form.get("use_demo") == "true":
        if not DEMO_DATASET_PATH.exists():
            return jsonify({
                "success": False,
                "error": "Demonstration dataset not found on server."
            }), 404
        file_storage = pd.read_csv(DEMO_DATASET_PATH)
        is_demo = True
    else:
        return jsonify({
            "success": False,
            "error": "No file uploaded and use_demo was not specified."
        }), 400

    try:
        response_payload = execute_pipeline(file_storage, is_demo=is_demo, custom_mapping=custom_mapping)
        return jsonify(response_payload), 200

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"Statistical estimation error: {str(exc)}"
        }), 500


@api_component2_bp.route("/load-demo", methods=["POST"])
def load_demo():
    """Load and analyze the validated synthetic benchmark dataset (N=250)."""
    if not DEMO_DATASET_PATH.exists():
        return jsonify({
            "success": False,
            "error": "Demonstration dataset not found."
        }), 404

    try:
        df = pd.read_csv(DEMO_DATASET_PATH)
        payload = execute_pipeline(df, is_demo=True)
        return jsonify(payload), 200

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"Error loading demonstration dataset: {str(exc)}"
        }), 500


@api_component2_bp.route("/export", methods=["POST"])
def export_results():
    """Export analytical results as a downloadable CSV or JSON file."""
    data = request.get_json(silent=True) or {}
    export_format = data.get("format", "csv").lower()
    csv_content = data.get("csv_content", "")

    if export_format == "csv":
        if not csv_content:
            return jsonify({"success": False, "error": "No CSV content provided to export."}), 400
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=Component2_SEM_Results.csv"}
        )
    elif export_format == "json":
        return Response(
            json.dumps(data, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=Component2_SEM_Results.json"}
        )
    else:
        return jsonify({"success": False, "error": "Supported formats are 'csv' and 'json'."}), 400


# =========================================================================== #
# Personalized Student Assessment API Endpoints                               #
# =========================================================================== #

@api_component2_bp.route("/questionnaire", methods=["GET"])
def get_questionnaire():
    """
    Return the 26 validated empirical questionnaire items grouped by construct,
    along with 5-point Likert response scale anchors and instructions.
    """
    grouped = {}
    for c in CONSTRUCTS:
        code = c["code"]
        grouped[code] = {
            "code": code,
            "name": c["name"],
            "description": c["description"],
            "items": [],
        }

    dimensions = {
        "AT1": "Information Reliability", "AT2": "Output Consistency", "AT3": "Factual Accuracy",
        "AT4": "Explanation Quality", "AT5": "Problem Solving", "AT6": "Coursework Advice",
        "VB1": "Academic Scrutiny", "VB2": "Source Triangulation", "VB3": "Fact Checking",
        "VB4": "Logic Inspection", "VB5": "Cross-Referencing",
        "PU1": "Learning Efficiency", "PU2": "Concept Clarity", "PU3": "Study Productivity",
        "PU4": "Academic Performance", "PU5": "Study Scaffolding",
        "AD1": "Task Reliance", "AD2": "Frequent Dependence", "AD3": "Assisted Solving",
        "AD4": "Process Integration", "AD5": "Unassisted Difficulty",
        "LC1": "Learning Capability", "LC2": "Problem Self-Efficacy", "LC3": "Task Mastery",
        "LC4": "Academic Retention", "LC5": "Complex Concepts",
    }

    for item_code, item_data in SURVEY_ITEMS_EMPIRICAL_26.items():
        c = item_data["construct"]
        if c in grouped:
            grouped[c]["items"].append({
                "code": item_code,
                "text": item_data.get("wording") or item_data.get("text", ""),
                "construct": c,
                "dimension": dimensions.get(item_code, "Psychometric Indicator"),
            })

    return jsonify({
        "success": True,
        "total_items": len(SURVEY_ITEMS_EMPIRICAL_26),
        "scale": [
            {"value": 1, "label": "Strongly Disagree"},
            {"value": 2, "label": "Disagree"},
            {"value": 3, "label": "Neutral / Undecided"},
            {"value": 4, "label": "Agree"},
            {"value": 5, "label": "Strongly Agree"},
        ],
        "constructs": grouped,
        "instructions": (
            "Please rate each statement based on your actual study habits and experience with Generative AI tools (e.g., ChatGPT, Claude, Gemini) during your academic coursework."
        ),
    }), 200


@api_component2_bp.route("/assess", methods=["POST"])
def assess_student():
    """
    Evaluate an individual student's questionnaire responses.
    Validates all 26 Likert indicators, computes unweighted and weighted
    construct scores, evaluates continuous behavioural profile, and generates
    traceable educational recommendations and visualizations.
    """
    if request.is_json:
        data = request.get_json(silent=True) or {}
        raw_responses = data.get("responses", {})
        student_id = data.get("student_id", "Anonymous Student")
    else:
        raw_responses = request.form.to_dict()
        student_id = raw_responses.pop("student_id", "Anonymous Student")

    if not raw_responses:
        return jsonify({
            "success": False,
            "error": "No questionnaire responses provided. Please complete all 26 survey items."
        }), 400

    # Validate that required empirical indicators are present and valid
    expected_items = list(SURVEY_ITEMS_EMPIRICAL_26.keys())
    missing_items = [item for item in expected_items if item not in raw_responses]
    if missing_items:
        return jsonify({
            "success": False,
            "error": f"Incomplete questionnaire. Missing {len(missing_items)} items: {', '.join(missing_items[:5])}{'...' if len(missing_items) > 5 else ''}",
            "missing_items": missing_items,
        }), 400

    # Validate Likert scale range (1-5)
    cleaned_responses = {}
    invalid_items = []
    for item in expected_items:
        val = raw_responses.get(item)
        try:
            num_val = float(val)
            if num_val < 1.0 or num_val > 5.0:
                invalid_items.append((item, val))
            else:
                cleaned_responses[item] = num_val
        except (ValueError, TypeError):
            invalid_items.append((item, val))

    if invalid_items:
        return jsonify({
            "success": False,
            "error": f"Invalid Likert response values (must be 1-5): {', '.join([f'{k}={v}' for k, v in invalid_items[:5]])}",
            "invalid_items": [k for k, _ in invalid_items],
        }), 400

    try:
        # 1. Compute Individual Scores & Cohort Benchmarks
        scoring_result = calculate_individual_scores(cleaned_responses)
        construct_scores = scoring_result["construct_scores"]

        # 2. Evaluate Continuous Behavioural Profile
        profile_result = evaluate_behavioral_profile(construct_scores)

        # 3. Generate Traceable Educational Recommendations
        recommendations = generate_recommendations(construct_scores, cleaned_responses)

        # 4. Generate Interactive Visualizations
        radar_chart = generate_student_radar_chart(construct_scores)
        at_score = construct_scores["AT"]["mean_score"]
        vb_score = construct_scores["VB"]["mean_score"]
        ad_score = construct_scores["AD"]["mean_score"]
        quadrant_chart = generate_student_quadrant_chart(at_score, vb_score, ad_score)

        return jsonify({
            "success": True,
            "student_id": student_id,
            "scoring": scoring_result,
            "profile": profile_result,
            "recommendations": recommendations,
            "charts": {
                "radar": radar_chart,
                "quadrant": quadrant_chart,
            },
            "disclaimer": (
                "Descriptive Self-Report Assessment: This report reflects individual perceptions measured on a 5-point Likert scale. "
                "Construct scores and behavioural profiles are referenced against an empirical undergraduate student cohort (N=375) "
                "and represent self-reported study habits, not objective task performance or clinical psychological diagnoses."
            ),
        }), 200

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"Error computing assessment: {str(exc)}"
        }), 500


@api_component2_bp.route("/student-report", methods=["POST"])
def student_report_export():
    """Export individual student assessment report as RFC 4180 CSV or JSON."""
    data = request.get_json(silent=True) or {}
    export_format = data.get("format", "csv").lower()
    scoring_result = data.get("scoring_result")
    profile_result = data.get("profile_result")
    recommendations = data.get("recommendations", [])
    student_meta = data.get("student_meta", {})

    if not scoring_result or not profile_result:
        return jsonify({
            "success": False,
            "error": "Assessment scoring and profile results are required for export."
        }), 400

    if export_format == "csv":
        csv_text = generate_student_csv_report(scoring_result, profile_result, recommendations, student_meta)
        return Response(
            csv_text,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=Student_AI_Trust_Assessment_Report.csv"}
        )
    elif export_format == "json":
        export_payload = {
            "title": "Student AI Trust and Verification Assessment Report",
            "component": "Component 2: Algorithmic Trust & Verification Analysis",
            "scoring": scoring_result,
            "profile": profile_result,
            "recommendations": recommendations,
            "meta": student_meta,
        }
        return Response(
            json.dumps(export_payload, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=Student_AI_Trust_Assessment_Report.json"}
        )
    else:
        return jsonify({"success": False, "error": "Supported formats are 'csv' and 'json'."}), 400


@api_component2_bp.route("/verification-scenarios", methods=["GET"])
def api_verification_scenarios():
    """Return sanitized scenario bank (with ground-truth answer keys masked) for student testing."""
    scenarios = get_sanitized_verification_scenarios()
    return jsonify({
        "success": True,
        "count": len(scenarios),
        "scenarios": scenarios,
    }), 200


@api_component2_bp.route("/evaluate-verification", methods=["POST"])
def api_evaluate_verification():
    """
    Evaluate submitted claim classifications and evidence justifications against expert keys.
    Computes multidimensional metrics and metacognitive calibration if survey scores are provided.
    """
    data = request.get_json(silent=True) or {}
    submissions = data.get("submissions", [])
    student_id = data.get("student_id", "ANON_STUDENT")
    consent_data = bool(data.get("consent_research_data", False))
    scoring_result = data.get("scoring_result")

    if not submissions:
        return jsonify({
            "success": False,
            "error": "No scenario submissions received for evaluation."
        }), 400

    try:
        # 1. Evaluate verification task performance
        eval_result = evaluate_student_verification(submissions, student_id=student_id)

        # 2. Compute calibration if survey scoring result is provided
        calibration_result = None
        if scoring_result and isinstance(scoring_result, dict) and "construct_scores" in scoring_result:
            calibration_result = compute_verification_calibration(
                construct_scores=scoring_result["construct_scores"],
                task_performance=eval_result,
            )

        # 3. Privacy-preserving pilot data logging (only if explicit consent granted)
        log_payload = {
            "student_id": student_id,
            "summary": eval_result.get("summary", {}),
            "calibration": calibration_result or {},
            "claim_evaluations": eval_result.get("claim_evaluations", []),
        }
        storage_status = save_pilot_evaluation_record(log_payload, consent_given=consent_data)

        return jsonify({
            "success": True,
            "student_id": student_id,
            "verification_evaluation": eval_result,
            "calibration": calibration_result,
            "storage_status": storage_status,
            "consent_recorded": consent_data,
        }), 200

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"Error evaluating verification submission: {str(exc)}"
        }), 500


@api_component2_bp.route("/combined-report", methods=["POST"])
def api_combined_report_export():
    """Export comprehensive combined psychometric and verification report (CSV or JSON)."""
    data = request.get_json(silent=True) or {}
    export_format = data.get("format", "csv").lower()
    scoring_result = data.get("scoring_result")
    verification_eval = data.get("verification_eval")
    calibration_result = data.get("calibration_result")
    student_meta = data.get("student_meta", {})

    if not verification_eval:
        return jsonify({
            "success": False,
            "error": "Verification evaluation results are required to generate the combined report."
        }), 400

    if export_format == "csv":
        csv_text = generate_combined_csv_report(
            scoring_result=scoring_result,
            verification_eval=verification_eval,
            calibration_result=calibration_result,
            student_meta=student_meta,
        )
        return Response(
            csv_text,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=Combined_AI_Trust_and_Verification_Report.csv"}
        )
    elif export_format == "json":
        combined_payload = {
            "title": "Combined Psychometric & AI Verification Performance Report",
            "component": "Component 2: Algorithmic Trust & Verification Analysis",
            "project": "J26-DS-310",
            "generated_at": datetime.now().isoformat(),
            "meta": student_meta,
            "survey_scoring": scoring_result,
            "verification_performance": verification_eval,
            "calibration_analysis": calibration_result,
        }
        return Response(
            json.dumps(combined_payload, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=Combined_AI_Trust_and_Verification_Report.json"}
        )
    else:
        return jsonify({"success": False, "error": "Supported formats are 'csv' and 'json'."}), 400


@api_component2_bp.route("/validation-protocol", methods=["GET"])
def api_validation_protocol():
    """Return the formal empirical validation protocol and study design specification."""
    return jsonify({
        "success": True,
        "protocol": VALIDATION_PROTOCOL_SPEC,
    }), 200
