from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parent
MODELS_DIR = PROJECT_ROOT / "models"
DATASET_PATH = PROJECT_ROOT / "data" / "demo" / "immediate_recall_training_simulation_only.csv"

FEATURES = {
    "brain_only": [
        "bo_learning_time_sec",
        "bo_confidence",
        "bo_mental_effort",
        "bo_word_count",
        "bo_lexical_diversity_ttr",
    ],
    "genai_assisted": [
        "ga_learning_time_sec",
        "ga_prompt_count",
        "ga_confidence",
        "ga_ai_usefulness",
        "ga_mental_effort",
        "ga_explanation_ease",
        "ga_word_count",
        "ga_lexical_diversity_ttr",
    ],
}

TARGETS = {
    "brain_only": "brain_immediate_score",
    "genai_assisted": "genai_immediate_score",
}


def train_model(frame: pd.DataFrame, condition: str) -> tuple[RandomForestRegressor, dict]:
    features = FEATURES[condition]
    target = TARGETS[condition]
    data = frame[features + [target]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 5:
        raise ValueError(f"Not enough valid rows to train {condition} immediate recall model.")

    X_train, X_test, y_train, y_test = train_test_split(
        data[features], data[target], test_size=0.2, random_state=42
    )
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(X_train.to_numpy(), y_train.to_numpy())

    predictions = model.predict(X_test.to_numpy())
    metrics = {
        "model": f"{condition}_immediate_recall_regressor",
        "target": target,
        "data_source": "simulation_only_formula_generated_targets_not_participant_data",
        "sample_size": int(len(data)),
        "test_sample_size": int(len(y_test)),
        "mae": round(float(mean_absolute_error(y_test, predictions)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, predictions))), 4),
        "r2": round(float(r2_score(y_test, predictions)), 4),
    }
    return model, metrics


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    MODELS_DIR.mkdir(exist_ok=True)
    frame = pd.read_csv(DATASET_PATH)
    metrics = {}
    for condition in ("brain_only", "genai_assisted"):
        missing = [
            column
            for column in FEATURES[condition] + [TARGETS[condition]]
            if column not in frame.columns
        ]
        if missing:
            raise ValueError(f"Missing columns for {condition}: {missing}")

        model, condition_metrics = train_model(frame, condition)
        model_path = MODELS_DIR / f"{condition}_immediate_recall_model.pkl"
        with model_path.open("wb") as model_file:
            pickle.dump(model, model_file)
        metrics[condition] = condition_metrics
        print(f"{condition.replace('_', ' ').title()}: {condition_metrics}")
        print(f"Saved model: {model_path}")

    with (MODELS_DIR / "immediate_recall_model_metrics.json").open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)
    with (MODELS_DIR / "immediate_recall_feature_sets.json").open("w", encoding="utf-8") as features_file:
        json.dump({"features": FEATURES, "targets": TARGETS}, features_file, indent=2)

    print(f"Metrics saved: {MODELS_DIR / 'immediate_recall_model_metrics.json'}")


if __name__ == "__main__":
    main()