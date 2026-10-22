from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import matplotlib

# Use a file-only backend so training works without a local Tk installation.
matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent
MODELS_DIR = PROJECT_ROOT / "models"
GRAPHS_DIR = MODELS_DIR / "delayed_recall_graphs"
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

    return model, metrics, preds


def save_model_graphs(condition: str, y_test, predictions, model, feature_names) -> None:
    """Save held-out prediction and random-forest feature-importance graphs."""
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    label = "GenAI-Assisted" if condition == "genai" else "Brain-Only"

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(y_test, predictions, alpha=0.75, edgecolor="white", linewidth=0.5)
    low = min(float(np.min(y_test)), float(np.min(predictions)))
    high = max(float(np.max(y_test)), float(np.max(predictions)))
    ax.plot([low, high], [low, high], "--", color="#d97706", label="Perfect prediction")
    ax.set(title=f"{label} Delayed Recall: Actual vs Predicted (Test Set)",
           xlabel="Actual delayed recall (items)", ylabel="Predicted delayed recall (items)")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / f"{condition}_actual_vs_predicted.png", dpi=160)
    plt.close(fig)

    importance = pd.Series(model.feature_importances_, index=feature_names).sort_values()
    fig, ax = plt.subplots(figsize=(8, max(4, len(importance) * 0.38)))
    importance.plot.barh(ax=ax, color="#3977c3")
    ax.set(title=f"{label} Delayed Recall: Feature Importance",
           xlabel="Relative feature importance", ylabel="Input feature")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / f"{condition}_feature_importance.png", dpi=160)
    plt.close(fig)


def save_metric_comparison(genai_metrics: dict, brain_metrics: dict) -> None:
    """Plot held-out error metrics for both models (lower is better)."""
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    labels = ["GenAI-Assisted", "Brain-Only"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, key, title in zip(axes, ("mae", "rmse"), ("Mean Absolute Error (MAE)", "Root Mean Squared Error (RMSE)")):
        values = [genai_metrics[key], brain_metrics[key]]
        bars = ax.bar(labels, values, color=["#e88922", "#3977c3"])
        ax.set_title(f"Test-Set {title}")
        ax.set_ylabel("Error (items; lower is better)")
        ax.bar_label(bars, fmt="%.3f", padding=3)
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("Delayed Recall Model Error Comparison")
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "model_error_comparison.png", dpi=160)
    plt.close(fig)


def main():
    MODELS_DIR.mkdir(exist_ok=True)

    print("=" * 72)
    print("DELAYED RECALL MODEL TRAINING")
    print("=" * 72)
    print("Purpose: train separate Brain-Only and GenAI-Assisted regressors.")
    print("Evaluation: held-out 20% test split; not proof of real-world performance.")
    print(f"Dataset: {DATASET_PATH}")

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

    print("\n[1/4] Training GenAI-Assisted delayed-recall model...")
    ga_model, ga_metrics, ga_predictions = build_regressor_model(
        X_ga_train, y_ga_train, X_ga_test, y_ga_test, "genai_delayed_recall_regressor"
    )

    X_brain = df[brain_features]
    y_brain = df[target_brain]

    X_brain_train, X_brain_test, y_brain_train, y_brain_test = train_test_split(
        X_brain, y_brain, test_size=0.2, random_state=42
    )

    print("[2/4] Training Brain-Only delayed-recall model...")
    brain_model, brain_metrics, brain_predictions = build_regressor_model(
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

    print("[3/4] Creating graphs...")
    save_model_graphs("genai", y_ga_test, ga_predictions, ga_model, genai_features)
    save_model_graphs("brain", y_brain_test, brain_predictions, brain_model, brain_features)
    save_metric_comparison(ga_metrics, brain_metrics)

    print("\n[4/4] TRAINING RESULTS")
    print("--- GenAI-Assisted Delayed Recall ---")
    print(f"MAE: {ga_metrics['mae']}")
    print(f"RMSE: {ga_metrics['rmse']}")
    print(f"R²: {ga_metrics['r2']}")
    print(f"Saved to: {ga_model_path}")

    print("\n--- Brain-Only Delayed Recall ---")
    print(f"MAE: {brain_metrics['mae']}")
    print(f"RMSE: {brain_metrics['rmse']}")
    print(f"R²: {brain_metrics['r2']}")
    print(f"Saved to: {brain_model_path}")

    print(f"\nMetrics summary saved to: {metrics_path}")
    print(f"Feature metadata saved to: {feature_path}")
    print(f"Evaluation graphs saved in: {GRAPHS_DIR}")
    print("Note: these graphs describe the held-out split only; feature importance is not causal evidence.")


if __name__ == "__main__":
    main()
