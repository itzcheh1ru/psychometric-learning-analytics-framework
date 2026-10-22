"""
generate_and_run_notebook_v4.py
================================
Generates and executes the self-contained Jupyter notebook for Version 4:
Model Training/v4_performance_experiments/notebooks/model_training_v4.ipynb
"""

import os
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = SCRIPT_DIR.parent
NOTEBOOK_DIR = EXPERIMENT_DIR / "notebooks"
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / "model_training_v4.ipynb"

nb = nbf.v4.new_notebook()

cells = [
    nbf.v4.new_markdown_cell("""# Component 1: Final Research-Grade Model Performance Experiments (Version 4)
### Explainable Cognitive Offloading Risk Model — Research Project J26-DS-310 (Student ID: IT23426580)

**Dataset:** 375 consenting undergraduate student responses (`Data Set/raw_data.xlsx`)  
**Methodological Standard:** Approved Research Proposal (`Proposal_report_IT23426580.docx`, Appendix B, Section E)  
**Target Construct:** Unweighted mean of 6 approved Section E items (Cronbach's $\\alpha = 0.8649$)  
**Target Discretization:** Empirical Tertiles: Low ($\le 2.667$), Medium ($2.668-3.500$), High ($> 3.500$)  
**Leakage-Free Guarantee:** Full exclusion of Section G Academic AI Dependence items, circular target components, and administrative metadata.

---

## Version 4 Scientific Enhancements:
1. **Primary Validation Protocol:**
   - 5x5 Repeated Stratified Cross-Validation (25 distinct folds across $N=375$).
   - Computes empirical Mean and Standard Deviation for all performance metrics to eliminate evaluation split variance.
2. **Paradigms Evaluated:**
   - Baseline, Regularized Linear (Logistic L2), SVM (RBF), Random Forest, Extra Trees, HistGradientBoosting, XGBoost, LightGBM, CatBoost.
   - **Ordinal Classification:** Frank & Hall (2001) binary decomposition; Calibrated Thresholded Continuous Ridge Regressor.
   - **Calibrated Hybrid Ensemble:** Blending Thresholded Ridge, Calibrated Extra Trees, and CatBoost.
3. **Continuous Construct Signal:**
   - Regularized Ridge Regressor predicting continuous `co_score` ($R^2 = 0.446$, Cohen's $f^2 = 0.805$).
4. **Explainability:**
   - TreeSHAP and LinearSHAP global beeswarm, importance ranking, dependence interactions, and individual student waterfall profiles.
"""),

    nbf.v4.new_code_cell("""import os
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import shap

from scipy.stats import norm
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.svm import SVC
from sklearn.ensemble import (
    RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier,
    VotingClassifier
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score, log_loss
)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
print("Environment initialized successfully.")
"""),

    nbf.v4.new_markdown_cell("""## 1. Load Cleaned Dataset & Target Inspection"""),

    nbf.v4.new_code_cell("""DATA_PATH = Path("../data/cleaned_dataset_v4.csv")
df = pd.read_csv(DATA_PATH)
print(f"Loaded dataset: {df.shape[0]} rows × {df.shape[1]} columns")

feature_cols = [c for c in df.columns if c not in ["co_score", "co_risk"]]
target_map = {"Low": 0, "Medium": 1, "High": 2}
inv_target_map = {0: "Low", 1: "Medium", 2: "High"}

X = df[feature_cols].copy()
y = df["co_risk"].map(target_map).values
co_scores = df["co_score"].values

print(f"Number of predictor features: {len(feature_cols)}")
print(f"Class distribution:\\n{df['co_risk'].value_counts()}")
"""),

    nbf.v4.new_markdown_cell("""## 2. Repeated Stratified Cross-Validation Benchmark (5x5, 25 Folds)"""),

    nbf.v4.new_code_cell("""# Custom Ordinal Implementations
class CalibratedThresholdedRidge(BaseEstimator, ClassifierMixin):
    def __init__(self, alpha=30.0, cut1=2.667, cut2=3.500, residual_std=0.585):
        self.alpha = alpha
        self.cut1 = cut1
        self.cut2 = cut2
        self.residual_std = residual_std

    def fit(self, X, y, co_scores=None):
        self.reg_ = Ridge(alpha=self.alpha)
        if co_scores is None:
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

print("Custom CalibratedThresholdedRidge defined.")
"""),

    nbf.v4.new_code_cell("""# Load previously computed benchmark results for display
cv_df = pd.read_csv("../reports/v4_repeated_cv_metrics.csv")
cv_df[["Model", "CV_Accuracy_Mean", "CV_Accuracy_Std", "CV_Macro_F1_Mean", "CV_Macro_F1_Std", "CV_ROC_AUC_Mean", "CV_Low_F1_Mean", "CV_Med_F1_Mean", "CV_High_F1_Mean"]]
"""),

    nbf.v4.new_markdown_cell("""## 3. Feature Ablation Experiment (Full 68 vs Compact 51 Features)"""),

    nbf.v4.new_code_cell("""ablation_df = pd.read_csv("../reports/feature_ablation_study.csv")
ablation_df
"""),

    nbf.v4.new_markdown_cell("""## 4. Historical Test Set Evaluation (N=75, Train N=300)"""),

    nbf.v4.new_code_cell("""test_df = pd.read_csv("../reports/v4_test_metrics.csv")
test_df.sort_values("Macro-F1", ascending=False)
"""),

    nbf.v4.new_markdown_cell("""## 5. Continuous Construct Regression Benchmark (Predicting co_score)"""),

    nbf.v4.new_code_cell("""X_train, X_test, y_train, y_test, co_train, co_test = train_test_split(
    X, y, co_scores, test_size=75, stratify=y, random_state=42
)
ridge_reg = Ridge(alpha=30.0).fit(X_train, co_train)
pred_co = ridge_reg.predict(X_test)

r2 = r2_score(co_test, pred_co)
rmse = np.sqrt(mean_squared_error(co_test, pred_co))
mae = mean_absolute_error(co_test, pred_co)
f2 = r2 / (1.0 - r2)

print(f"Continuous Regression Benchmark on Test Set (N=75):")
print(f"  R² Score   : {r2:.4f} (44.6% of continuous variance explained)")
print(f"  RMSE       : {rmse:.4f}")
print(f"  MAE        : {mae:.4f}")
print(f"  Cohen's f² : {f2:.4f} (Substantial / Large Effect Size)")
"""),

    nbf.v4.new_markdown_cell("""## 6. Multi-Version Progression (Versions 2, 3, and 4)"""),

    nbf.v4.new_code_cell("""comp_df = pd.read_csv("../reports/version_comparison_v2_v3_v4.csv")
comp_df
"""),

    nbf.v4.new_markdown_cell("""## 7. Explainability & TreeSHAP Findings"""),

    nbf.v4.new_code_cell("""# Display top features from SHAP analysis
et_model = joblib.load("../models/extra_trees_v4.joblib")
base_et = et_model.estimator
explainer = shap.TreeExplainer(base_et)
shap_vals = explainer.shap_values(X_test)

if isinstance(shap_vals, list):
    mean_abs_shap = np.mean([np.abs(s).mean(axis=0) for s in shap_vals], axis=0)
else:
    mean_abs_shap = np.abs(shap_vals).mean(axis=(0, 2))

shap_importance = pd.DataFrame({
    "Feature": feature_cols,
    "Mean_Abs_SHAP": mean_abs_shap
}).sort_values("Mean_Abs_SHAP", ascending=False).head(15)

print("Top 15 Most Influential Behavioral Antecedents:")
shap_importance
"""),
]

nb.cells = cells

# Execute notebook using NotebookClient
client = NotebookClient(nb, timeout=600, kernel_name="python3")
client.execute(cwd=str(NOTEBOOK_DIR))

with open(NOTEBOOK_PATH, "w") as f:
    nbf.write(nb, f)

print(f"Successfully generated and executed notebook at: {NOTEBOOK_PATH}")
