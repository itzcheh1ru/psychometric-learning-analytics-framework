import pandas as pd
import pytest

from app.services.longitudinal.analysis_service import (
    LongitudinalAnalysisService,
)
from app.services.longitudinal.feature_engineering import (
    calculate_shift_index,
    calculate_weekly_changes,
    generate_indicators,
)


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
