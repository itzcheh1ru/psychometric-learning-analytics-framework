/**
 * component2_assessment.js – Client-side script for Component 2:
 * Personalized Student Assessment & Behavioural Interpretation.
 *
 * Handles:
 * - 5-step questionnaire navigation and Likert response interaction
 * - Real-time progress calculation (0 to 26 items)
 * - Validation of complete survey responses
 * - AJAX submission to /api/component2/assess
 * - Dynamic rendering of personal construct scores, norms, and quartiles
 * - Plotly radar and quadrant chart rendering
 * - Behavioural profile presentation with SEM structural context
 * - Traceable educational recommendations rendering
 * - RFC 4180 CSV and JSON report export
 */

"use strict";

(function () {
    var ASSESS_API_URL = "/api/component2/assess";
    var REPORT_API_URL = "/api/component2/student-report";

    var currentStep = 1;
    var totalSteps = 5;
    var totalItems = 26;
    var lastAssessmentData = null;

    // Step item mappings
    var stepItemKeys = {
        1: ["AT1", "AT2", "AT3", "AT4", "AT5", "AT6"],
        2: ["VB1", "VB2", "VB3", "VB4", "VB5"],
        3: ["PU1", "PU2", "PU3", "PU4", "PU5"],
        4: ["AD1", "AD2", "AD3", "AD4", "AD5"],
        5: ["LC1", "LC2", "LC3", "LC4", "LC5"],
    };

    var stepTitles = {
        1: "Step 1 of 5: Algorithmic Trust (AT)",
        2: "Step 2 of 5: Verification Behaviour (VB)",
        3: "Step 3 of 5: Perceived Usefulness (PU)",
        4: "Step 4 of 5: AI Dependence (AD)",
        5: "Step 5 of 5: Learning Confidence (LC)",
    };

    document.addEventListener("DOMContentLoaded", function () {
        initStartButton();
        initLikertInteractions();
        initNavigationButtons();
        initExportButtons();
        initRetakeButton();
    });

    /**
     * Start assessment button reveal
     */
    function initStartButton() {
        var btnStart = document.getElementById("btnStartAssessment");
        if (btnStart) {
            btnStart.addEventListener("click", function () {
                var introCard = document.getElementById("introNoticeCard");
                var formContainer = document.getElementById("assessmentFormContainer");
                if (introCard) introCard.style.display = "none";
                if (formContainer) {
                    formContainer.style.display = "block";
                    formContainer.scrollIntoView({ behavior: "smooth" });
                }
                updateProgress();
            });
        }
    }

    /**
     * Likert radio interaction handlers
     */
    function initLikertInteractions() {
        var labels = document.querySelectorAll(".likert-option-label");
        labels.forEach(function (label) {
            label.addEventListener("click", function (e) {
                var itemCode = label.getAttribute("data-item");
                var radio = label.querySelector('input[type="radio"]');

                if (radio) {
                    radio.checked = true;

                    // Uncheck siblings visually
                    var parentCard = document.getElementById("card_" + itemCode);
                    if (parentCard) {
                        var siblings = parentCard.querySelectorAll(".likert-option-label");
                        siblings.forEach(function (sib) {
                            sib.classList.remove("likert-option-label--selected");
                        });
                        label.classList.add("likert-option-label--selected");

                        parentCard.classList.remove("question-item-card--unanswered", "question-item-card--error");
                        parentCard.classList.add("question-item-card--answered");
                    }

                    // Hide any active error banner
                    var errorBanner = document.getElementById("stepErrorBanner");
                    if (errorBanner) errorBanner.style.display = "none";

                    updateProgress();
                }
            });
        });
    }

    /**
     * Update progress fill bar and counter
     */
    function updateProgress() {
        var answeredCount = 0;
        for (var s = 1; s <= totalSteps; s++) {
            var items = stepItemKeys[s];
            items.forEach(function (key) {
                var checked = document.querySelector('input[name="' + key + '"]:checked');
                if (checked) answeredCount++;
            });
        }

        var percent = Math.round((answeredCount / totalItems) * 100);
        var progressFill = document.getElementById("stepperProgressFill");
        var countLabel = document.getElementById("progressCountLabel");

        if (progressFill) progressFill.style.width = percent + "%";
        if (countLabel) {
            countLabel.textContent = answeredCount + " of " + totalItems + " items answered (" + percent + "%)";
        }
    }

    /**
     * Step navigation logic
     */
    function initNavigationButtons() {
        var btnPrev = document.getElementById("btnPrevStep");
        var btnNext = document.getElementById("btnNextStep");
        var btnSubmit = document.getElementById("btnSubmitAssessment");

        if (btnPrev) {
            btnPrev.addEventListener("click", function () {
                if (currentStep > 1) {
                    showStep(currentStep - 1);
                }
            });
        }

        if (btnNext) {
            btnNext.addEventListener("click", function () {
                if (validateStep(currentStep)) {
                    showStep(currentStep + 1);
                }
            });
        }

        if (btnSubmit) {
            btnSubmit.addEventListener("click", function () {
                if (validateStep(currentStep)) {
                    submitAssessment();
                }
            });
        }
    }

    /**
     * Validate that all questions on a specific step have been answered
     */
    function validateStep(stepNum) {
        var items = stepItemKeys[stepNum];
        var unanswered = [];

        items.forEach(function (code) {
            var checked = document.querySelector('input[name="' + code + '"]:checked');
            var card = document.getElementById("card_" + code);
            if (!checked) {
                unanswered.push(code);
                if (card) {
                    card.classList.add("question-item-card--error");
                }
            } else {
                if (card) {
                    card.classList.remove("question-item-card--error");
                }
            }
        });

        var errorBanner = document.getElementById("stepErrorBanner");
        if (unanswered.length > 0) {
            if (errorBanner) {
                errorBanner.textContent = "Please answer all " + items.length + " questions in this section before proceeding (Missing: " + unanswered.join(", ") + ").";
                errorBanner.style.display = "block";
            }
            // Scroll to the first unanswered question
            var firstCard = document.getElementById("card_" + unanswered[0]);
            if (firstCard) {
                firstCard.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            return false;
        }

        if (errorBanner) errorBanner.style.display = "none";
        return true;
    }

    /**
     * Switch visible step pane
     */
    function showStep(stepNum) {
        currentStep = stepNum;

        // Hide all panes
        for (var s = 1; s <= totalSteps; s++) {
            var pane = document.getElementById("stepPane" + s);
            var ind = document.getElementById("stepIndicator" + s);
            if (pane) pane.style.display = s === stepNum ? "block" : "none";
            if (ind) {
                ind.classList.remove("step-item--active", "step-item--done");
                if (s === stepNum) {
                    ind.classList.add("step-item--active");
                } else if (s < stepNum) {
                    ind.classList.add("step-item--done");
                }
            }
        }

        // Update header label
        var titleLabel = document.getElementById("stepTitleLabel");
        if (titleLabel) titleLabel.textContent = stepTitles[stepNum];

        // Update button visibility
        var btnPrev = document.getElementById("btnPrevStep");
        var btnNext = document.getElementById("btnNextStep");
        var btnSubmit = document.getElementById("btnSubmitAssessment");

        if (btnPrev) btnPrev.style.display = stepNum > 1 ? "inline-flex" : "none";
        if (btnNext) btnNext.style.display = stepNum < totalSteps ? "inline-flex" : "none";
        if (btnSubmit) btnSubmit.style.display = stepNum === totalSteps ? "inline-flex" : "none";

        // Scroll to form top
        var formContainer = document.getElementById("assessmentFormContainer");
        if (formContainer) formContainer.scrollIntoView({ behavior: "smooth" });
    }

    /**
     * Collect responses and submit to assess API
     */
    function submitAssessment() {
        var btnSubmit = document.getElementById("btnSubmitAssessment");
        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.textContent = "Processing Assessment...";
        }

        var responses = {};
        for (var s = 1; s <= totalSteps; s++) {
            var items = stepItemKeys[s];
            items.forEach(function (code) {
                var checked = document.querySelector('input[name="' + code + '"]:checked');
                if (checked) {
                    responses[code] = parseFloat(checked.value);
                }
            });
        }

        var studentIdInput = document.getElementById("studentIdentifierInput");
        var studentId = (studentIdInput && studentIdInput.value.trim()) || "Anonymous Student";

        var payload = {
            responses: responses,
            student_id: studentId,
        };

        fetch(ASSESS_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then(function (res) {
                if (!res.ok) {
                    return res.json().then(function (err) {
                        throw new Error(err.error || "Assessment calculation failed.");
                    });
                }
                return res.json();
            })
            .then(function (data) {
                lastAssessmentData = data;
                try {
                    localStorage.setItem("c2_last_assessment", JSON.stringify(data));
                } catch (e) {
                    console.warn("Could not cache assessment to localStorage", e);
                }
                renderAssessmentResults(data);
            })
            .catch(function (err) {
                alert("Assessment Error: " + err.message);
            })
            .finally(function () {
                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.textContent = "Submit & View My Assessment \u2192";
                }
            });
    }

    /**
     * Render complete personal assessment results
     */
    function renderAssessmentResults(data) {
        var formContainer = document.getElementById("assessmentFormContainer");
        var resultsContainer = document.getElementById("assessmentResultsContainer");

        if (formContainer) formContainer.style.display = "none";
        if (resultsContainer) {
            resultsContainer.style.display = "block";
            resultsContainer.scrollIntoView({ behavior: "smooth" });
        }

        // 1. Meta tags
        var studentTag = document.getElementById("resStudentTag");
        var timestampTag = document.getElementById("resTimestampTag");
        if (studentTag) studentTag.textContent = "Student: " + (data.student_id || "Anonymous");
        if (timestampTag) timestampTag.textContent = "Completed: " + new Date().toLocaleTimeString();

        // 2. Render 5 Construct Score Cards
        renderConstructScoreCards(data.scoring);

        // 3. Render Plotly Charts
        if (window.Plotly && data.charts) {
            if (data.charts.radar) {
                Plotly.newPlot("studentRadarPlot", data.charts.radar.data, data.charts.radar.layout, { responsive: true, displayModeBar: false });
            }
            if (data.charts.quadrant) {
                Plotly.newPlot("studentQuadrantPlot", data.charts.quadrant.data, data.charts.quadrant.layout, { responsive: true, displayModeBar: false });
            }
        }

        // 4. Render Behavioural Profile Card
        renderProfileCard(data.profile);

        // 5. Render Recommendations
        renderRecommendations(data.recommendations);
    }

    /**
     * Render the 5 construct cards grid
     */
    function renderConstructScoreCards(scoring) {
        var grid = document.getElementById("constructScoresGrid");
        if (!grid || !scoring || !scoring.construct_scores) return;

        var scores = scoring.construct_scores;
        var html = "";

        var constructColors = {
            AT: "#1a6fa3",
            VB: "#217a50",
            PU: "#2563eb",
            AD: "#a3531a",
            LC: "#6a3fa3",
        };

        var codes = ["AT", "VB", "PU", "AD", "LC"];
        codes.forEach(function (c) {
            var item = scores[c];
            if (!item) return;

            var qClass = "quartile-badge--iqr";
            if (item.quartile_band.indexOf("> Q3") !== -1) {
                qClass = "quartile-badge--upper";
            } else if (item.quartile_band.indexOf("< Q1") !== -1) {
                qClass = "quartile-badge--lower";
            }

            var color = constructColors[c] || "#2563eb";

            html += '<div class="student-score-card" style="border-top: 4px solid ' + color + ';">';
            html += '  <div class="student-score-card__header">';
            html += '    <span style="font-weight:700; font-size:0.95rem; color:#1e293b;">' + item.name + '</span>';
            html += '    <span class="question-badge" style="background:#f1f5f9; color:#475569;">' + c + '</span>';
            html += '  </div>';

            html += '  <div class="student-score-val">' + item.mean_score.toFixed(2) + ' <span class="student-score-max">/ 5.00</span></div>';
            html += '  <div style="font-size:0.75rem; color:#64748b; margin-bottom:0.5rem;">Factor Sensitivity: ' + item.weighted_score.toFixed(2) + '</div>';

            html += '  <div class="student-percentile-wrap">';
            html += '    <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:600; color:#334155;">';
            html += '      <span>Cohort Percentile:</span>';
            html += '      <span>' + item.percentile_rank.toFixed(1) + 'th %ile</span>';
            html += '    </div>';
            html += '    <div class="percentile-bar-bg">';
            html += '      <div class="percentile-bar-fill" style="width:' + item.percentile_rank + '%; background:' + color + ';"></div>';
            html += '    </div>';
            html += '  </div>';

            html += '  <span class="quartile-badge ' + qClass + '">' + item.quartile_band + '</span>';

            html += '  <table class="benchmarks-table-mini" style="margin-top:1rem;">';
            html += '    <tr><td>Cohort Mean (N=375):</td><td>' + item.cohort_mean.toFixed(2) + '</td></tr>';
            html += '    <tr><td>Cohort Median:</td><td>' + item.cohort_median.toFixed(2) + '</td></tr>';
            html += '    <tr><td>Standardized z-score:</td><td>' + (item.z_score >= 0 ? "+" : "") + item.z_score.toFixed(2) + '</td></tr>';
            html += '  </table>';

            html += '</div>';
        });

        grid.innerHTML = html;
    }

    /**
     * Render behavioural profile card
     */
    function renderProfileCard(profile) {
        var card = document.getElementById("behaviouralProfileCard");
        if (!card || !profile) return;

        var html = "";
        html += '<span class="profile-quadrant-badge">' + profile.quadrant_id + ' Descriptive Pattern</span>';
        html += '<h3 class="profile-title">' + profile.profile_title + '</h3>';
        html += '<div class="profile-tagline">' + profile.tagline + '</div>';

        html += '<div class="profile-narrative">' + profile.summary + '</div>';
        html += '<div class="profile-narrative">' + profile.detailed_interpretation + '</div>';

        // SEM Insight Callout
        html += '<div class="sem-insight-box">';
        html += '  <strong>Empirical SEM Structural Alignment:</strong> ' + profile.sem_structural_insights;
        html += '</div>';

        // Context Cards
        html += '<div class="context-cards-row">';
        if (profile.dependence_context) {
            html += '<div class="context-card">';
            html += '  <h4>AI Dependence Context (' + profile.dependence_context.level + ' &mdash; ' + profile.dependence_context.score.toFixed(2) + '/5.0)</h4>';
            html += '  <p>' + profile.dependence_context.text + '</p>';
            html += '</div>';
        }
        if (profile.confidence_context) {
            html += '<div class="context-card">';
            html += '  <h4>Learning Confidence &amp; Utility Context (LC: ' + profile.confidence_context.score.toFixed(2) + ')</h4>';
            html += '  <p>' + profile.confidence_context.text + '</p>';
            html += '</div>';
        }
        html += '</div>';

        card.innerHTML = html;
    }

    /**
     * Render personalized recommendations cards
     */
    function renderRecommendations(recs) {
        var container = document.getElementById("recommendationsContainer");
        if (!container || !recs) return;

        var html = "";
        recs.forEach(function (r) {
            var pClass = "rec-priority-badge--guidance";
            var cardClass = "recommendation-card--guidance";
            if (r.priority === "High") {
                pClass = "rec-priority-badge--high";
                cardClass = "recommendation-card--high";
            } else if (r.priority === "Medium") {
                pClass = "rec-priority-badge--medium";
                cardClass = "recommendation-card--medium";
            }

            html += '<div class="recommendation-card ' + cardClass + '">';
            html += '  <div class="rec-header">';
            html += '    <h4 class="rec-title">' + r.title + '</h4>';
            html += '    <span class="rec-priority-badge ' + pClass + '">' + r.priority + ' Priority</span>';
            html += '  </div>';

            html += '  <div style="font-size:0.75rem; font-weight:700; color:#64748b; margin-bottom:0.4rem;">Target Construct: ' + r.construct + '</div>';

            html += '  <div class="rec-trace-box">';
            html += '    <strong>Evidence Trigger:</strong> ' + r.evidence_trace;
            html += '  </div>';

            html += '  <div class="rec-rationale">';
            html += '    <strong>Pedagogical &amp; SEM Rationale:</strong> ' + r.rationale;
            html += '  </div>';

            html += '  <div style="font-size:0.84rem; font-weight:700; color:#1e293b; margin-top:0.75rem;">Recommended Action Steps:</div>';
            html += '  <ol class="rec-actions-list">';
            (r.action_steps || []).forEach(function (step) {
                html += '    <li>' + step + '</li>';
            });
            html += '  </ol>';

            html += '  <div class="rec-caveat">';
            html += '    <em>Category: ' + (r.evidence_category || "Pedagogical Guidance") + ' &bull; Note: ' + (r.caveat || "") + '</em>';
            html += '  </div>';

            html += '</div>';
        });

        container.innerHTML = html;
    }

    /**
     * Export and print handlers
     */
    function initExportButtons() {
        var btnCsv = document.getElementById("btnExportCsv");
        var btnJson = document.getElementById("btnExportJson");
        var btnPrint = document.getElementById("btnPrintReport");

        if (btnCsv) {
            btnCsv.addEventListener("click", function () {
                if (!lastAssessmentData) return;
                exportReport("csv");
            });
        }

        if (btnJson) {
            btnJson.addEventListener("click", function () {
                if (!lastAssessmentData) return;
                exportReport("json");
            });
        }

        if (btnPrint) {
            btnPrint.addEventListener("click", function () {
                window.print();
            });
        }
    }

    /**
     * Post to report export endpoint and trigger file download
     */
    function exportReport(format) {
        var payload = {
            format: format,
            scoring_result: lastAssessmentData.scoring,
            profile_result: lastAssessmentData.profile,
            recommendations: lastAssessmentData.recommendations,
            student_meta: {
                student_id: lastAssessmentData.student_id || "Anonymous",
                timestamp: new Date().toISOString(),
            },
        };

        fetch(REPORT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then(function (res) {
                if (!res.ok) throw new Error("Failed to export report.");
                return res.blob();
            })
            .then(function (blob) {
                var filename = format === "csv" ? "Student_AI_Trust_Assessment_Report.csv" : "Student_AI_Trust_Assessment_Report.json";
                var a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            })
            .catch(function (err) {
                alert("Export error: " + err.message);
            });
    }

    /**
     * Retake assessment reset
     */
    function initRetakeButton() {
        var btnRetake = document.getElementById("btnRetakeAssessment");
        if (btnRetake) {
            btnRetake.addEventListener("click", function () {
                if (!confirm("Are you sure you want to reset your answers and retake the assessment?")) {
                    return;
                }

                // Reset radios
                var radios = document.querySelectorAll('input[type="radio"]');
                radios.forEach(function (r) { r.checked = false; });

                var labels = document.querySelectorAll(".likert-option-label");
                labels.forEach(function (l) { l.classList.remove("likert-option-label--selected"); });

                var cards = document.querySelectorAll(".question-item-card");
                cards.forEach(function (c) {
                    c.classList.remove("question-item-card--answered", "question-item-card--error");
                    c.classList.add("question-item-card--unanswered");
                });

                lastAssessmentData = null;
                currentStep = 1;

                var resultsContainer = document.getElementById("assessmentResultsContainer");
                var introCard = document.getElementById("introNoticeCard");
                var formContainer = document.getElementById("assessmentFormContainer");

                if (resultsContainer) resultsContainer.style.display = "none";
                if (introCard) introCard.style.display = "block";
                if (formContainer) formContainer.style.display = "none";

                showStep(1);
                updateProgress();
                window.scrollTo({ top: 0, behavior: "smooth" });
            });
        }
    }

})();
