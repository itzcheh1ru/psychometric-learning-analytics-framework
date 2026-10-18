from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "component3_weekly_features.csv"
)


class LongitudinalAnalysisService:

    COMPONENT_NAME = (
        "Longitudinal AI-Assisted Study Pattern "
        "Evolution and Prompt Behaviour Analysis"
    )

    def __init__(self):
        self.data_file = DATA_FILE

    # ---------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------

    def get_dataset(self):

        if not self.data_file.exists():
            return pd.DataFrame()

        return pd.read_csv(
            self.data_file
        )

    # ---------------------------------------------------------
    # Check availability
    # ---------------------------------------------------------

    def is_analysis_available(self):

        return self.data_file.exists()

    # ---------------------------------------------------------
    # Dataset status
    # ---------------------------------------------------------

    def get_status(self):

        df = self.get_dataset()

        if df.empty:

            return {
                "component": self.COMPONENT_NAME,
                "dataset_ready": False,
                "trend_analysis_available": False,
                "prompt_analysis_available": False,
                "study_pattern_results_available": False,
                "participants": 0,
                "weeks": 0,
                "records": 0,
            }

        weeks = df["study_week"].nunique()

        return {
            "component": self.COMPONENT_NAME,
            "dataset_ready": True,
            "trend_analysis_available": weeks >= 2,
            "prompt_analysis_available": True,
            "study_pattern_results_available": weeks >= 2,
            "participants": int(
                df["participant_reference"].nunique()
            ),
            "weeks": int(weeks),
            "records": int(len(df)),
        }

    # ---------------------------------------------------------
    # Weekly study share
    # ---------------------------------------------------------

    def get_weekly_study_share(self):

        df = self.get_dataset()

        if df.empty:
            return []

        result = (
            df.groupby("study_week")
            .agg(
                ai_study_share=(
                    "ai_study_share",
                    "mean"
                ),
                independent_study_share=(
                    "independent_study_share",
                    "mean"
                )
            )
            .reset_index()
        )

        return result.to_dict(
            orient="records"
        )

    # ---------------------------------------------------------
    # Weekly study hours
    # ---------------------------------------------------------

    def get_weekly_study_hours(self):

        df = self.get_dataset()

        if df.empty:
            return []

        result = (
            df.groupby("study_week")
            .agg(
                ai_study_hours=(
                    "ai_study_hours",
                    "mean"
                ),
                independent_study_hours=(
                    "independent_study_hours",
                    "mean"
                )
            )
            .reset_index()
        )

        return result.to_dict(
            orient="records"
        )

    # ---------------------------------------------------------
    # Weekly prompt frequency
    # ---------------------------------------------------------

    def get_weekly_prompt_frequency(self):

        df = self.get_dataset()

        if df.empty:
            return []

        result = (
            df.groupby("study_week")
            .agg(
                total_prompts=(
                    "prompt_count",
                    "sum"
                ),
                average_prompts=(
                    "prompt_count",
                    "mean"
                )
            )
            .reset_index()
        )

        return result.to_dict(
            orient="records"
        )

    # ---------------------------------------------------------
    # Prompt purpose distribution
    # ---------------------------------------------------------

    def get_prompt_purposes(self):

        df = self.get_dataset()

        if df.empty:
            return []

        result = (
            df.groupby(
                [
                    "study_week",
                    "prompt_purpose"
                ]
            )
            .size()
            .reset_index(
                name="count"
            )
        )

        return result.to_dict(
            orient="records"
        )

    # ---------------------------------------------------------
    # Study pattern shift
    # ---------------------------------------------------------

    def get_weekly_shift(self):

        df = self.get_dataset()

        if df.empty:
            return []

        result = (
            df.groupby("study_week")
            .agg(
                average_shift=(
                    "study_pattern_shift",
                    "mean"
                )
            )
            .reset_index()
        )

        return result.to_dict(
            orient="records"
        )


analysis_service = LongitudinalAnalysisService()