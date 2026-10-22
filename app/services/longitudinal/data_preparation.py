from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_week_file(file_path: Path, week_number: int) -> pd.DataFrame:
    df = pd.read_excel(file_path)

    df["study_week"] = f"Week {week_number}"

    return df


def load_all_real_weeks() -> pd.DataFrame:
    frames = []

    for week_number in range(1, 7):
        file_path = RAW_DIR / f"Week_{week_number:02d}_REAL.xlsx"

        if file_path.exists():
            frames.append(load_week_file(file_path, week_number))

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    df = load_all_real_weeks()

    print("Rows:", len(df))
    print("Weeks:", df["study_week"].unique() if not df.empty else [])

    output = PROCESSED_DIR / "combined_weekly_raw.csv"
    df.to_csv(output, index=False)

    print(f"Saved: {output}")