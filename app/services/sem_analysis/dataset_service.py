"""
app/services/sem_analysis/dataset_service.py

Data management, questionnaire column mapping, Likert scale cleaning & validation,
informed consent filtering, reverse-coding management, missing-value analysis,
and descriptive statistics for Component 2: Algorithmic Trust & Verification Analysis (CFA & SEM).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import io

import numpy as np
import pandas as pd
from scipy import stats

from app.services.sem_analysis.schemas import (
    CONSTRUCTS,
    SURVEY_ITEMS,
    SURVEY_ITEMS_EMPIRICAL_26,
    SURVEY_ITEMS_LEGACY_19,
)

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

LIKERT_VALUE_MAP: Dict[str, int] = {
    "strongly disagree": 1,
    "strongly disagree ": 1,
    "disagree": 2,
    "neutral": 3,
    "neither agree nor disagree": 3,
    "agree": 4,
    "strongly agree": 5,
}

# Key distinctive phrases for mapping full question wording from survey exports
DISTINCTIVE_QUESTION_PHRASES: Dict[str, List[str]] = {
    # Algorithmic Trust (AT) - 6 items
    "AT1": ["reliable information", "academic learning activities"],
    "AT2": ["consistent responses", "learning tasks"],
    "AT3": ["generally accurate", "academic purposes"],
    "AT4": ["explanations or solutions", "academic problems"],
    "AT5": ["more when they provide clear explanations", "clear explanations for their answers"],
    "AT6": ["appropriate support", "trusted to provide appropriate support"],
    # Verification Behaviour (VB) - 5 items
    "VB1": ["verify information provided", "before using it in academic work"],
    "VB2": ["compare generative ai-generated", "textbooks, lecture materials", "reliable sources"],
    "VB3": ["check whether generative ai responses are accurate", "accurate before accepting"],
    "VB4": ["understand the reasoning behind", "copying the output"],
    "VB5": ["modify or correct", "after reviewing its accuracy"],
    # Perceived Usefulness (PU) - 5 items
    "PU1": ["improves my understanding", "academic concepts and learning"],
    "PU2": ["complete academic tasks more effectively"],
    "PU3": ["increase my productivity", "studying or preparing"],
    "PU4": ["useful for achieving my academic learning goals"],
    "PU5": ["learn difficult topics by providing explanations"],
    # AI Dependence (AD) - 5 items
    "AD1": ["rely on generative ai tools when i face difficulties"],
    "AD2": ["frequently depend on generative ai-generated answers"],
    "AD3": ["instead of solving some academic problems independently", "use generative ai assistance instead"],
    "AD4": ["important part of my learning process"],
    "AD5": ["difficult to complete some academic tasks without assistance"],
    # Learning Confidence (LC) - 5 items
    "LC1": ["feel more capable of learning new academic concepts"],
    "LC2": ["feel more confident when solving academic problems"],
    "LC3": ["feel more capable of completing academic tasks after receiving support"],
    "LC4": ["feel more confident in my ability to complete academic tasks after using"],
    "LC5": ["approach challenging academic tasks with greater confidence"],
    # Legacy items (autonomy wording for AD4)
    "AD4_LEGACY": ["independently analyze and solve", "without using generative ai"],
}


LEGACY_19_ITEM_CODES = [
    "T1", "T2", "T3", "T4",
    "PU1", "PU2", "PU3", "PU4",
    "V1", "V2", "V3",
    "AD1", "AD2", "AD3", "AD4",
    "LC1", "LC2", "LC3", "LC4",
]

EMPIRICAL_26_ITEM_CODES = list(SURVEY_ITEMS_EMPIRICAL_26.keys())


def clean_likert_cell(val: Any) -> float:
    """
    Convert a raw Likert cell value (numeric or text string) into a numeric float.
    Normalizes non-breaking spaces, case, and standard Likert descriptors.
    Returns float(val) for numbers (even out-of-bounds numbers so range validation detects them).
    Returns np.nan if unparseable text or missing.
    """
    if pd.isna(val):
        return np.nan

    # If already a number, return float (preserve out-of-range values like 7 so range check catches it)
    if isinstance(val, (int, float, np.integer, np.floating)):
        try:
            return float(val)
        except (ValueError, TypeError):
            return np.nan

    # String cleaning & normalization
    s = str(val).replace("\xa0", " ").strip().lower()

    if s in LIKERT_VALUE_MAP:
        return float(LIKERT_VALUE_MAP[s])

    # Try numeric string (e.g. "4", "7", "5.0")
    try:
        return float(s)
    except (ValueError, TypeError):
        pass

    return np.nan


def filter_informed_consent(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Identify informed consent column and filter out participant records that declined consent.
    Returns (filtered_df, excluded_count).
    """
    consent_col = None
    for col in df.columns:
        norm = str(col).replace("\xa0", " ").strip().lower()
        if any(term in norm for term in ["consent", "voluntary", "participation", "participat", "agree to participate"]):
            consent_col = col
            break

    # If not found by keyword, check column index 4 if available
    if consent_col is None and len(df.columns) > 4:
        sample_val = str(df.iloc[0, 4]).replace("\xa0", " ").strip().lower()
        if "agree" in sample_val or "participat" in sample_val:
            consent_col = df.columns[4]

    if consent_col is None:
        return df.copy(), 0

    # Filter for positive consent
    consent_series = df[consent_col].astype(str).str.replace("\xa0", " ").str.strip().str.lower()
    is_consented = consent_series == "i agree to participate"
    filtered_df = df[is_consented].copy()
    excluded_count = int(len(df) - len(filtered_df))

    return filtered_df, excluded_count


def detect_column_mapping(
    columns: List[str], custom_mapping: Optional[Dict[str, str]] = None
) -> Tuple[Dict[str, str], List[str]]:
    """
    Map survey columns to psychometric item codes.
    Supports:
    - 26-item empirical instrument (AT1-AT6, VB1-VB5, PU1-PU5, AD1-AD5, LC1-LC5)
    - 19-item synthetic/legacy instrument (T1-T4, PU1-PU4, V1-V3, AD1-AD4, LC1-LC4)
    - Full questionnaire text wording matching
    - Explicit custom mappings
    """
    mapping: Dict[str, str] = {}
    normalized_cols = {str(c).strip(): str(c).replace("\xa0", " ").strip().lower() for c in columns}
    custom_mapping = custom_mapping or {}

    # 1. Apply explicit custom mapping first
    for item_code, col_name in custom_mapping.items():
        if col_name in columns:
            mapping[item_code] = col_name

    # Determine whether the dataset is using empirical 26-item or legacy 19-item naming
    # Check unique schema markers
    has_legacy_unique = any(
        norm_col in ["t1", "t2", "t3", "t4", "v1", "v2", "v3"]
        for norm_col in normalized_cols.values()
    )
    has_empirical_unique = any(
        norm_col in ["at1", "at2", "at3", "at4", "at5", "at6", "vb1", "vb2", "vb3", "vb4", "vb5", "pu5", "ad5", "lc5"]
        for norm_col in normalized_cols.values()
    )

    preferred_item_codes = (
        LEGACY_19_ITEM_CODES if (has_legacy_unique and not has_empirical_unique)
        else EMPIRICAL_26_ITEM_CODES
    )

    # 2. Match exact codes
    for item_code in preferred_item_codes + list(SURVEY_ITEMS.keys()):
        if item_code in mapping:
            continue

        item_code_lower = item_code.lower()
        matched_col = None

        # Exact code match
        for orig_col, norm_col in normalized_cols.items():
            if norm_col == item_code_lower:
                matched_col = orig_col
                break

        # Delimited code match (e.g., "at_at1", "vb_1", "pu-1")
        if not matched_col:
            for orig_col, norm_col in normalized_cols.items():
                parts = [p.strip() for p in norm_col.replace("-", "_").replace(".", "_").split("_")]
                if item_code_lower in parts:
                    matched_col = orig_col
                    break

        if matched_col and matched_col not in mapping.values():
            mapping[item_code] = matched_col

    # 3. Match by question wording key phrases (for raw survey export headers)
    for item_code, phrases in DISTINCTIVE_QUESTION_PHRASES.items():
        target_code = "AD4" if item_code == "AD4_LEGACY" else item_code
        if target_code in mapping:
            continue

        best_score = 0
        best_col = None

        for orig_col, norm_col in normalized_cols.items():
            if norm_col in SENSITIVE_COLUMNS or orig_col in mapping.values():
                continue

            score = sum(1 for phrase in phrases if phrase in norm_col)
            if score > 0 and score > best_score:
                best_score = score
                best_col = orig_col

        if best_col and best_col not in mapping.values():
            mapping[target_code] = best_col

    expected_set = preferred_item_codes
    unmapped = [code for code in expected_set if code not in mapping]
    return mapping, unmapped


def compute_descriptive_stats(df: pd.DataFrame, items: List[str]) -> Dict[str, Any]:
    """
    Compute rigorous descriptive statistics and univariate normality indices:
    Mean, SD, Median, Min, Max, Skewness, Kurtosis, and Valid N.
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

    # Construct-level composite statistics
    construct_stats: Dict[str, Any] = {}
    for c in CONSTRUCTS:
        c_code = c["code"]
        c_items = [it for it in c["items"] if it in df.columns]
        # Also check legacy items if empirical items not found
        if not c_items and "legacy_items" in c:
            c_items = [it for it in c["legacy_items"] if it in df.columns or (it == "AD4" and "AD4_R" in df.columns)]

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
    Read, clean, screen for consent, map columns, clean Likert responses,
    validate ranges, and prepare an empirical or demo research dataset for CFA & SEM.
    """
    filename = "dataset.csv"
    if isinstance(file_storage_or_df, pd.DataFrame):
        raw_df = file_storage_or_df.copy()
    else:
        if not file_storage_or_df or not getattr(file_storage_or_df, "filename", None):
            raise ValueError("Please select a dataset file.")

        filename = Path(file_storage_or_df.filename).name
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Only CSV (.csv) and Excel (.xlsx) files are supported.")

        try:
            if extension == ".csv":
                raw_df = pd.read_csv(file_storage_or_df, nrows=10001)
            else:
                raw_df = pd.read_excel(file_storage_or_df, nrows=10001, engine="openpyxl")
        except Exception as exc:
            raise ValueError(f"The file could not be read: {str(exc)}") from exc

    if len(raw_df) == 0:
        raise ValueError("The uploaded dataset is empty.")

    if len(raw_df) > 10000:
        raise ValueError("The dataset exceeds the 10,000-row limit.")

    if len(raw_df.columns) == 0:
        raise ValueError("No columns were found in the dataset.")

    # 1. Privacy screening & sensitive fields detection
    sensitive_columns_found = [
        str(col) for col in raw_df.columns
        if str(col).replace("\xa0", " ").strip().lower() in SENSITIVE_COLUMNS
    ]

    # 2. Informed consent screening
    consented_df, excluded_consent_rows = filter_informed_consent(raw_df)

    # 3. Detect column mapping to psychometric items
    mapping, unmapped = detect_column_mapping(list(consented_df.columns), custom_mapping)

    if len(mapping) == 0:
        raise ValueError(
            "None of the required questionnaire items could be mapped automatically. "
            "Please ensure column headers match research item codes or questionnaire wording."
        )

    # 4. Extract mapped columns and apply Likert text-to-numeric cleaning
    mapped_df = pd.DataFrame()
    for item_code, orig_col in mapping.items():
        mapped_df[item_code] = consented_df[orig_col].apply(clean_likert_cell)

    # 5. Validate Likert scale boundaries (1 to 5)
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

    # 6. Missing value screening & handling
    initial_rows = len(mapped_df)
    total_missing_cells = int(mapped_df.isna().sum().sum())
    missing_per_item = {col: int(mapped_df[col].isna().sum()) for col in mapped_df.columns}

    cleaned_df = mapped_df.copy()
    if handle_missing == "mean_impute":
        for col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
    else:
        # Default: listwise deletion for complete cases
        cleaned_df = cleaned_df.dropna()

    valid_rows = len(cleaned_df)

    if valid_rows < 30:
        raise ValueError(
            f"Insufficient valid cases: The dataset contains only {valid_rows} complete responses after screening. "
            f"A minimum of 30 complete responses is required to compute psychometric statistics."
        )

    # 7. Reverse-coding management
    # Scientific Rule: Only reverse-code if evidence from wording/scale supports it.
    # In the empirical 26-item survey, all AD items are standard polarity.
    # Reverse coding is ONLY applied for legacy 19-item synthetic datasets where AD4 is the autonomy item.
    is_legacy_19 = any(k in mapping for k in ["T1", "V1"])
    reverse_coded_applied = False
    if is_legacy_19 and "AD4" in cleaned_df.columns:
        cleaned_df["AD4_R"] = 6.0 - cleaned_df["AD4"]
        reverse_coded_applied = True

    # 8. Sample size assessment for SEM
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

    # 9. Compute descriptive statistics
    items_to_describe = [c for c in cleaned_df.columns if c != "AD4_R"]
    if "AD4_R" in cleaned_df.columns:
        items_to_describe.append("AD4_R")
    descriptives = compute_descriptive_stats(cleaned_df, items_to_describe)

    return {
        "success": True,
        "filename": filename,
        "rows": initial_rows,
        "valid_rows": valid_rows,
        "excluded_consent_rows": excluded_consent_rows,
        "columns": int(len(raw_df.columns)),
        "missing_values": total_missing_cells,
        "missing_per_item": missing_per_item,
        "duplicate_rows": int(raw_df.duplicated().sum()),
        "sensitive_columns_detected": len(sensitive_columns_found),
        "sensitive_column_names": sensitive_columns_found,
        "mapping": mapping,
        "unmapped_items": unmapped,
        "all_items_mapped": len(unmapped) == 0,
        "reverse_coded_applied": reverse_coded_applied,
        "reverse_coded_formula": (
            "AD4_R = 6 - AD4 (Legacy Autonomy item converted to Dependence polarity)"
            if reverse_coded_applied else "None (All empirical items standard polarity)"
        ),
        "sample_size_assessment": sample_assessment,
        "descriptive_statistics": descriptives,
        "cleaned_data": cleaned_df,
        "message": (
            f"Dataset validated successfully with {valid_rows} complete cases. "
            f"Mapped {len(mapping)} psychometric items. "
            f"{f'Filtered {excluded_consent_rows} non-consenting records. ' if excluded_consent_rows > 0 else ''}"
            f"{'Reverse coding applied to AD4.' if reverse_coded_applied else ''}"
        ),
    }


def validate_dataset(file_storage):
    """
    Backwards-compatible wrapper matching the previous simple validation interface.
    """
    result = validate_and_prepare_dataset(file_storage)
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
