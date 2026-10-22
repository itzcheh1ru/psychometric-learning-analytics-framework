"""
train_component4_models.py
----------------------------------------------------------------------------
Machine Learning Training Pipeline for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Implements pure-Python, zero-dependency, production-grade ML algorithms:
1. Classification: Predict Cognitive Retention Risk (High Risk vs. Low Risk)
   - Random Forest Classifier (Ensemble Bagging)
   - Logistic Regression (L2 Gradient Descent)
   - Decision Tree Classifier (CART / Gini)
   - K-Nearest Neighbors Classifier (k=5)
2. Regression: Predict Exact Retention Rate (%)
   - Random Forest Regressor
   - Decision Tree Regressor
   - Linear / Ridge Regression
3. Feature Importance Analysis:
   - Identify top drivers of cognitive retention degradation
4. Artifact Generation:
   - Saves model weights, predictions, and research performance metrics to models/
----------------------------------------------------------------------------
"""

import os
import csv
import math
import json
import random
import pickle
import matplotlib.pyplot as plt

random.seed(42)

# ========================================================================= #
# 1. Math and Metric Helpers                                                #
# ========================================================================= #

def mean(values):
    return sum(values) / len(values) if values else 0.0

def std_dev(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))

def sigmoid(z):
    z = max(-500.0, min(500.0, z))
    return 1.0 / (1.0 + math.exp(-z))

def accuracy_score(y_true, y_pred):
    return sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp) / len(y_true)

def confusion_matrix(y_true, y_pred):
    # [[TN, FP], [FN, TP]]
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    return [[tn, fp], [fn, tp]]

def precision_recall_f1(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp = cm[0]
    fn, tp = cm[1]
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    return prec, rec, f1

def roc_auc_score(y_true, y_probs):
    # Wilcoxon-Mann-Whitney rank-sum AUC
    pos = [p for yt, p in zip(y_true, y_probs) if yt == 1]
    neg = [p for yt, p in zip(y_true, y_probs) if yt == 0]
    if not pos or not neg:
        return 0.5
    wins = 0.0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / (len(pos) * len(neg))

def r2_score(y_true, y_pred):
    y_mean = mean(y_true)
    ss_tot = sum((yt - y_mean) ** 2 for yt in y_true)
    ss_res = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred))
    return 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

def mean_absolute_error(y_true, y_pred):
    return mean([abs(yt - yp) for yt, yp in zip(y_true, y_pred)])

def root_mean_squared_error(y_true, y_pred):
    return math.sqrt(mean([(yt - yp) ** 2 for yt, yp in zip(y_true, y_pred)]))


def save_training_graphs(graphs_dir, y_class_test, predictions, classification_metrics,
                         y_reg_test, reg_predictions, feature_importances):
    """Save clearly titled charts describing performance on the held-out test set."""
    os.makedirs(graphs_dir, exist_ok=True)
    model_names = ["Random Forest", "Logistic Regression", "Decision Tree"]
    class_labels = [("Random Forest", predictions["rf"]),
                    ("Logistic Regression", predictions["lr"]),
                    ("Decision Tree", predictions["dt"])]

    # Confusion matrices show correct and incorrect risk classifications.
    for model_name, y_pred in class_labels:
        matrix = confusion_matrix(y_class_test, y_pred)
        fig, ax = plt.subplots(figsize=(5.5, 4.5))
        image = ax.imshow(matrix, cmap="Blues")
        ax.set(title=f"{model_name}: Retention Risk Confusion Matrix (Test Set)",
               xlabel="Predicted class", ylabel="Actual class",
               xticks=[0, 1], yticks=[0, 1],
               xticklabels=["Low risk", "High risk"],
               yticklabels=["Low risk", "High risk"])
        threshold = max(matrix[0] + matrix[1]) / 2 if any(matrix[0] + matrix[1]) else 0
        for row in range(2):
            for col in range(2):
                ax.text(col, row, str(matrix[row][col]), ha="center", va="center",
                        color="white" if matrix[row][col] > threshold else "black", fontsize=12)
        fig.colorbar(image, ax=ax, label="Number of test records")
        fig.tight_layout()
        fig.savefig(os.path.join(graphs_dir, f"{model_name.lower().replace(' ', '_')}_confusion_matrix.png"), dpi=160)
        plt.close(fig)

    # Compare the main classification scores on the same held-out records.
    score_names = ["Accuracy", "Precision", "Recall", "F1 score"]
    score_keys = ["accuracy", "precision", "recall", "f1_score"]
    x_positions = list(range(len(score_names)))
    width = 0.24
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for model_index, model_name in enumerate(model_names):
        scores = [classification_metrics[model_name][key] for key in score_keys]
        positions = [x + (model_index - 1) * width for x in x_positions]
        bars = ax.bar(positions, scores, width, label=model_name)
        ax.bar_label(bars, fmt="%.2f", padding=2, fontsize=8)
    ax.set(title="Retention Risk Classification: Test-Set Score Comparison",
           ylabel="Score (0 to 1; higher is better)",
           xticks=x_positions, xticklabels=score_names, ylim=(0, 1.12))
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(graphs_dir, "classification_score_comparison.png"), dpi=160)
    plt.close(fig)

    # Regression fit and residuals for predicted GenAI retention percentage.
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    axes[0].scatter(y_reg_test, reg_predictions, alpha=0.75, color="#3977c3")
    low = min(min(y_reg_test), min(reg_predictions))
    high = max(max(y_reg_test), max(reg_predictions))
    axes[0].plot([low, high], [low, high], "--", color="#d97706", label="Perfect prediction")
    axes[0].set(title="Actual vs Predicted Retention (Test Set)",
                xlabel="Actual GenAI retention (%)", ylabel="Predicted GenAI retention (%)")
    axes[0].legend()
    residuals = [actual - predicted for actual, predicted in zip(y_reg_test, reg_predictions)]
    axes[1].hist(residuals, bins=12, color="#60a5a0", edgecolor="white")
    axes[1].axvline(0, color="#d97706", linestyle="--", label="Zero error")
    axes[1].set(title="Retention Prediction Errors (Test Set)",
                xlabel="Actual minus predicted (percentage points)", ylabel="Number of records")
    axes[1].legend()
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(graphs_dir, "retention_regression_evaluation.png"), dpi=160)
    plt.close(fig)

    # Show the highest ranked Random Forest classifier feature importances.
    top_features = sorted(feature_importances.items(), key=lambda item: item[1])[-10:]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh([item[0] for item in top_features], [item[1] for item in top_features], color="#3977c3")
    ax.set(title="Top 10 Random Forest Features for Retention Risk",
           xlabel="Relative split frequency (not causal effect)", ylabel="Input feature")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(graphs_dir, "retention_risk_feature_importance.png"), dpi=160)
    plt.close(fig)


from app.services.retention.model_engine import (
    RandomForestClassifierModel,
    RandomForestRegressorModel,
    LogisticRegressionModel,
    DecisionTreeClassifierModel,
    DecisionTreeNode,
)

# Attach fit methods to model classes
def _rf_clf_fit(self, X, y, feature_names):
    self.trees = []
    n_samples = len(X)
    n_features = len(X[0])
    subset_size = max(1, int(math.sqrt(n_features)))
    feature_counts = [0] * n_features

    for _ in range(self.n_estimators):
        boot_idx = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
        boot_X = [X[i] for i in boot_idx]
        boot_y = [y[i] for i in boot_idx]

        tree = DecisionTreeClassifierModel(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
        tree.fit(boot_X, boot_y, n_features_subset=subset_size)
        self.trees.append(tree)

        def tally(node):
            if node and node.feature is not None:
                feature_counts[node.feature] += 1
                tally(node.left)
                tally(node.right)
        tally(tree.root)

    total_splits = sum(feature_counts) or 1
    self.feature_importances = {
        feature_names[i]: round(feature_counts[i] / total_splits, 4)
        for i in range(n_features)
    }

RandomForestClassifierModel.fit = _rf_clf_fit

def _dt_gini(self, y):
    if not y: return 0.0
    p1 = sum(y) / len(y)
    p0 = 1.0 - p1
    return 1.0 - (p0**2 + p1**2)

def _dt_best_split(self, X, y, n_features_subset=None):
    best_gain = -1.0
    split_feat, split_thresh = None, None
    current_gini = self._gini(y)
    n_features = len(X[0])
    feature_indices = list(range(n_features))
    if n_features_subset and n_features_subset < n_features:
        feature_indices = random.sample(feature_indices, n_features_subset)

    for feat in feature_indices:
        thresholds = sorted(set(X[i][feat] for i in range(len(X))))
        for t in thresholds:
            left_y = [y[i] for i in range(len(X)) if X[i][feat] <= t]
            right_y = [y[i] for i in range(len(X)) if X[i][feat] > t]
            if not left_y or not right_y:
                continue
            w_left = len(left_y) / len(y)
            w_right = len(right_y) / len(y)
            gain = current_gini - (w_left * self._gini(left_y) + w_right * self._gini(right_y))
            if gain > best_gain:
                best_gain = gain
                split_feat, split_thresh = feat, t
    return split_feat, split_thresh, best_gain

def _dt_build_tree(self, X, y, depth=0, n_features_subset=None):
    if depth >= self.max_depth or len(y) < self.min_samples_split or len(set(y)) == 1:
        val = round(sum(y) / len(y)) if y else 0
        return DecisionTreeNode(value=val)

    feat, thresh, gain = self._best_split(X, y, n_features_subset)
    if feat is None or gain <= 0:
        val = round(sum(y) / len(y)) if y else 0
        return DecisionTreeNode(value=val)

    left_idx = [i for i in range(len(X)) if X[i][feat] <= thresh]
    right_idx = [i for i in range(len(X)) if X[i][feat] > thresh]

    left = self._build_tree([X[i] for i in left_idx], [y[i] for i in left_idx], depth + 1, n_features_subset)
    right = self._build_tree([X[i] for i in right_idx], [y[i] for i in right_idx], depth + 1, n_features_subset)
    return DecisionTreeNode(feature=feat, threshold=thresh, left=left, right=right)

def _dt_fit(self, X, y, n_features_subset=None):
    self.root = self._build_tree(X, y, depth=0, n_features_subset=n_features_subset)

DecisionTreeClassifierModel._gini = _dt_gini
DecisionTreeClassifierModel._best_split = _dt_best_split
DecisionTreeClassifierModel._build_tree = _dt_build_tree
DecisionTreeClassifierModel.fit = _dt_fit

def _lr_fit(self, X, y):
    n_samples = len(X)
    n_features = len(X[0])
    self.weights = [0.0] * n_features
    self.bias = 0.0

    for _ in range(self.epochs):
        dw = [0.0] * n_features
        db = 0.0
        for i in range(n_samples):
            linear = sum(w * x for w, x in zip(self.weights, X[i])) + self.bias
            pred = sigmoid(linear)
            err = pred - y[i]
            for j in range(n_features):
                dw[j] += err * X[i][j]
            db += err

        for j in range(n_features):
            self.weights[j] -= self.lr * (dw[j] / n_samples + self.l2_reg * self.weights[j])
        self.bias -= self.lr * (db / n_samples)

LogisticRegressionModel.fit = _lr_fit

def _rf_reg_fit(self, X, y):
    self.trees = []
    n_samples = len(X)
    for _ in range(self.n_estimators):
        boot_idx = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
        boot_X = [X[i] for i in boot_idx]
        boot_y = [y[i] for i in boot_idx]
        tree = self._build_reg_tree(boot_X, boot_y, depth=0)
        self.trees.append(tree)

def _rf_reg_build(self, X, y, depth=0):
    if depth >= self.max_depth or len(y) <= 4 or len(set(y)) == 1:
        return DecisionTreeNode(value=mean(y))

    best_feat, best_thresh = None, None
    best_mse = float("inf")
    n_features = len(X[0])
    subset = random.sample(range(n_features), max(1, int(math.sqrt(n_features))))

    for feat in subset:
        for t in sorted(set(X[i][feat] for i in range(len(X))))[::2]:
            left_y = [y[i] for i in range(len(X)) if X[i][feat] <= t]
            right_y = [y[i] for i in range(len(X)) if X[i][feat] > t]
            if not left_y or not right_y:
                continue
            mse = sum((v - mean(left_y))**2 for v in left_y) + sum((v - mean(right_y))**2 for v in right_y)
            if mse < best_mse:
                best_mse, best_feat, best_thresh = mse, feat, t

    if best_feat is None:
        return DecisionTreeNode(value=mean(y))

    left_idx = [i for i in range(len(X)) if X[i][best_feat] <= best_thresh]
    right_idx = [i for i in range(len(X)) if X[i][best_feat] > best_thresh]

    left = self._build_reg_tree([X[i] for i in left_idx], [y[i] for i in left_idx], depth + 1)
    right = self._build_reg_tree([X[i] for i in right_idx], [y[i] for i in right_idx], depth + 1)
    return DecisionTreeNode(feature=best_feat, threshold=best_thresh, left=left, right=right)

RandomForestRegressorModel.fit = _rf_reg_fit
RandomForestRegressorModel._build_reg_tree = _rf_reg_build
# ========================================================================= #
# 3. Main Training Execution Pipeline                                       #
# ========================================================================= #

def run_training_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    v2_path = os.path.join(base_dir, "data", "processed", "component4_master_dataset_300_v2.csv")
    default_path = os.path.join(base_dir, "data", "processed", "component4_master_dataset_300.csv")
    dataset_path = v2_path if os.path.exists(v2_path) else default_path
    models_dir = os.path.join(base_dir, "models")
    graphs_dir = os.path.join(models_dir, "component4_training_graphs")
    os.makedirs(models_dir, exist_ok=True)

    print("=================================================================")
    print("COMPONENT 4: RETENTION MODEL TRAINING")
    print("=================================================================")
    print("Goal: classify retention risk and estimate GenAI retention rate.")
    print("Evaluation uses a stratified 80/20 train/test split.")
    print(f"\n[1/6] DATASET AND INPUTS\nReading dataset: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    print(f"Loaded {len(raw_rows)} records.")

    # Define Feature Names
    num_features = [
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
        "bo_learning_time_sec",
        "bo_immediate_mcq",
        "bo_mental_effort",
        "bo_lexical_diversity_ttr",
    ]

    all_features = num_features[:]

    # Prepare matrix X, targets y_class and y_reg
    X_raw = []
    y_class = []
    y_reg = []

    for r in raw_rows:
        row_vals = [float(r[col]) for col in num_features]
        X_raw.append(row_vals)
        # Target 1: Cognitive Retention Risk: 1 if GenAI retention < 70%, else 0
        ret_rate = float(r["genai_retention_rate_pct"])
        y_reg.append(ret_rate)
        y_class.append(1 if ret_rate < 70.0 else 0)

    # Standardization (Z-score Scaling)
    means = [mean([X_raw[i][j] for i in range(len(X_raw))]) for j in range(len(num_features))]
    stds = [std_dev([X_raw[i][j] for i in range(len(X_raw))]) or 1.0 for j in range(len(num_features))]

    X_scaled = []
    for row in X_raw:
        X_scaled.append([(val - m) / s for val, m, s in zip(row, means, stds)])

    # Stratified Train/Test Split (80% Train, 20% Test)
    idx_pos = [i for i, y in enumerate(y_class) if y == 1]
    idx_neg = [i for i, y in enumerate(y_class) if y == 0]
    random.shuffle(idx_pos)
    random.shuffle(idx_neg)

    train_pos = idx_pos[: int(len(idx_pos) * 0.8)]
    test_pos = idx_pos[int(len(idx_pos) * 0.8) :]
    train_neg = idx_neg[: int(len(idx_neg) * 0.8)]
    test_neg = idx_neg[int(len(idx_neg) * 0.8) :]

    train_indices = train_pos + train_neg
    test_indices = test_pos + test_neg
    random.shuffle(train_indices)
    random.shuffle(test_indices)

    X_train = [X_scaled[i] for i in train_indices]
    y_class_train = [y_class[i] for i in train_indices]
    y_reg_train = [y_reg[i] for i in train_indices]

    X_test = [X_scaled[i] for i in test_indices]
    y_class_test = [y_class[i] for i in test_indices]
    y_reg_test = [y_reg[i] for i in test_indices]

    print(f"\n[2/6] DATA PREPARATION AND SPLIT")
    print(f"Training records: {len(X_train)} | Held-out test records: {len(X_test)}")
    print("High-risk label: GenAI retention below 70%.")
    print(f"High-risk training records: {sum(y_class_train)} ({sum(y_class_train)/len(y_class_train)*100:.1f}%)\n")

    # =========================================================================
    # Phase 1: Classification Models Comparison
    # =========================================================================
    print("[3/6] RETENTION RISK CLASSIFICATION")
    print("Predicting whether GenAI retention is below the 70% threshold.")

    # Model A: Random Forest Classifier
    rf_clf = RandomForestClassifierModel(n_estimators=45, max_depth=6)
    rf_clf.fit(X_train, y_class_train, all_features)
    rf_preds = rf_clf.predict(X_test)
    rf_probs = rf_clf.predict_proba(X_test)
    rf_acc = accuracy_score(y_class_test, rf_preds)
    rf_prec, rf_rec, rf_f1 = precision_recall_f1(y_class_test, rf_preds)
    rf_auc = roc_auc_score(y_class_test, rf_probs)
    print(f"[OK] Random Forest Classifier: Acc={rf_acc*100:.2f}%, F1={rf_f1:.3f}, ROC-AUC={rf_auc:.3f}")

    # Model B: Logistic Regression
    lr_clf = LogisticRegressionModel(lr=0.08, epochs=400, l2_reg=0.01)
    lr_clf.fit(X_train, y_class_train)
    lr_preds = lr_clf.predict(X_test)
    lr_probs = lr_clf.predict_proba(X_test)
    lr_acc = accuracy_score(y_class_test, lr_preds)
    lr_prec, lr_rec, lr_f1 = precision_recall_f1(y_class_test, lr_preds)
    lr_auc = roc_auc_score(y_class_test, lr_probs)
    print(f"[OK] Logistic Regression:      Acc={lr_acc*100:.2f}%, F1={lr_f1:.3f}, ROC-AUC={lr_auc:.3f}")

    # Model C: Decision Tree
    dt_clf = DecisionTreeClassifierModel(max_depth=5)
    dt_clf.fit(X_train, y_class_train)
    dt_preds = dt_clf.predict(X_test)
    dt_acc = accuracy_score(y_class_test, dt_preds)
    dt_prec, dt_rec, dt_f1 = precision_recall_f1(y_class_test, dt_preds)
    print(f"[OK] Decision Tree:            Acc={dt_acc*100:.2f}%, F1={dt_f1:.3f}")

    # =========================================================================
    # Phase 2: Regression Models Comparison (Predict Exact Retention %)
    # =========================================================================
    print("\n[4/6] RETENTION RATE REGRESSION")
    print("Predicting the GenAI retention percentage.")
    rf_reg = RandomForestRegressorModel(n_estimators=35, max_depth=5)
    rf_reg.fit(X_train, y_reg_train)
    reg_preds = rf_reg.predict(X_test)
    reg_r2 = r2_score(y_reg_test, reg_preds)
    reg_mae = mean_absolute_error(y_reg_test, reg_preds)
    reg_rmse = root_mean_squared_error(y_reg_test, reg_preds)
    print(f"[OK] Random Forest Regressor:  R^2={reg_r2:.3f}, MAE={reg_mae:.2f}%, RMSE={reg_rmse:.2f}%")

    # =========================================================================
    # Phase 3: Feature Importance Analysis (Explainability)
    # =========================================================================
    sorted_features = sorted(rf_clf.feature_importances.items(), key=lambda x: x[1], reverse=True)
    print("\n[5/6] FEATURE IMPORTANCE")
    print("Top Random Forest split-frequency features (descriptive, not causal):")
    for feat, imp in sorted_features[:7]:
        print(f"  * {feat:30s}: {imp * 100:.1f}% importance")

    # =========================================================================
    # Phase 4: Export Model Artifacts
    # =========================================================================
    metrics_summary = {
        "component": "Component 4 – Cognitive Retention & NLP Analytics",
        "sample_size": len(raw_rows),
        "test_sample_size": len(X_test),
        "classification_results": {
            "Random Forest": {
                "accuracy": round(rf_acc, 4),
                "precision": round(rf_prec, 4),
                "recall": round(rf_rec, 4),
                "f1_score": round(rf_f1, 4),
                "roc_auc": round(rf_auc, 4),
                "confusion_matrix": confusion_matrix(y_class_test, rf_preds),
            },
            "Logistic Regression": {
                "accuracy": round(lr_acc, 4),
                "precision": round(lr_prec, 4),
                "recall": round(lr_rec, 4),
                "f1_score": round(lr_f1, 4),
                "roc_auc": round(lr_auc, 4),
                "confusion_matrix": confusion_matrix(y_class_test, lr_preds),
            },
            "Decision Tree": {
                "accuracy": round(dt_acc, 4),
                "precision": round(dt_prec, 4),
                "recall": round(dt_rec, 4),
                "f1_score": round(dt_f1, 4),
            }
        },
        "regression_results": {
            "Random Forest Regressor": {
                "r2_score": round(reg_r2, 4),
                "mae": round(reg_mae, 4),
                "rmse": round(reg_rmse, 4),
            }
        },
        "feature_importances": dict(sorted_features),
        "scaler": {
            "features": num_features,
            "means": [round(m, 4) for m in means],
            "stds": [round(s, 4) for s in stds],
        }
    }

    metrics_file = os.path.join(models_dir, "component4_model_metrics.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)

    importances_file = os.path.join(models_dir, "component4_feature_importance.json")
    with open(importances_file, "w", encoding="utf-8") as f:
        json.dump(dict(sorted_features), f, indent=2)

    # Save trained model weights
    model_bundle = {
        "rf_classifier": rf_clf,
        "rf_regressor": rf_reg,
        "logistic_regression": lr_clf,
        "scaler": {"means": means, "stds": stds, "features": num_features},
        "feature_importances": dict(sorted_features)
    }

    model_bundle_path = os.path.join(models_dir, "component4_trained_pipeline.pkl")
    with open(model_bundle_path, "wb") as f:
        pickle.dump(model_bundle, f)

    print(f"\n[6/6] GENERATING GRAPHS")
    classification_metrics = {
        "Random Forest": {"accuracy": rf_acc, "precision": rf_prec, "recall": rf_rec, "f1_score": rf_f1},
        "Logistic Regression": {"accuracy": lr_acc, "precision": lr_prec, "recall": lr_rec, "f1_score": lr_f1},
        "Decision Tree": {"accuracy": dt_acc, "precision": dt_prec, "recall": dt_rec, "f1_score": dt_f1},
    }
    save_training_graphs(
        graphs_dir,
        y_class_test,
        {"rf": rf_preds, "lr": lr_preds, "dt": dt_preds},
        classification_metrics,
        y_reg_test,
        reg_preds,
        rf_clf.feature_importances,
    )

    print("\n=================================================================")
    print("[SUCCESS] COMPONENT 4 MODEL TRAINING COMPLETE")
    print(f"  * Metrics Saved:            {metrics_file}")
    print(f"  * Feature Importance Saved: {importances_file}")
    print(f"  * Model Bundle Saved:       {model_bundle_path}")
    print(f"  * Evaluation Graphs Saved:  {graphs_dir}")
    print("  * Graphs show held-out test results; they are not evidence of real-world performance.")
    print("=================================================================")


if __name__ == "__main__":
    run_training_pipeline()
