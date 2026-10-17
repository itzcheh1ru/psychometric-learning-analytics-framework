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
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "component4_master_dataset_300.csv"


def save_pickle(obj, path: Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def save_json(data, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_regressor_model(X_train, y_train, X_test, y_test, model_name: str):
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(X_train.to_numpy(), y_train.to_numpy())

    preds = model.predict(X_test.to_numpy())
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    metrics = {
        "model": model_name,
        "sample_size": len(X_train) + len(X_test),
        "test_sample_size": len(y_test),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
    }

    return model, metrics


def main():
    MODELS_DIR.mkdir(exist_ok=True)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    genai_features = [
        "ga_learning_time_sec",
        "ga_immediate_mcq",
        "ga_prompt_count",
        "ga_confidence",
        "ga_ai_usefulness",
        "ga_mental_effort",
        "ga_explanation_ease",
        "ga_word_count",
        "ga_lexical_diversity_ttr",
        "cognitive_ownership_score",
        "explanation_autonomy_score",
        "perceived_ai_dependency_score",
    ]

    brain_features = [
        "bo_learning_time_sec",
        "bo_immediate_mcq",
        "bo_mental_effort",
        "bo_word_count",
        "bo_lexical_diversity_ttr",
        "cognitive_ownership_score",
        "explanation_autonomy_score",
        "perceived_ai_dependency_score",
    ]

    target_genai = "genai_delayed_recall_score"
    target_brain = "brain_delayed_recall_score"

    missing_genai = [col for col in genai_features + [target_genai] if col not in df.columns]
    missing_brain = [col for col in brain_features + [target_brain] if col not in df.columns]

    if missing_genai or missing_brain:
        raise ValueError(
            "Missing required columns. "
            f"GenAI missing: {missing_genai}. Brain missing: {missing_brain}."
        )

    X_ga = df[genai_features]
    y_ga = df[target_genai]

    X_ga_train, X_ga_test, y_ga_train, y_ga_test = train_test_split(
        X_ga, y_ga, test_size=0.2, random_state=42
    )

    ga_model, ga_metrics = build_regressor_model(
        X_ga_train, y_ga_train, X_ga_test, y_ga_test, "genai_delayed_recall_regressor"
    )

    X_brain = df[brain_features]
    y_brain = df[target_brain]

    X_brain_train, X_brain_test, y_brain_train, y_brain_test = train_test_split(
        X_brain, y_brain, test_size=0.2, random_state=42
    )

    brain_model, brain_metrics = build_regressor_model(
        X_brain_train, y_brain_train, X_brain_test, y_brain_test, "brain_delayed_recall_regressor"
    )

    ga_model_path = MODELS_DIR / "genai_delayed_recall_model.pkl"
    brain_model_path = MODELS_DIR / "brain_delayed_recall_model.pkl"
    metrics_path = MODELS_DIR / "delayed_recall_model_metrics.json"
    feature_path = MODELS_DIR / "delayed_recall_feature_sets.json"

    save_pickle(ga_model, ga_model_path)
    save_pickle(brain_model, brain_model_path)

    save_json({"genai": ga_metrics, "brain": brain_metrics}, metrics_path)
    save_json(
        {
            "genai_features": genai_features,
            "brain_features": brain_features,
            "genai_target": target_genai,
            "brain_target": target_brain,
        },
        feature_path,
    )

    print("=== GenAI Delayed Recall Model ===")
    print(f"MAE: {ga_metrics['mae']}")
    print(f"RMSE: {ga_metrics['rmse']}")
    print(f"R²: {ga_metrics['r2']}")
    print(f"Saved to: {ga_model_path}")

    print("\n=== Brain-only Delayed Recall Model ===")
    print(f"MAE: {brain_metrics['mae']}")
    print(f"RMSE: {brain_metrics['rmse']}")
    print(f"R²: {brain_metrics['r2']}")
    print(f"Saved to: {brain_model_path}")

    print(f"\nMetrics summary saved to: {metrics_path}")
    print(f"Feature metadata saved to: {feature_path}")


if __name__ == "__main__":
    main()
