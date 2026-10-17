/**
 * component1.js – Client-side logic for the Component 1 prototype workflow.
 * Psychometric Learning Analytics Framework – J26-DS-310
 *
 * Responsibilities:
 *   - Required-field client-side validation (before sending to API)
 *   - Submit form data as JSON via fetch() to /api/component1/validate-input
 *   - Render validation success/error results
 *   - Populate the prototype input summary table
 *   - Reset form
 *
 * IMPORTANT:
 *   - No risk prediction logic is present here.
 *   - No risk probability is calculated in the frontend.
 *   - No fake risk category is determined here.
 *   - Research decisions are made only by trained models (pending).
 */

"use strict";

(function () {

    /* ------------------------------------------------------------------
       Constants
    ------------------------------------------------------------------ */
    var VALIDATE_URL = "/api/component1/validate-input";

    var REQUIRED_FIELDS = [
        { id: "participant_reference", label: "Participant Reference ID",         errorId: "ref_error" },
        { id: "genai_usage_frequency", label: "GenAI Usage Frequency",           errorId: "freq_error" },
        { id: "weekly_genai_usage",    label: "Weekly GenAI Usage",              errorId: "weekly_error" },
        { id: "academic_purpose",      label: "Main Academic Purpose",           errorId: "purpose_error" },
        { id: "verification_frequency",label: "Verification Frequency",          errorId: "verif_error" },
        { id: "independent_learning",  label: "Independent Learning Engagement", errorId: "indep_error" },
    ];

    var FIELD_LABELS = {
        participant_reference:  "Participant Reference ID",
        genai_usage_frequency:  "GenAI Usage Frequency",
        weekly_genai_usage:     "Weekly GenAI Usage",
        academic_purpose:       "Main Academic Purpose",
        verification_frequency: "Verification Frequency",
        independent_learning:   "Independent Learning Engagement",
        academic_year:          "Academic Year",
    };

    /* ------------------------------------------------------------------
       DOM references
    ------------------------------------------------------------------ */
    var form        = document.getElementById("component1Form");
    var submitBtn   = document.getElementById("submitBtn");
    var resetBtn    = document.getElementById("resetBtn");

    var resultSection   = document.getElementById("validationResultSection");
    var successDiv      = document.getElementById("validationSuccess");
    var errorDiv        = document.getElementById("validationError");
    var errorList       = document.getElementById("errorList");
    var summaryTbody    = document.getElementById("summaryTableBody");

    if (!form) return; // Guard: only run on component1 page

    /* ------------------------------------------------------------------
       Utility: show / hide inline field error
    ------------------------------------------------------------------ */
    function showFieldError(errorId, message) {
        var el = document.getElementById(errorId);
        if (!el) return;
        el.textContent = message;
        el.removeAttribute("hidden");
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

    function clearAllFieldErrors() {
        REQUIRED_FIELDS.forEach(function (f) {
            clearFieldError(f.errorId, f.id);
        });
        clearFieldError("year_error", "academic_year");
    }

    /* ------------------------------------------------------------------
       Client-side validation
    ------------------------------------------------------------------ */
    function clientValidate() {
        var errors = [];
        clearAllFieldErrors();

        REQUIRED_FIELDS.forEach(function (f) {
            var el = document.getElementById(f.id);
            if (!el) return;
            var val = el.value.trim();
            if (!val) {
                errors.push(f.label + " is required.");
                showFieldError(f.errorId, f.label + " is required.");
                el.classList.add("input--error");
            }
        });

        return errors.length === 0;
    }

    /* ------------------------------------------------------------------
       Build JSON payload from form
    ------------------------------------------------------------------ */
    function buildPayload() {
        var payload = {};
        var ids = [
            "participant_reference",
            "genai_usage_frequency",
            "weekly_genai_usage",
            "academic_purpose",
            "verification_frequency",
            "independent_learning",
            "academic_year",
        ];
        ids.forEach(function (id) {
            var el = document.getElementById(id);
            if (el) {
                var val = el.value.trim();
                if (val) payload[id] = val;
            }
        });
        return payload;
    }

    /* ------------------------------------------------------------------
       Render: populate summary table
    ------------------------------------------------------------------ */
    function populateSummary(validatedInput) {
        if (!summaryTbody) return;
        summaryTbody.innerHTML = "";

        Object.keys(FIELD_LABELS).forEach(function (key) {
            if (validatedInput[key]) {
                var tr = document.createElement("tr");
                var th = document.createElement("td");
                th.textContent = FIELD_LABELS[key];
                var td = document.createElement("td");
                td.textContent = validatedInput[key];
                tr.appendChild(th);
                tr.appendChild(td);
                summaryTbody.appendChild(tr);
            }
        });
    }

    /* ------------------------------------------------------------------
       Render: show success state
    ------------------------------------------------------------------ */
    function showSuccess(responseData) {
        resultSection.removeAttribute("hidden");
        successDiv.removeAttribute("hidden");
        errorDiv.setAttribute("hidden", "");

        if (responseData.validated_input) {
            populateSummary(responseData.validated_input);
        }

        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    /* ------------------------------------------------------------------
       Render: show server-side error state
    ------------------------------------------------------------------ */
    function showServerErrors(errors) {
        resultSection.removeAttribute("hidden");
        errorDiv.removeAttribute("hidden");
        successDiv.setAttribute("hidden", "");

        if (errorList) {
            errorList.innerHTML = "";
            errors.forEach(function (msg) {
                var li = document.createElement("li");
                li.textContent = msg;
                errorList.appendChild(li);
            });
        }

        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    /* ------------------------------------------------------------------
       Render: show network / unexpected error
    ------------------------------------------------------------------ */
    function showNetworkError(message) {
        resultSection.removeAttribute("hidden");
        errorDiv.removeAttribute("hidden");
        successDiv.setAttribute("hidden", "");

        if (errorList) {
            errorList.innerHTML = "";
            var li = document.createElement("li");
            li.textContent = message || "An unexpected error occurred. Please try again.";
            errorList.appendChild(li);
        }

        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    /* ------------------------------------------------------------------
       Form submission
    ------------------------------------------------------------------ */
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        // Client-side validation first
        if (!clientValidate()) {
            // Scroll to the first error
            var firstError = form.querySelector(".form-input.input--error, .form-select.input--error");
            if (firstError) firstError.focus();
            return;
        }

        var payload = buildPayload();

        // Disable submit button during request
        submitBtn.disabled = true;
        submitBtn.textContent = "Validating…";

        fetch(VALIDATE_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
        .then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, status: response.status, data: data };
            });
        })
        .then(function (result) {
            if (result.ok) {
                showSuccess(result.data);
            } else {
                var errors = (result.data && result.data.errors) ? result.data.errors : ["Validation failed."];
                showServerErrors(errors);
            }
        })
        .catch(function () {
            showNetworkError("Could not reach the validation service. Please check your connection.");
        })
        .finally(function () {
            submitBtn.disabled = false;
            submitBtn.textContent = "Validate Prototype Input";
        });
    });

    /* ------------------------------------------------------------------
       Reset button
    ------------------------------------------------------------------ */
    if (resetBtn) {
        resetBtn.addEventListener("click", function () {
            form.reset();
            clearAllFieldErrors();
            if (resultSection) resultSection.setAttribute("hidden", "");
            if (successDiv)    successDiv.setAttribute("hidden", "");
            if (errorDiv)      errorDiv.setAttribute("hidden", "");
        });
    }

}());
