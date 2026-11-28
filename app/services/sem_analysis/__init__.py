"""
app/services/sem_analysis/__init__.py

Service package for Component 2:
Algorithmic Trust & Verification Analysis (SEM / CFA).

Exports schemas, validation, CFA/SEM analysis pipelines,
visualization generators, reporting services, and individual scoring.
"""

from app.services.sem_analysis.schemas import (
    CONSTRUCTS,
    MODEL_SPECIFICATION,
    PLANNED_MEASUREMENT_METRICS,
    PLANNED_STRUCTURAL_METRICS,
    PLANNED_MODEL_FIT_METRICS,
    SURVEY_ITEMS,
    SURVEY_ITEMS_EMPIRICAL_26,
    SURVEY_ITEMS_LEGACY_19,
    RESEARCH_HYPOTHESES,
    EMPIRICAL_COHORT_BENCHMARKS,
)
from app.services.sem_analysis.status_service import (
    SemStatusService,
    status_service,
)
from app.services.sem_analysis.result_service import (
    SemResultsNotAvailableError,
    SemResultService,
    result_service,
)
from app.services.sem_analysis.dataset_service import (
    validate_dataset,
    validate_and_prepare_dataset,
    compute_descriptive_stats,
    detect_column_mapping,
    filter_informed_consent,
    clean_likert_cell,
)
from app.services.sem_analysis.cfa_service import (
    run_cfa_analysis,
    calculate_cronbach_alpha,
    calculate_htmt,
)
from app.services.sem_analysis.sem_service import (
    run_sem_analysis,
    run_bootstrap_mediation,
)
from app.services.sem_analysis.visualization_service import (
    generate_loadings_chart,
    generate_htmt_heatmap,
    generate_path_diagram,
    generate_effects_comparison_chart,
    generate_student_radar_chart,
    generate_student_quadrant_chart,
)
from app.services.sem_analysis.report_service import (
    generate_results_csv,
    generate_apa_summary,
)
from app.services.sem_analysis.scoring_service import (
    calculate_individual_scores,
)
from app.services.sem_analysis.profile_service import (
    evaluate_behavioral_profile,
)
from app.services.sem_analysis.recommendation_service import (
    generate_recommendations,
)
from app.services.sem_analysis.student_report_service import (
    generate_student_csv_report,
)
from app.services.sem_analysis.verification_task_service import (
    VERIFICATION_SCENARIOS,
    get_sanitized_verification_scenarios,
    get_scenario_by_id,
    evaluate_student_verification,
    grade_explanation_rubric,
    evaluate_explanation_quality,
)
from app.services.sem_analysis.calibration_service import (
    compute_verification_calibration,
)
from app.services.sem_analysis.validation_protocol import (
    VALIDATION_PROTOCOL_SPEC,
    compute_sample_correlation,
    save_pilot_evaluation_record,
    compute_item_difficulty,
    compute_item_discrimination,
    compute_item_discrimination_from_scores,
    compute_completion_time_metrics,
)
from app.services.sem_analysis.combined_report_service import (
    generate_combined_csv_report,
)

__all__ = [
    "CONSTRUCTS",
    "MODEL_SPECIFICATION",
    "PLANNED_MEASUREMENT_METRICS",
    "PLANNED_STRUCTURAL_METRICS",
    "PLANNED_MODEL_FIT_METRICS",
    "SURVEY_ITEMS",
    "SURVEY_ITEMS_EMPIRICAL_26",
    "SURVEY_ITEMS_LEGACY_19",
    "RESEARCH_HYPOTHESES",
    "EMPIRICAL_COHORT_BENCHMARKS",
    "SemStatusService",
    "status_service",
    "SemResultsNotAvailableError",
    "SemResultService",
    "result_service",
    "validate_dataset",
    "validate_and_prepare_dataset",
    "compute_descriptive_stats",
    "detect_column_mapping",
    "filter_informed_consent",
    "clean_likert_cell",
    "run_cfa_analysis",
    "calculate_cronbach_alpha",
    "calculate_htmt",
    "run_sem_analysis",
    "run_bootstrap_mediation",
    "generate_loadings_chart",
    "generate_htmt_heatmap",
    "generate_path_diagram",
    "generate_effects_comparison_chart",
    "generate_student_radar_chart",
    "generate_student_quadrant_chart",
    "generate_results_csv",
    "generate_apa_summary",
    "calculate_individual_scores",
    "evaluate_behavioral_profile",
    "generate_recommendations",
    "generate_student_csv_report",
    "VERIFICATION_SCENARIOS",
    "get_sanitized_verification_scenarios",
    "get_scenario_by_id",
    "evaluate_student_verification",
    "grade_explanation_rubric",
    "evaluate_explanation_quality",
    "compute_verification_calibration",
    "VALIDATION_PROTOCOL_SPEC",
    "compute_sample_correlation",
    "save_pilot_evaluation_record",
    "compute_item_difficulty",
    "compute_item_discrimination",
    "compute_item_discrimination_from_scores",
    "compute_completion_time_metrics",
    "generate_combined_csv_report",
]
