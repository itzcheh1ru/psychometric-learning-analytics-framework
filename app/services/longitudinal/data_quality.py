import pandas as pd


def validate_dataset(df):

    print("\n===== DATA QUALITY REPORT =====")

    print("\nRows:", len(df))

    print("\nUnique participants:",
          df["participant_reference"].nunique())

    print("\nWeeks:")
    print(df["study_week"].value_counts().sort_index())

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDuplicate participant-week records:")

    duplicates = df[
        df.duplicated(
            subset=["participant_reference", "study_week"],
            keep=False
        )
    ]

    print(len(duplicates))

    print("\nNegative study hours:")

    print(
        df[
            (df["ai_study_hours"] < 0) |
            (df["independent_study_hours"] < 0)
        ]
    )

    print("\nUnusually high AI study hours (>80):")

    print(
        df[df["ai_study_hours"] > 80][
            ["participant_reference", "study_week", "ai_study_hours"]
        ]
    )

    print("\nUnusually high independent study hours (>80):")

    print(
        df[df["independent_study_hours"] > 80][
            ["participant_reference",
             "study_week",
             "independent_study_hours"]
        ]
    )

    print("\n================================")