from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


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
        "academic_period",

    "Approximately how many academic GenAI prompts did you use this week?":
        "prompt_count",

    "What was the main purpose of your academic GenAI prompts this week?":
        "prompt_purpose",

    "Which other purposes did you also use GenAI for this week?":
        "other_prompt_purposes",

    "Rate the average detail/specificity of your academic prompts this week.":
        "prompt_detail",

    "Optional: Please provide up to three examples of what you typed/asked GenAI (your prompts only — not the AI's response) during this week.":
        "prompt_text",
}


def clean_week_file(file_path, week_number):

    df = pd.read_excel(file_path)

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
        "academic_period",
        "prompt_count",
        "prompt_purpose",
        "other_prompt_purposes",
        "prompt_detail",
        "prompt_text",
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

    # Convert numerical fields
    numeric_columns = [
        "ai_study_hours",
        "independent_study_hours",
        "ai_sessions",
        "prompt_count",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def build_dataset():

    frames = []

    for week in range(1, 7):

        file_path = RAW_DIR / f"Week_{week:02d}_REAL.xlsx"

        if file_path.exists():

            print(f"Loading {file_path.name}")

            week_df = clean_week_file(file_path, week)

            frames.append(week_df)

    if not frames:
        raise FileNotFoundError("No weekly REAL Excel files found.")

    combined = pd.concat(frames, ignore_index=True)

    output = PROCESSED_DIR / "component3_weekly_clean.csv"

    combined.to_csv(output, index=False)

    print(f"\nSaved: {output}")
    print(f"Rows: {len(combined)}")

    return combined


if __name__ == "__main__":
    build_dataset()