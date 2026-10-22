from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CONSENT_COLUMN = "Do you agree to participate in this research study?"
CONSENTED_VALUE = "Yes, I agree"


COLUMN_MAP = {
    "Please enter the participant code provided to you.": "participant_reference",

    "Approximately how many hours did you study with GenAI assistance this week?":
        "ai_study_hours",

    "Approximately how many hours did you study independently without GenAI assistance this week?":
        "independent_study_hours",

    "Approximately how many AI-supported study sessions did you complete this week?":
        "ai_sessions",

    "What was your main academic activity this week?":
        "learning_activity",

    "What was the academic workload/deadline pressure this week?":
        "workload_pressure",

    "Which study methods did you mainly use this week?":
        "study_methods",

    "How productive do you feel your studying was this week?":
        "perceived_productivity",

    "Approximately how many academic GenAI prompts did you use this week?":
        "prompt_count",

    "What was the main purpose of your academic GenAI prompts this week?":
        "prompt_purpose",

    "Which other purposes did you also use GenAI for this week?":
        "other_prompt_purposes",

    "Rate the average detail/specificity of your academic prompts this week.":
        "prompt_detail",

}

LEARNING_ACTIVITY_MAP = {
    "coding/programming": "Coding / debugging",
    "assignment": "Assignment work",
    "research": "Reading / research",
    "report writing": "Writing",
    "exam preparation": "Revision / exam preparation",
}

PROMPT_PURPOSE_MAP = {
    "coding/programming": "Coding / debugging",
    "debugging": "Coding / debugging",
    "exam preparation": "Exam revision",
    "writing improvement": "Writing support",
    "caption writing": "Writing support",
    "nothing": "No prompts this week",
    "-": "No prompts this week",
}


def _normalize_category(value, mapping):
    if pd.isna(value):
        return pd.NA

    normalized = str(value).strip()
    if not normalized:
        return pd.NA

    return mapping.get(normalized.casefold(), normalized)


def _normalize_multi_select(value, mapping):
    if pd.isna(value):
        return pd.NA

    normalized_values = []
    for item in str(value).split(";"):
        normalized = _normalize_category(item, mapping)
        if pd.notna(normalized) and normalized not in normalized_values:
            normalized_values.append(normalized)

    return ";".join(normalized_values) if normalized_values else pd.NA


def clean_week_file(
    file_path,
    week_number,
    consented_participant_references=None,
):

    df = pd.read_excel(file_path)
    has_consent_column = CONSENT_COLUMN in df.columns

    if not has_consent_column and consented_participant_references is None:
        raise ValueError(
            f"Required consent column '{CONSENT_COLUMN}' is missing from "
            f"{Path(file_path).name}, and no previously consented participant "
            "references are available; the export cannot be included safely."
        )

    if has_consent_column:
        consented = (
            df[CONSENT_COLUMN]
            .astype("string")
            .str.strip()
            .str.casefold()
            .eq(CONSENTED_VALUE.casefold())
            .fillna(False)
        )
        excluded_consent_count = int((~consented).sum())
        if excluded_consent_count:
            print(
                f"Excluding {excluded_consent_count} non-consenting or "
                f"unconfirmed row(s) from {Path(file_path).name}."
            )
        df = df.loc[consented].copy()

    # Rename only columns that exist
    rename_map = {
        old: new
        for old, new in COLUMN_MAP.items()
        if old in df.columns
    }

    df = df.rename(columns=rename_map)

    # Add week
    df["study_week"] = week_number

    # Keep only useful research variables
    required_columns = [
        "participant_reference",
        "study_week",
        "ai_study_hours",
        "independent_study_hours",
        "ai_sessions",
        "learning_activity",
        "workload_pressure",
        "study_methods",
        "perceived_productivity",
        "prompt_count",
        "prompt_purpose",
        "other_prompt_purposes",
        "prompt_detail",
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = pd.NA

    df = df[required_columns]

    # Clean participant codes
    df["participant_reference"] = (
        df["participant_reference"]
        .astype("string")
        .str.strip()
        .str.upper()
    )
    df["participant_reference"] = df["participant_reference"].replace(
        "",
        pd.NA
    )

    missing_reference_count = int(
        df["participant_reference"].isna().sum()
    )
    if missing_reference_count:
        print(
            f"Excluding {missing_reference_count} row(s) with no participant code "
            f"from {Path(file_path).name}."
        )
        df = df[df["participant_reference"].notna()].copy()

    if not has_consent_column:
        previously_consented = {
            str(reference).strip().upper()
            for reference in consented_participant_references
        }
        eligible = df["participant_reference"].isin(previously_consented)
        excluded_count = int((~eligible).sum())
        if excluded_count:
            print(
                f"Excluding {excluded_count} row(s) from {Path(file_path).name} "
                "without a matching previously consented participant code."
            )
        df = df.loc[eligible].copy()

    duplicate_mask = df.duplicated(
        subset=["participant_reference", "study_week"],
        keep="first"
    )
    duplicate_count = int(duplicate_mask.sum())
    if duplicate_count:
        print(
            f"Excluding {duplicate_count} duplicate participant-week row(s) "
            f"from {Path(file_path).name}; retaining the first source row."
        )
        df = df.loc[~duplicate_mask].copy()

    df["learning_activity"] = df["learning_activity"].apply(
        lambda value: _normalize_category(value, LEARNING_ACTIVITY_MAP)
    )
    df["prompt_purpose"] = df["prompt_purpose"].apply(
        lambda value: _normalize_category(value, PROMPT_PURPOSE_MAP)
    )
    df["other_prompt_purposes"] = df["other_prompt_purposes"].apply(
        lambda value: _normalize_multi_select(value, PROMPT_PURPOSE_MAP)
    )
    df["study_methods"] = (
        df["study_methods"]
        .astype("string")
        .str.split(";")
        .apply(
            lambda methods: ";".join(
                dict.fromkeys(
                    method.strip()
                    for method in methods
                    if method.strip()
                )
            )
            if isinstance(methods, list)
            else pd.NA
        )
    )

    # Convert numerical fields
    numeric_columns = [
        "ai_study_hours",
        "independent_study_hours",
        "ai_sessions",
        "prompt_count",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["prompt_detail"] = pd.to_numeric(
        df["prompt_detail"]
        .astype("string")
        .str.extract(r"^\s*([1-5])", expand=False),
        errors="coerce"
    )

    return df


def build_dataset():

    frames = []
    consented_participant_references = None

    for week in range(1, 7):

        file_path = RAW_DIR / f"Week_{week:02d}_REAL.xlsx"

        if file_path.exists():

            print(f"Loading {file_path.name}")

            week_df = clean_week_file(
                file_path,
                week,
                consented_participant_references,
            )

            frames.append(week_df)
            references_in_week = set(
                week_df["participant_reference"].dropna().astype(str)
            )
            if consented_participant_references is None:
                consented_participant_references = references_in_week
            else:
                consented_participant_references.update(references_in_week)

    if not frames:
        raise FileNotFoundError("No weekly REAL Excel files found.")

    combined = pd.concat(frames, ignore_index=True)

    duplicate_mask = combined.duplicated(
        subset=["participant_reference", "study_week"],
        keep="first"
    )
    duplicate_count = int(duplicate_mask.sum())
    if duplicate_count:
        print(
            f"Excluding {duplicate_count} duplicate participant-week row(s) "
            "across weekly files; retaining the first source row."
        )
        combined = combined.loc[~duplicate_mask].copy()

    output = PROCESSED_DIR / "component3_weekly_clean.csv"

    combined.to_csv(output, index=False)

    print(f"\nSaved: {output}")
    print(f"Rows: {len(combined)}")
    print(
        "Weeks included: "
        f"{sorted(combined['study_week'].dropna().unique().tolist())}"
    )
    print(
        "Participants included: "
        f"{combined['participant_reference'].nunique()}"
    )
    print(
        "Missing workload pressure: "
        f"{int(combined['workload_pressure'].isna().sum())}"
    )
    print(
        "Missing study methods: "
        f"{int(combined['study_methods'].isna().sum())}"
    )
    print(
        "Missing perceived productivity: "
        f"{int(combined['perceived_productivity'].isna().sum())}"
    )
    print(
        "Missing prompt-detail ratings: "
        f"{int(combined['prompt_detail'].isna().sum())}"
    )
    print(
        "Missing AI study hours: "
        f"{int(combined['ai_study_hours'].isna().sum())}"
    )
    print(
        "Missing independent study hours: "
        f"{int(combined['independent_study_hours'].isna().sum())}"
    )
    print(
        "Missing prompt counts: "
        f"{int(combined['prompt_count'].isna().sum())}"
    )

    return combined


if __name__ == "__main__":
    build_dataset()