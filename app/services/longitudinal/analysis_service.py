from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "component3_weekly_features.csv"
)


class LongitudinalAnalysisNotAvailableError(RuntimeError):
    """Raised when longitudinal results lack sufficient valid weekly data."""


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
        return self.get_status()["trend_analysis_available"]

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
                "repeated_participants": 0,
                "weeks": 0,
                "records": 0,
            }

        ai_hours = pd.to_numeric(
            df.get("ai_study_hours", pd.Series(index=df.index, dtype="object")),
            errors="coerce",
        )
        independent_hours = pd.to_numeric(
            df.get(
                "independent_study_hours",
                pd.Series(index=df.index, dtype="object"),
            ),
            errors="coerce",
        )
        valid_study_records = df[
            ai_hours.notna()
            & independent_hours.notna()
            & (ai_hours + independent_hours).gt(0)
        ].copy()
        valid_repeats = (
            valid_study_records.groupby("participant_reference")["study_week"]
            .nunique()
            .ge(2)
        )
        repeated_valid_participant_references = set(
            valid_repeats[valid_repeats].index
        )
        study_shifts = pd.to_numeric(
            df.get(
                "study_pattern_shift",
                pd.Series(index=df.index, dtype="object"),
            ),
            errors="coerce",
        )
        participants_with_shift = set(
            df.loc[study_shifts.notna(), "participant_reference"].dropna()
        )
        has_valid_repeated_shift = bool(
            repeated_valid_participant_references
            & participants_with_shift
        )
        prompt_counts = pd.to_numeric(
            df.get("prompt_count", pd.Series(index=df.index, dtype="object")),
            errors="coerce",
        )
        weeks = df["study_week"].nunique()
        participant_week_counts = (
            df.groupby("participant_reference")["study_week"]
            .nunique()
        )
        repeated_participants = int(
            participant_week_counts.ge(2).sum()
        )

        return {
            "component": self.COMPONENT_NAME,
            "dataset_ready": True,
            "trend_analysis_available": has_valid_repeated_shift,
            "prompt_analysis_available": bool(prompt_counts.notna().any()),
            "study_pattern_results_available": has_valid_repeated_shift,
            "participants": int(
                df["participant_reference"].nunique()
            ),
            "repeated_participants": repeated_participants,
            "weeks": int(weeks),
            "records": int(len(df)),
        }

    def get_trends(self):
        """Return weekly study-share trends when valid repeat observations exist."""
        status = self.get_status()
        if not status["trend_analysis_available"]:
            raise LongitudinalAnalysisNotAvailableError(
                "Longitudinal trends are not available until the required "
                "multi-week research dataset has been collected with valid "
                "study-hour observations for the same participants."
            )

        return self.get_weekly_study_share()

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

        participant_shares = (
            df.groupby(["study_week", "participant_reference"])
            .agg(
                ai_study_hours=("ai_study_hours", "sum"),
                independent_study_hours=("independent_study_hours", "sum"),
            )
            .reset_index()
        )
        participant_shares["total_study_hours"] = (
            participant_shares["ai_study_hours"]
            + participant_shares["independent_study_hours"]
        )
        participant_shares = participant_shares[
            participant_shares["total_study_hours"].gt(0)
        ]
        participant_shares["ai_study_share"] = (
            participant_shares["ai_study_hours"]
            / participant_shares["total_study_hours"]
            * 100
        )
        participant_shares["independent_study_share"] = (
            participant_shares["independent_study_hours"]
            / participant_shares["total_study_hours"]
            * 100
        )
        participant_summary = (
            participant_shares.groupby("study_week")
            .agg(
                median_participant_ai_study_share=("ai_study_share", "median"),
                median_participant_independent_study_share=(
                    "independent_study_share",
                    "median",
                ),
                participant_share_n=("participant_reference", "nunique"),
            )
            .reset_index()
        )
        result = result.merge(participant_summary, on="study_week", how="left")

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

        prompt_records = df.copy()
        prompt_records["prompt_count"] = pd.to_numeric(
            prompt_records.get(
                "prompt_count",
                pd.Series(index=prompt_records.index, dtype="object"),
            ),
            errors="coerce",
        )
        weeks = pd.Index(
            sorted(df["study_week"].dropna().unique()),
            name="study_week",
        )
        valid_prompt_records = prompt_records[
            prompt_records["prompt_count"].notna()
        ]
        result = (
            valid_prompt_records.groupby("study_week")
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
            .reindex(weeks)
            .rename_axis("study_week")
            .reset_index()
        )
        result["total_prompts"] = result["total_prompts"].where(
            result["records"].notna()
        )
        result["average_prompts"] = result["average_prompts"].where(
            result["records"].notna()
        )
        result[["records", "participants"]] = (
            result[["records", "participants"]]
            .fillna(0)
            .astype(int)
        )

        records = result.to_dict(orient="records")
        for record in records:
            for field in ("total_prompts", "average_prompts"):
                if pd.isna(record[field]):
                    record[field] = None

        return records

    # ---------------------------------------------------------
    # Weekly self-reported prompt detail
    # ---------------------------------------------------------

    def get_weekly_prompt_detail(self):

        df = self.get_dataset()

        if df.empty or "prompt_detail" not in df:
            return []

        df = df.copy()
        df["prompt_detail"] = pd.to_numeric(
            df["prompt_detail"],
            errors="coerce"
        )
        df = df[df["prompt_detail"].between(1, 5)]

        if df.empty:
            return []

        result = (
            df.groupby("study_week")
            .agg(
                average_prompt_detail=("prompt_detail", "mean"),
                records=("prompt_detail", "count"),
                participants=("participant_reference", "nunique"),
            )
            .reset_index()
        )

        return result.to_dict(orient="records")

    # ---------------------------------------------------------
    # Weekly perceived productivity distribution
    # ---------------------------------------------------------

    def get_weekly_productivity(self):

        df = self.get_dataset()

        if df.empty or "perceived_productivity" not in df:
            return []

        ratings = df[
            ["study_week", "participant_reference", "perceived_productivity"]
        ].copy()
        ratings["perceived_productivity"] = (
            ratings["perceived_productivity"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        ratings = ratings[ratings["perceived_productivity"].ne("")]

        if ratings.empty:
            return []

        result = (
            ratings.groupby(["study_week", "perceived_productivity"])
            .agg(
                records=("participant_reference", "size"),
                participants=("participant_reference", "nunique"),
            )
            .reset_index()
        )
        weekly_totals = result.groupby("study_week")["records"].transform("sum")
        result["percentage"] = result["records"] / weekly_totals * 100

        return result.to_dict(orient="records")

    # ---------------------------------------------------------
    # Weekly study method distribution
    # ---------------------------------------------------------

    def get_weekly_study_methods(self):

        df = self.get_dataset()

        if df.empty or "study_methods" not in df:
            return []

        methods = df[
            ["study_week", "participant_reference", "study_methods"]
        ].copy()
        methods["study_methods"] = (
            methods["study_methods"]
            .fillna("")
            .astype(str)
            .str.split(";")
        )
        valid_method_records = methods[
            methods["study_methods"].map(
                lambda values: any(value.strip() for value in values)
            )
        ].groupby("study_week")["participant_reference"].nunique()
        methods = methods.explode("study_methods")
        methods["study_method"] = methods.pop("study_methods").str.strip()
        methods = methods[methods["study_method"].ne("")]
        methods["_record_id"] = methods.index
        methods = methods.drop_duplicates(
            subset=["study_week", "_record_id", "study_method"]
        )

        if methods.empty:
            return []

        result = (
            methods.groupby(["study_week", "study_method"])
            .agg(
                records=("_record_id", "nunique"),
                participants=("participant_reference", "nunique"),
            )
            .reset_index()
        )
        result["valid_records"] = result["study_week"].map(
            valid_method_records
        )
        result["percentage"] = (
            result["records"] / result["valid_records"] * 100
        )

        return result.to_dict(orient="records")

    # ---------------------------------------------------------
    # Weekly study and prompt activity by workload pressure
    # ---------------------------------------------------------

    def get_weekly_workload_comparison(self):

        df = self.get_dataset()

        if df.empty or "workload_pressure" not in df:
            return []

        comparison = df[
            [
                "study_week",
                "participant_reference",
                "workload_pressure",
                "ai_study_hours",
                "prompt_count",
            ]
        ].copy()
        comparison["workload_pressure"] = (
            comparison["workload_pressure"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        comparison = comparison[
            comparison["workload_pressure"].isin(
                ["Low", "Moderate", "High"]
            )
        ]

        if comparison.empty:
            return []

        for column in ["ai_study_hours", "prompt_count"]:
            comparison[column] = pd.to_numeric(
                comparison[column],
                errors="coerce"
            )

        result = (
            comparison.groupby(["study_week", "workload_pressure"])
            .agg(
                average_ai_study_hours=("ai_study_hours", "mean"),
                average_prompts=("prompt_count", "mean"),
                records=("participant_reference", "count"),
                participants=("participant_reference", "nunique"),
                ai_hours_records=("ai_study_hours", "count"),
                prompt_records=("prompt_count", "count"),
            )
            .reset_index()
        )

        return result.to_dict(orient="records")

    # ---------------------------------------------------------
    # Prompt purpose distribution
    # ---------------------------------------------------------

    def get_prompt_purposes(self):

        df = self.get_dataset()

        if df.empty:
            return []

        primary_purposes = df[
            ["study_week", "participant_reference", "prompt_purpose"]
        ].copy()
        primary_purposes["_record_id"] = df.index

        purpose_records = [primary_purposes]

        if "other_prompt_purposes" in df.columns:
            other_purposes = df[
                ["study_week", "participant_reference", "other_prompt_purposes"]
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
                    [
                        "study_week",
                        "participant_reference",
                        "prompt_purpose",
                        "_record_id",
                    ]
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
            & purposes["prompt_purpose"].ne("No prompts this week")
        ].drop_duplicates(
            subset=["study_week", "prompt_purpose", "_record_id"]
        )

        result = (
            purposes.groupby(
                ["study_week", "prompt_purpose"]
            )
            .agg(
                count=("_record_id", "count"),
                participants=("participant_reference", "nunique"),
                valid_records=("_record_id", "nunique"),
            )
            .reset_index()
        )
        weekly_totals = purposes.groupby("study_week")["_record_id"].nunique()
        result["valid_records"] = result["study_week"].map(weekly_totals)
        result["percentage"] = (
            result["count"] / result["valid_records"] * 100
        )

        return result.to_dict(
            orient="records"
        )

    # ---------------------------------------------------------
    # Weekly measure coverage
    # ---------------------------------------------------------

    def get_weekly_data_coverage(self):

        df = self.get_dataset()

        if df.empty:
            return []

        def text_answered(series):
            return (
                series.fillna("")
                .astype(str)
                .str.strip()
                .ne("")
            )

        def numeric_values(frame, column):
            return pd.to_numeric(
                frame.get(column, pd.Series(index=frame.index, dtype="object")),
                errors="coerce",
            )

        coverage_rows = []
        for study_week, weekly in df.groupby("study_week"):
            weekly_records = len(weekly)
            ai_hours = numeric_values(weekly, "ai_study_hours")
            independent_hours = numeric_values(
                weekly,
                "independent_study_hours",
            )
            study_total = ai_hours + independent_hours
            methods = weekly.get(
                "study_methods",
                pd.Series(index=weekly.index, dtype="object"),
            )
            methods_answered = methods.fillna("").astype(str).str.split(";").map(
                lambda values: any(value.strip() for value in values)
            )
            workload = weekly.get(
                "workload_pressure",
                pd.Series(index=weekly.index, dtype="object"),
            ).fillna("").astype(str).str.strip()
            prompt_detail = numeric_values(weekly, "prompt_detail")
            productivity = weekly.get(
                "perceived_productivity",
                pd.Series(index=weekly.index, dtype="object"),
            )
            activity = weekly.get(
                "learning_activity",
                pd.Series(index=weekly.index, dtype="object"),
            )
            prompt_purpose = weekly.get(
                "prompt_purpose",
                pd.Series(index=weekly.index, dtype="object"),
            )
            prompt_purpose_answered = text_answered(prompt_purpose)

            measures = [
                (
                    "AI vs independent study share",
                    (ai_hours.notna() & independent_hours.notna() & study_total.gt(0)).sum(),
                ),
                ("AI-assisted study hours", ai_hours.notna().sum()),
                (
                    "Independent study hours",
                    independent_hours.notna().sum(),
                ),
                (
                    "AI-supported study sessions",
                    numeric_values(weekly, "ai_sessions").notna().sum(),
                ),
                ("Main academic activity", text_answered(activity).sum()),
                (
                    "Workload / deadline pressure",
                    workload.isin(["Low", "Moderate", "High"]).sum(),
                ),
                ("Study methods", methods_answered.sum()),
                (
                    "Perceived productivity",
                    text_answered(productivity).sum(),
                ),
                (
                    "Academic GenAI prompt count",
                    numeric_values(weekly, "prompt_count").notna().sum(),
                ),
                ("Prompt purpose", prompt_purpose_answered.sum()),
                (
                    "Self-reported prompt detail",
                    prompt_detail.between(1, 5).sum(),
                ),
            ]

            for measure, usable_responses in measures:
                usable_responses = int(usable_responses)
                coverage_rows.append(
                    {
                        "study_week": study_week,
                        "measure": measure,
                        "weekly_records": weekly_records,
                        "usable_responses": usable_responses,
                        "not_available_records": (
                            weekly_records - usable_responses
                        ),
                        "coverage_percent": (
                            usable_responses / weekly_records * 100
                            if weekly_records
                            else 0
                        ),
                    }
                )

        return coverage_rows

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
            comparisons.groupby(
                ["_previous_study_week", "study_week"]
            )
            .agg(
                average_shift=("study_pattern_shift", "mean"),
                median_shift=("study_pattern_shift", "median"),
                records=("study_pattern_shift", "count"),
                participants=("participant_reference", "nunique"),
            )
            .reset_index()
            .rename(
                columns={"_previous_study_week": "previous_study_week"}
            )
        )
        return result.to_dict(
            orient="records"
        )


analysis_service = LongitudinalAnalysisService()