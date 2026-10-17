"""
app/services/cognitive_offloading/validation.py

Backend input validation and sanitization for the Component 1
prototype input form.

Validates:
- required field presence
- allowed category values per schema
- participant reference format (alphanumeric/hyphen, max 20 chars)
- rejects any field value not defined in the allowed schema
- does not persist or log submitted values

Status: Prototype — research data collection in progress.
"""

from __future__ import annotations

from typing import Any

from app.services.cognitive_offloading.schemas import (
    FIELD_ALLOWED_VALUES,
    PARTICIPANT_REFERENCE_PATTERN,
    MAX_PARTICIPANT_REF_LENGTH,
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS,
)


# --------------------------------------------------------------------------- #
# Result dataclass                                                             #
# --------------------------------------------------------------------------- #

class ValidationResult:
    """Holds the outcome of a prototype input validation run."""

    def __init__(
        self,
        is_valid: bool,
        errors: list[str] | None = None,
        sanitized: dict[str, str] | None = None,
    ) -> None:
        self.is_valid = is_valid
        self.errors: list[str] = errors or []
        self.sanitized: dict[str, str] = sanitized or {}


# --------------------------------------------------------------------------- #
# Public validation function                                                   #
# --------------------------------------------------------------------------- #

def validate_prototype_input(data: dict[str, Any]) -> ValidationResult:
    """
    Validate and sanitize a prototype behavioural input payload.

    Args:
        data: Raw request payload (dict from JSON body).

    Returns:
        ValidationResult with is_valid flag, list of errors, and
        sanitized values if valid.

    Note:
        This function does NOT perform any cognitive-offloading risk
        prediction. It only validates that the submitted behavioural
        predictor values conform to the prototype schema.
    """
    if not isinstance(data, dict):
        return ValidationResult(is_valid=False, errors=["Request body must be a JSON object."])

    errors: list[str] = []
    sanitized: dict[str, str] = {}

    # -- 1. Check for required fields --------------------------------------- #
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            errors.append(f"Missing required field: '{field}'.")

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    # -- 2. Validate participant reference ---------------------------------- #
    ref = str(data["participant_reference"]).strip()
    if len(ref) > MAX_PARTICIPANT_REF_LENGTH:
        errors.append(
            f"Participant reference must not exceed {MAX_PARTICIPANT_REF_LENGTH} characters."
        )
    elif not PARTICIPANT_REFERENCE_PATTERN.match(ref):
        errors.append(
            "Participant reference must contain only letters, digits and hyphens "
            "(no names, emails, or personal identifiers)."
        )
    else:
        sanitized["participant_reference"] = ref

    # -- 3. Validate categorical fields ------------------------------------- #
    all_fields = REQUIRED_FIELDS[1:] + OPTIONAL_FIELDS  # exclude participant_reference
    for field in all_fields:
        raw_value = data.get(field)

        # Optional fields may be absent or blank
        if field in OPTIONAL_FIELDS and (raw_value is None or str(raw_value).strip() == ""):
            continue

        value = str(raw_value).strip() if raw_value is not None else ""

        allowed = FIELD_ALLOWED_VALUES.get(field, set())
        if value not in allowed:
            errors.append(
                f"Invalid value for '{field}': '{value}'. "
                f"Accepted values are: {sorted(allowed)}."
            )
        else:
            sanitized[field] = value

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    return ValidationResult(is_valid=True, sanitized=sanitized)
