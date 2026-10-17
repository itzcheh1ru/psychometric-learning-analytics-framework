"""
app/services/longitudinal/validation.py

Backend validation for Component 3: Weekly Study Record prototype input.

Validates:
- Presence of all required fields
- Rejection of unknown / unexpected fields
- Anonymised participant reference format
- Valid study week (Week 1–6)
- Numerical ranges for study hours (0–168, non-negative)
- Non-negative integer for prompt count (rejects negative numbers and floats)
- Categorical validation for academic period, learning activity, and prompt purpose
- Safe sanitisation without data persistence

Status: Prototype – data collection in progress.
"""

from typing import Any, Dict, List, Optional

from app.services.longitudinal.schemas import (
    ACADEMIC_PERIODS,
    ACCEPTED_FIELDS,
    ALLOWED_WEEKS,
    LEARNING_ACTIVITIES,
    MAX_PARTICIPANT_REF_LENGTH,
    MAX_PROMPT_COUNT,
    MAX_STUDY_HOURS,
    MIN_PROMPT_COUNT,
    MIN_STUDY_HOURS,
    PARTICIPANT_REFERENCE_PATTERN,
    PROMPT_PURPOSES,
)


class ValidationResult:
    """Holds the outcome of a weekly record validation run."""

    def __init__(
        self,
        is_valid: bool,
        errors: Optional[List[str]] = None,
        sanitized: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.is_valid = is_valid
        self.errors: List[str] = errors or []
        self.sanitized: Dict[str, Any] = sanitized or {}


def validate_weekly_record(data: Any) -> ValidationResult:
    """
    Validate and sanitize a prototype weekly study record.

    Args:
        data: Raw request body (expected dict).

    Returns:
        ValidationResult: Result object containing validity status,
        list of validation errors, and sanitized values if valid.
    """
    if not isinstance(data, dict):
        return ValidationResult(
            is_valid=False,
            errors=["Request body must be a valid JSON object."],
        )

    errors: List[str] = []
    sanitized: Dict[str, Any] = {}

    # 1. Reject unknown / unexpected fields
    unknown_fields = set(data.keys()) - ACCEPTED_FIELDS
    if unknown_fields:
        errors.append(
            f"Unknown fields are not permitted: {sorted(list(unknown_fields))}."
        )

    # 2. Check for missing required fields
    for field in sorted(list(ACCEPTED_FIELDS)):
        if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
            errors.append(f"Missing required field: '{field}'.")

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    # 3. Validate participant reference
    raw_ref = data["participant_reference"]
    if not isinstance(raw_ref, str):
        errors.append("Participant reference must be a string identifier.")
    else:
        ref = raw_ref.strip()
        if not ref:
            errors.append("Participant reference ID cannot be empty.")
        elif len(ref) > MAX_PARTICIPANT_REF_LENGTH:
            errors.append(
                f"Participant reference must not exceed {MAX_PARTICIPANT_REF_LENGTH} characters."
            )
        elif not PARTICIPANT_REFERENCE_PATTERN.match(ref):
            errors.append(
                "Participant reference must contain only letters, numbers, and hyphens (no email, names, or special symbols)."
            )
        else:
            sanitized["participant_reference"] = ref

    # 4. Validate study week
    raw_week = data["study_week"]
    if not isinstance(raw_week, str) or raw_week.strip() not in ALLOWED_WEEKS:
        errors.append(
            f"Invalid study week '{raw_week}'. Accepted weeks are: {sorted(list(ALLOWED_WEEKS))}."
        )
    else:
        sanitized["study_week"] = raw_week.strip()

    # 5. Validate AI-assisted study hours
    raw_ai_hours = data["ai_study_hours"]
    if isinstance(raw_ai_hours, bool) or not isinstance(raw_ai_hours, (int, float)):
        errors.append("AI-assisted study hours must be a valid number.")
    else:
        ai_hours = float(raw_ai_hours)
        if ai_hours < MIN_STUDY_HOURS:
            errors.append("AI-assisted study hours cannot be negative.")
        elif ai_hours > MAX_STUDY_HOURS:
            errors.append(
                f"AI-assisted study hours cannot exceed {MAX_STUDY_HOURS} hours per week."
            )
        else:
            sanitized["ai_study_hours"] = round(ai_hours, 2)

    # 6. Validate Independent study hours
    raw_ind_hours = data["independent_study_hours"]
    if isinstance(raw_ind_hours, bool) or not isinstance(raw_ind_hours, (int, float)):
        errors.append("Independent study hours must be a valid number.")
    else:
        ind_hours = float(raw_ind_hours)
        if ind_hours < MIN_STUDY_HOURS:
            errors.append("Independent study hours cannot be negative.")
        elif ind_hours > MAX_STUDY_HOURS:
            errors.append(
                f"Independent study hours cannot exceed {MAX_STUDY_HOURS} hours per week."
            )
        else:
            sanitized["independent_study_hours"] = round(ind_hours, 2)

    # 7. Validate Academic Period
    raw_period = data["academic_period"]
    if not isinstance(raw_period, str) or raw_period.strip() not in ACADEMIC_PERIODS:
        errors.append(
            f"Invalid academic period '{raw_period}'. Accepted categories: {sorted(list(ACADEMIC_PERIODS))}."
        )
    else:
        sanitized["academic_period"] = raw_period.strip()

    # 8. Validate Learning Activity
    raw_activity = data["learning_activity"]
    if not isinstance(raw_activity, str) or raw_activity.strip() not in LEARNING_ACTIVITIES:
        errors.append(
            f"Invalid learning activity '{raw_activity}'. Accepted categories: {sorted(list(LEARNING_ACTIVITIES))}."
        )
    else:
        sanitized["learning_activity"] = raw_activity.strip()

    # 9. Validate Prompt Count (must be non-negative integer, not boolean or float)
    raw_prompts = data["prompt_count"]
    if isinstance(raw_prompts, bool) or not isinstance(raw_prompts, int):
        errors.append("Prompt count must be an integer count.")
    else:
        if raw_prompts < MIN_PROMPT_COUNT:
            errors.append("Prompt count cannot be negative.")
        elif raw_prompts > MAX_PROMPT_COUNT:
            errors.append(f"Prompt count cannot exceed {MAX_PROMPT_COUNT} per week.")
        else:
            sanitized["prompt_count"] = raw_prompts

    # 10. Validate Prompt Purpose
    raw_purpose = data["prompt_purpose"]
    if not isinstance(raw_purpose, str) or raw_purpose.strip() not in PROMPT_PURPOSES:
        errors.append(
            f"Invalid prompt purpose '{raw_purpose}'. Accepted categories: {sorted(list(PROMPT_PURPOSES))}."
        )
    else:
        sanitized["prompt_purpose"] = raw_purpose.strip()

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    return ValidationResult(is_valid=True, sanitized=sanitized)
