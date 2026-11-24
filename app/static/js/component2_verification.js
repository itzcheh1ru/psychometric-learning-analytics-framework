/**
 * component2_verification.js – Client-side script for Component 2:
 * Practical AI Verification Performance Assessment & Metacognitive Calibration.
 *
 * Handles:
 * - Detecting local survey session data from localStorage
 * - Scenario-by-scenario navigation and claim-level classification (Correct / Erroneous / Unsupported)
 * - Method selection and justification input tracking
 * - Real-time claim progress calculation (0 to 24 claims)
 * - AJAX submission to /api/component2/evaluate-verification
 * - Binary confusion matrix rendering (TP, TN, FP, FN)
 * - Metacognitive calibration analysis with interactive Plotly scatter matrix (VB_norm vs. Accuracy)
 * - Scenario-by-scenario solution reveal with expert academic derivations and genuine literature citations
 * - Explanation rubric scoring (0-2 scale)
 * - Combined RFC 4180 CSV and JSON report export
 */

"use strict";

(function () {
    var EVALUATE_API_URL = "/api/component2/evaluate-verification";
    var COMBINED_REPORT_API_URL = "/api/component2/combined-report";

    var currentScenarioIndex = 0;
    var totalScenarios = 8;
    var cachedSurveyData = null;
    var lastEvaluationData = null;

    document.addEventListener("DOMContentLoaded", function () {
        initSurveyLinkage();
        initStartButton();
        initVerdictRadioButtons();
        initScenarioNavigation();
        initSubmission();
        initExportButtons();
        initRetakeButton();
    });

    /**
     * 1. Detect and link existing 26-item survey assessment data from localStorage
     */
    function initSurveyLinkage() {
        var rawData = localStorage.getItem("c2_last_assessment");
        var badge = document.getElementById("surveyLinkStatusBadge");
        var desc = document.getElementById("surveyLinkStatusDesc");
        var studentInput = document.getElementById("inputStudentId");

        if (rawData) {
            try {
                var parsed = JSON.parse(rawData);
                if (parsed && parsed.scoring && parsed.scoring.construct_scores) {
                    cachedSurveyData = parsed;
                    var vbScore = parsed.scoring.construct_scores.VB ? parsed.scoring.construct_scores.VB.mean_score : 3.0;
                    var atScore = parsed.scoring.construct_scores.AT ? parsed.scoring.construct_scores.AT.mean_score : 3.0;
                    var studentId = parsed.student_id || "Student";

                    if (badge) {
                        badge.innerHTML = '<span class="status-badge status-badge--success" style="font-size: 0.75rem;">' +
                            '&#10003; Linked: ' + escapeHtml(studentId) + ' (VB: ' + vbScore.toFixed(2) + ', AT: ' + atScore.toFixed(2) + ')' +
                            '</span>';
                    }
                    if (desc) {
                        desc.textContent = "Self-reported survey scores detected. Your practical verification performance will be automatically calibrated against your self-reported Verification Behaviour (VB).";
                    }
                    if (studentInput && !studentInput.value) {
                        studentInput.value = studentId;
                    }
                    return;
                }
            } catch (e) {
                console.warn("Could not parse existing c2_last_assessment from localStorage", e);
            }
        }

        if (badge) {
            badge.innerHTML = '<span class="status-badge status-badge--preparation" style="font-size: 0.75rem;">' +
                'No Survey Detected in this Session' +
                '</span>';
        }
        if (desc) {
            desc.textContent = "You can complete this verification assessment independently. To unlock full metacognitive calibration, complete the 26-item survey.";
        }
    }

    /**
     * 2. Start Assessment Button Handler
     */
    function initStartButton() {
        var btnStart = document.getElementById("btnStartVerificationTask");
        if (btnStart) {
            btnStart.addEventListener("click", function () {
                var introCard = document.getElementById("introNoticeCard");
                var formContainer = document.getElementById("verificationFormContainer");

                if (introCard) introCard.style.display = "none";
                if (formContainer) {
                    formContainer.style.display = "block";
                    formContainer.scrollIntoView({ behavior: "smooth" });
                }
                updateOverallProgress();
            });
        }
    }

    /**
     * 3. Verdict Radio Option Click Handlers
     */
    function initVerdictRadioButtons() {
        var optionBtns = document.querySelectorAll(".verdict-option-btn");
        optionBtns.forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                var claimId = btn.getAttribute("data-claim-id");
                var verdict = btn.getAttribute("data-verdict");
                var radio = btn.querySelector('input[type="radio"]');

                if (radio) {
                    radio.checked = true;

                    // Update visual selection styles within this claim card
                    var parentCard = document.getElementById("card_" + claimId);
                    if (parentCard) {
                        var siblings = parentCard.querySelectorAll(".verdict-option-btn");
                        siblings.forEach(function (sib) {
                            sib.classList.remove("verdict-option-btn--selected");
                        });
                        btn.classList.add("verdict-option-btn--selected");

                        parentCard.classList.remove("claim-card--unanswered", "claim-card--error");
                        parentCard.classList.add("claim-card--evaluated");
                    }

                    // Hide any active error banner
                    var errorBanner = document.getElementById("scenarioErrorBanner");
                    if (errorBanner) errorBanner.style.display = "none";

                    updateOverallProgress();
                }
            });
        });
    }

    /**
     * 4. Stepper & Scenario Navigation Controls
     */
    function initScenarioNavigation() {
        // Pill click navigation
        var pills = document.querySelectorAll(".scenario-pill");
        pills.forEach(function (pill) {
            pill.addEventListener("click", function () {
                var targetIdx = parseInt(pill.getAttribute("data-scenario-index"), 10);
                showScenario(targetIdx);
            });
        });

        // Next scenario buttons
        var nextBtns = document.querySelectorAll(".btnNextScenario");
        nextBtns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                if (validateCurrentScenario()) {
                    showScenario(currentScenarioIndex + 1);
                }
            });
        });

        // Prev scenario buttons
        var prevBtns = document.querySelectorAll(".btnPrevScenario");
        prevBtns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                showScenario(currentScenarioIndex - 1);
            });
        });
    }

    /**
     * Validate that all claims in current scenario have a selected verdict
     */
    function validateCurrentScenario() {
        var panes = document.querySelectorAll(".scenario-pane");
        var activePane = panes[currentScenarioIndex];
        if (!activePane) return true;

        var claimCards = activePane.querySelectorAll(".claim-card");
        var hasUnanswered = false;

        claimCards.forEach(function (card) {
            var claimId = card.getAttribute("data-claim-id");
            var checked = card.querySelector('input[name="verdict_' + claimId + '"]:checked');
            if (!checked) {
                hasUnanswered = true;
                card.classList.remove("claim-card--evaluated");
                card.classList.add("claim-card--error");
            } else {
                card.classList.remove("claim-card--error");
            }
        });

        var errorBanner = document.getElementById("scenarioErrorBanner");
        if (hasUnanswered) {
            if (errorBanner) {
                errorBanner.style.display = "block";
                errorBanner.textContent = "Please select a classification verdict for each claim in this scenario before continuing.";
                errorBanner.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            return false;
        }

        if (errorBanner) errorBanner.style.display = "none";
        return true;
    }

    /**
     * Switch visible scenario pane
     */
    function showScenario(index) {
        if (index < 0 || index >= totalScenarios) return;

        var panes = document.querySelectorAll(".scenario-pane");
        var pills = document.querySelectorAll(".scenario-pill");

        panes.forEach(function (pane, idx) {
            pane.style.display = idx === index ? "block" : "none";
        });

        pills.forEach(function (pill, idx) {
            pill.classList.remove("scenario-pill--active");
            if (idx === index) {
                pill.classList.add("scenario-pill--active");
            }
        });

        currentScenarioIndex = index;

        // Update header badge
        var currentPane = panes[index];
        var domainBadge = document.getElementById("scenarioDomainBadge");
        if (domainBadge && currentPane) {
            var sId = currentPane.getAttribute("data-scenario-id");
            domainBadge.textContent = "Scenario " + (index + 1) + " of " + totalScenarios + " (" + sId + ")";
        }

        // Scroll to container top
        var formContainer = document.getElementById("verificationFormContainer");
        if (formContainer) formContainer.scrollIntoView({ behavior: "smooth" });
    }

    /**
     * Update progress indicator bars and pills
     */
    function updateOverallProgress() {
        var panes = document.querySelectorAll(".scenario-pane");
        var totalClaims = 0;
        var answeredClaims = 0;

        panes.forEach(function (pane, pIdx) {
            var sId = pane.getAttribute("data-scenario-id");
            var cards = pane.querySelectorAll(".claim-card");
            var paneAnswered = 0;

            cards.forEach(function (card) {
                totalClaims++;
                var cId = card.getAttribute("data-claim-id");
                var checked = card.querySelector('input[name="verdict_' + cId + '"]:checked');
                if (checked) {
                    answeredClaims++;
                    paneAnswered++;
                }
            });

            // If all claims in pane answered, mark pill as done
            var pill = document.getElementById("pill_" + sId);
            if (pill) {
                if (paneAnswered === cards.length && cards.length > 0) {
                    pill.classList.add("scenario-pill--done");
                } else {
                    pill.classList.remove("scenario-pill--done");
                }
            }
        });

        var pct = totalClaims > 0 ? (answeredClaims / totalClaims) * 100 : 0;
        var fill = document.getElementById("scenarioProgressFill");
        var text = document.getElementById("overallClaimProgressText");

        if (fill) fill.style.width = Math.max(12.5, pct) + "%";
        if (text) text.textContent = answeredClaims + " of " + totalClaims + " Claims Evaluated";
    }

    /**
     * 5. Submission Handler
     */
    function initSubmission() {
        var btnSubmit = document.getElementById("btnSubmitVerification");
        if (btnSubmit) {
            btnSubmit.addEventListener("click", function () {
                if (!validateAllScenarios()) return;

                btnSubmit.disabled = true;
                btnSubmit.textContent = "Grading & Computing Calibration...";

                var studentId = document.getElementById("inputStudentId") ? document.getElementById("inputStudentId").value.trim() : "";
                if (!studentId) studentId = "ANON_" + Math.random().toString(36).substring(2, 8).toUpperCase();

                var consentChk = document.getElementById("chkResearchConsent");
                var consentGiven = consentChk ? consentChk.checked : false;

                // Collect scenario submissions
                var submissions = collectSubmissions();

                var payload = {
                    submissions: submissions,
                    student_id: studentId,
                    consent_research_data: consentGiven,
                    scoring_result: cachedSurveyData ? cachedSurveyData.scoring : null,
                };

                fetch(EVALUATE_API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                })
                    .then(function (res) {
                        if (!res.ok) {
                            return res.json().then(function (err) {
                                throw new Error(err.error || "Verification evaluation failed.");
                            });
                        }
                        return res.json();
                    })
                    .then(function (data) {
                        lastEvaluationData = data;
                        renderTaskResults(data);
                    })
                    .catch(function (err) {
                        alert("Evaluation Error: " + err.message);
                    })
                    .finally(function () {
                        btnSubmit.disabled = false;
                        btnSubmit.textContent = "Submit Complete Verification Assessment \u2192";
                    });
            });
        }
    }

    /**
     * Validate all 8 scenarios prior to final submission
     */
    function validateAllScenarios() {
        var panes = document.querySelectorAll(".scenario-pane");
        var firstUnansweredPaneIdx = -1;

        panes.forEach(function (pane, pIdx) {
            var cards = pane.querySelectorAll(".claim-card");
            cards.forEach(function (card) {
                var cId = card.getAttribute("data-claim-id");
                var checked = card.querySelector('input[name="verdict_' + cId + '"]:checked');
                if (!checked) {
                    card.classList.add("claim-card--error");
                    if (firstUnansweredPaneIdx === -1) {
                        firstUnansweredPaneIdx = pIdx;
                    }
                }
            });
        });

        if (firstUnansweredPaneIdx !== -1) {
            showScenario(firstUnansweredPaneIdx);
            var banner = document.getElementById("scenarioErrorBanner");
            if (banner) {
                banner.style.display = "block";
                banner.textContent = "Incomplete Submission: Please classify all claims in Scenario " + (firstUnansweredPaneIdx + 1) + " before submitting.";
                banner.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            return false;
        }

        return true;
    }

    /**
     * Collect all claim verdicts, justification texts, and methods
     */
    function collectSubmissions() {
        var panes = document.querySelectorAll(".scenario-pane");
        var submissions = [];

        panes.forEach(function (pane) {
            var sId = pane.getAttribute("data-scenario-id");
            var claimList = [];
            var cards = pane.querySelectorAll(".claim-card");

            cards.forEach(function (card) {
                var cId = card.getAttribute("data-claim-id");
                var checked = card.querySelector('input[name="verdict_' + cId + '"]:checked');
                var methodSelect = document.getElementById("method_" + cId);
                var justTextarea = document.getElementById("just_" + cId);

                claimList.push({
                    claim_id: cId,
                    selected_verdict: checked ? checked.value : "CORRECT",
                    verification_method: methodSelect ? methodSelect.value : "Prior Domain Knowledge",
                    justification: justTextarea ? justTextarea.value.trim() : "",
                });
            });

            submissions.push({
                scenario_id: sId,
                claims: claimList,
            });
        });

        return submissions;
    }

    /**
     * 6. Render Post-Submission Evaluation Results Dashboard
     */
    function renderTaskResults(data) {
        var formContainer = document.getElementById("verificationFormContainer");
        var resultsContainer = document.getElementById("verificationResultsContainer");

        if (formContainer) formContainer.style.display = "none";
        if (resultsContainer) {
            resultsContainer.style.display = "block";
            resultsContainer.scrollIntoView({ behavior: "smooth" });
        }

        var evalData = data.verification_evaluation || {};
        var summary = evalData.summary || {};
        var cm = evalData.confusion_matrix || {};
        var calibration = data.calibration;

        // Meta tags
        var studentTag = document.getElementById("heroStudentTag");
        var timestampTag = document.getElementById("heroTimestampTag");
        if (studentTag) studentTag.textContent = "Participant: " + (data.student_id || "Anonymous");
        if (timestampTag) timestampTag.textContent = "Completed: " + new Date().toLocaleTimeString();

        // Hero Metric Values
        var accPct = summary.accuracy_pct !== undefined ? summary.accuracy_pct : (summary.accuracy * 100);
        var recPct = (summary.recall * 100);
        var precPct = (summary.precision * 100);
        var rubricPct = summary.rubric_pct || 0;

        document.getElementById("valHeroAccuracy").textContent = accPct.toFixed(1) + "%";
        document.getElementById("valHeroRecall").textContent = recPct.toFixed(1) + "%";
        document.getElementById("valHeroPrecision").textContent = precPct.toFixed(1) + "%";
        document.getElementById("valHeroRubric").textContent = rubricPct.toFixed(1) + "%";

        // Calibration Hero Badge
        var badgeHero = document.getElementById("calibrationBadgeHero");
        if (badgeHero) {
            if (calibration && calibration.calibration_zone) {
                var zId = calibration.calibration_zone.zone_id.toLowerCase();
                var badgeClass = "calib-badge--q1";
                if (zId.indexOf("q2") !== -1) badgeClass = "calib-badge--q2";
                else if (zId.indexOf("q3") !== -1) badgeClass = "calib-badge--q3";
                else if (zId.indexOf("q4") !== -1) badgeClass = "calib-badge--q4";

                badgeHero.innerHTML = '<div class="calib-badge ' + badgeClass + '">' +
                    escapeHtml(calibration.calibration_zone.zone_title) +
                    '</div>';
            } else {
                badgeHero.innerHTML = '<div class="calib-badge calib-badge--q3">' +
                    'Independent Task Evaluation' +
                    '</div>';
            }
        }

        // Section 1: Confusion Matrix & Detailed Metrics
        document.getElementById("countTP").textContent = cm.true_positives !== undefined ? cm.true_positives : 0;
        document.getElementById("countFN").textContent = cm.false_negatives !== undefined ? cm.false_negatives : 0;
        document.getElementById("countFP").textContent = cm.false_positives !== undefined ? cm.false_positives : 0;
        document.getElementById("countTN").textContent = cm.true_negatives !== undefined ? cm.true_negatives : 0;

        document.getElementById("rateAccuracyText").textContent = accPct.toFixed(1) + "% (" + summary.correct_classifications + "/" + summary.total_claims_evaluated + ")";
        document.getElementById("barAccuracy").style.width = accPct + "%";

        document.getElementById("rateRecallText").textContent = recPct.toFixed(1) + "%";
        document.getElementById("barRecall").style.width = recPct + "%";

        var specPct = (summary.specificity * 100);
        document.getElementById("rateSpecificityText").textContent = specPct.toFixed(1) + "%";
        document.getElementById("barSpecificity").style.width = specPct + "%";

        document.getElementById("rateF1Text").textContent = (summary.f1_score !== undefined ? summary.f1_score : 0).toFixed(3);
        document.getElementById("barF1").style.width = ((summary.f1_score || 0) * 100) + "%";

        document.getElementById("rateRubricText").textContent = (summary.rubric_points_earned || 0) + " / " + (summary.rubric_points_possible || 48) + " (" + rubricPct.toFixed(1) + "%)";
        document.getElementById("barRubric").style.width = rubricPct + "%";

        // Section 2: Metacognitive Calibration Analysis
        renderCalibrationSection(calibration, summary);

        // Section 3: Scenario-by-Scenario Solutions Breakdown
        renderSolutionsBreakdown(evalData.claim_evaluations || []);

        // Section 4: Dual-Tier Recommendations
        renderRecommendations(evalData.performance_feedback || [], calibration);
    }

    /**
     * Render Section 2: Metacognitive Calibration & Plotly Scatter Matrix
     */
    function renderCalibrationSection(calib, summary) {
        var container = document.getElementById("calibrationContainer");
        if (!container) return;

        if (!calib) {
            container.innerHTML = '<div class="card" style="padding: 1.5rem; background: #f8fafc; border: 1px dashed #cbd5e1; text-align: center;">' +
                '<h4 style="margin: 0 0 0.5rem; color: #1e293b;">Survey Linkage Required for Calibration</h4>' +
                '<p style="font-size: 0.88rem; color: #64748b; max-width: 650px; margin: 0 auto 1.25rem;">' +
                'Metacognitive calibration compares your self-reported Verification Behaviour (VB) with your demonstrated task accuracy. Complete the 26-item survey to reveal your calibration quadrant position.' +
                '</p>' +
                '<a href="/component2/assessment" class="btn btn--primary btn--sm">&#8594; Complete 26-Item Student Survey</a>' +
                '</div>';
            return;
        }

        var m = calib.metrics || {};
        var z = calib.calibration_zone || {};
        var delta = m.discrepancy_index_delta !== undefined ? m.discrepancy_index_delta : 0;
        var deltaColor = delta > 0.15 ? "#dc2626" : (delta < -0.15 ? "#0284c7" : "#16a34a");

        var html = '<div class="card" style="padding: 1.5rem; margin-bottom: 1.5rem;">' +
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">' +
            '<div>' +
            '<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">' +
            '<span class="calib-badge calib-badge--q1" style="font-size: 0.75rem;">' + escapeHtml(z.zone_id) + '</span>' +
            '<h4 style="margin: 0; font-size: 1.05rem; color: #0f172a;">' + escapeHtml(z.zone_title) + '</h4>' +
            '</div>' +
            '<p style="font-size: 0.88rem; color: #334155; line-height: 1.55; margin-bottom: 1rem;">' + escapeHtml(calib.alignment_summary) + '</p>' +
            '<div style="background: #f1f5f9; padding: 0.9rem; border-radius: var(--radius-sm); font-size: 0.82rem; margin-bottom: 1rem;">' +
            '<div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">' +
            '<span>Self-Reported VB (1-5):</span> <strong>' + m.self_reported_vb_mean.toFixed(2) + ' (' + m.vb_percentile.toFixed(1) + 'th %ile)</strong>' +
            '</div>' +
            '<div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">' +
            '<span>Normalized VB [0, 1]:</span> <strong>' + m.normalized_vb_minmax.toFixed(3) + '</strong>' +
            '</div>' +
            '<div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">' +
            '<span>Demonstrated Task Accuracy:</span> <strong>' + (m.task_accuracy * 100).toFixed(1) + '%</strong>' +
            '</div>' +
            '<div style="display: flex; justify-content: space-between; padding-top: 0.35rem; border-top: 1px dashed #cbd5e1; color:' + deltaColor + ';">' +
            '<span>Discrepancy Index (&Delta;<sub>calib</sub> = VB<sub>norm</sub> &minus; Acc):</span> <strong>' + (delta > 0 ? "+" : "") + delta.toFixed(3) + '</strong>' +
            '</div>' +
            '</div>' +
            '<p style="font-size: 0.82rem; color: #475569; line-height: 1.5; margin: 0;">' + escapeHtml(calib.detailed_interpretation) + '</p>' +
            '</div>' +
            '<div>' +
            '<h5 style="margin: 0 0 0.5rem; font-size: 0.88rem; color: #1e293b; text-align: center;">Metacognitive Calibration Matrix (Plotly)</h5>' +
            '<div id="plotlyCalibrationPlot" style="min-height: 340px;"></div>' +
            '</div>' +
            '</div>' +
            '</div>';

        container.innerHTML = html;

        // Render Plotly Calibration Chart
        renderPlotlyCalibration(m.normalized_vb_minmax, m.task_accuracy, z.zone_title);
    }

    /**
     * Interactive Plotly 4-Quadrant Calibration Scatter Chart
     */
    function renderPlotlyCalibration(vbNorm, taskAcc, zoneTitle) {
        var plotDiv = document.getElementById("plotlyCalibrationPlot");
        if (!plotDiv || typeof Plotly === "undefined") return;

        var studentTrace = {
            x: [vbNorm],
            y: [taskAcc],
            mode: "markers+text",
            type: "scatter",
            text: ["Your Score"],
            textposition: "top center",
            textfont: { family: "sans-serif", size: 12, color: "#1e293b" },
            marker: {
                size: 16,
                color: "#2563eb",
                line: { color: "#ffffff", width: 2 },
                symbol: "diamond",
            },
            name: "Your Score",
            hoverinfo: "text",
            hovertext: ["Normalized VB: " + vbNorm.toFixed(2) + "<br>Task Accuracy: " + (taskAcc * 100).toFixed(1) + "%<br>" + zoneTitle],
        };

        var layout = {
            margin: { t: 30, r: 25, b: 45, l: 45 },
            xaxis: {
                title: "Normalized Self-Reported VB [0, 1]",
                range: [0, 1.05],
                tickvals: [0, 0.25, 0.5, 0.7, 1.0],
                gridcolor: "#e2e8f0",
                zeroline: false,
            },
            yaxis: {
                title: "Demonstrated Task Accuracy [0, 1]",
                range: [0, 1.05],
                tickvals: [0, 0.25, 0.5, 0.7, 1.0],
                gridcolor: "#e2e8f0",
                zeroline: false,
            },
            shapes: [
                // Vertical cohort median line at VB=3.80 => norm = 0.70
                {
                    type: "line",
                    x0: 0.70, x1: 0.70, y0: 0, y1: 1,
                    line: { color: "#94a3b8", width: 1.5, dash: "dot" },
                },
                // Horizontal mastery line at Acc = 0.70
                {
                    type: "line",
                    x0: 0, x1: 1, y0: 0.70, y1: 0.70,
                    line: { color: "#94a3b8", width: 1.5, dash: "dot" },
                },
            ],
            annotations: [
                { x: 0.90, y: 0.95, text: "Q1: Calibrated", showarrow: false, font: { size: 10, color: "#15803d" } },
                { x: 0.90, y: 0.15, text: "Q2: Illusion", showarrow: false, font: { size: 10, color: "#b91c1c" } },
                { x: 0.25, y: 0.95, text: "Q3: Cautious", showarrow: false, font: { size: 10, color: "#0369a1" } },
                { x: 0.25, y: 0.15, text: "Q4: Vulnerable", showarrow: false, font: { size: 10, color: "#92400e" } },
            ],
            showlegend: false,
            autosize: true,
        };

        var config = { responsive: true, displayModeBar: false };
        Plotly.newPlot(plotDiv, [studentTrace], layout, config);
    }

    /**
     * Render Section 3: Scenario-by-Scenario Detailed Solutions Breakdown
     */
    function renderSolutionsBreakdown(claimEvals) {
        var container = document.getElementById("solutionsBreakdownContainer");
        if (!container) return;

        if (!claimEvals || claimEvals.length === 0) {
            container.innerHTML = '<p style="color: #64748b;">No claim evaluations recorded.</p>';
            return;
        }

        var html = '<div style="display: flex; flex-direction: column; gap: 0.75rem;">';

        claimEvals.forEach(function (ev, idx) {
            var isCorrect = ev.is_correct_classification;
            var borderClass = isCorrect ? "solution-claim-row--correct" : "solution-claim-row--incorrect";
            var statusIcon = isCorrect ? '<span style="color:#16a34a; font-weight:700;">&#10003; Correct</span>' : '<span style="color:#dc2626; font-weight:700;">&#10007; Missed</span>';

            html += '<div class="solution-claim-row ' + borderClass + '">' +
                '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">' +
                '<span style="font-size: 0.75rem; font-weight: 700; color: #475569;">' + escapeHtml(ev.scenario_id) + ' &bull; ' + escapeHtml(ev.claim_id) + '</span>' +
                '<div>' + statusIcon + ' &bull; <span style="font-size: 0.75rem; font-weight:600;">Rubric: ' + ev.rubric_score + '/2 pts</span></div>' +
                '</div>' +
                '<div style="font-size: 0.88rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">&ldquo;' + escapeHtml(ev.statement) + '&rdquo;</div>' +
                '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.8rem; margin-bottom: 0.5rem; background: #f8fafc; padding: 0.6rem; border-radius: 4px;">' +
                '<div><strong>Your Verdict:</strong> ' + escapeHtml(ev.student_verdict) + '</div>' +
                '<div><strong>Expert Ground Truth:</strong> <span style="font-weight:700; color:' + (ev.ground_truth === "CORRECT" ? "#16a34a" : "#dc2626") + ';">' + escapeHtml(ev.ground_truth) + '</span></div>' +
                '</div>' +
                '<div style="font-size: 0.82rem; color: #334155; line-height: 1.5; margin-bottom: 0.4rem;">' +
                '<strong>Expert Derivation:</strong> ' + escapeHtml(ev.expert_explanation) +
                '</div>' +
                '<div style="font-size: 0.75rem; color: #64748b; font-style: italic;">' +
                'Academic Citation: ' + escapeHtml(ev.reference_citation) +
                '</div>' +
                '</div>';
        });

        html += '</div>';
        container.innerHTML = html;
    }

    /**
     * Render Section 4: Dual-Tier Educational Recommendations
     */
    function renderRecommendations(feedbackList, calibration) {
        var container = document.getElementById("verificationRecommendationsContainer");
        if (!container) return;

        var html = '<div style="display: flex; flex-direction: column; gap: 1rem;">';

        if (feedbackList && feedbackList.length > 0) {
            feedbackList.forEach(function (fb) {
                var borderCol = fb.priority === "HIGH" ? "#dc2626" : (fb.priority === "MEDIUM" ? "#2563eb" : "#16a34a");
                html += '<div class="card" style="padding: 1.25rem; border-left: 4px solid ' + borderCol + ';">' +
                    '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">' +
                    '<h4 style="margin: 0; font-size: 0.95rem; color: #0f172a;">' + escapeHtml(fb.title) + '</h4>' +
                    '<span class="badge" style="font-size: 0.7rem; background: #f1f5f9; color: #475569;">' + escapeHtml(fb.category) + ' &bull; ' + escapeHtml(fb.priority) + '</span>' +
                    '</div>' +
                    '<p style="font-size: 0.85rem; color: #475569; margin: 0 0 0.6rem; line-height: 1.5;">' + escapeHtml(fb.diagnostic) + '</p>' +
                    '<div style="font-size: 0.82rem; color: #1e293b; background: #f8fafc; padding: 0.6rem 0.8rem; border-radius: 4px;">' +
                    '<strong>Recommended Action:</strong> ' + escapeHtml(fb.action_strategy) +
                    '</div>' +
                    '</div>';
            });
        }

        // Add SEM structural context if calibration available
        if (calibration && calibration.trust_dependence_context) {
            var ctx = calibration.trust_dependence_context;
            html += '<div class="card" style="padding: 1.25rem; border-left: 4px solid #6366f1; background: #fbfbfe;">' +
                '<h4 style="margin: 0 0 0.35rem; font-size: 0.95rem; color: #3730a3;">SEM Structural Model Alignment: ' + escapeHtml(ctx.risk_category) + '</h4>' +
                '<p style="font-size: 0.84rem; color: #4338ca; margin: 0; line-height: 1.55;">' + escapeHtml(ctx.description) + '</p>' +
                '</div>';
        }

        html += '</div>';
        container.innerHTML = html;
    }

    /**
     * 7. Export Combined Report Handlers (CSV & JSON)
     */
    function initExportButtons() {
        var btnCsv = document.getElementById("btnDownloadCombinedCsv");
        var btnJson = document.getElementById("btnDownloadCombinedJson");

        if (btnCsv) {
            btnCsv.addEventListener("click", function () {
                exportCombinedReport("csv");
            });
        }

        if (btnJson) {
            btnJson.addEventListener("click", function () {
                exportCombinedReport("json");
            });
        }
    }

    function exportCombinedReport(format) {
        if (!lastEvaluationData) {
            alert("Please complete the verification assessment before exporting.");
            return;
        }

        var payload = {
            format: format,
            scoring_result: cachedSurveyData ? cachedSurveyData.scoring : null,
            verification_eval: lastEvaluationData.verification_evaluation,
            calibration_result: lastEvaluationData.calibration,
            student_meta: {
                student_id: lastEvaluationData.student_id || "Anonymous",
                timestamp: new Date().toISOString(),
            },
        };

        fetch(COMBINED_REPORT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then(function (res) {
                if (!res.ok) throw new Error("Combined report export failed.");
                return res.blob();
            })
            .then(function (blob) {
                var url = window.URL.createObjectURL(blob);
                var a = document.createElement("a");
                a.style.display = "none";
                a.href = url;
                a.download = format === "csv" ? "Combined_AI_Trust_and_Verification_Report.csv" : "Combined_AI_Trust_and_Verification_Report.json";
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(function (err) {
                alert("Export Error: " + err.message);
            });
    }

    /**
     * 8. Retake Task Handler
     */
    function initRetakeButton() {
        var btnRetake = document.getElementById("btnRetakeTask");
        if (btnRetake) {
            btnRetake.addEventListener("click", function () {
                if (confirm("Are you sure you want to retake the verification assessment? Your current answers will be reset.")) {
                    window.location.reload();
                }
            });
        }
    }

    /**
     * HTML escape helper
     */
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

})();
