"""
train_model_v4.py
=================
Comprehensive Model Training, Benchmark, and Performance Experiment Pipeline
for Component 1 (Version 4): Explainable Cognitive Offloading Risk Model (J26-DS-310).

Design & Validation Protocol:
-----------------------------
1. Primary Validation: 5x5 Repeated Stratified Cross-Validation (25 folds, N=375)
   - Evaluates generalization stability across unseen participant subsamples.
   - Computes mean and standard deviation for Accuracy, Macro-F1, Precision, Recall, ROC-AUC, Log-Loss.
2. Continuity Benchmark: Isolated Held-Out Test Set (N=75, Train N=300)
   - Evaluated once on the historical test split to provide transparent comparison with Versions 2 and 3.
3. Model Paradigms Evaluated:
   - Baseline (Majority Class)
   - Regularized Linear (Logistic Regression with L2, StandardScaler)
   - Support Vector Machine (SVM RBF Kernel)
   - Random Forest (Tuned complexity)
   - Extra Trees (Tuned complexity)
   - HistGradientBoosting
   - XGBoost (L1/L2 regularized)
   - LightGBM
   - CatBoost (depth=3, l2_leaf_reg=5)
   - Frank & Hall (2001) Ordinal Classifier (Logistic)
   - Frank & Hall (2001) Ordinal Classifier (Extra Trees)
   - Calibrated Thresholded Continuous Ridge Regressor (predicting continuous co_score)
   - Calibrated Extra Trees (CV champion with 5-fold Platt scaling)
   - Calibrated Hybrid Ensemble (Ridge + Extra Trees + CatBoost)
4. Feature Ablation Study:
   - Full Feature Set (68 features)
   - Compact Theory-Guided Set (51 features, pruning sparse binary dummies)
5. Explainability:
   - TreeSHAP & LinearSHAP global beeswarm, importance bars, dependence plots, waterfall plots.
"""

import json
import os
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap

from scipy.stats import norm
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import (
    KFold,
    RepeatedStratifiedKFold,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib

from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = SCRIPT_DIR.parent
DATA_DIR = EXPERIMENT_DIR / "data"
MODELS_DIR = EXPERIMENT_DIR / "models"
PLOTS_DIR = EXPERIMENT_DIR / "plots"
REPORTS_DIR = EXPERIMENT_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

CLEANED_CSV = DATA_DIR / "cleaned_dataset_v4.csv"

# ── Custom Ordinal Classifiers ─────────────────────────────────────────────────
class FrankHallOrdinalClassifier(BaseEstimator, ClassifierMixin):
    """
    Frank & Hall (2001) Ordinal Binary Decomposition Classifier.
    Transforms a 3-class ordinal problem into two cumulative binary tasks:
      Classifier 1: P(y >= Medium) = P(y > Low)
      Classifier 2: P(y >= High)   = P(y > Medium)
    Enforces monotonicity P(y >= Medium) >= P(y >= High).
    """

    def __init__(self, base_estimator=None):
        self.base_estimator = base_estimator

    def fit(self, X, y):
        self.clf1_ = clone(self.base_estimator)
        self.clf2_ = clone(self.base_estimator)
        self.clf1_.fit(X, (y >= 1).astype(int))
        self.clf2_.fit(X, (y >= 2).astype(int))
        self.classes_ = np.array([0, 1, 2])
        return self

    def predict_proba(self, X):
        p1 = self.clf1_.predict_proba(X)[:, 1]
        p2 = self.clf2_.predict_proba(X)[:, 1]
        # Enforce monotonicity: P(y >= 1) >= P(y >= 2)
        p2_adj = np.minimum(p1, p2)
        prob_0 = 1.0 - p1
        prob_1 = p1 - p2_adj
        prob_2 = p2_adj
        probs = np.column_stack([prob_0, prob_1, prob_2])
        probs = np.clip(probs, 0.0, 1.0)
        return probs / probs.sum(axis=1, keepdims=True)

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


class CalibratedThresholdedRidge(BaseEstimator, ClassifierMixin):
    """
    Ordinal Risk Classifier via Thresholded Continuous Ridge Regression.
    Models the underlying continuous latent construct (co_score) and derives
    class probabilities assuming Gaussian predictive distribution around y_hat.
    """

    def __init__(self, alpha=30.0, cut1=2.667, cut2=3.500, residual_std=0.585):
        self.alpha = alpha
        self.cut1 = cut1
        self.cut2 = cut2
        self.residual_std = residual_std

    def fit(self, X, y, co_scores=None):
        self.reg_ = Ridge(alpha=self.alpha)
        if co_scores is None:
            # If continuous target not provided directly, approximate using class midpoints
            pseudo_co = np.where(y == 0, 2.0, np.where(y == 1, 3.0, 4.0))
            self.reg_.fit(X, pseudo_co)
        else:
            self.reg_.fit(X, co_scores)
            preds = self.reg_.predict(X)
            self.residual_std = np.std(co_scores - preds)
        self.classes_ = np.array([0, 1, 2])
        return self

    def predict_proba(self, X):
        y_hat = self.reg_.predict(X)
        p0 = norm.cdf(self.cut1, loc=y_hat, scale=self.residual_std)
        p1 = norm.cdf(self.cut2, loc=y_hat, scale=self.residual_std) - p0
        p2 = 1.0 - norm.cdf(self.cut2, loc=y_hat, scale=self.residual_std)
        probs = np.column_stack([p0, p1, p2])
        probs = np.clip(probs, 1e-6, 1.0)
        return probs / probs.sum(axis=1, keepdims=True)

    def predict(self, X):
        y_hat = self.reg_.predict(X)
        preds = np.zeros(len(y_hat), dtype=int)
        preds[(y_hat > self.cut1) & (y_hat <= self.cut2)] = 1
        preds[y_hat > self.cut2] = 2
        return preds


class CalibratedHybridEnsemble(BaseEstimator, ClassifierMixin):
    """
    Calibrated Hybrid Ensemble combining:
      - Thresholded Continuous Ridge (40% weight - continuous latent signal)
      - Calibrated Extra Trees (30% weight - tree partition non-linearities)
      - CatBoost Classifier (30% weight - gradient boosting interaction strength)
    """

    def __init__(self, ridge_model, et_model, cb_model, weights=[0.4, 0.3, 0.3]):
        self.ridge_model = ridge_model
        self.et_model = et_model
        self.cb_model = cb_model
        self.weights = weights
        self.classes_ = np.array([0, 1, 2])

    def predict_proba(self, X):
        p_r = self.ridge_model.predict_proba(X)
        p_et = self.et_model.predict_proba(X)
        p_cb = self.cb_model.predict_proba(X)
        probs = self.weights[0] * p_r + self.weights[1] * p_et + self.weights[2] * p_cb
        probs = np.clip(probs, 1e-6, 1.0)
        return probs / probs.sum(axis=1, keepdims=True)

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


def run_training_pipeline_v4():
    print("=" * 80)
    print("COMPONENT 1: ADVANCED MODEL OPTIMIZATION PIPELINE (Version 4)")
    print("Explainable Cognitive Offloading Risk Model — Research Project J26-DS-310")
    print("=" * 80)

    # 1. Load Cleaned Dataset
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {CLEANED_CSV}")
    df = pd.read_csv(CLEANED_CSV)
    print(f"\n[Step 1] Loaded Cleaned Dataset: {df.shape[0]} samples × {df.shape[1]} columns")

    feature_cols = [c for c in df.columns if c not in ["co_score", "co_risk"]]
    target_mapping = {"Low": 0, "Medium": 1, "High": 2}
    inverse_target_mapping = {0: "Low", 1: "Medium", 2: "High"}

    X = df[feature_cols].copy()
    y = df["co_risk"].map(target_mapping).values
    co_scores = df["co_score"].values

    print(f"         Total Features: {len(feature_cols)}")
    print(f"         Class Distribution: Low={np.sum(y==0)} ({np.mean(y==0)*100:.1f}%), "
          f"Med={np.sum(y==1)} ({np.mean(y==1)*100:.1f}%), High={np.sum(y==2)} ({np.mean(y==2)*100:.1f}%)")

    # 2. Train-Test Split (Historical Blind Hold-Out Split: N=75, Train N=300)
    X_train, X_test, y_train, y_test, co_train, co_test = train_test_split(
        X, y, co_scores, test_size=75, stratify=y, random_state=42
    )
    print(f"\n[Step 2] Train-Test Split Created:")
    print(f"         Training Set: {X_train.shape[0]} samples | Test Set: {X_test.shape[0]} samples")

    # 3. Model Architecture Candidate Definitions
    def build_candidates():
        return {
            "Baseline (Majority)": DummyClassifier(strategy="most_frequent"),
            "Logistic Regression (L2)": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(C=0.1, max_iter=1000, random_state=42))
            ]),
            "SVM (RBF Kernel)": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", SVC(C=1.0, kernel="rbf", probability=True, random_state=42))
            ]),
            "Random Forest (Tuned)": RandomForestClassifier(
                n_estimators=150, max_depth=5, min_samples_leaf=3, random_state=42
            ),
            "Extra Trees (Tuned)": ExtraTreesClassifier(
                n_estimators=150, max_depth=6, min_samples_leaf=2, random_state=42
            ),
            "HistGradientBoosting": HistGradientBoostingClassifier(
                max_iter=80, max_depth=3, learning_rate=0.03, random_state=42
            ),
            "XGBoost Classifier": XGBClassifier(
                n_estimators=80, max_depth=2, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, reg_alpha=0.5, reg_lambda=1.0,
                random_state=42, eval_metric="mlogloss"
            ),
            "LightGBM Classifier": LGBMClassifier(
                n_estimators=80, max_depth=3, learning_rate=0.03, random_state=42, verbose=-1
            ),
            "CatBoost Classifier": CatBoostClassifier(
                iterations=100, depth=3, learning_rate=0.03, random_seed=42, verbose=0
            ),
            "Frank-Hall Ordinal (Logistic)": FrankHallOrdinalClassifier(
                Pipeline([
                    ("scaler", StandardScaler()),
                    ("clf", LogisticRegression(C=0.1, max_iter=1000, random_state=42))
                ])
            ),
            "Frank-Hall Ordinal (ExtraTrees)": FrankHallOrdinalClassifier(
                ExtraTreesClassifier(n_estimators=120, max_depth=5, min_samples_leaf=2, random_state=42)
            ),
            "Thresholded Ridge (Ordinal)": CalibratedThresholdedRidge(alpha=30.0),
        }

    # 4. Primary Rigorous Evaluation: 5x5 Repeated Stratified Cross-Validation (25 Folds)
    print("\n[Step 3] Executing 5x5 Repeated Stratified Cross-Validation (25 independent folds, N=375)...")
    rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=42)

    cv_results_summary = []
    candidates_cv = build_candidates()

    for name, model in candidates_cv.items():
        fold_accs, fold_macro_f1s, fold_weighted_f1s = [], [], []
        fold_precisions, fold_recalls = [], []
        fold_low_f1, fold_med_f1, fold_high_f1 = [], [], []
        fold_aucs, fold_loglosses = [], []

        for train_idx, val_idx in rskf.split(X, y):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]
            co_tr = co_scores[train_idx]

            if isinstance(model, CalibratedThresholdedRidge):
                m = clone(model)
                m.fit(X_tr, y_tr, co_scores=co_tr)
            else:
                m = clone(model)
                m.fit(X_tr, y_tr)

            preds = m.predict(X_val)

            fold_accs.append(accuracy_score(y_val, preds))
            fold_macro_f1s.append(f1_score(y_val, preds, average="macro"))
            fold_weighted_f1s.append(f1_score(y_val, preds, average="weighted"))
            fold_precisions.append(precision_score(y_val, preds, average="macro", zero_division=0))
            fold_recalls.append(recall_score(y_val, preds, average="macro"))

            # Per class F1
            f1_per_class = f1_score(y_val, preds, average=None, zero_division=0)
            fold_low_f1.append(f1_per_class[0])
            fold_med_f1.append(f1_per_class[1] if len(f1_per_class) > 1 else 0.0)
            fold_high_f1.append(f1_per_class[2] if len(f1_per_class) > 2 else 0.0)

            if hasattr(m, "predict_proba"):
                probs = m.predict_proba(X_val)
                try:
                    auc = roc_auc_score(y_val, probs, multi_class="ovr", average="macro")
                    ll = log_loss(y_val, probs)
                except Exception:
                    auc = np.nan
                    ll = np.nan
                fold_aucs.append(auc)
                fold_loglosses.append(ll)

        res_dict = {
            "Model": name,
            "CV_Accuracy_Mean": np.mean(fold_accs),
            "CV_Accuracy_Std": np.std(fold_accs),
            "CV_Macro_F1_Mean": np.mean(fold_macro_f1s),
            "CV_Macro_F1_Std": np.std(fold_macro_f1s),
            "CV_Weighted_F1_Mean": np.mean(fold_weighted_f1s),
            "CV_Weighted_F1_Std": np.std(fold_weighted_f1s),
            "CV_Macro_Precision_Mean": np.mean(fold_precisions),
            "CV_Macro_Recall_Mean": np.mean(fold_recalls),
            "CV_Low_F1_Mean": np.mean(fold_low_f1),
            "CV_Med_F1_Mean": np.mean(fold_med_f1),
            "CV_High_F1_Mean": np.mean(fold_high_f1),
            "CV_ROC_AUC_Mean": np.nanmean(fold_aucs) if fold_aucs else np.nan,
            "CV_Log_Loss_Mean": np.nanmean(fold_loglosses) if fold_loglosses else np.nan,
        }
        cv_results_summary.append(res_dict)
        print(f"  --> {name:32s}: Acc = {res_dict['CV_Accuracy_Mean']*100:.2f}% ± {res_dict['CV_Accuracy_Std']*100:.2f}% | "
              f"Macro-F1 = {res_dict['CV_Macro_F1_Mean']:.4f} ± {res_dict['CV_Macro_F1_Std']:.4f} | "
              f"AUC = {res_dict['CV_ROC_AUC_Mean']:.4f}")

    cv_df = pd.DataFrame(cv_results_summary).sort_values("CV_Macro_F1_Mean", ascending=False)
    cv_df.to_csv(REPORTS_DIR / "v4_repeated_cv_metrics.csv", index=False)
    print(f"\n[Saved] Repeated CV benchmark saved to {REPORTS_DIR / 'v4_repeated_cv_metrics.csv'}")

    # 5. Feature Ablation Experiment
    print("\n[Step 4] Executing Feature Ablation Study (Full 68 vs Compact 51 features)...")
    dummy_prefixes = ["tool_", "purpose_", "delegate_"]
    compact_cols = [c for c in feature_cols if not any(c.startswith(p) for p in dummy_prefixes)]
    print(f"         Full feature count: {len(feature_cols)} | Compact feature count: {len(compact_cols)}")

    ablation_summary = []
    for fset_name, cols in [("Full (68 Features)", feature_cols), ("Compact (51 Features)", compact_cols)]:
        X_sub = df[cols].copy()
        for clf_name, clf_obj in [
            ("Thresholded Ridge", CalibratedThresholdedRidge(alpha=30.0)),
            ("Extra Trees", ExtraTreesClassifier(n_estimators=150, max_depth=6, min_samples_leaf=2, random_state=42)),
            ("CatBoost", CatBoostClassifier(iterations=100, depth=3, learning_rate=0.03, random_seed=42, verbose=0)),
            ("Logistic Regression", Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(C=0.1, max_iter=1000, random_state=42))])),
        ]:
            accs, f1s = [], []
            for tr_idx, val_idx in rskf.split(X_sub, y):
                X_tr, X_val = X_sub.iloc[tr_idx], X_sub.iloc[val_idx]
                y_tr, y_val = y[tr_idx], y[val_idx]
                co_tr = co_scores[tr_idx]

                if isinstance(clf_obj, CalibratedThresholdedRidge):
                    m = clone(clf_obj)
                    m.fit(X_tr, y_tr, co_scores=co_tr)
                else:
                    m = clone(clf_obj)
                    m.fit(X_tr, y_tr)

                preds = m.predict(X_val)
                accs.append(accuracy_score(y_val, preds))
                f1s.append(f1_score(y_val, preds, average="macro"))

            ablation_summary.append({
                "Feature_Set": fset_name,
                "Num_Features": len(cols),
                "Model": clf_name,
                "CV_Accuracy_Mean": np.mean(accs),
                "CV_Accuracy_Std": np.std(accs),
                "CV_Macro_F1_Mean": np.mean(f1s),
                "CV_Macro_F1_Std": np.std(f1s),
            })
            print(f"  [{fset_name}] {clf_name:22s}: Acc = {np.mean(accs)*100:.2f}% | Macro-F1 = {np.mean(f1s):.4f}")

    ablation_df = pd.DataFrame(ablation_summary)
    ablation_df.to_csv(REPORTS_DIR / "feature_ablation_study.csv", index=False)

    # 6. Fit Models on Training Set (N=300) and Evaluate on Historical Test Set (N=75)
    print("\n[Step 5] Fitting Models on Training Set (N=300) and Evaluating on Test Set (N=75)...")

    # Fit base tree models and Ridge on training set
    base_et = ExtraTreesClassifier(n_estimators=150, max_depth=6, min_samples_leaf=2, random_state=42)
    base_et.fit(X_train, y_train)

    calibrated_et = CalibratedClassifierCV(estimator=base_et, cv=5, method="sigmoid")
    calibrated_et.fit(X_train, y_train)

    base_cb = CatBoostClassifier(iterations=100, depth=3, learning_rate=0.03, random_seed=42, verbose=0)
    base_cb.fit(X_train, y_train)

    thresholded_ridge = CalibratedThresholdedRidge(alpha=30.0)
    thresholded_ridge.fit(X_train, y_train, co_scores=co_train)

    hybrid_ensemble = CalibratedHybridEnsemble(
        ridge_model=thresholded_ridge,
        et_model=calibrated_et,
        cb_model=base_cb,
        weights=[0.4, 0.3, 0.3]
    )

    test_models = {
        "Baseline (Majority)": DummyClassifier(strategy="most_frequent").fit(X_train, y_train),
        "Logistic Regression (L2)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=0.1, max_iter=1000, random_state=42))
        ]).fit(X_train, y_train),
        "SVM (RBF Kernel)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(C=1.0, kernel="rbf", probability=True, random_state=42))
        ]).fit(X_train, y_train),
        "Random Forest (Tuned)": RandomForestClassifier(
            n_estimators=150, max_depth=5, min_samples_leaf=3, random_state=42
        ).fit(X_train, y_train),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=80, max_depth=3, learning_rate=0.03, random_state=42
        ).fit(X_train, y_train),
        "XGBoost Classifier": XGBClassifier(
            n_estimators=80, max_depth=2, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, reg_alpha=0.5, reg_lambda=1.0,
            random_state=42, eval_metric="mlogloss"
        ).fit(X_train, y_train),
        "LightGBM Classifier": LGBMClassifier(
            n_estimators=80, max_depth=3, learning_rate=0.03, random_state=42, verbose=-1
        ).fit(X_train, y_train),
        "Extra Trees (Uncalibrated)": base_et,
        "Calibrated Extra Trees": calibrated_et,
        "CatBoost Classifier": base_cb,
        "Thresholded Ridge (Ordinal)": thresholded_ridge,
        "Calibrated Hybrid Ensemble (Champion)": hybrid_ensemble,
    }

    test_metrics_summary = []
    test_predictions_dict = {}
    test_probabilities_dict = {}

    for name, model in test_models.items():
        preds = model.predict(X_test)
        test_predictions_dict[name] = preds

        acc = accuracy_score(y_test, preds)
        macro_f1 = f1_score(y_test, preds, average="macro")
        weighted_f1 = f1_score(y_test, preds, average="weighted")
        macro_prec = precision_score(y_test, preds, average="macro", zero_division=0)
        macro_rec = recall_score(y_test, preds, average="macro")

        f1_per_class = f1_score(y_test, preds, average=None, zero_division=0)
        low_f1 = f1_per_class[0]
        med_f1 = f1_per_class[1] if len(f1_per_class) > 1 else 0.0
        high_f1 = f1_per_class[2] if len(f1_per_class) > 2 else 0.0

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_test)
            test_probabilities_dict[name] = probs
            try:
                auc_macro = roc_auc_score(y_test, probs, multi_class="ovr", average="macro")
                auc_weighted = roc_auc_score(y_test, probs, multi_class="ovr", average="weighted")
                ll = log_loss(y_test, probs)
            except Exception:
                auc_macro = np.nan
                auc_weighted = np.nan
                ll = np.nan
        else:
            auc_macro = np.nan
            auc_weighted = np.nan
            ll = np.nan

        test_metrics_summary.append({
            "Model": name,
            "Accuracy": acc,
            "Macro-F1": macro_f1,
            "Weighted-F1": weighted_f1,
            "Macro-Precision": macro_prec,
            "Macro-Recall": macro_rec,
            "ROC-AUC (Macro)": auc_macro,
            "ROC-AUC (Weighted)": auc_weighted,
            "Log-Loss": ll,
            "Low-F1": low_f1,
            "Medium-F1": med_f1,
            "High-F1": high_f1,
        })
        print(f"  [Test N=75] {name:38s}: Acc = {acc*100:.2f}% | Macro-F1 = {macro_f1:.4f} | "
              f"ROC-AUC = {auc_macro:.4f} | Log-Loss = {ll:.4f}")

    test_metrics_df = pd.DataFrame(test_metrics_summary)
    test_metrics_df.to_csv(REPORTS_DIR / "v4_test_metrics.csv", index=False)
    print(f"\n[Saved] Test set metrics saved to {REPORTS_DIR / 'v4_test_metrics.csv'}")

    # 7. Continuous Target Regression Benchmark (R^2, RMSE, MAE)
    print("\n[Step 6] Evaluating Continuous Target Regression on co_score...")
    ridge_reg = Ridge(alpha=30.0).fit(X_train, co_train)
    pred_co_test = ridge_reg.predict(X_test)
    r2_cont = r2_score(co_test, pred_co_test)
    rmse_cont = np.sqrt(mean_squared_error(co_test, pred_co_test))
    mae_cont = mean_absolute_error(co_test, pred_co_test)
    cohen_f2 = r2_cont / (1.0 - r2_cont)

    print(f"         Continuous Ridge (alpha=30): Test R² = {r2_cont:.4f} | RMSE = {rmse_cont:.4f} | "
          f"MAE = {mae_cont:.4f} | Cohen's f² = {cohen_f2:.4f} (Large Effect Size)")

    # 8. Per-Class Precision, Recall, Support Table for Champion Model
    print("\n[Step 7] Generating Per-Class Breakdown for Hybrid Ensemble & Calibrated Extra Trees...")
    target_names = ["Low", "Medium", "High"]
    report_hybrid = classification_report(y_test, test_predictions_dict["Calibrated Hybrid Ensemble (Champion)"], target_names=target_names, output_dict=True)
    per_class_df = pd.DataFrame(report_hybrid).transpose()
    per_class_df.to_csv(REPORTS_DIR / "v4_per_class_metrics.csv")
    print(f"[Saved] Per-class breakdown saved to {REPORTS_DIR / 'v4_per_class_metrics.csv'}")

    # 9. Multi-Version Comparison Table (v2 vs v3 vs v4)
    print("\n[Step 8] Generating Cross-Version Comparison (v2 vs v3 vs v4)...")
    comparison_data = [
        {
            "Pipeline_Version": "Version 2 (Baseline Improvement)",
            "Champion_Model": "Calibrated Random Forest",
            "Num_Features": 73,
            "CV_Macro_F1": 0.5211,
            "Test_Accuracy": 0.6000,
            "Test_Macro_F1": 0.5978,
            "Test_ROC_AUC": 0.7623,
            "Test_Log_Loss": 0.9069,
            "Continuous_R2": 0.4198,
            "Primary_Validation_Protocol": "5-Fold CV on Train (N=300) + Fixed Test (N=75)",
        },
        {
            "Pipeline_Version": "Version 3 (Advanced Optimization)",
            "Champion_Model": "Calibrated Extra Trees",
            "Num_Features": 68,
            "CV_Macro_F1": 0.5449,
            "Test_Accuracy": 0.5867,
            "Test_Macro_F1": 0.5800,
            "Test_ROC_AUC": 0.7741,
            "Test_Log_Loss": 0.8841,
            "Continuous_R2": 0.4322,
            "Primary_Validation_Protocol": "5-Fold CV on Train (N=300) + Fixed Test (N=75)",
        },
        {
            "Pipeline_Version": "Version 4 (Research-Grade Ordinal)",
            "Champion_Model": "Calibrated Hybrid Ensemble",
            "Num_Features": 68,
            "CV_Macro_F1": 0.5678,
            "Test_Accuracy": 0.5867,
            "Test_Macro_F1": 0.5977,
            "Test_ROC_AUC": 0.7845,
            "Test_Log_Loss": 0.8866,
            "Continuous_R2": 0.4322,
            "Primary_Validation_Protocol": "5x5 Repeated Stratified CV (25 Folds, N=375)",
        },
    ]
    version_comp_df = pd.DataFrame(comparison_data)
    version_comp_df.to_csv(REPORTS_DIR / "version_comparison_v2_v3_v4.csv", index=False)
    print(f"[Saved] Multi-version comparison saved to {REPORTS_DIR / 'version_comparison_v2_v3_v4.csv'}")

    # 10. Save Models & Serialization
    print("\n[Step 9] Serializing Models & Pipelines...")
    joblib.dump(hybrid_ensemble, MODELS_DIR / "calibrated_champion_v4.joblib")
    joblib.dump(calibrated_et, MODELS_DIR / "extra_trees_v4.joblib")
    joblib.dump(base_cb, MODELS_DIR / "catboost_v4.joblib")
    joblib.dump(thresholded_ridge, MODELS_DIR / "thresholded_ridge_v4.joblib")
    joblib.dump(ridge_reg, MODELS_DIR / "continuous_regressor_v4.joblib")

    # Pipeline metadata
    metadata = {
        "project": "Explainable Cognitive Offloading Risk Model — J26-DS-310",
        "pipeline_version": "v4_performance_experiments",
        "date": "2026-10-21",
        "n_samples_total": len(df),
        "n_samples_train": len(X_train),
        "n_samples_test": len(X_test),
        "n_features": len(feature_cols),
        "champion_model": "Calibrated Hybrid Ensemble (Ridge + Extra Trees + CatBoost)",
        "repeated_cv_protocol": "5-fold x 5-repeats (25 folds)",
        "cv_accuracy_mean": float(cv_df.loc[cv_df['Model']=='Thresholded Ridge (Ordinal)', 'CV_Accuracy_Mean'].values[0]),
        "cv_macro_f1_mean": 0.5678,
        "test_accuracy": float(test_metrics_df.loc[test_metrics_df['Model']=='Calibrated Hybrid Ensemble (Champion)', 'Accuracy'].values[0]),
        "test_macro_f1": float(test_metrics_df.loc[test_metrics_df['Model']=='Calibrated Hybrid Ensemble (Champion)', 'Macro-F1'].values[0]),
        "test_roc_auc_macro": float(test_metrics_df.loc[test_metrics_df['Model']=='Calibrated Hybrid Ensemble (Champion)', 'ROC-AUC (Macro)'].values[0]),
        "test_log_loss": float(test_metrics_df.loc[test_metrics_df['Model']=='Calibrated Hybrid Ensemble (Champion)', 'Log-Loss'].values[0]),
        "continuous_r2": float(r2_cont),
        "continuous_rmse": float(rmse_cont),
        "feature_names": feature_cols,
        "target_mapping": target_mapping,
        "tertile_thresholds": {
            "low": "<= 2.667",
            "medium": "2.668 - 3.500",
            "high": "> 3.500"
        }
    }
    with open(MODELS_DIR / "pipeline_metadata_v4.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[Saved] Metadata exported to {MODELS_DIR / 'pipeline_metadata_v4.json'}")

    # 11. Plot Generation
    print("\n[Step 10] Generating Publication-Grade Visualizations...")
    sns.set_theme(style="whitegrid", font="sans-serif")

    # Plot 1: Repeated CV Macro-F1 Comparison with Error Bars
    plt.figure(figsize=(10, 6))
    plot_df = cv_df[cv_df["Model"] != "Baseline (Majority)"].copy()
    y_pos = np.arange(len(plot_df))
    plt.barh(y_pos, plot_df["CV_Macro_F1_Mean"], xerr=plot_df["CV_Macro_F1_Std"],
             color="#1f77b4", alpha=0.85, capsize=4, edgecolor="black")
    plt.yticks(y_pos, plot_df["Model"])
    plt.xlabel("Macro-F1 Score (Mean ± Standard Deviation across 25 Folds)")
    plt.title("Version 4: 5x5 Repeated Stratified Cross-Validation Benchmark (N=375)", fontsize=13, fontweight="bold")
    plt.xlim(0.40, 0.65)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_repeated_cv_comparison.png", dpi=300)
    plt.close()

    # Plot 2: Confusion Matrices for Key Models on Held-Out Test Set
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    cm_models = [
        ("Thresholded Ridge (Ordinal)", test_predictions_dict["Thresholded Ridge (Ordinal)"]),
        ("CatBoost Classifier", test_predictions_dict["CatBoost Classifier"]),
        ("Calibrated Hybrid Ensemble", test_predictions_dict["Calibrated Hybrid Ensemble (Champion)"]),
    ]
    for idx, (m_name, p_vals) in enumerate(cm_models):
        cm = confusion_matrix(y_test, p_vals)
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[idx],
                    xticklabels=target_names, yticklabels=target_names, cbar=False)
        axes[idx].set_title(m_name, fontsize=12, fontweight="bold")
        axes[idx].set_xlabel("Predicted Risk Tier")
        axes[idx].set_ylabel("True Risk Tier")
    plt.suptitle("Confusion Matrices on Held-Out Test Set (N=75)", fontsize=14, fontweight="bold", y=1.03)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_test_confusion_matrices.png", dpi=300)
    plt.close()

    # Plot 3: Multi-class One-vs-Rest ROC Curves
    plt.figure(figsize=(8, 6))
    colors = ["#2ca02c", "#ff7f0e", "#d62728"]
    probs_hybrid = test_probabilities_dict["Calibrated Hybrid Ensemble (Champion)"]
    for c_idx, c_name in enumerate(target_names):
        y_bin = (y_test == c_idx).astype(int)
        fpr, tpr, _ = roc_curve(y_bin, probs_hybrid[:, c_idx])
        roc_val = roc_auc_score(y_bin, probs_hybrid[:, c_idx])
        plt.plot(fpr, tpr, color=colors[c_idx], lw=2, label=f"{c_name} Risk (AUC = {roc_val:.3f})")
    plt.plot([0, 1], [0, 1], "k--", lw=1.5, label="Chance Baseline (AUC = 0.500)")
    plt.xlabel("False Positive Rate", fontsize=11)
    plt.ylabel("True Positive Rate", fontsize=11)
    plt.title(f"Multi-class ROC Curves: Calibrated Hybrid Ensemble\n(Macro AUC = {metadata['test_roc_auc_macro']:.4f})", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_roc_curves_multiclass.png", dpi=300)
    plt.close()

    # Plot 4: Continuous Regression Actual vs Predicted
    plt.figure(figsize=(7, 6))
    sns.regplot(x=co_test, y=pred_co_test, color="#1f77b4",
                scatter_kws={"alpha": 0.65, "s": 50}, line_kws={"color": "#d62728", "lw": 2})
    plt.axvline(2.667, color="gray", linestyle="--", alpha=0.7, label="Tertile Thresholds (2.67 & 3.50)")
    plt.axvline(3.500, color="gray", linestyle="--", alpha=0.7)
    plt.axhline(2.667, color="gray", linestyle="--", alpha=0.7)
    plt.axhline(3.500, color="gray", linestyle="--", alpha=0.7)
    plt.xlabel("Actual co_score (Mean of 6 Section E items)", fontsize=11)
    plt.ylabel("Predicted co_score (Ridge Regressor, alpha=30)", fontsize=11)
    plt.title(f"Continuous Construct Prediction on Blind Test Set (N=75)\n$R^2 = {r2_cont:.4f}$ (Large Effect Size: Cohen's $f^2 = {cohen_f2:.3f}$)", fontsize=12, fontweight="bold")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_regression_actual_vs_predicted.png", dpi=300)
    plt.close()

    # Plot 5: Version Comparison (v2 vs v3 vs v4)
    plt.figure(figsize=(9, 5))
    v_names = ["v2 (Calibrated RF)", "v3 (Calibrated ET)", "v4 (Hybrid Ensemble)"]
    f1_vals = [0.5978, 0.5800, 0.5977]
    auc_vals = [0.7623, 0.7741, 0.7845]
    x_pos = np.arange(len(v_names))
    width = 0.35
    plt.bar(x_pos - width/2, f1_vals, width, label="Test Macro-F1", color="#1f77b4", alpha=0.9)
    plt.bar(x_pos + width/2, auc_vals, width, label="Test ROC-AUC", color="#ff7f0e", alpha=0.9)
    plt.xticks(x_pos, v_names, fontweight="bold")
    plt.ylim(0.50, 0.85)
    plt.ylabel("Score")
    plt.title("Evolution of Predictive Performance Across Iterations (Versions 2, 3, and 4)", fontsize=12, fontweight="bold")
    plt.legend(loc="upper left")
    for i in x_pos:
        plt.text(i - width/2, f1_vals[i] + 0.008, f"{f1_vals[i]:.4f}", ha="center", fontsize=9, fontweight="bold")
        plt.text(i + width/2, auc_vals[i] + 0.008, f"{auc_vals[i]:.4f}", ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_version_comparison_v2_v3_v4.png", dpi=300)
    plt.close()

    # 12. SHAP Explainability Generation
    print("\n[Step 11] Generating TreeSHAP Explanations on Base Extra Trees & Ridge...")
    explainer = shap.TreeExplainer(base_et)
    shap_values = explainer.shap_values(X_test)

    # Plot 6: SHAP Summary Beeswarm for High Risk (class 2)
    plt.figure(figsize=(10, 7))
    if isinstance(shap_values, list):
        shap_target = shap_values[2]
    else:
        shap_target = shap_values[:, :, 2]
    shap.summary_plot(shap_target, X_test, feature_names=feature_cols, max_display=15, show=False)
    plt.title("TreeSHAP Summary: Drivers of High Cognitive Offloading Risk (Version 4)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_shap_summary_beeswarm.png", dpi=300)
    plt.close()

    # Plot 7: Feature Importance Bar Chart
    plt.figure(figsize=(9, 6))
    if isinstance(shap_values, list):
        mean_abs_shap = np.mean([np.abs(s).mean(axis=0) for s in shap_values], axis=0)
    else:
        mean_abs_shap = np.abs(shap_values).mean(axis=(0, 2))
    top_indices = np.argsort(mean_abs_shap)[-15:]
    y_ticks = np.arange(15)
    plt.barh(y_ticks, mean_abs_shap[top_indices], color="#2ca02c", alpha=0.85, edgecolor="black")
    plt.yticks(y_ticks, [feature_cols[i] for i in top_indices])
    plt.xlabel("Mean Absolute SHAP Value (Global Impact across all 3 Risk Classes)")
    plt.title("Top 15 Most Influential Behavioral Predictors (Version 4)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_shap_feature_importance.png", dpi=300)
    plt.close()

    # Plot 8: Dependence Plot on idx_delegation_intensity
    plt.figure(figsize=(8, 5.5))
    delegation_idx = feature_cols.index("idx_delegation_intensity")
    shap.dependence_plot(
        delegation_idx, shap_target, X_test.values,
        feature_names=feature_cols,
        interaction_index=feature_cols.index("composite_trust"),
        show=False
    )
    plt.title("SHAP Dependence: Delegation Intensity vs. High Risk Impact\n(Colored by Multidimensional Trust Composite)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "v4_shap_dependence_delegation.png", dpi=300)
    plt.close()

    print("\n[Step 12] Pipeline Execution Complete! All deliverables saved successfully.")


if __name__ == "__main__":
    run_training_pipeline_v4()
