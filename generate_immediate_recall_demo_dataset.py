"""Create a simulation-only dataset for testing the immediate-recall ML pipeline.

The targets below are generated from explicit formulas and seeded random noise.
They are not participant observations or research findings.
"""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_PATH = PROJECT_ROOT / "data" / "processed" / "component4_master_dataset_300.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "demo" / "immediate_recall_training_simulation_only.csv"

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
        "cognitive_ownership_score",
        "explanation_autonomy_score",
        "perceived_ai_dependency_score",
    ],
}


def main() -> None:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Feature source dataset not found: {SOURCE_PATH}")

    source = pd.read_csv(SOURCE_PATH)
    required = sorted({feature for features in FEATURES.values() for feature in features})
    missing = [feature for feature in required if feature not in source.columns]
    if missing:
        raise ValueError(f"Missing source features: {missing}")

    rng = np.random.default_rng(2025)
    brain_noise = rng.normal(0, 0.25, len(source))
    genai_noise = rng.normal(0, 0.25, len(source))

    brain_target = (
        7.8
        + 0.5 * (source["bo_confidence"] - 3.8)
        + 0.55 * (source["bo_mental_effort"] - 3.9)
        + 0.01 * (source["bo_learning_time_sec"] - 225)
        + 1.5 * (source["bo_lexical_diversity_ttr"] - 0.72)
        + 0.01 * (source["bo_word_count"] - 42)
        + brain_noise
    )
    genai_target = (
        8.2
        + 0.5 * (source["ga_confidence"] - 4.3)
        + 0.4 * (source["ga_ai_usefulness"] - 4.4)
        + 0.6 * (source["ga_mental_effort"] - 2.4)
        + 0.01 * (source["ga_learning_time_sec"] - 170)
        + 0.15 * (source["ga_prompt_count"] - 3.2)
        + 1.5 * (source["ga_lexical_diversity_ttr"] - 0.65)
        + 0.004 * (source["ga_word_count"] - 45)
        + genai_noise
    )

    demo = source[required].copy()
    demo["brain_immediate_score"] = np.clip(brain_target, 4, 10).round(1)
    demo["genai_immediate_score"] = np.clip(genai_target, 5, 10).round(1)
    demo["data_origin"] = "simulation_only_formula_generated_target_not_participant_data"

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    demo.to_csv(OUTPUT_PATH, index=False)
    print(f"Created {len(demo)} simulation-only rows: {OUTPUT_PATH}")
    print("Immediate-recall targets are formula-generated and are not research evidence.")


if __name__ == "__main__":
    main()
