import pandas as pd
import pytest

from app.services.longitudinal.analysis_service import (
    LongitudinalAnalysisNotAvailableError,
    LongitudinalAnalysisService,
)
from app.services.longitudinal.feature_engineering import (
    calculate_shift_index,
    calculate_weekly_changes,
    generate_indicators,
)
from app.services.longitudinal.prepare_dataset import clean_week_file


def service_with_data(monkeypatch, rows):
    service = LongitudinalAnalysisService()
    monkeypatch.setattr(
        service,
        "get_dataset",
        lambda: pd.DataFrame(rows),
    )
    return service


def test_study_share_is_weighted_and_excludes_zero_hour_records(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "ai_study_hours": 9,
                "independent_study_hours": 1,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "ai_study_hours": 0,
                "independent_study_hours": 30,
            },
            {
                "study_week": 1,
                "participant_reference": "P3",
                "ai_study_hours": 0,
                "independent_study_hours": 0,
            },
        ],
    )

    result = service.get_weekly_study_share()[0]

    assert result["ai_study_share"] == pytest.approx(22.5)
    assert result["independent_study_share"] == pytest.approx(77.5)
    assert result["total_study_hours"] == 40
    assert result["records"] == 2
    assert result["participants"] == 2
    assert result["median_participant_ai_study_share"] == pytest.approx(45)
    assert result["median_participant_independent_study_share"] == pytest.approx(55)
    assert result["participant_share_n"] == 2


def test_study_share_reports_participant_median_alongside_pooled_share(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "ai_study_hours": 9,
                "independent_study_hours": 1,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "ai_study_hours": 0,
                "independent_study_hours": 30,
            },
        ],
    )

    result = service.get_weekly_study_share()[0]

    assert result["ai_study_share"] == pytest.approx(22.5)
    assert result["median_participant_ai_study_share"] == pytest.approx(45)
    assert result["median_participant_independent_study_share"] == pytest.approx(55)


def test_weekly_import_requires_consent_and_normalizes_survey_categories(
    monkeypatch,
):
    from app.services.longitudinal import prepare_dataset

    source = pd.DataFrame(
        [
            {
                prepare_dataset.CONSENT_COLUMN: "Yes, I agree",
                "Please enter the participant code provided to you.": " p01 ",
                "What was your main academic activity this week?": "Assignment",
                "What was the main purpose of your academic GenAI prompts this week?": (
                    "Exam preparation"
                ),
                "Which other purposes did you also use GenAI for this week?": (
                    "Writing improvement;Exam preparation;Writing improvement;"
                ),
                "Which study methods did you mainly use this week?": "Reading;",
            },
            {
                prepare_dataset.CONSENT_COLUMN: "No, I do not agree",
                "Please enter the participant code provided to you.": "P02",
            },
            {
                prepare_dataset.CONSENT_COLUMN: None,
                "Please enter the participant code provided to you.": "P03",
            },
        ]
    )
    monkeypatch.setattr(prepare_dataset.pd, "read_excel", lambda _path: source)

    result = clean_week_file("week.xlsx", 1)

    assert len(result) == 1
    assert result.iloc[0]["participant_reference"] == "P01"
    assert result.iloc[0]["learning_activity"] == "Assignment work"
    assert result.iloc[0]["prompt_purpose"] == "Exam revision"
    assert result.iloc[0]["other_prompt_purposes"] == (
        "Writing support;Exam revision"
    )
    assert result.iloc[0]["study_methods"] == "Reading"


def test_weekly_import_fails_closed_when_consent_question_is_missing(monkeypatch):
    from app.services.longitudinal import prepare_dataset

    monkeypatch.setattr(
        prepare_dataset.pd,
        "read_excel",
        lambda _path: pd.DataFrame(
            {"Please enter the participant code provided to you.": ["P01"]}
        ),
    )

    with pytest.raises(ValueError, match="consent column"):
        clean_week_file("week.xlsx", 1)


def test_build_dataset_uses_week_one_consent_for_follow_up_exports(
    monkeypatch,
    tmp_path,
):
    from app.services.longitudinal import prepare_dataset

    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    (raw_dir / "Week_01_REAL.xlsx").touch()
    (raw_dir / "Week_02_REAL.xlsx").touch()
    monkeypatch.setattr(prepare_dataset, "RAW_DIR", raw_dir)
    monkeypatch.setattr(prepare_dataset, "PROCESSED_DIR", processed_dir)

    week_one = pd.DataFrame(
        [
            {
                prepare_dataset.CONSENT_COLUMN: "Yes, I agree",
                "Please enter the participant code provided to you.": "P01",
                "Approximately how many hours did you study with GenAI assistance this week?": 2,
            },
            {
                prepare_dataset.CONSENT_COLUMN: "No, I do not agree",
                "Please enter the participant code provided to you.": "P02",
                "Approximately how many hours did you study with GenAI assistance this week?": 3,
            },
        ]
    )
    week_two = pd.DataFrame(
        [
            {
                "Please enter the participant code provided to you.": "P01",
                "Approximately how many hours did you study with GenAI assistance this week?": 4,
            },
            {
                "Please enter the participant code provided to you.": "P02",
                "Approximately how many hours did you study with GenAI assistance this week?": 5,
            },
            {
                "Please enter the participant code provided to you.": "P03",
                "Approximately how many hours did you study with GenAI assistance this week?": 6,
            },
        ]
    )
    exports = {
        "Week_01_REAL.xlsx": week_one,
        "Week_02_REAL.xlsx": week_two,
    }
    monkeypatch.setattr(
        prepare_dataset.pd,
        "read_excel",
        lambda path: exports[path.name].copy(),
    )

    result = prepare_dataset.build_dataset()

    assert result[["participant_reference", "study_week"]].to_dict("records") == [
        {"participant_reference": "P01", "study_week": 1},
        {"participant_reference": "P01", "study_week": 2},
    ]
    assert (processed_dir / "component3_weekly_clean.csv").exists()


def test_prompt_frequency_reports_average_totals_and_sample_sizes(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "prompt_count": 10,
            },
            {
                "study_week": 1,
                "participant_reference": "P1",
                "prompt_count": 20,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "prompt_count": 0,
            },
        ],
    )

    result = service.get_weekly_prompt_frequency()[0]

    assert result["total_prompts"] == 30
    assert result["average_prompts"] == pytest.approx(10)
    assert result["records"] == 3
    assert result["participants"] == 2


def test_prompt_frequency_does_not_convert_missing_counts_to_zero(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "prompt_count": None,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "prompt_count": None,
            },
            {
                "study_week": 2,
                "participant_reference": "P1",
                "prompt_count": 0,
            },
        ],
    )

    result = service.get_weekly_prompt_frequency()

    assert result[0] == {
        "study_week": 1,
        "total_prompts": None,
        "average_prompts": None,
        "records": 0,
        "participants": 0,
    }
    assert result[1]["study_week"] == 2
    assert result[1]["total_prompts"] == 0
    assert result[1]["average_prompts"] == 0
    assert result[1]["records"] == 1
    assert result[1]["participants"] == 1


def test_readiness_requires_valid_repeated_study_hour_observations(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "ai_study_hours": 0,
                "independent_study_hours": 0,
                "prompt_count": None,
            },
            {
                "study_week": 2,
                "participant_reference": "P1",
                "ai_study_hours": 4,
                "independent_study_hours": 2,
                "prompt_count": None,
            },
        ],
    )

    status = service.get_status()

    assert status["repeated_participants"] == 1
    assert status["trend_analysis_available"] is False
    assert status["study_pattern_results_available"] is False
    assert status["prompt_analysis_available"] is False
    with pytest.raises(LongitudinalAnalysisNotAvailableError):
        service.get_trends()


def test_readiness_and_trends_require_same_participant_valid_hours_twice(
    monkeypatch,
):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "ai_study_hours": 4,
                "independent_study_hours": 6,
                "prompt_count": 2,
                "study_pattern_shift": None,
            },
            {
                "study_week": 2,
                "participant_reference": "P1",
                "ai_study_hours": 6,
                "independent_study_hours": 4,
                "prompt_count": 5,
                "study_pattern_shift": 20,
            },
        ],
    )

    assert service.get_status()["trend_analysis_available"] is True
    assert service.get_status()["study_pattern_results_available"] is True
    assert len(service.get_trends()) == 2


def test_study_shift_requires_a_repeat_week_and_omits_baseline(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "study_pattern_shift": 0,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "study_pattern_shift": 0,
            },
        ],
    )

    assert service.get_weekly_shift() == []

    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "study_pattern_shift": float("nan"),
            },
            {
                "study_week": 2,
                "participant_reference": "P1",
                "study_pattern_shift": 20,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "study_pattern_shift": float("nan"),
            },
            {
                "study_week": 2,
                "participant_reference": "P2",
                "study_pattern_shift": 10,
            },
        ],
    )

    result = service.get_weekly_shift()

    assert len(result) == 1
    assert result[0]["study_week"] == 2
    assert result[0]["previous_study_week"] == 1
    assert result[0]["average_shift"] == pytest.approx(15)
    assert result[0]["median_shift"] == pytest.approx(15)
    assert result[0]["records"] == 2
    assert result[0]["participants"] == 2


def test_feature_engineering_leaves_baseline_and_zero_hour_shift_missing():
    weekly = pd.DataFrame(
        [
            {
                "participant_reference": "P1",
                "study_week": 1,
                "ai_study_hours": 4,
                "independent_study_hours": 6,
                "ai_sessions": 1,
                "prompt_count": 5,
            },
            {
                "participant_reference": "P1",
                "study_week": 2,
                "ai_study_hours": 6,
                "independent_study_hours": 4,
                "ai_sessions": 1,
                "prompt_count": 6,
            },
            {
                "participant_reference": "P2",
                "study_week": 1,
                "ai_study_hours": 0,
                "independent_study_hours": 0,
                "ai_sessions": 0,
                "prompt_count": 0,
            },
            {
                "participant_reference": "P2",
                "study_week": 2,
                "ai_study_hours": 3,
                "independent_study_hours": 7,
                "ai_sessions": 1,
                "prompt_count": 2,
            },
        ]
    )

    result = calculate_shift_index(
        calculate_weekly_changes(
            generate_indicators(weekly)
        )
    )

    baseline = result[
        result["study_week"] == 1
    ]
    valid_change = result[
        (result["participant_reference"] == "P1")
        & (result["study_week"] == 2)
    ]["study_pattern_shift"].iloc[0]
    invalid_change = result[
        (result["participant_reference"] == "P2")
        & (result["study_week"] == 2)
    ]["study_pattern_shift"].iloc[0]

    assert baseline["study_pattern_shift"].isna().all()
    assert valid_change == pytest.approx(20)
    assert pd.isna(invalid_change)


def test_feature_engineering_preserves_missing_responses():
    weekly = pd.DataFrame(
        [
            {
                "participant_reference": "P1",
                "study_week": 1,
                "ai_study_hours": None,
                "independent_study_hours": 4,
                "ai_sessions": None,
                "prompt_count": None,
            }
        ]
    )

    result = generate_indicators(weekly)

    assert pd.isna(result.loc[0, "ai_study_hours"])
    assert pd.isna(result.loc[0, "ai_sessions"])
    assert pd.isna(result.loc[0, "prompt_count"])
    assert pd.isna(result.loc[0, "ai_study_share"])


def test_prompt_purpose_counts_overlapping_categories_once_per_record(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "prompt_purpose": "Explanation",
                "other_prompt_purposes": "Explanation;Summarisation",
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "prompt_purpose": "Summarisation",
                "other_prompt_purposes": "Explanation",
            },
        ],
    )

    result = {
        row["prompt_purpose"]: row["count"]
        for row in service.get_prompt_purposes()
    }

    assert result == {
        "Explanation": 2,
        "Summarisation": 2,
    }
    rows = service.get_prompt_purposes()
    assert all(row["valid_records"] == 2 for row in rows)
    assert all(row["percentage"] == pytest.approx(100) for row in rows)


def test_study_methods_count_each_selected_method_once_per_record(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "study_methods": "Reading;Reading;AI-guided learning",
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "study_methods": "Reading;Flashcards",
            },
        ],
    )

    result = {
        row["study_method"]: row["records"]
        for row in service.get_weekly_study_methods()
    }

    assert result == {
        "AI-guided learning": 1,
        "Flashcards": 1,
        "Reading": 2,
    }
    rows = service.get_weekly_study_methods()
    assert all(row["valid_records"] == 2 for row in rows)
    assert {row["study_method"]: row["percentage"] for row in rows} == {
        "AI-guided learning": 50,
        "Flashcards": 50,
        "Reading": 100,
    }


def test_productivity_distribution_is_weekly_and_uses_valid_ratings(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "perceived_productivity": "Very productive",
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "perceived_productivity": "Neutral",
            },
            {
                "study_week": 1,
                "participant_reference": "P3",
                "perceived_productivity": "",
            },
        ],
    )

    result = service.get_weekly_productivity()

    assert sum(row["percentage"] for row in result) == pytest.approx(100)
    assert sum(row["records"] for row in result) == 2


def test_prompt_detail_and_workload_comparison_expose_samples(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "prompt_detail": 2,
                "workload_pressure": "High",
                "ai_study_hours": 4,
                "prompt_count": 10,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "prompt_detail": 4,
                "workload_pressure": "High",
                "ai_study_hours": 6,
                "prompt_count": 20,
            },
        ],
    )

    detail = service.get_weekly_prompt_detail()[0]
    workload = service.get_weekly_workload_comparison()[0]

    assert detail["average_prompt_detail"] == pytest.approx(3)
    assert detail["records"] == 2
    assert workload["average_ai_study_hours"] == pytest.approx(5)
    assert workload["average_prompts"] == pytest.approx(15)
    assert workload["ai_hours_records"] == 2
    assert workload["prompt_records"] == 2


def test_weekly_data_coverage_counts_missing_and_unusable_responses(monkeypatch):
    service = service_with_data(
        monkeypatch,
        [
            {
                "study_week": 1,
                "participant_reference": "P1",
                "ai_study_hours": 2,
                "independent_study_hours": 3,
                "workload_pressure": "High",
                "prompt_count": 4,
            },
            {
                "study_week": 1,
                "participant_reference": "P2",
                "ai_study_hours": 0,
                "independent_study_hours": 0,
                "workload_pressure": None,
                "prompt_count": None,
            },
        ],
    )

    coverage = service.get_weekly_data_coverage()
    by_measure = {row["measure"]: row for row in coverage}

    assert by_measure["AI vs independent study share"]["usable_responses"] == 1
    assert by_measure["AI vs independent study share"]["not_available_records"] == 1
    assert by_measure["Workload / deadline pressure"]["usable_responses"] == 1
    assert by_measure["Academic GenAI prompt count"]["not_available_records"] == 1
    assert by_measure["AI vs independent study share"]["coverage_percent"] == 50
