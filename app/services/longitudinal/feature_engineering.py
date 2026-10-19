from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "component3_weekly_clean.csv"
OUTPUT_FILE = PROCESSED_DIR / "component3_weekly_features.csv"


def generate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Component 3 behavioural indicators.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # 1. Convert numerical columns
    # ---------------------------------------------------------

    numeric_columns = [
        "ai_study_hours",
        "independent_study_hours",
        "ai_sessions",
        "prompt_count",
        "prompt_detail",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # ---------------------------------------------------------
    # 2. Total recorded study hours
    # ---------------------------------------------------------

    df["total_recorded_study_hours"] = (
        df["ai_study_hours"]
        + df["independent_study_hours"]
    )

    # ---------------------------------------------------------
    # 3. AI Study Share
    # ---------------------------------------------------------

    valid_total = df["total_recorded_study_hours"] > 0

    df["ai_study_share"] = float("nan")
    df.loc[valid_total, "ai_study_share"] = (
        df.loc[valid_total, "ai_study_hours"]
        / df.loc[valid_total, "total_recorded_study_hours"]
        * 100
    )

    # ---------------------------------------------------------
    # 4. Independent Learning Share
    # ---------------------------------------------------------

    df["independent_study_share"] = float("nan")
    df.loc[valid_total, "independent_study_share"] = (
        df.loc[valid_total, "independent_study_hours"]
        / df.loc[valid_total, "total_recorded_study_hours"]
        * 100
    )

    return df


def calculate_weekly_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate week-to-week behavioural changes
    for each participant.
    """

    df = df.copy()

    # Ensure correct ordering
    df = df.sort_values(
        ["participant_reference", "study_week"]
    ).reset_index(drop=True)

    grouped = df.groupby(
        "participant_reference",
        group_keys=False
    )

    # AI share change
    df["ai_share_change"] = (
        grouped["ai_study_share"].diff()
    )

    # Independent share change
    df["independent_share_change"] = (
        grouped["independent_study_share"].diff()
    )

    # AI hours change
    df["ai_hours_change"] = (
        grouped["ai_study_hours"].diff()
    )

    # Prompt count change
    df["prompt_count_change"] = (
        grouped["prompt_count"].diff()
    )

    return df


def calculate_shift_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate a simple Study Pattern Shift Indicator.

    This is an analytical indicator for the prototype.
    It is NOT presented as a validated psychometric scale.
    """

    df = df.copy()

    df["study_pattern_shift"] = (
        df["ai_share_change"].abs()
        + df["independent_share_change"].abs()
    ) / 2

    return df


def build_feature_dataset():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    print(f"Loading: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Input rows: {len(df)}")

    # Step 1
    df = generate_indicators(df)

    # Step 2
    df = calculate_weekly_changes(df)

    # Step 3
    df = calculate_shift_index(df)

    # Save
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nFeature engineering completed.")

    print(f"Participants: {df['participant_reference'].nunique()}")

    print(
        f"Weeks: "
        f"{sorted(df['study_week'].dropna().unique().tolist())}"
    )

    print(f"Rows: {len(df)}")

    print(f"\nSaved to:")
    print(OUTPUT_FILE)

    return df


if __name__ == "__main__":
    from app.services.longitudinal.prepare_dataset import build_dataset

    build_dataset()
    build_feature_dataset()