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

    var immediateRecallForm = document.getElementById("immediateRecallForm");
    var immediateRecallError = document.getElementById("immediateRecallError");
    var immediateRecallResult = document.getElementById("immediateRecallResult");

    if (immediateRecallForm) {
        immediateRecallForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (immediateRecallError) {
                immediateRecallError.hidden = true;
                immediateRecallError.textContent = "";
            }

            var payload = {
                brain_only_count: document.getElementById("brainImmediateCount").value,
                genai_assisted_count: document.getElementById("genaiImmediateCount").value,
            };

            fetch("/api/component4/preview-immediate-recall", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (immediateRecallError) {
                            immediateRecallError.textContent = (response.body.errors || []).join(" ");
                            immediateRecallError.hidden = false;
                        }
                        if (immediateRecallResult) immediateRecallResult.hidden = true;
                        return;
                    }

                    var preview = response.body.preview;
                    document.getElementById("previewBrainCount").textContent = preview.brain_only_count + " items";
                    document.getElementById("previewGenaiCount").textContent = preview.genai_assisted_count + " items";
                    var difference = preview.difference_genai_minus_brain;
                    var unit = Math.abs(difference) === 1 ? " item" : " items";
                    document.getElementById("previewRecallDifference").textContent = difference + unit;
                    document.getElementById("immediateRecallNote").textContent = response.body.note;
                    if (immediateRecallResult) immediateRecallResult.hidden = false;
                })
                .catch(function () {
                    if (immediateRecallError) {
                        immediateRecallError.textContent = "Could not preview these scores. Please try again.";
                        immediateRecallError.hidden = false;
                    }
                });
        });

        immediateRecallForm.addEventListener("reset", function () {
            if (immediateRecallError) {
                immediateRecallError.hidden = true;
                immediateRecallError.textContent = "";
            }
            if (immediateRecallResult) immediateRecallResult.hidden = true;
        });
    }

    var predictorForm = document.getElementById("immediateRecallPredictorForm");
    var conditionSelect = document.getElementById("immediateModelCondition");
    var predictorError = document.getElementById("immediateRecallPredictionError");
    var predictorResult = document.getElementById("immediateRecallPredictionResult");

    function updatePredictorCondition() {
        if (!conditionSelect) return;
        document.querySelectorAll(".immediate-model-feature-group").forEach(function (group) {
            var active = group.dataset.modelCondition === conditionSelect.value;
            group.hidden = !active;
            group.querySelectorAll("input").forEach(function (input) {
                input.disabled = !active;
            });
        });
    }

    if (predictorForm && conditionSelect) {
        updatePredictorCondition();
        conditionSelect.addEventListener("change", updatePredictorCondition);

        predictorForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (predictorError) {
                predictorError.hidden = true;
                predictorError.textContent = "";
            }

            var activeGroup = document.querySelector(
                '.immediate-model-feature-group[data-model-condition="' + conditionSelect.value + '"]'
            );
            var features = {};
            activeGroup.querySelectorAll("input[data-feature]").forEach(function (input) {
                features[input.dataset.feature] = input.value;
            });

            fetch("/api/component4/predict-immediate-recall", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ condition: conditionSelect.value, features: features }),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (predictorError) {
                            predictorError.textContent = response.body.error || "Prediction failed.";
                            predictorError.hidden = false;
                        }
                        if (predictorResult) predictorResult.hidden = true;
                        return;
                    }

                    document.getElementById("predictedImmediateRecall").textContent =
                        response.body.predicted_immediate_recall.toFixed(1) + " / 10 correct MCQs";
                    document.getElementById("immediateRecallPredictionNote").textContent = response.body.note;
                    if (predictorResult) predictorResult.hidden = false;
                })
                .catch(function () {
                    if (predictorError) {
                        predictorError.textContent = "Could not generate a prediction. Please try again.";
                        predictorError.hidden = false;
                    }
                });
        });
    }

    var delayedPredictorForm = document.getElementById("delayedRecallPredictorForm");
    var delayedConditionSelect = document.getElementById("delayedModelCondition");
    var delayedPredictorError = document.getElementById("delayedRecallPredictionError");
    var delayedPredictorResult = document.getElementById("delayedRecallPredictionResult");

    function updateDelayedPredictorCondition() {
        if (!delayedConditionSelect) return;
        document.querySelectorAll(".delayed-model-feature-group").forEach(function (group) {
            var active = group.dataset.modelCondition === delayedConditionSelect.value;
            group.hidden = !active;
            group.querySelectorAll("input").forEach(function (input) {
                input.disabled = !active;
            });
        });
    }

    if (delayedPredictorForm && delayedConditionSelect) {
        updateDelayedPredictorCondition();
        delayedConditionSelect.addEventListener("change", updateDelayedPredictorCondition);

        delayedPredictorForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (delayedPredictorError) {
                delayedPredictorError.hidden = true;
                delayedPredictorError.textContent = "";
            }

            var activeGroup = document.querySelector(
                '.delayed-model-feature-group[data-model-condition="' + delayedConditionSelect.value + '"]'
            );
            var features = {};
            activeGroup.querySelectorAll("input[data-feature]").forEach(function (input) {
                features[input.dataset.feature] = input.value;
            });

            fetch("/api/component4/predict-delayed-recall", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ condition: delayedConditionSelect.value, features: features }),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (delayedPredictorError) {
                            delayedPredictorError.textContent = response.body.error || "Prediction failed.";
                            delayedPredictorError.hidden = false;
                        }
                        if (delayedPredictorResult) delayedPredictorResult.hidden = true;
                        return;
                    }

                    document.getElementById("predictedDelayedRecall").textContent =
                        response.body.predicted_delayed_recall.toFixed(1) + " items";
                    document.getElementById("delayedRecallPredictionNote").textContent = response.body.note;
                    if (delayedPredictorResult) delayedPredictorResult.hidden = false;
                })
                .catch(function () {
                    if (delayedPredictorError) {
                        delayedPredictorError.textContent = "Could not generate a delayed-recall prediction. Please try again.";
                        delayedPredictorError.hidden = false;
                    }
                });
        });
    }

    var delayedRecallForm = document.getElementById("delayedRecallForm");
    var delayedRecallError = document.getElementById("delayedRecallError");
    var delayedRecallResult = document.getElementById("delayedRecallResult");

    if (delayedRecallForm) {
        delayedRecallForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (delayedRecallError) {
                delayedRecallError.hidden = true;
                delayedRecallError.textContent = "";
            }

            var payload = {
                brain_only_count: document.getElementById("brainDelayedCount").value,
                genai_assisted_count: document.getElementById("genaiDelayedCount").value,
            };

            fetch("/api/component4/preview-delayed-recall", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (delayedRecallError) {
                            delayedRecallError.textContent = (response.body.errors || []).join(" ");
                            delayedRecallError.hidden = false;
                        }
                        if (delayedRecallResult) delayedRecallResult.hidden = true;
                        return;
                    }

                    var preview = response.body.preview;
                    document.getElementById("previewBrainDelayedCount").textContent = preview.brain_only_count + " items";
                    document.getElementById("previewGenaiDelayedCount").textContent = preview.genai_assisted_count + " items";
                    var difference = preview.difference_genai_minus_brain;
                    var unit = Math.abs(difference) === 1 ? " item" : " items";
                    document.getElementById("previewDelayedRecallDifference").textContent = difference + unit;
                    document.getElementById("delayedRecallNote").textContent = response.body.note;
                    if (delayedRecallResult) delayedRecallResult.hidden = false;
                })
                .catch(function () {
                    if (delayedRecallError) {
                        delayedRecallError.textContent = "Could not preview these delayed-recall counts. Please try again.";
                        delayedRecallError.hidden = false;
                    }
                });
        });

        delayedRecallForm.addEventListener("reset", function () {
            if (delayedRecallError) {
                delayedRecallError.hidden = true;
                delayedRecallError.textContent = "";
            }
            if (delayedRecallResult) delayedRecallResult.hidden = true;
        });
    }

    var ownershipEffortForm = document.getElementById("ownershipEffortForm");
    var ownershipEffortError = document.getElementById("ownershipEffortError");
    var ownershipEffortResult = document.getElementById("ownershipEffortResult");

    if (ownershipEffortForm) {
        ownershipEffortForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (ownershipEffortError) {
                ownershipEffortError.hidden = true;
                ownershipEffortError.textContent = "";
            }

            var payload = {
                brain_only_ownership: document.getElementById("brainOwnershipRating").value,
                genai_assisted_ownership: document.getElementById("genaiOwnershipRating").value,
                brain_only_effort: document.getElementById("brainEffortRating").value,
                genai_assisted_effort: document.getElementById("genaiEffortRating").value,
            };

            fetch("/api/component4/preview-ownership-effort", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (ownershipEffortError) {
                            ownershipEffortError.textContent = (response.body.errors || []).join(" ");
                            ownershipEffortError.hidden = false;
                        }
                        if (ownershipEffortResult) ownershipEffortResult.hidden = true;
                        return;
                    }

                    var preview = response.body.preview;
                    document.getElementById("previewBrainOwnership").textContent = preview.brain_only_ownership + " / 5";
                    document.getElementById("previewGenaiOwnership").textContent = preview.genai_assisted_ownership + " / 5";
                    document.getElementById("previewOwnershipDifference").textContent = preview.ownership_difference_genai_minus_brain + " rating points";
                    document.getElementById("previewBrainEffort").textContent = preview.brain_only_effort + " / 5";
                    document.getElementById("previewGenaiEffort").textContent = preview.genai_assisted_effort + " / 5";
                    document.getElementById("previewEffortDifference").textContent = preview.effort_difference_genai_minus_brain + " rating points";
                    document.getElementById("ownershipEffortNote").textContent = response.body.note;
                    if (ownershipEffortResult) ownershipEffortResult.hidden = false;
                })
                .catch(function () {
                    if (ownershipEffortError) {
                        ownershipEffortError.textContent = "Could not preview these ratings. Please try again.";
                        ownershipEffortError.hidden = false;
                    }
                });
        });

        ownershipEffortForm.addEventListener("reset", function () {
            if (ownershipEffortError) {
                ownershipEffortError.hidden = true;
                ownershipEffortError.textContent = "";
            }
            if (ownershipEffortResult) ownershipEffortResult.hidden = true;
        });
    }

    var nlpExtractionForm = document.getElementById("nlpExtractionForm");
    var nlpSampleText = document.getElementById("nlpSampleText");
    var nlpExtractionError = document.getElementById("nlpExtractionError");
    var nlpExtractionResult = document.getElementById("nlpExtractionResult");
    var nlpSampleCharCount = document.getElementById("nlpSampleCharCount");

    function updateNlpCharCount() {
        if (nlpSampleText && nlpSampleCharCount) {
            nlpSampleCharCount.textContent = nlpSampleText.value.length + " / 10,000 characters";
        }
    }

    function renderNlpKeywords(keywords) {
        var output = document.getElementById("nlpExtractKeywords");
        if (!output) return;
        output.textContent = keywords.length ? keywords.join(", ") : "None found";
    }

    if (nlpExtractionForm && nlpSampleText) {
        nlpSampleText.addEventListener("input", updateNlpCharCount);
        updateNlpCharCount();

        nlpExtractionForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (nlpExtractionError) {
                nlpExtractionError.hidden = true;
                nlpExtractionError.textContent = "";
            }

            fetch("/api/component4/analyze-text", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: nlpSampleText.value }),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (nlpExtractionError) {
                            nlpExtractionError.textContent = response.body.error || "Could not analyze this sample.";
                            nlpExtractionError.hidden = false;
                        }
                        if (nlpExtractionResult) nlpExtractionResult.hidden = true;
                        return;
                    }

                    var metrics = response.body;
                    document.getElementById("nlpExtractWordCount").textContent = metrics.word_count;
                    document.getElementById("nlpExtractSentenceCount").textContent = metrics.sentence_count;
                    document.getElementById("nlpExtractUniqueWords").textContent = metrics.unique_words;
                    document.getElementById("nlpExtractTtr").textContent = metrics.ttr.toFixed(3);
                    document.getElementById("nlpExtractRootTtr").textContent = metrics.root_ttr.toFixed(3);
                    document.getElementById("nlpExtractSentenceLength").textContent = metrics.avg_sentence_length.toFixed(1) + " words";
                    document.getElementById("nlpExtractWordLength").textContent = metrics.avg_word_length.toFixed(2) + " characters";
                    document.getElementById("nlpExtractLexicalDensity").textContent = metrics.lexical_density.toFixed(1) + "%";
                    document.getElementById("nlpExtractReadability").textContent = metrics.readability_index;
                    document.getElementById("nlpExtractHapax").textContent = metrics.hapax_count;
                    document.getElementById("nlpExtractContentWords").textContent = metrics.content_words_count;
                    renderNlpKeywords(metrics.keywords || []);
                    document.getElementById("nlpExtractionNote").textContent = metrics.note;
                    if (nlpExtractionResult) nlpExtractionResult.hidden = false;
                })
                .catch(function () {
                    if (nlpExtractionError) {
                        nlpExtractionError.textContent = "Could not analyze this sample. Please try again.";
                        nlpExtractionError.hidden = false;
                    }
                });
        });

        nlpExtractionForm.addEventListener("reset", function () {
            if (nlpExtractionError) {
                nlpExtractionError.hidden = true;
                nlpExtractionError.textContent = "";
            }
            if (nlpExtractionResult) nlpExtractionResult.hidden = true;
            updateNlpCharCount();
        });
    }

    var humanRubricForm = document.getElementById("humanRubricForm");
    var humanRubricError = document.getElementById("humanRubricError");
    var humanRubricResult = document.getElementById("humanRubricResult");

    if (humanRubricForm) {
        humanRubricForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (humanRubricError) {
                humanRubricError.hidden = true;
                humanRubricError.textContent = "";
            }

            var ratings = {};
            humanRubricForm.querySelectorAll("input[data-criterion]").forEach(function (input) {
                var criterion = input.dataset.criterion;
                var condition = input.dataset.condition;
                var rater = input.dataset.rater;
                if (!ratings[criterion]) ratings[criterion] = {};
                if (!ratings[criterion][condition]) ratings[criterion][condition] = {};
                ratings[criterion][condition][rater] = input.value;
            });

            fetch("/api/component4/preview-human-rubric", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ratings: ratings }),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (humanRubricError) {
                            humanRubricError.textContent = (response.body.errors || []).join(" ");
                            humanRubricError.hidden = false;
                        }
                        if (humanRubricResult) humanRubricResult.hidden = true;
                        return;
                    }

                    var preview = response.body.preview;
                    document.getElementById("rubricBrainMean").textContent = preview.brain_only_mean.toFixed(2);
                    document.getElementById("rubricGenaiMean").textContent = preview.genai_assisted_mean.toFixed(2);
                    document.getElementById("rubricConditionDifference").textContent = preview.difference_genai_minus_brain.toFixed(2);
                    document.getElementById("rubricAgreement").textContent =
                        preview.exact_agreement_count + " / " + preview.agreement_pair_count + " (" + preview.exact_agreement_percent.toFixed(1) + "%)";
                    document.getElementById("humanRubricNote").textContent = response.body.note;
                    if (humanRubricResult) humanRubricResult.hidden = false;
                })
                .catch(function () {
                    if (humanRubricError) {
                        humanRubricError.textContent = "Could not calculate the rubric preview. Please try again.";
                        humanRubricError.hidden = false;
                    }
                });
        });

        humanRubricForm.addEventListener("reset", function () {
            if (humanRubricError) {
                humanRubricError.hidden = true;
                humanRubricError.textContent = "";
            }
            if (humanRubricResult) humanRubricResult.hidden = true;
        });
    }

    var conditionComparisonForm = document.getElementById("conditionComparisonForm");
    var conditionComparisonError = document.getElementById("conditionComparisonError");
    var conditionComparisonResult = document.getElementById("conditionComparisonResult");

    if (conditionComparisonForm) {
        conditionComparisonForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (conditionComparisonError) {
                conditionComparisonError.hidden = true;
                conditionComparisonError.textContent = "";
            }

            var payload = { brain_only: {}, genai_assisted: {} };
            conditionComparisonForm.querySelectorAll("input[data-condition][data-measure]").forEach(function (input) {
                payload[input.dataset.condition][input.dataset.measure] = input.value;
            });

            fetch("/api/component4/preview-condition-comparison", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, body: data };
                    });
                })
                .then(function (response) {
                    if (!response.ok) {
                        if (conditionComparisonError) {
                            conditionComparisonError.textContent = (response.body.errors || []).join(" ");
                            conditionComparisonError.hidden = false;
                        }
                        if (conditionComparisonResult) conditionComparisonResult.hidden = true;
                        return;
                    }

                    var resultsBody = document.getElementById("conditionComparisonResultsBody");
                    resultsBody.innerHTML = "";
                    Object.keys(response.body.comparisons).forEach(function (key) {
                        var comparison = response.body.comparisons[key];
                        var row = document.createElement("tr");

                        var outcome = document.createElement("th");
                        outcome.scope = "row";
                        outcome.textContent = comparison.label;
                        row.appendChild(outcome);

                        function formatValue(value, isDifference) {
                            if (comparison.unit === "items") {
                                return value + (Math.abs(value) === 1 ? " item" : " items");
                            }
                            return isDifference ? value + " rating points" : value + " / 5";
                        }

                        [
                            formatValue(comparison.brain_only, false),
                            formatValue(comparison.genai_assisted, false),
                            formatValue(comparison.difference_genai_minus_brain, true),
                        ].forEach(function (value) {
                            var cell = document.createElement("td");
                            cell.textContent = value;
                            row.appendChild(cell);
                        });
                        resultsBody.appendChild(row);
                    });
                    document.getElementById("conditionComparisonNote").textContent = response.body.note;
                    if (conditionComparisonResult) conditionComparisonResult.hidden = false;
                })
                .catch(function () {
                    if (conditionComparisonError) {
                        conditionComparisonError.textContent = "Could not compare these condition values. Please try again.";
                        conditionComparisonError.hidden = false;
                    }
                });
        });

        conditionComparisonForm.addEventListener("reset", function () {
            if (conditionComparisonError) {
                conditionComparisonError.hidden = true;
                conditionComparisonError.textContent = "";
            }
            if (conditionComparisonResult) conditionComparisonResult.hidden = true;
        });
    }

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

    // ----------------------------------------------------------------------
    // Real-Time Machine Learning Retention Predictor Handler
    // ----------------------------------------------------------------------
    var btnPredict = document.getElementById("btnRunPrediction");
    if (btnPredict) {
        btnPredict.addEventListener("click", function () {
            var dep = parseInt(document.getElementById("inpDependency").value, 10);
            var eff = parseInt(document.getElementById("inpEffort").value, 10);
            var own = parseInt(document.getElementById("inpOwnership").value, 10);
            var timeVal = parseFloat(document.getElementById("inpTime").value) || 150.0;
            var mcqVal = parseFloat(document.getElementById("inpMcq").value) || 8.5;

            var payload = {
                perceived_ai_dependency_score: dep,
                ga_mental_effort: eff,
                cognitive_ownership_score: own,
                ga_learning_time_sec: timeVal,
                ga_immediate_mcq: mcqVal
            };

            btnPredict.disabled = true;
            btnPredict.textContent = "Analyzing Patterns...";

            fetch("/api/component4/predict-risk", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                btnPredict.disabled = false;
                btnPredict.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg> Predict Retention Risk';

                var badge = document.getElementById("riskBadge");
                var probVal = document.getElementById("riskProbVal");
                var retVal = document.getElementById("predRetentionVal");
                var rec = document.getElementById("recommendationText");

                if (badge) {
                    badge.className = "risk-badge " + (data.risk_class === 1 ? "risk-badge--high" : "risk-badge--stable");
                    badge.textContent = data.prediction || (data.risk_class === 1 ? "High Retention Risk" : "Stable Retention");
                }

                if (probVal) {
                    probVal.textContent = (data.risk_probability * 100).toFixed(1) + "%";
                }

                if (retVal) {
                    retVal.textContent = (data.predicted_retention_rate || 70.0) + "%";
                }

                if (rec && data.recommendation) {
                    rec.innerHTML = "<strong>Pedagogical Insight:</strong> " + data.recommendation;
                }
            })
            .catch(function () {
                btnPredict.disabled = false;
                btnPredict.textContent = "Predict Retention Risk";
            });
        });
    }

    // ----------------------------------------------------------------------
    // Real-Time NLP Text Comparison Handler
    // ----------------------------------------------------------------------
    var btnNlpCompare = document.getElementById("btnRunNlpCompare");
    if (btnNlpCompare) {
        btnNlpCompare.addEventListener("click", function () {
            var humanText = (document.getElementById("txtHumanSample") || {}).value || "";
            var aiText = (document.getElementById("txtAiSample") || {}).value || "";

            btnNlpCompare.disabled = true;
            btnNlpCompare.textContent = "Computing NLP Metrics...";

            fetch("/api/component4/compare-nlp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ human_text: humanText, ai_text: aiText })
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                btnNlpCompare.disabled = false;
                btnNlpCompare.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg> Analyze & Compare NLP Metrics';

                var bo = data.brain_only || {};
                var ga = data.genai_assisted || {};
                var comp = data.comparison || {};

                // Update Brain-Only output
                var boWords = document.getElementById("nlpBoWords");
                var boTtr = document.getElementById("nlpBoTtr");
                var boRttr = document.getElementById("nlpBoRttr");
                var boSent = document.getElementById("nlpBoSentLen");
                var boDen = document.getElementById("nlpBoDensity");
                var boKw = document.getElementById("nlpBoKeywords");

                if (boWords) boWords.textContent = (bo.word_count || 0) + " words";
                if (boTtr) boTtr.textContent = (bo.ttr || 0.0).toFixed(3);
                if (boRttr) boRttr.textContent = (bo.root_ttr || 0.0).toFixed(3);
                if (boSent) boSent.textContent = (bo.avg_sentence_length || 0.0).toFixed(1) + " words";
                if (boDen) boDen.textContent = (bo.lexical_density || 0.0).toFixed(1) + "%";

                if (boKw && bo.keywords) {
                    boKw.innerHTML = bo.keywords.map(function (k) {
                        return '<span class="keyword-pill">' + k + '</span>';
                    }).join("");
                }

                // Update GenAI output
                var gaWords = document.getElementById("nlpGaWords");
                var gaTtr = document.getElementById("nlpGaTtr");
                var gaRttr = document.getElementById("nlpGaRttr");
                var gaSent = document.getElementById("nlpGaSentLen");
                var gaDen = document.getElementById("nlpGaDensity");
                var gaKw = document.getElementById("nlpGaKeywords");

                if (gaWords) gaWords.textContent = (ga.word_count || 0) + " words";
                if (gaTtr) gaTtr.textContent = (ga.ttr || 0.0).toFixed(3);
                if (gaRttr) gaRttr.textContent = (ga.root_ttr || 0.0).toFixed(3);
                if (gaSent) gaSent.textContent = (ga.avg_sentence_length || 0.0).toFixed(1) + " words";
                if (gaDen) gaDen.textContent = (ga.lexical_density || 0.0).toFixed(1) + "%";

                if (gaKw && ga.keywords) {
                    gaKw.innerHTML = ga.keywords.map(function (k) {
                        return '<span class="keyword-pill">' + k + '</span>';
                    }).join("");
                }

                // Update Verdict
                var verdict = document.getElementById("nlpVerdictBanner");
                if (verdict && comp.verdict) {
                    verdict.innerHTML = "<strong>Comparative NLP Verdict:</strong> " + comp.verdict;
                }
            })
            .catch(function () {
                btnNlpCompare.disabled = false;
                btnNlpCompare.textContent = "Analyze & Compare NLP Metrics";
            });
        });
    }
})();
