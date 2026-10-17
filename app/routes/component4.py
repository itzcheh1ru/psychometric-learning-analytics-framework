"""
app/routes/component4.py – Routes for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Endpoints:
  GET  /component4/                       – Interactive prototype UI
  GET  /api/component4/status             – Experimental pipeline status (JSON)
  GET  /api/component4/specification      – Research specification metadata (JSON)
  POST /api/component4/validate-session   – Experimental session prototype validation (JSON)

Status: Prototype – data collection in progress.
        No empirical retention results, mock essays, or simulated statistics.
"""

from flask import Blueprint, jsonify, render_template, request

from app.services.retention import (
    CONDITION_ORDERS,
    CONDITION_COMPARISON_MEASURES,
    EXPERIMENTAL_CONDITIONS,
    LEARNING_OUTCOMES,
    NLP_FEATURES,
    RETENTION_SPECIFICATION,
    SESSION_STAGES,
    RUBRIC_CRITERIA,
    analysis_service,
    validate_experimental_session,
    validate_immediate_recall_counts,
    validate_ownership_effort_ratings,
    validate_rubric_ratings,
    validate_condition_comparison,
)

component4_bp = Blueprint("component4", __name__, url_prefix="/component4")
api_component4_bp = Blueprint("api_component4", __name__, url_prefix="/api/component4")


from app.services.retention.nlp_pipeline import (
    get_corpus_nlp_summary,
    compare_texts,
    analyze_text,
)


# =========================================================================== #
# UI Routes                                                                   #
# =========================================================================== #

@component4_bp.route("/")
def index():
    """
    Component 4 interactive prototype page.
    Renders controlled conditions, counterbalancing, session form, and NLP framework.
    """
    return render_template(
        "components/component4.html",
        conditions=sorted(list(EXPERIMENTAL_CONDITIONS)),
        condition_orders=sorted(list(CONDITION_ORDERS)),
        session_stages=list(SESSION_STAGES),
        outcomes=LEARNING_OUTCOMES,
        nlp_features=NLP_FEATURES,
        rubric_criteria=RUBRIC_CRITERIA,
        comparison_measures=CONDITION_COMPARISON_MEASURES,
        specification=RETENTION_SPECIFICATION,
        model_metrics=analysis_service.get_model_metrics(),
        feature_importances=analysis_service.get_feature_importances(),
        nlp_summary=get_corpus_nlp_summary(),
        recall_summary=analysis_service.get_recall_summary(),
        immediate_recall_metrics=analysis_service.get_immediate_recall_model_metrics(),
        delayed_recall_metrics=analysis_service.get_delayed_recall_model_metrics(),
        research_status=analysis_service.get_status(),
        research_recommendations=analysis_service.get_research_recommendations(),
    )


# =========================================================================== #
# API Routes                                                                  #
# =========================================================================== #

@api_component4_bp.route("/status", methods=["GET"])
def status():
    """
    Return the readiness status of the cognitive retention evaluation pipeline.

    Response:
        200 JSON – pipeline status metadata.
    """
    return jsonify(analysis_service.get_status()), 200


@api_component4_bp.route("/specification", methods=["GET"])
def specification():
    """
    Return the research specification metadata for Component 4.

    Response:
        200 JSON – conditions, outcomes, NLP features, and evaluation criteria.
    """
    return jsonify(RETENTION_SPECIFICATION), 200


@api_component4_bp.route("/validate-session", methods=["POST"])
def validate_session():
    """
    Validate a prototype experimental session record.

    Validates session metadata structure, counterbalancing order, and consent.
    Does NOT calculate learning retention or writing scores.
    Does NOT store or log participant submissions.

    Returns:
        200 JSON – validation success with analysis_ready = False
        400 JSON – validation errors
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "valid": False,
            "status": "invalid",
            "message": "Request body must be valid JSON.",
            "errors": ["No JSON body received."],
        }), 400

    result = validate_experimental_session(data)

    if not result.is_valid:
        return jsonify({
            "valid": False,
            "status": "invalid",
            "message": "Prototype experimental session validation failed.",
            "errors": result.errors,
        }), 400

    return jsonify({
        "valid": True,
        "status": "valid",
        "message": "Prototype experimental session validated successfully.",
        "analysis_ready": False,
        "research_stage": "experimental_data_collection",
        "persistence": False,
        "validated_session": result.sanitized,
    }), 200


@api_component4_bp.route("/preview-immediate-recall", methods=["POST"])
def preview_immediate_recall():
    """Validate and compare manually counted immediate-recall items in memory."""
    data = request.get_json(silent=True)
    result = validate_immediate_recall_counts(data)
    if not result.is_valid:
        return jsonify({
            "valid": False,
            "errors": result.errors,
            "persistence": False,
        }), 400

    brain_count = result.sanitized["brain_only_count"]
    genai_count = result.sanitized["genai_assisted_count"]
    return jsonify({
        "valid": True,
        "analysis_ready": False,
        "persistence": False,
        "preview": {
            "brain_only_count": brain_count,
            "genai_assisted_count": genai_count,
            "difference_genai_minus_brain": genai_count - brain_count,
        },
        "note": "Manual item-count preview only. Values are not saved and are not empirical findings.",
    }), 200


@api_component4_bp.route("/preview-delayed-recall", methods=["POST"])
def preview_delayed_recall():
    """Validate and compare manually counted delayed-recall items in memory."""
    data = request.get_json(silent=True)
    result = validate_immediate_recall_counts(data)
    if not result.is_valid:
        return jsonify({
            "valid": False,
            "errors": result.errors,
            "persistence": False,
        }), 400

    brain_count = result.sanitized["brain_only_count"]
    genai_count = result.sanitized["genai_assisted_count"]
    return jsonify({
        "valid": True,
        "analysis_ready": False,
        "persistence": False,
        "preview": {
            "brain_only_count": brain_count,
            "genai_assisted_count": genai_count,
            "difference_genai_minus_brain": genai_count - brain_count,
        },
        "note": "Manual delayed-recall item-count preview only. Values are not saved and are not empirical findings.",
    }), 200


@api_component4_bp.route("/predict-immediate-recall", methods=["POST"])
def predict_immediate_recall():
    """Return a prototype immediate-recall prediction from a trained regressor."""
    data = request.get_json(silent=True) or {}
    try:
        result = analysis_service.predict_immediate_recall(
            data.get("condition", ""), data.get("features", {})
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify(result), 200


@api_component4_bp.route("/predict-delayed-recall", methods=["POST"])
def predict_delayed_recall():
    """Return a delayed-recall prediction from the saved condition-specific model."""
    data = request.get_json(silent=True) or {}
    try:
        result = analysis_service.predict_delayed_recall(
            data.get("condition", ""), data.get("features", {})
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify(result), 200


@api_component4_bp.route("/preview-ownership-effort", methods=["POST"])
def preview_ownership_effort():
    """Validate paired self-report ratings and return a non-persistent comparison."""
    data = request.get_json(silent=True)
    result = validate_ownership_effort_ratings(data)
    if not result.is_valid:
        return jsonify({
            "valid": False,
            "errors": result.errors,
            "persistence": False,
        }), 400

    ratings = result.sanitized
    return jsonify({
        "valid": True,
        "analysis_ready": False,
        "persistence": False,
        "preview": {
            **ratings,
            "ownership_difference_genai_minus_brain": (
                ratings["genai_assisted_ownership"] - ratings["brain_only_ownership"]
            ),
            "effort_difference_genai_minus_brain": (
                ratings["genai_assisted_effort"] - ratings["brain_only_effort"]
            ),
        },
        "note": "Manual Likert-rating preview only. Values are not saved and are not empirical findings.",
    }), 200


@api_component4_bp.route("/preview-human-rubric", methods=["POST"])
def preview_human_rubric():
    """Return draft rubric means and raw exact-rater agreement without persisting scores."""
    result = validate_rubric_ratings(request.get_json(silent=True))
    if not result.is_valid:
        return jsonify({"valid": False, "errors": result.errors, "persistence": False}), 400

    ratings = result.sanitized
    criteria = [criterion["key"] for criterion in RUBRIC_CRITERIA]
    conditions = ("brain_only", "genai_assisted")
    raters = ("rater_1", "rater_2")
    condition_means = {}
    exact_matches = 0
    pair_count = len(criteria) * len(conditions)

    for condition in conditions:
        values = [
            ratings[criterion][condition][rater]
            for criterion in criteria
            for rater in raters
        ]
        condition_means[condition] = round(sum(values) / len(values), 2)

    for criterion in criteria:
        for condition in conditions:
            exact_matches += int(
                ratings[criterion][condition]["rater_1"]
                == ratings[criterion][condition]["rater_2"]
            )

    difference = round(
        condition_means["genai_assisted"] - condition_means["brain_only"], 2
    )
    return jsonify({
        "valid": True,
        "analysis_ready": False,
        "persistence": False,
        "preview": {
            "brain_only_mean": condition_means["brain_only"],
            "genai_assisted_mean": condition_means["genai_assisted"],
            "difference_genai_minus_brain": difference,
            "exact_agreement_count": exact_matches,
            "agreement_pair_count": pair_count,
            "exact_agreement_percent": round(100 * exact_matches / pair_count, 1),
        },
        "note": "Draft rubric preview only. Exact agreement is descriptive, not a formal inter-rater reliability statistic. Scores are not saved or empirical findings.",
    }), 200


@api_component4_bp.route("/preview-condition-comparison", methods=["POST"])
def preview_condition_comparison():
    """Return independent paired measure differences without saving or combining outcomes."""
    result = validate_condition_comparison(request.get_json(silent=True))
    if not result.is_valid:
        return jsonify({"valid": False, "errors": result.errors, "persistence": False}), 400

    values = result.sanitized
    comparisons = {}
    for measure in CONDITION_COMPARISON_MEASURES:
        key = measure["key"]
        comparisons[key] = {
            "label": measure["label"],
            "unit": measure["unit"],
            "brain_only": values["brain_only"][key],
            "genai_assisted": values["genai_assisted"][key],
            "difference_genai_minus_brain": round(
                values["genai_assisted"][key] - values["brain_only"][key], 2
            ),
        }

    return jsonify({
        "valid": True,
        "analysis_ready": False,
        "persistence": False,
        "combined_score": None,
        "comparisons": comparisons,
        "note": "Paired descriptive prototype only. Values are not saved; no overall score, inferential test, or real research finding is produced.",
    }), 200


@api_component4_bp.route("/model-metrics", methods=["GET"])
def model_metrics():
    """Return trained machine learning evaluation metrics."""
    return jsonify(analysis_service.get_model_metrics()), 200


@api_component4_bp.route("/feature-importance", methods=["GET"])
def feature_importance():
    """Return feature importance rankings for retention risk prediction."""
    return jsonify(analysis_service.get_feature_importances()), 200


@api_component4_bp.route("/predict-risk", methods=["POST"])
def predict_risk():
    """
    Predict cognitive retention risk based on student behavioral inputs.

    Request JSON payload:
        {
            "perceived_ai_dependency_score": 1-5,
            "ga_mental_effort": 1-5,
            "cognitive_ownership_score": 1-5,
            "ga_learning_time_sec": float,
            "ga_immediate_mcq": float
        }
    """
    data = request.get_json(silent=True) or {}
    result = analysis_service.predict_retention_risk(data)
    return jsonify(result), 200


@api_component4_bp.route("/nlp-summary", methods=["GET"])
def nlp_summary():
    """Return aggregated NLP linguistic metrics for the 300 participant research corpus."""
    return jsonify(get_corpus_nlp_summary()), 200


@api_component4_bp.route("/analyze-text", methods=["POST"])
def api_analyze_text():
    """Analyze one anonymous text sample in memory; never persist submitted text."""
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Provide a non-empty text sample."}), 400
    if len(text) > 10000:
        return jsonify({"error": "Text sample must be 10,000 characters or fewer."}), 400

    result = analyze_text(text.strip())
    result.update({
        "status": "prototype_analysis",
        "persistence": False,
        "note": "Text metrics are a lightweight prototype calculation. Submitted text is not stored and results are not empirical research findings.",
    })
    return jsonify(result), 200


@api_component4_bp.route("/compare-nlp", methods=["POST"])
def api_compare_nlp():
    """Compare Condition A (Brain-Only) vs. Condition B (GenAI-Assisted) writing samples."""
    data = request.get_json(silent=True) or {}
    human_text = data.get("human_text", "")
    ai_text = data.get("ai_text", "")
    return jsonify(compare_texts(human_text, ai_text)), 200
