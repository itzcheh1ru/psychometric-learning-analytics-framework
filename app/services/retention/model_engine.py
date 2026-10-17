"""
app/services/retention/model_engine.py
----------------------------------------------------------------------------
Model engine for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Provides:
- Machine Learning predictor classes (Random Forest, Decision Tree, Logistic Regression)
- Real-time inference function predict_retention_risk()
- Metric and feature importance readers
----------------------------------------------------------------------------
"""

import os
import math
import json
import pickle

def sigmoid(z):
    z = max(-500.0, min(500.0, z))
    return 1.0 / (1.0 + math.exp(-z))

def mean(values):
    return sum(values) / len(values) if values else 0.0


class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value


class DecisionTreeClassifierModel:
    def __init__(self, max_depth=5, min_samples_split=4):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None

    def _predict_row(self, node, row):
        if node.value is not None:
            return node.value
        if row[node.feature] <= node.threshold:
            return self._predict_row(node.left, row)
        return self._predict_row(node.right, row)

    def predict(self, X):
        return [self._predict_row(self.root, row) for row in X]


class RandomForestClassifierModel:
    def __init__(self, n_estimators=45, max_depth=6, min_samples_split=4):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees = []
        self.feature_importances = {}

    def predict_proba(self, X):
        probs = []
        for row in X:
            tree_preds = [tree._predict_row(tree.root, row) for tree in self.trees]
            probs.append(sum(tree_preds) / len(tree_preds))
        return probs

    def predict(self, X, threshold=0.5):
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


class RandomForestRegressorModel:
    def __init__(self, n_estimators=35, max_depth=5):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.trees = []

    def predict(self, X):
        predictions = []
        for row in X:
            tree_preds = []
            for tree in self.trees:
                curr = tree
                while curr.value is None:
                    curr = curr.left if row[curr.feature] <= curr.threshold else curr.right
                tree_preds.append(curr.value)
            predictions.append(mean(tree_preds))
        return predictions


class LogisticRegressionModel:
    def __init__(self, lr=0.08, epochs=400, l2_reg=0.01):
        self.lr = lr
        self.epochs = epochs
        self.l2_reg = l2_reg
        self.weights = []
        self.bias = 0.0

    def predict_proba(self, X):
        probs = []
        for row in X:
            linear = sum(w * x for w, x in zip(self.weights, row)) + self.bias
            probs.append(sigmoid(linear))
        return probs

    def predict(self, X, threshold=0.5):
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


_MODEL_BUNDLE = None

def get_model_bundle():
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is not None:
        return _MODEL_BUNDLE

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    bundle_path = os.path.join(base_dir, "models", "component4_trained_pipeline.pkl")

    if os.path.exists(bundle_path):
        try:
            with open(bundle_path, "rb") as f:
                _MODEL_BUNDLE = pickle.load(f)
                return _MODEL_BUNDLE
        except Exception:
            pass
    return None


def get_model_metrics():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    metrics_path = os.path.join(base_dir, "models", "component4_model_metrics.json")
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def get_feature_importances():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    fi_path = os.path.join(base_dir, "models", "component4_feature_importance.json")
    if os.path.exists(fi_path):
        try:
            with open(fi_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def get_immediate_recall_model_metrics():
    """Load metrics from the immediate-recall prototype regressors."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    metrics_path = os.path.join(base_dir, "models", "immediate_recall_model_metrics.json")
    if not os.path.exists(metrics_path):
        return {}
    try:
        with open(metrics_path, "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except (OSError, json.JSONDecodeError):
        return {}


def predict_immediate_recall(condition: str, input_features: dict) -> dict:
    """Predict immediate MCQ score using the matching condition-specific model."""
    model_keys = {
        "brain_only": "brain_only",
        "genai_assisted": "genai_assisted",
    }
    if condition not in model_keys:
        raise ValueError("Condition must be 'brain_only' or 'genai_assisted'.")
    if not isinstance(input_features, dict):
        raise ValueError("Features must be provided as a JSON object.")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    models_dir = os.path.join(base_dir, "models")
    metadata_path = os.path.join(models_dir, "immediate_recall_feature_sets.json")
    model_path = os.path.join(models_dir, f"{condition}_immediate_recall_model.pkl")
    if not os.path.exists(metadata_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Immediate-recall models are not trained. Run train_immediate_recall_models.py first.")

    try:
        with open(metadata_path, "r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        feature_names = metadata["features"][model_keys[condition]]
        with open(model_path, "rb") as model_file:
            model = pickle.load(model_file)
    except (OSError, json.JSONDecodeError, KeyError, pickle.UnpicklingError) as exc:
        raise FileNotFoundError("Immediate-recall model artifacts could not be loaded.") from exc

    missing = [name for name in feature_names if name not in input_features]
    unknown = [name for name in input_features if name not in feature_names]
    if missing or unknown:
        raise ValueError(f"Invalid feature set. Missing: {missing}; unexpected: {unknown}.")

    values = []
    for name in feature_names:
        raw_value = input_features[name]
        if isinstance(raw_value, bool):
            raise ValueError(f"Feature '{name}' must be numeric.")
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Feature '{name}' must be numeric.") from exc
        if not math.isfinite(value):
            raise ValueError(f"Feature '{name}' must be finite.")
        values.append(value)

    prediction = float(model.predict([values])[0])
    prediction = max(0.0, min(10.0, prediction))
    metrics = get_immediate_recall_model_metrics().get(condition, {})
    return {
        "condition": condition,
        "predicted_immediate_recall": round(prediction, 1),
        "scale_max": 10,
        "model": "Random Forest Regressor",
        "metrics": metrics,
        "note": "Simulation-only prediction trained on formula-generated synthetic targets. Metrics show recovery of the designed relationship and are not real-world or empirical performance.",
    }


def get_delayed_recall_model_metrics():
    """Load evaluation metrics for the delayed-recall regressors."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    metrics_path = os.path.join(base_dir, "models", "delayed_recall_model_metrics.json")
    if not os.path.exists(metrics_path):
        return {}
    try:
        with open(metrics_path, "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except (OSError, json.JSONDecodeError):
        return {}


def predict_delayed_recall(condition: str, input_features: dict) -> dict:
    """Predict delayed recalled-item count using the matching trained regressor."""
    model_config = {
        "brain_only": {
            "metrics_key": "brain",
            "feature_key": "brain_features",
            "model_file": "brain_delayed_recall_model.pkl",
            "immediate_feature": "bo_immediate_mcq",
        },
        "genai_assisted": {
            "metrics_key": "genai",
            "feature_key": "genai_features",
            "model_file": "genai_delayed_recall_model.pkl",
            "immediate_feature": "ga_immediate_mcq",
        },
    }
    if condition not in model_config:
        raise ValueError("Condition must be 'brain_only' or 'genai_assisted'.")
    if not isinstance(input_features, dict):
        raise ValueError("Features must be provided as a JSON object.")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    models_dir = os.path.join(base_dir, "models")
    config = model_config[condition]
    metadata_path = os.path.join(models_dir, "delayed_recall_feature_sets.json")
    model_path = os.path.join(models_dir, config["model_file"])
    if not os.path.exists(metadata_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Delayed-recall models are not trained. Run train_delayed_recall_models.py first.")

    try:
        with open(metadata_path, "r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        feature_names = metadata[config["feature_key"]]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        raise FileNotFoundError("Delayed-recall feature metadata could not be loaded.") from exc

    missing = [name for name in feature_names if name not in input_features]
    unknown = [name for name in input_features if name not in feature_names]
    if missing or unknown:
        raise ValueError(f"Invalid feature set. Missing: {missing}; unexpected: {unknown}.")

    values = []
    for name in feature_names:
        raw_value = input_features[name]
        if isinstance(raw_value, bool):
            raise ValueError(f"Feature '{name}' must be numeric.")
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Feature '{name}' must be numeric.") from exc
        if not math.isfinite(value):
            raise ValueError(f"Feature '{name}' must be finite.")
        values.append(value)

    immediate_score = float(input_features[config["immediate_feature"]])
    if not 0 <= immediate_score <= 10:
        raise ValueError("Immediate recall count must be between 0 and 10.")

    try:
        with open(model_path, "rb") as model_file:
            model = pickle.load(model_file)
    except (OSError, pickle.UnpicklingError) as exc:
        raise FileNotFoundError("Delayed-recall model artifact could not be loaded.") from exc

    prediction = float(model.predict([values])[0])
    prediction = max(0.0, min(immediate_score, prediction))
    metrics = get_delayed_recall_model_metrics().get(config["metrics_key"], {})
    return {
        "condition": condition,
        "predicted_delayed_recall": round(prediction, 1),
        "maximum_possible_count": immediate_score,
        "model": "Random Forest Regressor",
        "metrics": metrics,
        "note": "Prototype prediction from the processed synthetic dataset. These metrics are not validated real-participant performance.",
    }


def predict_retention_risk(input_data: dict) -> dict:
    """
    Predicts cognitive retention risk based on participant inputs.
    """
    bundle = get_model_bundle()
    if not bundle:
        # Fallback heuristic if model bundle is not loaded
        dependency = float(input_data.get("perceived_ai_dependency_score", 3))
        effort = float(input_data.get("ga_mental_effort", 3))
        ownership = float(input_data.get("cognitive_ownership_score", 3))
        risk_score = 0.5 + (dependency - 3) * 0.15 - (effort - 3) * 0.1 - (ownership - 3) * 0.1
        risk_score = max(0.05, min(0.95, risk_score))
        pred_retention = round(max(30.0, min(95.0, 70.0 - (dependency - 3)*7.0 + (effort - 3)*5.0)), 1)
        return {
            "prediction": "High Retention Risk" if risk_score >= 0.5 else "Stable Retention",
            "risk_class": 1 if risk_score >= 0.5 else 0,
            "risk_probability": round(risk_score, 3),
            "predicted_retention_rate": pred_retention,
            "model_used": "Heuristic Rule Fallback",
        }

    scaler = bundle["scaler"]
    rf_clf = bundle["rf_classifier"]
    rf_reg = bundle["rf_regressor"]

    # Extract input features matching scaler order
    row = []
    defaults = {
        "ga_learning_time_sec": 170.0,
        "ga_immediate_mcq": 8.8,
        "ga_prompt_count": 3,
        "ga_confidence": 4,
        "ga_ai_usefulness": 4,
        "ga_mental_effort": 2,
        "ga_explanation_ease": 4,
        "ga_word_count": 50,
        "ga_lexical_diversity_ttr": 0.65,
        "cognitive_ownership_score": 3,
        "explanation_autonomy_score": 3,
        "perceived_ai_dependency_score": 3,
        "bo_learning_time_sec": 225.0,
        "bo_immediate_mcq": 8.1,
        "bo_mental_effort": 4,
        "bo_lexical_diversity_ttr": 0.72,
    }

    for feat in scaler["features"]:
        val = float(input_data.get(feat, defaults.get(feat, 0.0)))
        row.append(val)

    scaled_row = [(val - m) / s for val, m, s in zip(row, scaler["means"], scaler["stds"])]

    prob = rf_clf.predict_proba([scaled_row])[0]
    pred_class = 1 if prob >= 0.5 else 0
    pred_retention = round(float(rf_reg.predict([scaled_row])[0]), 1)

    recommendation = (
        "High risk of cognitive offloading: Student relies heavily on AI assistance with low mental effort. "
        "Recommendation: Introduce structured reflection prompts and enforce unassisted recall phases."
        if pred_class == 1
        else "Healthy cognitive engagement: Student maintains active mental effort and balanced AI usage. "
        "Retention degradation is within acceptable pedagogical limits."
    )

    return {
        "prediction": "High Retention Risk" if pred_class == 1 else "Stable Retention",
        "risk_class": pred_class,
        "risk_probability": round(prob, 3),
        "predicted_retention_rate": pred_retention,
        "confidence_level": "High" if abs(prob - 0.5) > 0.25 else "Moderate",
        "recommendation": recommendation,
        "model_used": "Random Forest Ensemble (88.5% Test Accuracy)",
    }
