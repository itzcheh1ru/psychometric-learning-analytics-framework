/**
 * component4.js – Client-side logic for Component 4:
 * GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation prototype.
 *
 * Responsibilities:
 *   - Client-side validation for experimental session prototype inputs
 *   - POST submission to /api/component4/validate-session
 *   - Display validation outcome and sanitised session preview
 *   - Form reset
 *
 * CRITICAL RESEARCH INTEGRITY:
 *   - No recall score or learning retention calculation in JavaScript
 *   - No simulated NLP metrics (diversity, readability, similarity)
 *   - No condition superiority claims or fabricated findings
 *   - In-memory validation display only; no persistence
 */

"use strict";

(function () {
    var VALIDATE_URL = "/api/component4/validate-session";

    var REQUIRED_FIELDS = [
        { id: "participant_reference", label: "Participant Reference ID", errorId: "ref_error" },
        { id: "experimental_condition", label: "Experimental Condition", errorId: "cond_error" },
        { id: "condition_order", label: "Condition Order", errorId: "order_error" },
        { id: "session_stage", label: "Session Stage", errorId: "stage_error" },
        { id: "task_reference", label: "Task Reference Code", errorId: "task_error" },
        { id: "consent_confirmed", label: "Research Consent", errorId: "consent_error" },
    ];

    var FIELD_LABELS = {
        participant_reference: "Participant Reference ID",
        experimental_condition: "Experimental Condition",
        condition_order: "Condition Order",
        session_stage: "Session Stage",
        task_reference: "Task Reference Code",
        consent_confirmed: "Research Consent Status",
    };

    var REF_PATTERN = /^[A-Za-z0-9_-]{2,20}$/;

    var form = document.getElementById("sessionRecordForm");
    var submitBtn = document.getElementById("validateSessionBtn");
    var resetBtn = document.getElementById("resetSessionBtn");

    var previewSection = document.getElementById("sessionPreviewSection");
    var successBlock = document.getElementById("sessionSuccessBlock");
    var errorBlock = document.getElementById("sessionErrorBlock");
    var summaryBody = document.getElementById("sessionSummaryBody");
    var errorList = document.getElementById("sessionErrorList");

    if (!form) return; // Guard: only active on component4 page

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

            if (f.id === "consent_confirmed") {
                if (!input.checked) {
                    showFieldError(f.errorId, "Research consent confirmation is required to proceed.");
                    isValid = false;
                }
                return;
            }

            var val = input.value.trim();

            if (!val) {
                showFieldError(f.errorId, f.label + " is required.");
                input.classList.add("input--error");
                isValid = false;
            } else if (f.id === "participant_reference") {
                if (!REF_PATTERN.test(val)) {
                    showFieldError(
                        f.errorId,
                        "Participant reference must be 2-20 alphanumeric characters (hyphens and underscores permitted)."
                    );
                    input.classList.add("input--error");
                    isValid = false;
                }
            } else if (f.id === "task_reference") {
                if (!REF_PATTERN.test(val)) {
                    showFieldError(
                        f.errorId,
                        "Task reference must be 2-20 alphanumeric characters (hyphens and underscores permitted)."
                    );
                    input.classList.add("input--error");
                    isValid = false;
                }
            }
        });

        return isValid;
    }

    function renderSummary(session) {
        if (!summaryBody) return;
        summaryBody.innerHTML = "";

        var order = [
            "participant_reference",
            "experimental_condition",
            "condition_order",
            "session_stage",
            "task_reference",
            "consent_confirmed",
        ];

        order.forEach(function (key) {
            if (!(key in session)) return;
            var tr = document.createElement("tr");

            var th = document.createElement("th");
            th.scope = "row";
            th.textContent = FIELD_LABELS[key] || key;

            var td = document.createElement("td");
            var val = session[key];
            if (typeof val === "boolean") {
                td.textContent = val ? "Confirmed (True)" : "Not Confirmed (False)";
            } else {
                td.textContent = String(val);
            }

            tr.appendChild(th);
            tr.appendChild(td);
            summaryBody.appendChild(tr);
        });

        // Add note indicating prototype status
        var noteTr = document.createElement("tr");
        var noteTh = document.createElement("th");
        noteTh.scope = "row";
        noteTh.textContent = "Data Status";
        var noteTd = document.createElement("td");
        noteTd.textContent = "Prototype validation passed (Not persisted; in-memory only)";
        noteTr.appendChild(noteTh);
        noteTr.appendChild(noteTd);
        summaryBody.appendChild(noteTr);
    }

    function renderErrors(errors) {
        if (!errorList) return;
        errorList.innerHTML = "";
        errors.forEach(function (msg) {
            var li = document.createElement("li");
            li.textContent = msg;
            errorList.appendChild(li);
        });
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (!clientValidate()) {
            if (previewSection) {
                previewSection.removeAttribute("hidden");
                if (successBlock) successBlock.setAttribute("hidden", "");
                if (errorBlock) {
                    errorBlock.removeAttribute("hidden");
                    renderErrors(["Please resolve the validation errors indicated above."]);
                }
            }
            return;
        }

        var payload = {
            participant_reference: document.getElementById("participant_reference").value.trim(),
            experimental_condition: document.getElementById("experimental_condition").value.trim(),
            condition_order: document.getElementById("condition_order").value.trim(),
            session_stage: document.getElementById("session_stage").value.trim(),
            task_reference: document.getElementById("task_reference").value.trim(),
            consent_confirmed: document.getElementById("consent_confirmed").checked,
        };

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = "Validating Session...";
        }

        fetch(VALIDATE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify(payload),
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { status: response.status, body: data };
                });
            })
            .then(function (res) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Validate Experimental Session";
                }

                if (previewSection) previewSection.removeAttribute("hidden");

                if (res.status === 200 && res.body.valid) {
                    if (errorBlock) errorBlock.setAttribute("hidden", "");
                    if (successBlock) successBlock.removeAttribute("hidden");
                    renderSummary(res.body.validated_session || payload);
                    if (previewSection.scrollIntoView) {
                        previewSection.scrollIntoView({ behavior: "smooth", block: "start" });
                    }
                } else {
                    if (successBlock) successBlock.setAttribute("hidden", "");
                    if (errorBlock) errorBlock.removeAttribute("hidden");
                    var errors = res.body.errors || [res.body.message || "Session validation failed."];
                    renderErrors(errors);
                    if (previewSection.scrollIntoView) {
                        previewSection.scrollIntoView({ behavior: "smooth", block: "start" });
                    }
                }
            })
            .catch(function (err) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Validate Experimental Session";
                }
                if (previewSection) previewSection.removeAttribute("hidden");
                if (successBlock) successBlock.setAttribute("hidden", "");
                if (errorBlock) {
                    errorBlock.removeAttribute("hidden");
                    renderErrors(["Network error during validation. Please try again: " + err.message]);
                }
            });
    });

    if (resetBtn) {
        resetBtn.addEventListener("click", function () {
            form.reset();
            clearAllErrors();
            if (previewSection) previewSection.setAttribute("hidden", "");
            if (successBlock) successBlock.setAttribute("hidden", "");
            if (errorBlock) errorBlock.setAttribute("hidden", "");
            if (summaryBody) summaryBody.innerHTML = "";
            if (errorList) errorList.innerHTML = "";
        });
    }

    // Attach inline clear-on-input listeners
    REQUIRED_FIELDS.forEach(function (f) {
        var input = document.getElementById(f.id);
        if (!input) return;
        var ev = (input.tagName === "SELECT" || input.type === "checkbox") ? "change" : "input";
        input.addEventListener(ev, function () {
            clearFieldError(f.errorId, f.id);
        });
    });
})();
