import pandas as pd


def generate_indicators(df):

    df = df.copy()

    # Total recorded study time
    df["total_recorded_study_hours"] = (
        df["ai_study_hours"].fillna(0)
        + df["independent_study_hours"].fillna(0)
    )

    # Avoid division by zero
    valid_total = df["total_recorded_study_hours"] > 0

    df["ai_study_share"] = 0.0
    df["independent_study_share"] = 0.0

    df.loc[valid_total, "ai_study_share"] = (
        df.loc[valid_total, "ai_study_hours"]
        / df.loc[valid_total, "total_recorded_study_hours"]
        * 100
    )

    df.loc[valid_total, "independent_study_share"] = (
        df.loc[valid_total, "independent_study_hours"]
        / df.loc[valid_total, "total_recorded_study_hours"]
        * 100
    )

    return df