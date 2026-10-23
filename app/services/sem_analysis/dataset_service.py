"""
app/services/sem_analysis/dataset_service.py

Data management, questionnaire column mapping, Likert validation,
reverse-coding, missing-value analysis, and descriptive statistics
for Component 2: Algorithmic Trust & Verification Analysis (CFA & SEM).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import io

import numpy as np
import pandas as pd
from scipy import stats

from app.services.sem_analysis.schemas import SURVEY_ITEMS, CONSTRUCTS

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}

SENSITIVE_COLUMNS = {
    "id",
    "email",
    "name",
    "first name",
    "last name",
    "student id",
    "ip",
    "ip address",
    "timestamp",
    "start time",
    "completion time",
    "last modified time",
}

EXPECTED_ITEM_CODES = list(SURVEY_ITEMS.keys())


def detect_column_mapping(columns: List[str], custom_mapping: Optional[Dict[str, str]] = None) -> Tuple[Dict[str, str], List[str]]:
    """
    Map survey columns to the 19 expected research items (T1-T4, PU1-PU4, V1-V3, AD1-AD4, LC1-LC4).
    Supports exact matching, prefix/suffix matching, fuzzy wording matching, and custom mappings.
    """
    mapping: Dict[str, str] = {}
    normalized_cols = {str(c).strip(): str(c).strip().lower() for c in columns}
    custom_mapping = custom_mapping or {}

    # 1. Apply explicit custom mapping first
    for item_code, col_name in custom_mapping.items():
        if item_code in EXPECTED_ITEM_CODES and col_name in columns:
            mapping[item_code] = col_name

    # 2. Match remaining item codes
    for item_code, item_meta in SURVEY_ITEMS.items():
        if item_code in mapping:
            continue

        item_code_lower = item_code.lower()
        matched_col = None

        # Check for exact code match (case-insensitive)
        for orig_col, norm_col in normalized_cols.items():
            if norm_col == item_code_lower:
                matched_col = orig_col
                break

        # Check for code with delimiter (e.g., "at_t1", "t1_trust", "pu_pu1")
        if not matched_col:
            for orig_col, norm_col in normalized_cols.items():
                parts = [p.strip() for p in norm_col.replace("-", "_").replace(".", "_").split("_")]
                if item_code_lower in parts:
                    matched_col = orig_col
                    break

        # Check for wording keywords match
        if not matched_col:
            # Check key phrases in questionnaire wording
            wording_words = [w.lower() for w in item_meta["wording"].split() if len(w) > 4]
            best_score = 0
            best_col = None
            for orig_col, norm_col in normalized_cols.items():
                if norm_col in SENSITIVE_COLUMNS:
                    continue
                score = sum(1 for w in wording_words if w in norm_col)
                if score >= 3 and score > best_score:
                    best_score = score
                    best_col = orig_col
            if best_col and best_col not in mapping.values():
                matched_col = best_col

        if matched_col and matched_col not in mapping.values():
            mapping[item_code] = matched_col

    unmapped = [code for code in EXPECTED_ITEM_CODES if code not in mapping]
    return mapping, unmapped


def compute_descriptive_stats(df: pd.DataFrame, items: List[str]) -> Dict[str, Any]:
    """
    Compute rigorous descriptive statistics and univariate normality indices:
    Mean, SD, Median, Min, Max, Skewness, Kurtosis, and Missing count.
    """
    stats_dict: Dict[str, Any] = {}

    for item in items:
        if item not in df.columns:
            continue
        series = pd.to_numeric(df[item], errors="coerce").dropna()
        if len(series) == 0:
            continue

        mean_val = float(series.mean())
        std_val = float(series.std(ddof=1)) if len(series) > 1 else 0.0
        median_val = float(series.median())
        min_val = float(series.min())
        max_val = float(series.max())
        skew_val = float(stats.skew(series)) if len(series) > 2 else 0.0
        kurt_val = float(stats.kurtosis(series)) if len(series) > 3 else 0.0

        stats_dict[item] = {
            "mean": round(mean_val, 3),
            "sd": round(std_val, 3),
            "median": round(median_val, 3),
            "min": round(min_val, 3),
            "max": round(max_val, 3),
            "skewness": round(skew_val, 3),
            "kurtosis": round(kurt_val, 3),
            "n": int(len(series)),
        }

    # Also compute construct-level composite statistics
    construct_stats: Dict[str, Any] = {}
    for c in CONSTRUCTS:
        c_code = c["code"]
        c_items = [it for it in c["items"] if it in df.columns or (it == "AD4" and "AD4_R" in df.columns)]
        actual_cols = ["AD4_R" if it == "AD4" and "AD4_R" in df.columns else it for it in c_items]

        if actual_cols:
            c_series = df[actual_cols].mean(axis=1).dropna()
            if len(c_series) > 0:
                construct_stats[c_code] = {
                    "name": c["name"],
                    "items": actual_cols,
                    "mean": round(float(c_series.mean()), 3),
                    "sd": round(float(c_series.std(ddof=1)), 3),
                    "median": round(float(c_series.median()), 3),
                    "min": round(float(c_series.min()), 3),
                    "max": round(float(c_series.max()), 3),
                    "skewness": round(float(stats.skew(c_series)), 3) if len(c_series) > 2 else 0.0,
                    "kurtosis": round(float(stats.kurtosis(c_series)), 3) if len(c_series) > 3 else 0.0,
                    "n": int(len(c_series)),
                }

    return {
        "items": stats_dict,
        "constructs": construct_stats,
    }


def validate_and_prepare_dataset(
    file_storage_or_df: Any,
    custom_mapping: Optional[Dict[str, str]] = None,
    handle_missing: str = "listwise",
) -> Dict[str, Any]:
    """
    Read, validate, screen, map, and prepare a research dataset for CFA & SEM.

    Args:
        file_storage_or_df: Flask FileStorage, file path, bytes, or pandas DataFrame.
        custom_mapping: Optional user-provided column to item dictionary.
        handle_missing: 'listwise' (drop rows with missing items) or 'mean_impute'.

    Returns:
        Structured dictionary containing validation status, mapping, descriptives,
        and cleaned data ready for statistical estimation.
    """
    filename = "dataset.csv"
    if isinstance(file_storage_or_df, pd.DataFrame):
        df = file_storage_or_df.copy()
    else:
        if not file_storage_or_df or not getattr(file_storage_or_df, "filename", None):
            raise ValueError("Please select a dataset file.")

        filename = Path(file_storage_or_df.filename).name
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Only CSV (.csv) and Excel (.xlsx) files are supported.")

        try:
            if extension == ".csv":
                df = pd.read_csv(file_storage_or_df, nrows=10001)
            else:
                df = pd.read_excel(file_storage_or_df, nrows=10001, engine="openpyxl")
        except Exception as exc:
            raise ValueError(f"The file could not be read: {str(exc)}") from exc

    if len(df) == 0:
        raise ValueError("The uploaded dataset is empty.")

    if len(df) > 10000:
        raise ValueError("The dataset exceeds the 10,000-row limit.")

    if len(df.columns) == 0:
        raise ValueError("No columns were found in the dataset.")

    # Check for empty or duplicate column names
    normalized_columns = [str(col).strip().lower() for col in df.columns]
    if any(not col for col in normalized_columns):
        raise ValueError("The dataset contains an empty column name.")

    if len(normalized_columns) != len(set(normalized_columns)):
        raise ValueError("Duplicate column names were found in the dataset. Please remove duplicate headers.")

    # Privacy check: identify sensitive participant fields
    sensitive_columns_found = [
        str(col) for col in df.columns if str(col).strip().lower() in SENSITIVE_COLUMNS
    ]

    # Map survey columns to psychometric items
    mapping, unmapped = detect_column_mapping(list(df.columns), custom_mapping)

    if len(mapping) == 0:
        raise ValueError(
            "None of the required questionnaire items (T1-T4, PU1-PU4, V1-V3, AD1-AD4, LC1-LC4) "
            "could be mapped automatically. Please ensure column headers match item codes."
        )

    # Extract mapped item dataframe
    mapped_df = pd.DataFrame()
    for item_code, orig_col in mapping.items():
        mapped_df[item_code] = pd.to_numeric(df[orig_col], errors="coerce")

    # Likert scale validation (1-5 range check)
    out_of_bounds_items = {}
    for col in mapped_df.columns:
        valid_vals = mapped_df[col].dropna()
        if len(valid_vals) > 0:
            invalid_count = int(((valid_vals < 1) | (valid_vals > 5)).sum())
            if invalid_count > 0:
                out_of_bounds_items[col] = invalid_count

    if out_of_bounds_items:
        details = ", ".join([f"{k} ({v} invalid values)" for k, v in out_of_bounds_items.items()])
        raise ValueError(
            f"Likert scale validation failed: Items must have values between 1 and 5 (1=Strongly Disagree, 5=Strongly Agree). "
            f"Found out-of-range values in: {details}"
        )

    # Missing value handling
    initial_rows = len(mapped_df)
    total_missing_cells = int(mapped_df.isna().sum().sum())
    missing_per_item = {col: int(mapped_df[col].isna().sum()) for col in mapped_df.columns}

    cleaned_df = mapped_df.copy()
    if handle_missing == "mean_impute":
        for col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
    else:
        # Default: listwise deletion for complete cases analysis
        cleaned_df = cleaned_df.dropna()

    valid_rows = len(cleaned_df)

    if valid_rows < 30:
        raise ValueError(
            f"Insufficient valid cases: The dataset contains only {valid_rows} complete responses after screening. "
            f"A minimum of 30 complete responses is required to compute psychometric statistics."
        )

    # Reverse coding for AD4 (Autonomy item in AI Dependence scale)
    # AD4: "I can independently analyze and solve coursework problems without using Generative AI."
    # Reverse coded: AD4_R = 6 - AD4
    reverse_coded_applied = False
    if "AD4" in cleaned_df.columns:
        cleaned_df["AD4_R"] = 6.0 - cleaned_df["AD4"]
        reverse_coded_applied = True

    # Sample size assessment for SEM
    # Rule of thumb: at least 10 observations per indicator (19 * 10 = 190) or N >= 100
    if valid_rows < 100:
        sample_assessment = {
            "status": "marginal",
            "message": f"Sample size (N={valid_rows}) is suitable for exploratory analysis but below the recommended N=100+ for stable asymptotic SEM fit indices.",
            "adequate": False,
        }
    elif valid_rows < 200:
        sample_assessment = {
            "status": "acceptable",
            "message": f"Sample size (N={valid_rows}) is acceptable for Confirmatory Factor Analysis and Structural Equation Modeling.",
            "adequate": True,
        }
    else:
        sample_assessment = {
            "status": "good",
            "message": f"Sample size (N={valid_rows}) provides strong statistical power for CFA and SEM path estimation.",
            "adequate": True,
        }

    # Compute descriptive statistics
    items_to_describe = [c for c in cleaned_df.columns if c != "AD4_R"]
    if "AD4_R" in cleaned_df.columns:
        items_to_describe.append("AD4_R")
    descriptives = compute_descriptive_stats(cleaned_df, items_to_describe)

    return {
        "success": True,
        "filename": filename,
        "rows": initial_rows,
        "valid_rows": valid_rows,
        "columns": int(len(df.columns)),
        "missing_values": total_missing_cells,
        "missing_per_item": missing_per_item,
        "duplicate_rows": int(df.duplicated().sum()),
        "sensitive_columns_detected": len(sensitive_columns_found),
        "sensitive_column_names": sensitive_columns_found,
        "mapping": mapping,
        "unmapped_items": unmapped,
        "all_items_mapped": len(unmapped) == 0,
        "reverse_coded_applied": reverse_coded_applied,
        "reverse_coded_formula": "AD4_R = 6 - AD4 (Autonomy item converted to Dependence polarity)",
        "sample_size_assessment": sample_assessment,
        "descriptive_statistics": descriptives,
        "cleaned_data": cleaned_df,
        "message": (
            f"Dataset validated successfully with {valid_rows} complete cases. "
            f"Mapped {len(mapping)}/19 psychometric items. "
            f"{'Reverse coding applied to AD4.' if reverse_coded_applied else ''}"
        ),
    }


def validate_dataset(file_storage):
    """
    Backwards-compatible wrapper matching the previous simple validation interface.
    """
    result = validate_and_prepare_dataset(file_storage)
    # Return minimal summary expected by existing tests
    return {
        "success": True,
        "filename": result["filename"],
        "rows": result["rows"],
        "columns": result["columns"],
        "missing_values": result["missing_values"],
        "duplicate_rows": result["duplicate_rows"],
        "sensitive_columns_detected": result["sensitive_columns_detected"],
        "column_names": [str(c) for c in result["mapping"].values()],
        "message": (
            "Dataset read successfully. Review data quality and privacy "
            "before proceeding to statistical analysis."
        ),
    }
