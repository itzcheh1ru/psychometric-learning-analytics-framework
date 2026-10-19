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

        df = df.copy()
        df["ai_study_hours"] = pd.to_numeric(
            df["ai_study_hours"],
            errors="coerce"
        )
        df["independent_study_hours"] = pd.to_numeric(
            df["independent_study_hours"],
            errors="coerce"
        )
        df["total_study_hours"] = (
            df["ai_study_hours"]
            + df["independent_study_hours"]
        )
        df = df[
            df["total_study_hours"].gt(0)
            & df["ai_study_hours"].notna()
            & df["independent_study_hours"].notna()
        ]

        if df.empty:
            return []

        result = (
            df.groupby("study_week")
            .agg(
                ai_study_hours=("ai_study_hours", "sum"),
                independent_study_hours=("independent_study_hours", "sum"),
                total_study_hours=("total_study_hours", "sum"),
                records=("study_week", "size"),
                participants=("participant_reference", "nunique"),
            )
            .reset_index()
        )
        result["ai_study_share"] = (
            result["ai_study_hours"]
            / result["total_study_hours"]
            * 100
        )
        result["independent_study_share"] = (
            result["independent_study_hours"]
            / result["total_study_hours"]
            * 100
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
                ),
                records=("prompt_count", "count"),
                participants=("participant_reference", "nunique"),
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

        primary_purposes = df[
            ["study_week", "prompt_purpose"]
        ].copy()
        primary_purposes["_record_id"] = df.index

        purpose_records = [primary_purposes]

        if "other_prompt_purposes" in df.columns:
            other_purposes = df[
                ["study_week", "other_prompt_purposes"]
            ].copy()
            other_purposes["_record_id"] = df.index
            other_purposes["prompt_purpose"] = (
                other_purposes.pop("other_prompt_purposes")
                .fillna("")
                .astype(str)
                .str.split(";")
            )
            other_purposes = other_purposes.explode("prompt_purpose")
            purpose_records.append(
                other_purposes[
                    ["study_week", "prompt_purpose", "_record_id"]
                ]
            )

        purposes = pd.concat(
            purpose_records,
            ignore_index=True
        )
        purposes["prompt_purpose"] = (
            purposes["prompt_purpose"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        purposes = purposes[
            purposes["prompt_purpose"].ne("")
            & purposes["prompt_purpose"].ne("-")
        ].drop_duplicates(
            subset=["study_week", "prompt_purpose", "_record_id"]
        )

        result = (
            purposes.groupby(
                ["study_week", "prompt_purpose"]
            )
            .size()
            .reset_index(name="count")
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

        df = df.sort_values(
            ["participant_reference", "study_week"]
        ).copy()
        df["_previous_study_week"] = (
            df.groupby("participant_reference")["study_week"].shift()
        )
        comparisons = df[
            df["_previous_study_week"].notna()
            & df["study_week"].gt(df["_previous_study_week"])
        ].dropna(
            subset=["study_pattern_shift"]
        )

        if comparisons.empty:
            return []

        result = (
            comparisons.groupby("study_week")
            .agg(
                average_shift=("study_pattern_shift", "mean"),
                median_shift=("study_pattern_shift", "median"),
                records=("study_pattern_shift", "count"),
                participants=("participant_reference", "nunique"),
            )
            .reset_index()
        )

        return result.to_dict(
            orient="records"
        )


analysis_service = LongitudinalAnalysisService()