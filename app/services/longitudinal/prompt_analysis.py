from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "component3_weekly_features.csv"
)


def load_data():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


def weekly_prompt_frequency(df):

    result = (
        df.groupby("study_week")["prompt_count"]
        .agg(
            total_prompts="sum",
            average_prompts="mean",
            participants="count"
        )
        .reset_index()
    )

    return result


def prompt_purpose_distribution(df):

    result = (
        df.groupby(
            ["study_week", "prompt_purpose"]
        )
        .size()
        .reset_index(
            name="count"
        )
    )

    return result


def prompt_detail_distribution(df):

    if "prompt_detail" not in df.columns:
        return pd.DataFrame()

    result = (
        df.groupby(
            ["study_week", "prompt_detail"]
        )
        .size()
        .reset_index(
            name="count"
        )
    )

    return result


def print_summary():

    df = load_data()

    print("\n========== PROMPT ANALYSIS ==========")

    print("\nWeekly Prompt Frequency:")
    print(
        weekly_prompt_frequency(df)
        .to_string(index=False)
    )

    print("\nPrompt Purpose Distribution:")
    print(
        prompt_purpose_distribution(df)
        .to_string(index=False)
    )

    print("\n======================================")


if __name__ == "__main__":
    print_summary()