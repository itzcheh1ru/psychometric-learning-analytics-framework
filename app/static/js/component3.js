/**
 * component3.js – Client-side logic for Component 3:
 * Longitudinal AI-Assisted Study Pattern Analytics prototype.
 *
 * Responsibilities:
 *   - Client-side validation for weekly study record inputs
 *   - POST submission to /api/component3/validate-weekly-record
 *   - Display validation outcome and sanitised record preview
 *   - Form reset
 *
 * CRITICAL RESEARCH INTEGRITY:
 *   - No longitudinal trend calculation in JavaScript
 *   - No AI Study Share calculation as research findings
 *   - No study-pattern classification or mock histories
 */

"use strict";

(function () {
    var VALIDATE_URL = "/api/component3/validate-weekly-record";

    var REQUIRED_FIELDS = [
        { id: "participant_reference", label: "Participant Reference ID", errorId: "ref_error" },
        { id: "study_week", label: "Study Week", errorId: "week_error" },
        { id: "ai_study_hours", label: "AI-Assisted Study Hours", errorId: "ai_hours_error" },
        { id: "independent_study_hours", label: "Independent Study Hours", errorId: "ind_hours_error" },
        { id: "academic_period", label: "Academic Period", errorId: "period_error" },
        { id: "learning_activity", label: "Learning Activity", errorId: "activity_error" },
        { id: "prompt_count", label: "Prompt Count", errorId: "prompt_count_error" },
        { id: "prompt_purpose", label: "Primary Prompt Purpose", errorId: "purpose_error" },
    ];

    var FIELD_LABELS = {
        participant_reference: "Participant Reference ID",
        study_week: "Study Week",
        ai_study_hours: "AI-Assisted Study Hours",
        independent_study_hours: "Independent Study Hours",
        academic_period: "Academic Period / Context",
        learning_activity: "Main Learning Activity",
        prompt_count: "Academic GenAI Prompt Count",
        prompt_purpose: "Primary Prompt Purpose",
    };

    var form = document.getElementById("weeklyRecordForm");
    var submitBtn = document.getElementById("validateWeeklyBtn");
    var resetBtn = document.getElementById("resetWeeklyBtn");

    var previewSection = document.getElementById("validationPreviewSection");
    var successBlock = document.getElementById("validationSuccessBlock");
    var errorBlock = document.getElementById("validationErrorBlock");
    var summaryBody = document.getElementById("weeklyRecordSummaryBody");
    var errorList = document.getElementById("weeklyErrorList");

    if (!form) return; // Guard: only active on component3 page

    function showFieldError(errorId, message) {
        var el = document.getElementById(errorId);
        if (el) {
            el.textContent = message;
            el.removeAttribute("hidden");
        }
    }

    function clearFieldError(errorId, inputId) {
        var el = document.getElementById(errorId);
        if (el) {
            el.textContent = "";
            el.setAttribute("hidden", "");
        }
        var input = document.getElementById(inputId);
        if (input) input.classList.remove("input--error");
    }

    function clearAllErrors() {
        REQUIRED_FIELDS.forEach(function (f) {
            clearFieldError(f.errorId, f.id);
        });
    }

    function clientValidate() {
        var isValid = true;
        clearAllErrors();

        REQUIRED_FIELDS.forEach(function (f) {
            var input = document.getElementById(f.id);
            if (!input) return;
            var val = input.value.trim();

            if (!val) {
                showFieldError(f.errorId, f.label + " is required.");
                input.classList.add("input--error");
                isValid = false;
            } else if (f.id === "ai_study_hours" || f.id === "independent_study_hours") {
                var num = parseFloat(val);
                if (isNaN(num) || num < 0 || num > 168) {
                    showFieldError(f.errorId, f.label + " must be between 0 and 168 hours.");
                    input.classList.add("input--error");
                    isValid = false;
                }
            } else if (f.id === "prompt_count") {
                var pCount = Number(val);
                if (!Number.isInteger(pCount) || pCount < 0) {
                    showFieldError(f.errorId, "Prompt count must be a non-negative whole number.");
                    input.classList.add("input--error");
                    isValid = false;
                }
            }
        });

        return isValid;
    }

    function buildPayload() {
        return {
            participant_reference: document.getElementById("participant_reference").value.trim(),
            study_week: document.getElementById("study_week").value.trim(),
            ai_study_hours: parseFloat(document.getElementById("ai_study_hours").value.trim()),
            independent_study_hours: parseFloat(document.getElementById("independent_study_hours").value.trim()),
            academic_period: document.getElementById("academic_period").value.trim(),
            learning_activity: document.getElementById("learning_activity").value.trim(),
            prompt_count: parseInt(document.getElementById("prompt_count").value.trim(), 10),
            prompt_purpose: document.getElementById("prompt_purpose").value.trim(),
        };
    }

    function renderSummary(validatedRecord) {
        if (!summaryBody) return;
        summaryBody.innerHTML = "";

        Object.keys(FIELD_LABELS).forEach(function (key) {
            if (validatedRecord[key] !== undefined && validatedRecord[key] !== null) {
                var tr = document.createElement("tr");
                var th = document.createElement("td");
                th.textContent = FIELD_LABELS[key];
                var td = document.createElement("td");
                td.textContent = String(validatedRecord[key]);
                tr.appendChild(th);
                tr.appendChild(td);
                summaryBody.appendChild(tr);
            }
        });
    }

    function showSuccess(data) {
        previewSection.removeAttribute("hidden");
        successBlock.removeAttribute("hidden");
        errorBlock.setAttribute("hidden", "");

        if (data.validated_record) {
            renderSummary(data.validated_record);
        }

        previewSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function showErrors(errors) {
        previewSection.removeAttribute("hidden");
        errorBlock.removeAttribute("hidden");
        successBlock.setAttribute("hidden", "");

        if (errorList) {
            errorList.innerHTML = "";
            errors.forEach(function (msg) {
                var li = document.createElement("li");
                li.textContent = msg;
                errorList.appendChild(li);
            });
        }

        previewSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (!clientValidate()) {
            var firstErr = form.querySelector(".form-input.input--error, .form-select.input--error");
            if (firstErr) firstErr.focus();
            return;
        }

        var payload = buildPayload();
        submitBtn.disabled = true;
        submitBtn.textContent = "Validating…";

        fetch(VALIDATE_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
        .then(function (res) {
            return res.json().then(function (data) {
                return { ok: res.ok, data: data };
            });
        })
        .then(function (result) {
            if (result.ok) {
                showSuccess(result.data);
            } else {
                var errors = (result.data && result.data.errors) ? result.data.errors : ["Validation failed."];
                showErrors(errors);
            }
        })
        .catch(function () {
            showErrors(["Could not reach the validation service. Please check your network connection."]);
        })
        .finally(function () {
            submitBtn.disabled = false;
            submitBtn.textContent = "Validate Weekly Record";
        });
    });

    if (resetBtn) {
        resetBtn.addEventListener("click", function () {
            form.reset();
            clearAllErrors();
            if (previewSection) previewSection.setAttribute("hidden", "");
            if (successBlock) successBlock.setAttribute("hidden", "");
            if (errorBlock) errorBlock.setAttribute("hidden", "");
        });
    }
})();
