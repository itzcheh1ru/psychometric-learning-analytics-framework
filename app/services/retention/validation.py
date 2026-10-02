"""
app/services/retention/validation.py

Backend validation for Component 4: Experimental Session prototype records.

Validates:
- Presence of all required session fields
- Rejection of unknown / unexpected fields
- Anonymised participant reference format
- Valid experimental condition (Brain-only vs. GenAI-assisted)
- Valid condition order for counterbalancing
- Valid session stage
- Safe task reference code format
- Explicit confirmation of research consent requirement (boolean True)
- Safe sanitisation without database persistence

Status: Prototype – experimental data collection in progress.
"""

from typing import Any, Dict, List, Optional

from app.services.retention.schemas import (
    ACCEPTED_SESSION_FIELDS,
    CONDITION_ORDERS,
    EXPERIMENTAL_CONDITIONS,
    MAX_REF_LENGTH,
    MIN_REF_LENGTH,
    PARTICIPANT_REFERENCE_PATTERN,
    SESSION_STAGES,
    TASK_REFERENCE_PATTERN,
)


class ValidationResult:
    """Holds the outcome of an experimental session validation run."""

    def __init__(
        self,
        is_valid: bool,
        errors: Optional[List[str]] = None,
        sanitized: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.is_valid = is_valid
        self.errors: List[str] = errors or []
        self.sanitized: Dict[str, Any] = sanitized or {}


def validate_experimental_session(data: Any) -> ValidationResult:
    """
    Validate and sanitize a prototype experimental session record.

    Args:
        data: Raw request payload (expected dict).

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
    unknown_fields = set(data.keys()) - ACCEPTED_SESSION_FIELDS
    if unknown_fields:
        errors.append(
            f"Unknown fields are not permitted: {sorted(list(unknown_fields))}."
        )

    # 2. Check for missing required fields
    for field in sorted(list(ACCEPTED_SESSION_FIELDS)):
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
        elif len(ref) < MIN_REF_LENGTH:
            errors.append(
                f"Participant reference must be at least {MIN_REF_LENGTH} characters."
            )
        elif len(ref) > MAX_REF_LENGTH:
            errors.append(
                f"Participant reference must not exceed {MAX_REF_LENGTH} characters."
            )
        elif not PARTICIPANT_REFERENCE_PATTERN.match(ref):
            errors.append(
                "Participant reference must contain only letters, numbers, and hyphens (no emails, names, or special symbols)."
            )
        else:
            sanitized["participant_reference"] = ref

    # 4. Validate experimental condition
    raw_cond = data["experimental_condition"]
    if not isinstance(raw_cond, str) or raw_cond.strip() not in EXPERIMENTAL_CONDITIONS:
        errors.append(
            f"Invalid experimental condition '{raw_cond}'. Accepted conditions: {sorted(list(EXPERIMENTAL_CONDITIONS))}."
        )
    else:
        sanitized["experimental_condition"] = raw_cond.strip()

    # 5. Validate condition order
    raw_order = data["condition_order"]
    if not isinstance(raw_order, str) or raw_order.strip() not in CONDITION_ORDERS:
        errors.append(
            f"Invalid condition order '{raw_order}'. Accepted orders: {sorted(list(CONDITION_ORDERS))}."
        )
    else:
        sanitized["condition_order"] = raw_order.strip()

    # 6. Validate session stage
    raw_stage = data["session_stage"]
    if not isinstance(raw_stage, str) or raw_stage.strip() not in SESSION_STAGES:
        errors.append(
            f"Invalid session stage '{raw_stage}'. Accepted stages: {sorted(list(SESSION_STAGES))}."
        )
    else:
        sanitized["session_stage"] = raw_stage.strip()

    # 7. Validate task reference code
    raw_task = data["task_reference"]
    if not isinstance(raw_task, str):
        errors.append("Task reference must be a string code.")
    else:
        task = raw_task.strip()
        if not task:
            errors.append("Task reference code cannot be empty.")
        elif len(task) < MIN_REF_LENGTH:
            errors.append(
                f"Task reference must be at least {MIN_REF_LENGTH} characters."
            )
        elif len(task) > MAX_REF_LENGTH:
            errors.append(
                f"Task reference must not exceed {MAX_REF_LENGTH} characters."
            )
        elif not TASK_REFERENCE_PATTERN.match(task):
            errors.append(
                "Task reference must contain only alphanumeric characters and hyphens (e.g. TASK01)."
            )
        else:
            sanitized["task_reference"] = task

    # 8. Validate research consent confirmation (must be strictly True)
    raw_consent = data.get("consent_confirmed")
    if not isinstance(raw_consent, bool):
        errors.append("Research consent must be a boolean True confirmation.")
    elif raw_consent is not True:
        errors.append(
            "Research consent must be confirmed according to the study protocol before session validation."
        )
    else:
        sanitized["consent_confirmed"] = True

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    return ValidationResult(is_valid=True, sanitized=sanitized)
