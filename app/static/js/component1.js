/**
 * component1.js — Component 1: AI Study Habits Assessment
 * Psychometric Learning Analytics Framework (J26-DS-310)
 *
 * Implements a 3-stage progressive user journey:
 * 1. Intro View  -> Concise overview & optional viva demo presets
 * 2. Wizard View -> 4-step guided form over exact 20 behavioral inputs
 * 3. Results View -> Plain-language risk profile, calibrated scale, directional
 *                   factor bars, practical suggestions, and expandable LinearSHAP table
 */

(function () {
    "use strict";

    /* ==================================================================
       1. Constants, Validation Schema & Validated Content
    ================================================================== */
    var PREDICT_URL = "/api/component1/predict";

    var SECTION_REQUIREMENTS = {
        1: [
            { id: "pred_degree_field", type: "select", cardId: "card_degree_field", errId: "err_degree_field", hintId: "hint_degree_field", label: "Q1: Academic Field / Discipline" },
            { id: "pred_academic_year", type: "select", cardId: "card_academic_year", errId: "err_academic_year", hintId: "hint_academic_year", label: "Q2: Current Academic Year" },
            { id: "pred_age_group", type: "select", cardId: "card_age_group", errId: "err_age_group", hintId: "hint_age_group", label: "Q3: Age Group" },
            { name: "ai_usage_freq", type: "radio", cardId: "card_ai_usage_freq", errId: "err_ai_usage_freq", label: "Q4: Frequency of Generative AI Usage" },
            { id: "pred_ai_time_per_week", type: "select", cardId: "card_ai_time_per_week", errId: "err_ai_time_per_week", hintId: "hint_ai_time_per_week", label: "Q5: Estimated Weekly AI Usage Time" },
            { name: "tools_used", type: "checkbox", cardId: "card_tools_used", errId: "err_tools_used", label: "Q6: Generative AI Tools Actively Utilized" }
        ],
        2: [
            { name: "Q20_task_delegation_freq", type: "radio", cardId: "card_Q20", errId: "err_Q20", label: "Q7: Frequency of Delegating Complete Tasks" },
            { name: "tasks_delegated", type: "checkbox", cardId: "card_tasks_delegated", errId: "err_tasks_delegated", label: "Q8: Academic Tasks Typically Delegated" },
            { name: "Q1_direct_use_freq", type: "radio", cardId: "card_Q1", errId: "err_Q1", label: "Q9: Direct Use Without Modification" },
            { name: "Q22_effort_on_ai_answers", type: "radio", cardId: "card_Q22", errId: "err_Q22", label: "Q10: Cognitive Effort Reviewing AI Outputs" }
        ],
        3: [
            { name: "Q2_verify_info", type: "radio", cardId: "card_Q2", errId: "err_Q2", label: "Q11: Verification of AI-Generated Claims" },
            { name: "Q3_compare_sources", type: "radio", cardId: "card_Q3", errId: "err_Q3", label: "Q12: Cross-Referencing Independent Sources" },
            { name: "Q4_check_accuracy", type: "radio", cardId: "card_Q4", errId: "err_Q4", label: "Q13: Checking Numerical & Formula Accuracy" },
            { name: "Q5_understand_reasoning", type: "radio", cardId: "card_Q5", errId: "err_Q5", label: "Q14: Conceptual Comprehension Before Adoption" },
            { name: "Q6_modify_content", type: "radio", cardId: "card_Q6", errId: "err_Q6", label: "Q15: Personal Voice & Critical Synthesis" }
        ],
        4: [
            { name: "Q7_attempt_independently", type: "radio", cardId: "card_Q7", errId: "err_Q7", label: "Q16: Independent Attempt Before Prompting" },
            { name: "Q8_complete_without_ai", type: "radio", cardId: "card_Q8", errId: "err_Q8", label: "Q17: Confidence Without AI" },
            { name: "Q9_learning_assistant", type: "radio", cardId: "card_Q9", errId: "err_Q9", label: "Q18: Explanatory Study Companion Mindset" },
            { name: "Q30_trust_accuracy", type: "radio", cardId: "card_Q30", errId: "err_Q30", label: "Q19: Uncritical Trust in AI Accuracy" },
            { name: "Q33_trust_appropriate_support", type: "radio", cardId: "card_Q33", errId: "err_Q33", label: "Q20: Deference to AI Problem Guidance" }
        ]
    };

    var PRESETS = {
        low: {
            label: "Low-Risk sample profile",
            data: {
                degree_field: "Natural_Applied_Sciences",
                academic_year: "3",
                age_group: "2",
                ai_usage_freq: "1",
                ai_time_per_week: "1",
                tools_used: ["ChatGPT"],
                Q20_task_delegation_freq: "1",
                tasks_delegated: ["Explaining concepts"],
                Q1_direct_use_freq: "1",
                Q22_effort_on_ai_answers: "5",
                Q2_verify_info: "5",
                Q3_compare_sources: "5",
                Q4_check_accuracy: "5",
                Q5_understand_reasoning: "5",
                Q6_modify_content: "5",
                Q7_attempt_independently: "5",
                Q8_complete_without_ai: "5",
                Q9_learning_assistant: "5",
                Q30_trust_accuracy: "2",
                Q33_trust_appropriate_support: "2"
            }
        },
        med: {
            label: "Medium-Risk sample profile",
            data: {
                degree_field: "Computing_IT",
                academic_year: "2",
                age_group: "2",
                ai_usage_freq: "2",
                ai_time_per_week: "3",
                tools_used: ["ChatGPT", "Google Gemini"],
                Q20_task_delegation_freq: "3",
                tasks_delegated: ["Explaining concepts", "Summarising materials"],
                Q1_direct_use_freq: "3",
                Q22_effort_on_ai_answers: "3",
                Q2_verify_info: "3",
                Q3_compare_sources: "3",
                Q4_check_accuracy: "3",
                Q5_understand_reasoning: "3",
                Q6_modify_content: "3",
                Q7_attempt_independently: "3",
                Q8_complete_without_ai: "3",
                Q9_learning_assistant: "3",
                Q30_trust_accuracy: "3",
                Q33_trust_appropriate_support: "3"
            }
        },
        high: {
            label: "High-Risk sample profile",
            data: {
                degree_field: "Business_Economics",
                academic_year: "1",
                age_group: "1",
                ai_usage_freq: "4",
                ai_time_per_week: "5",
                tools_used: ["ChatGPT", "Claude", "Perplexity AI"],
                Q20_task_delegation_freq: "5",
                tasks_delegated: [
                    "Writing assignments",
                    "Summarising materials",
                    "Programming problems",
                    "Mathematical problems"
                ],
                Q1_direct_use_freq: "5",
                Q22_effort_on_ai_answers: "1",
                Q2_verify_info: "1",
                Q3_compare_sources: "1",
                Q4_check_accuracy: "1",
                Q5_understand_reasoning: "1",
                Q6_modify_content: "1",
                Q7_attempt_independently: "1",
                Q8_complete_without_ai: "1",
                Q9_learning_assistant: "1",
                Q30_trust_accuracy: "5",
                Q33_trust_appropriate_support: "5"
            }
        }
    };

    var ACTIONABLE_IDEAS = {
        low: [
            {
                title: "Maintain First-Principles Problem Solving",
                text: "Continue attempting coursework challenges independently before consulting AI. This productive struggle builds durable understanding and exam readiness."
            },
            {
                title: "Use AI as a Critique Companion",
                text: "Prompt the AI to critique your written reasoning or challenge your assumptions rather than asking it to generate first drafts directly."
            },
            {
                title: "Keep Auditing Citations & Logic",
                text: "Continue verifying references and technical steps against lecture notes and primary textbooks to catch subtle errors early."
            }
        ],
        medium: [
            {
                title: "Set Independent Focus Windows",
                text: "Spend 25 to 30 minutes working on each new assignment problem yourself before opening an AI assistant."
            },
            {
                title: "Reconstruct Concepts From Memory",
                text: "After reading an AI explanation, close the tab and write out the key steps or reasoning in your own words."
            },
            {
                title: "Check Core Assertions",
                text: "Avoid accepting AI answers as final. Cross-check formulas, code behavior, and arguments against official documentation or course slides."
            }
        ],
        high: [
            {
                title: "Step Back From Whole-Task Delegation",
                text: "Avoid asking AI to solve complete assignments. Restrict usage to outlining ideas or troubleshooting specific roadblocks."
            },
            {
                title: "Practice Unassisted Problem Solving",
                text: "Work through foundational exercises without AI tools to rebuild confidence in your own analytical ability."
            },
            {
                title: "Verify Before Adopting",
                text: "Treat every AI response as an unverified draft—inspect logic, calculations, and sources thoroughly before submitting work."
            }
        ]
    };

    var RISK_INTERPRETATION = {
        low: "Your responses reflect strong independent study habits. You generally attempt problems yourself first, verify AI claims critically, and use Generative AI as a learning support rather than a replacement for your own thinking.",
        medium: "Your responses suggest a mixed pattern of AI use. While you maintain some verification practices, delegating complete tasks or skipping independent first attempts can gradually reduce your problem-solving confidence.",
        high: "Your responses indicate elevated reliance on Generative AI. Frequent delegation of full coursework tasks, limited editing or verification, and lower confidence working without AI point toward noticeable cognitive offloading."
    };

    /* ==================================================================
       2. DOM Elements & State
    ================================================================== */
    var viewIntro           = document.getElementById("c1ViewIntro");
    var viewWizard          = document.getElementById("c1ViewWizard");
    var viewResults         = document.getElementById("reflectionResultSection");
    var liveAnnouncer       = document.getElementById("c1LiveAnnouncer");

    var introTitle          = document.getElementById("c1IntroTitle");
    var btnStartAssessment  = document.getElementById("btnStartAssessment");
    var btnBackToIntro      = document.getElementById("btnBackToIntro");
    var answeredCounter     = document.getElementById("c1AnsweredCounter");
    var progressBar         = document.getElementById("c1ProgressBar");

    var demoNotice          = document.getElementById("c1DemoActiveNotice");
    var demoNoticeText      = document.getElementById("c1DemoActiveText");
    var btnJumpToReview     = document.getElementById("btnJumpToReview");

    var assessmentForm      = document.getElementById("reflectionAssessmentForm");
    var sectionErrorBanner  = document.getElementById("sectionValidationError");
    var sectionErrorList    = document.getElementById("sectionValidationErrorList");

    var stepPills = [
        document.getElementById("stepPill1"),
        document.getElementById("stepPill2"),
        document.getElementById("stepPill3"),
        document.getElementById("stepPill4")
    ];

    var stepPanels = [
        document.getElementById("formStep1"),
        document.getElementById("formStep2"),
        document.getElementById("formStep3"),
        document.getElementById("formStep4")
    ];

    var stepHeadings = [
        document.getElementById("stepHeading1"),
        document.getElementById("stepHeading2"),
        document.getElementById("stepHeading3"),
        document.getElementById("stepHeading4")
    ];

    var btnNextStep1        = document.getElementById("btnNextStep1");
    var btnPrevStep2        = document.getElementById("btnPrevStep2");
    var btnNextStep2        = document.getElementById("btnNextStep2");
    var btnPrevStep3        = document.getElementById("btnPrevStep3");
    var btnNextStep3        = document.getElementById("btnNextStep3");
    var btnPrevStep4        = document.getElementById("btnPrevStep4");

    var btnCalculatePrediction = document.getElementById("btnCalculatePrediction");
    var btnResetAssessment  = document.getElementById("btnResetAssessment");
    var btnClearProfile     = document.getElementById("btnClearProfile");
    var btnPresetLow        = document.getElementById("btnPresetLow");
    var btnPresetMed        = document.getElementById("btnPresetMed");
    var btnPresetHigh       = document.getElementById("btnPresetHigh");

    // Results Elements
    var predictionResultCard      = document.getElementById("predictionResultCard");
    var resultsHeading            = document.getElementById("resultsHeading");
    var riskCategoryBadge         = document.getElementById("riskCategoryBadge");
    var riskInterpretationSummary = document.getElementById("riskInterpretationSummary");
    var continuousScoreVal        = document.getElementById("continuousScoreVal");
    var scoreSpectrumMarker       = document.getElementById("scoreSpectrumMarker");
    var scoreMarkerLabel          = document.getElementById("scoreMarkerLabel");
    var scaleAriaSummary          = document.getElementById("c1ScaleAriaSummary");

    var elevatingContainer        = document.getElementById("elevatingFactorsContainer");
    var mitigatingContainer       = document.getElementById("mitigatingFactorsContainer");
    var actionableIdeasGrid       = document.getElementById("actionableIdeasGrid");

    var btnStartNewAssessment     = document.getElementById("btnStartNewAssessment");
    var btnReviewAnswers          = document.getElementById("btnReviewAnswers");
    var btnToggleDetails          = document.getElementById("btnToggleDetails");
    var resultsTechnicalDetails   = document.getElementById("resultsTechnicalDetails");

    var probBarLow                = document.getElementById("probBarLow");
    var probValLow                = document.getElementById("probValLow");
    var probBarMed                = document.getElementById("probBarMed");
    var probValMed                = document.getElementById("probValMed");
    var probBarHigh               = document.getElementById("probBarHigh");
    var probValHigh               = document.getElementById("probValHigh");
    var modelArchVal              = document.getElementById("c1ModelArchVal");
    var rawScoreVal               = document.getElementById("c1RawScoreVal");
    var shapTableBody             = document.getElementById("c1ShapTableBody");
    var backendDisclaimerEl       = document.getElementById("c1BackendDisclaimer");

    var currentStep = 1;
    var activeView = "intro";

    /* ==================================================================
       3. Utilities (Motion, Announcements, View Transitions)
    ================================================================== */
    function getScrollBehavior() {
        var prefersReduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        return prefersReduced ? "auto" : "smooth";
    }

    function announce(message) {
        if (!liveAnnouncer) return;
        liveAnnouncer.textContent = "";
        setTimeout(function () {
            liveAnnouncer.textContent = message;
        }, 50);
    }

    function focusSafely(el) {
        if (!el || typeof el.focus !== "function") return;
        try {
            el.focus({ preventScroll: false });
        } catch (e) {
            el.focus();
        }
    }

    function showView(viewName, focusTarget) {
        activeView = viewName;

        if (viewIntro) {
            if (viewName === "intro") viewIntro.removeAttribute("hidden");
            else viewIntro.setAttribute("hidden", "");
        }
        if (viewWizard) {
            if (viewName === "wizard") viewWizard.removeAttribute("hidden");
            else viewWizard.setAttribute("hidden", "");
        }
        if (viewResults) {
            if (viewName === "results") viewResults.removeAttribute("hidden");
            else viewResults.setAttribute("hidden", "");
        }

        if (focusTarget) {
            focusSafely(focusTarget);
        }
        window.scrollTo({ top: 0, behavior: getScrollBehavior() });
    }

    function countAnsweredQuestions() {
        var totalAnswered = 0;
        for (var s = 1; s <= 4; s++) {
            var reqs = SECTION_REQUIREMENTS[s];
            reqs.forEach(function (req) {
                if (req.type === "select") {
                    var el = document.getElementById(req.id);
                    if (el && el.value && el.value.trim() !== "") totalAnswered++;
                } else if (req.type === "radio") {
                    if (document.querySelector('input[name="' + req.name + '"]:checked')) totalAnswered++;
                } else if (req.type === "checkbox") {
                    if (document.querySelectorAll('input[name="' + req.name + '"]:checked').length > 0) totalAnswered++;
                }
            });
        }
        return totalAnswered;
    }

    function updateAnsweredCounter() {
        if (!answeredCounter) return;
        var count = countAnsweredQuestions();
        answeredCounter.textContent = count + " of 20 answered";
    }

    /* ==================================================================
       4. Stepper Navigation
    ================================================================== */
    function isStepComplete(stepNumber) {
        var reqs = SECTION_REQUIREMENTS[stepNumber] || [];
        return reqs.every(function (req) {
            if (req.type === "select") {
                var el = document.getElementById(req.id);
                return !!(el && el.value && el.value.trim() !== "");
            }
            if (req.type === "radio") {
                return !!document.querySelector('input[name="' + req.name + '"]:checked');
            }
            if (req.type === "checkbox") {
                return document.querySelectorAll('input[name="' + req.name + '"]:checked').length > 0;
            }
            return true;
        });
    }

    function showStep(stepNumber, shouldFocusHeading) {
        currentStep = stepNumber;

        stepPanels.forEach(function (panel, idx) {
            if (!panel) return;
            if (idx + 1 === stepNumber) {
                panel.removeAttribute("hidden");
            } else {
                panel.setAttribute("hidden", "");
            }
        });

        stepPills.forEach(function (pill, idx) {
            if (!pill) return;
            var num = idx + 1;
            pill.classList.remove("is-active", "is-completed");
            pill.removeAttribute("aria-current");

            if (num === stepNumber) {
                pill.classList.add("is-active");
                pill.setAttribute("aria-current", "step");
            } else if (isStepComplete(num)) {
                pill.classList.add("is-completed");
            }
        });

        if (progressBar) {
            progressBar.value = stepNumber;
            progressBar.textContent = "Section " + stepNumber + " of 4";
        }

        hideSectionValidationBanner();

        if (shouldFocusHeading && stepHeadings[stepNumber - 1]) {
            focusSafely(stepHeadings[stepNumber - 1]);
            window.scrollTo({ top: 0, behavior: getScrollBehavior() });
        }
    }

    /* ==================================================================
       5. Accessible Validation & Focus Management
    ================================================================== */
    function getFirstControlForReq(req) {
        if (req.type === "select") {
            return document.getElementById(req.id);
        }
        return document.querySelector('input[name="' + req.name + '"]');
    }

    function syncControlErrorAria(req, hasError) {
        var controls = [];
        if (req.type === "select") {
            var el = document.getElementById(req.id);
            if (el) controls.push(el);
        } else {
            controls = Array.prototype.slice.call(
                document.querySelectorAll('input[name="' + req.name + '"]')
            );
        }

        controls.forEach(function (ctrl, idx) {
            if (hasError) {
                if (idx === 0) {
                    ctrl.setAttribute("aria-invalid", "true");
                    var described = [];
                    if (req.hintId) described.push(req.hintId);
                    described.push(req.errId);
                    ctrl.setAttribute("aria-describedby", described.join(" "));
                }
                if (req.type === "select") ctrl.classList.add("c1-user-invalid");
            } else {
                ctrl.setAttribute("aria-invalid", "false");
                if (req.hintId) ctrl.setAttribute("aria-describedby", req.hintId);
                else ctrl.removeAttribute("aria-describedby");
                if (req.type === "select") ctrl.classList.remove("c1-user-invalid");
            }
        });
    }

    function clearRequirementError(req) {
        var card = document.getElementById(req.cardId);
        if (card) {
            card.classList.remove("c1-q-card--error");
        }
        var errEl = document.getElementById(req.errId);
        if (errEl) {
            errEl.textContent = "";
            errEl.setAttribute("hidden", "");
        }
        syncControlErrorAria(req, false);
    }

    function showRequirementError(req, message) {
        var card = document.getElementById(req.cardId);
        if (card) {
            card.classList.add("c1-q-card--error");
        }
        var errEl = document.getElementById(req.errId);
        if (errEl) {
            errEl.textContent = message;
            errEl.removeAttribute("hidden");
        }
        syncControlErrorAria(req, true);
    }

    function showSectionValidationBanner(missingItems) {
        if (!sectionErrorBanner || !sectionErrorList) return;
        var titleEl = document.getElementById("c1ValidationHeading");
        if (titleEl) {
            titleEl.textContent = "Please complete all required questions in this section:";
        }
        var frag = document.createDocumentFragment();

        missingItems.forEach(function (req) {
            var li = document.createElement("li");
            li.setAttribute("data-card-id", req.cardId);
            var jumpBtn = document.createElement("button");
            jumpBtn.type = "button";
            jumpBtn.className = "c1-error-jump";
            jumpBtn.textContent = req.label;
            jumpBtn.addEventListener("click", function () {
                var targetCtrl = getFirstControlForReq(req);
                var card = document.getElementById(req.cardId);
                if (card) card.scrollIntoView({ behavior: getScrollBehavior(), block: "center" });
                focusSafely(targetCtrl);
            });
            li.appendChild(jumpBtn);
            frag.appendChild(li);
        });

        sectionErrorList.replaceChildren(frag);
        sectionErrorBanner.removeAttribute("hidden");
        focusSafely(sectionErrorBanner);
        sectionErrorBanner.scrollIntoView({ behavior: getScrollBehavior(), block: "nearest" });
    }

    function showRequestErrorBanner(message) {
        if (!sectionErrorBanner || !sectionErrorList) return;
        var titleEl = document.getElementById("c1ValidationHeading");
        if (titleEl) {
            titleEl.textContent = "Unable to generate assessment results";
        }
        var li = document.createElement("li");
        li.textContent = message;
        sectionErrorList.replaceChildren(li);
        sectionErrorBanner.removeAttribute("hidden");
        focusSafely(sectionErrorBanner);
        sectionErrorBanner.scrollIntoView({ behavior: getScrollBehavior(), block: "nearest" });
    }

    function hideSectionValidationBanner() {
        if (!sectionErrorBanner) return;
        sectionErrorBanner.setAttribute("hidden", "");
        if (sectionErrorList) sectionErrorList.replaceChildren();
    }

    function validateSection(stepNumber) {
        var reqs = SECTION_REQUIREMENTS[stepNumber] || [];
        var missing = [];

        reqs.forEach(function (req) {
            clearRequirementError(req);

            if (req.type === "select") {
                var selectEl = document.getElementById(req.id);
                if (!selectEl || !selectEl.value || selectEl.value.trim() === "") {
                    missing.push(req);
                    showRequirementError(req, "Please choose an option to continue.");
                }
            } else if (req.type === "radio") {
                if (!document.querySelector('input[name="' + req.name + '"]:checked')) {
                    missing.push(req);
                    showRequirementError(req, "Please select one rating on the scale.");
                }
            } else if (req.type === "checkbox") {
                if (document.querySelectorAll('input[name="' + req.name + '"]:checked').length === 0) {
                    missing.push(req);
                    showRequirementError(req, "Please select at least one option.");
                }
            }
        });

        if (missing.length > 0) {
            showSectionValidationBanner(missing);
            return false;
        }

        hideSectionValidationBanner();
        return true;
    }

    function validateAllSections() {
        for (var s = 1; s <= 4; s++) {
            if (!validateSection(s)) {
                showStep(s, false);
                validateSection(s);
                return false;
            }
        }
        return true;
    }

    function findRequirementByTarget(target) {
        if (!target) return null;
        for (var s = 1; s <= 4; s++) {
            var reqs = SECTION_REQUIREMENTS[s];
            for (var i = 0; i < reqs.length; i++) {
                var r = reqs[i];
                if (r.id && target.id === r.id) return r;
                if (r.name && target.name === r.name) return r;
            }
        }
        return null;
    }

    /* ==================================================================
       6. Payload Construction (Preserves Exact 20-Item Contract)
    ================================================================== */
    function getSelectedRadioValue(name) {
        var el = document.querySelector('input[name="' + name + '"]:checked');
        return el ? parseFloat(el.value) : null;
    }

    function getSelectedCheckboxes(name) {
        var checked = document.querySelectorAll('input[name="' + name + '"]:checked');
        var values = [];
        checked.forEach(function (cb) {
            values.push(cb.value);
        });
        return values;
    }

    function buildAssessmentPayload() {
        var payload = {};

        var degEl = document.getElementById("pred_degree_field");
        if (degEl && degEl.value) payload.degree_field = degEl.value;

        var yrEl = document.getElementById("pred_academic_year");
        if (yrEl && yrEl.value) payload.academic_year = parseFloat(yrEl.value);

        var ageEl = document.getElementById("pred_age_group");
        if (ageEl && ageEl.value) payload.age_group = parseFloat(ageEl.value);

        var freq = getSelectedRadioValue("ai_usage_freq");
        if (freq !== null) payload.ai_usage_freq = freq;

        var timeEl = document.getElementById("pred_ai_time_per_week");
        if (timeEl && timeEl.value) payload.ai_time_per_week = parseFloat(timeEl.value);

        payload.tools_used = getSelectedCheckboxes("tools_used");

        var q20 = getSelectedRadioValue("Q20_task_delegation_freq");
        if (q20 !== null) payload.Q20_task_delegation_freq = q20;

        payload.tasks_delegated = getSelectedCheckboxes("tasks_delegated");

        var q1 = getSelectedRadioValue("Q1_direct_use_freq");
        if (q1 !== null) payload.Q1_direct_use_freq = q1;

        var q22 = getSelectedRadioValue("Q22_effort_on_ai_answers");
        if (q22 !== null) payload.Q22_effort_on_ai_answers = q22;

        var q2 = getSelectedRadioValue("Q2_verify_info");
        if (q2 !== null) payload.Q2_verify_info = q2;

        var q3 = getSelectedRadioValue("Q3_compare_sources");
        if (q3 !== null) payload.Q3_compare_sources = q3;

        var q4 = getSelectedRadioValue("Q4_check_accuracy");
        if (q4 !== null) payload.Q4_check_accuracy = q4;

        var q5 = getSelectedRadioValue("Q5_understand_reasoning");
        if (q5 !== null) payload.Q5_understand_reasoning = q5;

        var q6 = getSelectedRadioValue("Q6_modify_content");
        if (q6 !== null) payload.Q6_modify_content = q6;

        var q7 = getSelectedRadioValue("Q7_attempt_independently");
        if (q7 !== null) payload.Q7_attempt_independently = q7;

        var q8 = getSelectedRadioValue("Q8_complete_without_ai");
        if (q8 !== null) payload.Q8_complete_without_ai = q8;

        var q9 = getSelectedRadioValue("Q9_learning_assistant");
        if (q9 !== null) payload.Q9_learning_assistant = q9;

        var q30 = getSelectedRadioValue("Q30_trust_accuracy");
        if (q30 !== null) payload.Q30_trust_accuracy = q30;

        var q33 = getSelectedRadioValue("Q33_trust_appropriate_support");
        if (q33 !== null) payload.Q33_trust_appropriate_support = q33;

        return {
            user_inputs: payload,
            top_factors_count: 5
        };
    }

    /* ==================================================================
       7. Form State & Sample Presets
    ================================================================== */
    function syncTargetSelection(target) {
        if (!target) {
            syncSelectionClasses();
            return;
        }
        var card = target.closest ? target.closest(".c1-q-card") : null;
        if (card) {
            card.querySelectorAll(".c1-likert-option, .c1-choice-tile, .c1-check-tile").forEach(function (el) {
                var inp = el.querySelector("input");
                el.classList.toggle("is-selected", !!(inp && inp.checked));
            });
        }
        updateAnsweredCounter();
    }

    function syncSelectionClasses() {
        if (!assessmentForm) return;

        var groups = [
            { itemSel: ".c1-likert-option", inputSel: 'input[type="radio"]' },
            { itemSel: ".c1-choice-tile", inputSel: 'input[type="radio"]' },
            { itemSel: ".c1-check-tile", inputSel: 'input[type="checkbox"]' }
        ];

        groups.forEach(function (g) {
            assessmentForm.querySelectorAll(g.itemSel).forEach(function (el) {
                var inp = el.querySelector(g.inputSel);
                el.classList.toggle("is-selected", !!(inp && inp.checked));
            });
        });

        updateAnsweredCounter();
    }

    function clearAssessmentForm() {
        if (!assessmentForm) return;

        try {
            assessmentForm.reset();
        } catch (e) {
            // Safe fallback below
        }

        assessmentForm.querySelectorAll("select").forEach(function (s) {
            s.selectedIndex = 0;
            s.value = "";
        });

        assessmentForm.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(function (inp) {
            inp.checked = false;
        });

        for (var s = 1; s <= 4; s++) {
            (SECTION_REQUIREMENTS[s] || []).forEach(clearRequirementError);
        }

        hideSectionValidationBanner();

        if (demoNotice) demoNotice.setAttribute("hidden", "");
        if (resultsTechnicalDetails) resultsTechnicalDetails.open = false;

        syncSelectionClasses();
        showStep(1, false);
    }

    function applyPresetProfile(presetObj) {
        clearAssessmentForm();
        var profileData = presetObj.data;

        if (profileData.degree_field) {
            var degEl = document.getElementById("pred_degree_field");
            if (degEl) degEl.value = profileData.degree_field;
        }
        if (profileData.academic_year) {
            var yrEl = document.getElementById("pred_academic_year");
            if (yrEl) yrEl.value = String(profileData.academic_year);
        }
        if (profileData.age_group) {
            var ageEl = document.getElementById("pred_age_group");
            if (ageEl) ageEl.value = String(profileData.age_group);
        }
        if (profileData.ai_time_per_week) {
            var timeEl = document.getElementById("pred_ai_time_per_week");
            if (timeEl) timeEl.value = String(profileData.ai_time_per_week);
        }

        var radioKeys = [
            "ai_usage_freq",
            "Q20_task_delegation_freq",
            "Q1_direct_use_freq",
            "Q22_effort_on_ai_answers",
            "Q2_verify_info",
            "Q3_compare_sources",
            "Q4_check_accuracy",
            "Q5_understand_reasoning",
            "Q6_modify_content",
            "Q7_attempt_independently",
            "Q8_complete_without_ai",
            "Q9_learning_assistant",
            "Q30_trust_accuracy",
            "Q33_trust_appropriate_support"
        ];

        radioKeys.forEach(function (name) {
            if (profileData[name] !== undefined) {
                var radio = document.querySelector('input[name="' + name + '"][value="' + profileData[name] + '"]');
                if (radio) radio.checked = true;
            }
        });

        if (Array.isArray(profileData.tools_used)) {
            profileData.tools_used.forEach(function (toolVal) {
                var cb = document.querySelector('input[name="tools_used"][value="' + toolVal + '"]');
                if (cb) cb.checked = true;
            });
        }

        if (Array.isArray(profileData.tasks_delegated)) {
            var allTaskBoxes = document.querySelectorAll('input[name="tasks_delegated"]');
            profileData.tasks_delegated.forEach(function (taskVal) {
                var targetLower = String(taskVal).toLowerCase();
                allTaskBoxes.forEach(function (cb) {
                    var cbLower = cb.value.toLowerCase();
                    if (cbLower === targetLower || cbLower.indexOf(targetLower) !== -1 || targetLower.indexOf(cbLower) !== -1) {
                        cb.checked = true;
                    }
                });
            });
        }

        syncSelectionClasses();
        if (demoNotice && demoNoticeText) {
            demoNoticeText.textContent = "Loaded " + presetObj.label + " (20/20 responses pre-filled).";
            demoNotice.removeAttribute("hidden");
        }
        showView("wizard", null);
        showStep(1, true);
        announce("Loaded " + presetObj.label + ". All 20 items are pre-filled.");
    }

    /* ==================================================================
       8. Results & LinearSHAP Rendering
    ================================================================== */
    function renderActionableIdeas(catKey) {
        if (!actionableIdeasGrid) return;
        var frag = document.createDocumentFragment();

        var ideas = ACTIONABLE_IDEAS[catKey] || ACTIONABLE_IDEAS.medium;
        ideas.forEach(function (idea, idx) {
            var card = document.createElement("article");
            card.className = "c1-rec-card";

            var stepEl = document.createElement("span");
            stepEl.className = "c1-rec-card__step";
            stepEl.textContent = "Suggestion " + (idx + 1);

            var titleEl = document.createElement("h3");
            titleEl.className = "c1-rec-card__title";
            titleEl.textContent = idea.title;

            var textEl = document.createElement("p");
            textEl.className = "c1-rec-card__text";
            textEl.textContent = idea.text;

            card.appendChild(stepEl);
            card.appendChild(titleEl);
            card.appendChild(textEl);
            frag.appendChild(card);
        });

        actionableIdeasGrid.replaceChildren(frag);
    }

    function createFactorCard(factor, isMitigating, maxAbs) {
        var card = document.createElement("div");
        card.className = "c1-factor-card";

        var topRow = document.createElement("div");
        topRow.className = "c1-factor-card__top";

        var nameEl = document.createElement("span");
        nameEl.className = "c1-factor-card__name";
        nameEl.textContent = factor.human_label || factor.feature_name;

        var tagEl = document.createElement("span");
        tagEl.className = "c1-factor-card__tag " + (isMitigating ? "c1-factor-card__tag--protect" : "c1-factor-card__tag--risk");
        tagEl.textContent = isMitigating ? "Lowers risk" : "Raises risk";

        topRow.appendChild(nameEl);
        topRow.appendChild(tagEl);

        var contrib = Math.abs(parseFloat(factor.linear_shap_contribution) || 0);
        var pct = maxAbs > 0 ? Math.max(12, Math.round((contrib / maxAbs) * 100)) : 35;

        var meter = document.createElement("div");
        meter.className = "c1-factor-meter";
        meter.setAttribute("aria-hidden", "true");

        var meterFill = document.createElement("div");
        meterFill.className = "c1-factor-meter__fill " + (isMitigating ? "c1-factor-meter__fill--protect" : "c1-factor-meter__fill--risk");
        meterFill.style.width = pct + "%";
        meter.appendChild(meterFill);

        var descEl = document.createElement("p");
        descEl.className = "c1-factor-card__desc";
        descEl.textContent = factor.plain_explanation || (
            isMitigating ? "This habit helps keep learning independent." : "This habit contributes to higher AI reliance."
        );

        card.appendChild(topRow);
        card.appendChild(meter);
        card.appendChild(descEl);
        return card;
    }

    function renderShapFactors(factors) {
        if (!mitigatingContainer || !elevatingContainer) return;

        var mitigating = [];
        var elevating = [];
        var maxAbs = 0;

        factors.forEach(function (f) {
            var val = parseFloat(f.linear_shap_contribution) || 0;
            if (Math.abs(val) > maxAbs) maxAbs = Math.abs(val);
            var isMitigating = val <= 0 || (f.effect && f.effect.indexOf("mitigates") !== -1);
            if (isMitigating) mitigating.push(f);
            else elevating.push(f);
        });

        var elevFrag = document.createDocumentFragment();
        if (elevating.length === 0) {
            var emptyRisk = document.createElement("p");
            emptyRisk.className = "c1-factor-empty";
            emptyRisk.textContent = "None of your top behaviors substantially increased offloading risk.";
            elevFrag.appendChild(emptyRisk);
        } else {
            elevating.forEach(function (f) {
                elevFrag.appendChild(createFactorCard(f, false, maxAbs));
            });
        }
        elevatingContainer.replaceChildren(elevFrag);

        var mitFrag = document.createDocumentFragment();
        if (mitigating.length === 0) {
            var emptyProtect = document.createElement("p");
            emptyProtect.className = "c1-factor-empty";
            emptyProtect.textContent = "No strong protective habits stood out in your top contributing indicators.";
            mitFrag.appendChild(emptyProtect);
        } else {
            mitigating.forEach(function (f) {
                mitFrag.appendChild(createFactorCard(f, true, maxAbs));
            });
        }
        mitigatingContainer.replaceChildren(mitFrag);

        // Render full technical SHAP table inside expandable disclosure
        if (shapTableBody) {
            var tableFrag = document.createDocumentFragment();
            factors.forEach(function (f) {
                var contrib = parseFloat(f.linear_shap_contribution) || 0;
                var isRisk = contrib > 0 && !(f.effect && f.effect.indexOf("mitigates") !== -1);

                var tr = document.createElement("tr");

                var tdLabel = document.createElement("td");
                tdLabel.textContent = f.human_label || f.feature_name;

                var tdKey = document.createElement("td");
                var codeEl = document.createElement("code");
                codeEl.textContent = f.feature_name;
                tdKey.appendChild(codeEl);

                var tdVal = document.createElement("td");
                tdVal.textContent = f.student_value !== undefined ? String(f.student_value) : "—";

                var tdDir = document.createElement("td");
                tdDir.textContent = isRisk ? "Increases Risk" : "Reduces Risk";

                var tdShap = document.createElement("td");
                tdShap.textContent = (contrib > 0 ? "+" : "") + contrib.toFixed(4);

                tr.appendChild(tdLabel);
                tr.appendChild(tdKey);
                tr.appendChild(tdVal);
                tr.appendChild(tdDir);
                tr.appendChild(tdShap);
                tableFrag.appendChild(tr);
            });
            shapTableBody.replaceChildren(tableFrag);
        }
    }

    function syncDetailsButton() {
        if (!btnToggleDetails || !resultsTechnicalDetails) return;
        var isOpen = !!resultsTechnicalDetails.open;
        btnToggleDetails.setAttribute("aria-expanded", String(isOpen));
        btnToggleDetails.textContent = isOpen ? "Hide Detailed Explanation" : "View Detailed Explanation";
    }

    function renderPredictionResult(data) {
        if (!viewResults || !predictionResultCard) return;

        var rawCategory = (data.predicted_category || "Medium").toLowerCase();
        var catKey = rawCategory === "low" ? "low" : (rawCategory === "high" ? "high" : "medium");

        predictionResultCard.classList.remove("c1-tier--low", "c1-tier--medium", "c1-tier--high");
        predictionResultCard.classList.add("c1-tier--" + catKey);

        var titleText = catKey === "low" ? "Low Risk" : (catKey === "high" ? "High Risk" : "Medium Risk");
        var badgeText = catKey === "low" ? "High Study Autonomy" : (catKey === "high" ? "Elevated AI Reliance" : "Balanced / Mixed Reliance");

        if (resultsHeading) resultsHeading.textContent = titleText;
        if (riskCategoryBadge) {
            riskCategoryBadge.classList.remove("c1-tier-pill--low", "c1-tier-pill--medium", "c1-tier-pill--high");
            riskCategoryBadge.classList.add("c1-tier-pill--" + catKey);
            riskCategoryBadge.textContent = badgeText;
        }

        if (riskInterpretationSummary) {
            riskInterpretationSummary.textContent = RISK_INTERPRETATION[catKey];
        }

        if (data.continuous_risk_score !== null && data.continuous_risk_score !== undefined) {
            var sc = parseFloat(data.continuous_risk_score);
            if (continuousScoreVal) continuousScoreVal.textContent = sc.toFixed(3);
            if (scoreMarkerLabel) scoreMarkerLabel.textContent = sc.toFixed(2);

            if (scoreSpectrumMarker) {
                var spectrumPct = Math.max(2, Math.min(98, ((sc - 1.0) / 4.0) * 100));
                scoreSpectrumMarker.style.left = spectrumPct.toFixed(1) + "%";
            }

            if (scaleAriaSummary) {
                scaleAriaSummary.textContent =
                    "Your predicted score of " + sc.toFixed(3) + " places your habits in the " + titleText + " zone.";
            }

            if (rawScoreVal) {
                var rawSc = data.raw_regression_score !== undefined ? parseFloat(data.raw_regression_score).toFixed(3) : sc.toFixed(3);
                rawScoreVal.textContent = rawSc + " raw / " + sc.toFixed(3) + " bounded [1.000–5.000]";
            }
        }

        if (modelArchVal && data.model_architecture) {
            modelArchVal.textContent = data.model_architecture;
        }

        if (data.probabilities) {
            var pLow  = Math.max(0, Math.min(100, (data.probabilities.low * 100) || 0));
            var pMed  = Math.max(0, Math.min(100, (data.probabilities.medium * 100) || 0));
            var pHigh = Math.max(0, Math.min(100, (data.probabilities.high * 100) || 0));

            if (probBarLow)  probBarLow.style.width  = pLow.toFixed(1) + "%";
            if (probValLow)  probValLow.textContent  = pLow.toFixed(1) + "%";

            if (probBarMed)  probBarMed.style.width  = pMed.toFixed(1) + "%";
            if (probValMed)  probValMed.textContent  = pMed.toFixed(1) + "%";

            if (probBarHigh) probBarHigh.style.width = pHigh.toFixed(1) + "%";
            if (probValHigh) probValHigh.textContent = pHigh.toFixed(1) + "%";
        }

        if (backendDisclaimerEl && data.disclaimer) {
            backendDisclaimerEl.textContent = data.disclaimer;
        }

        renderShapFactors(data.top_contributing_factors || []);
        renderActionableIdeas(catKey);

        if (resultsTechnicalDetails) {
            resultsTechnicalDetails.open = false;
            syncDetailsButton();
        }

        showView("results", resultsHeading);
        announce("Assessment complete. Your Cognitive Offloading Risk is " + titleText + ".");
    }

    /* ==================================================================
       9. Event Listeners
    ================================================================== */
    if (btnStartAssessment) {
        btnStartAssessment.addEventListener("click", function () {
            showView("wizard", null);
            showStep(currentStep || 1, true);
        });
    }

    if (btnBackToIntro) {
        btnBackToIntro.addEventListener("click", function () {
            showView("intro", introTitle);
        });
    }

    if (btnJumpToReview) {
        btnJumpToReview.addEventListener("click", function () {
            showStep(4, true);
        });
    }

    if (btnNextStep1) {
        btnNextStep1.addEventListener("click", function () {
            if (validateSection(1)) showStep(2, true);
        });
    }
    if (btnPrevStep2) {
        btnPrevStep2.addEventListener("click", function () {
            showStep(1, true);
        });
    }
    if (btnNextStep2) {
        btnNextStep2.addEventListener("click", function () {
            if (validateSection(2)) showStep(3, true);
        });
    }
    if (btnPrevStep3) {
        btnPrevStep3.addEventListener("click", function () {
            showStep(2, true);
        });
    }
    if (btnNextStep3) {
        btnNextStep3.addEventListener("click", function () {
            if (validateSection(3)) showStep(4, true);
        });
    }
    if (btnPrevStep4) {
        btnPrevStep4.addEventListener("click", function () {
            showStep(3, true);
        });
    }

    stepPills.forEach(function (pill, idx) {
        var targetStep = idx + 1;
        if (!pill) return;
        pill.addEventListener("click", function () {
            if (targetStep > currentStep) {
                for (var s = currentStep; s < targetStep; s++) {
                    if (!validateSection(s)) {
                        showStep(s, false);
                        validateSection(s);
                        return;
                    }
                }
            }
            showStep(targetStep, true);
        });
    });

    var isSubmitting = false;

    function submitAssessment() {
        if (isSubmitting) return;
        if (!validateAllSections()) return;

        var payload = buildAssessmentPayload();
        isSubmitting = true;

        var controller = typeof AbortController === "function" ? new AbortController() : null;
        var timeoutId = controller
            ? setTimeout(function () {
                controller.abort();
            }, 15000)
            : null;

        if (btnCalculatePrediction) {
            btnCalculatePrediction.disabled = true;
            btnCalculatePrediction.setAttribute("aria-busy", "true");
            var lblLoading = btnCalculatePrediction.querySelector(".c1-btn-label");
            if (lblLoading) lblLoading.textContent = "Analyzing Responses…";
        }

        var fetchOpts = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        };
        if (controller) {
            fetchOpts.signal = controller.signal;
        }

        fetch(PREDICT_URL, fetchOpts)
        .then(function (res) {
            return res.text().then(function (rawText) {
                var parsed = null;
                try {
                    parsed = rawText ? JSON.parse(rawText) : null;
                } catch (e) {
                    parsed = null;
                }
                return { ok: res.ok, status: res.status, data: parsed };
            });
        })
        .then(function (result) {
            var data = result.data;
            var catLower = data && data.predicted_category
                ? String(data.predicted_category).toLowerCase()
                : "";
            var validCategory = catLower === "low" || catLower === "medium" || catLower === "high";
            var validScore = data && typeof data.continuous_risk_score === "number" && isFinite(data.continuous_risk_score);

            if (result.ok && data && data.status === "success" && validCategory && validScore) {
                hideSectionValidationBanner();
                renderPredictionResult(data);
            } else if (!result.ok && result.status === 503) {
                showRequestErrorBanner(
                    (data && data.message)
                        ? data.message
                        : "The prediction model is temporarily unavailable. Please verify model artifacts on the server."
                );
            } else {
                var errorMsg = (data && data.message)
                    ? data.message
                    : ("Unexpected assessment response (HTTP " + result.status + "). Please try again.");
                showRequestErrorBanner(errorMsg);
            }
        })
        .catch(function (err) {
            if (err && err.name === "AbortError") {
                showRequestErrorBanner("The assessment request timed out. Please try submitting again.");
            } else {
                showRequestErrorBanner("Unable to reach the assessment service. Please confirm the local server is running and try again.");
            }
        })
        .finally(function () {
            if (timeoutId) clearTimeout(timeoutId);
            isSubmitting = false;
            if (btnCalculatePrediction) {
                btnCalculatePrediction.disabled = false;
                btnCalculatePrediction.setAttribute("aria-busy", "false");
                var lblDone = btnCalculatePrediction.querySelector(".c1-btn-label");
                if (lblDone) lblDone.textContent = "View Results";
            }
        });
    }

    if (assessmentForm) {
        assessmentForm.addEventListener("submit", function (e) {
            e.preventDefault();
            if (currentStep < 4) {
                if (validateSection(currentStep)) {
                    showStep(currentStep + 1, true);
                }
            } else {
                submitAssessment();
            }
        });

        assessmentForm.addEventListener("change", function (e) {
            syncTargetSelection(e.target);
            var req = findRequirementByTarget(e.target);
            if (req) {
                var isNowValid = true;
                if (req.type === "checkbox") {
                    isNowValid = document.querySelectorAll('input[name="' + req.name + '"]:checked').length > 0;
                }
                if (isNowValid) {
                    clearRequirementError(req);
                    if (sectionErrorList) {
                        var item = sectionErrorList.querySelector('li[data-card-id="' + req.cardId + '"]');
                        if (item) item.remove();
                        if (sectionErrorList.children.length === 0) {
                            hideSectionValidationBanner();
                        }
                    }
                }
            }
        });
    }

    if (btnResetAssessment) {
        btnResetAssessment.addEventListener("click", function () {
            clearAssessmentForm();
            showStep(1, true);
            announce("Form reset. All selections cleared.");
        });
    }

    if (btnClearProfile) {
        btnClearProfile.addEventListener("click", function () {
            clearAssessmentForm();
            announce("All sample selections cleared.");
        });
    }

    if (btnPresetLow) {
        btnPresetLow.addEventListener("click", function () {
            applyPresetProfile(PRESETS.low);
        });
    }
    if (btnPresetMed) {
        btnPresetMed.addEventListener("click", function () {
            applyPresetProfile(PRESETS.med);
        });
    }
    if (btnPresetHigh) {
        btnPresetHigh.addEventListener("click", function () {
            applyPresetProfile(PRESETS.high);
        });
    }

    if (btnStartNewAssessment) {
        btnStartNewAssessment.addEventListener("click", function () {
            clearAssessmentForm();
            showView("wizard", null);
            showStep(1, true);
        });
    }

    if (btnReviewAnswers) {
        btnReviewAnswers.addEventListener("click", function () {
            showView("wizard", null);
            showStep(currentStep || 1, true);
        });
    }

    if (btnToggleDetails && resultsTechnicalDetails) {
        btnToggleDetails.addEventListener("click", function () {
            resultsTechnicalDetails.open = !resultsTechnicalDetails.open;
            syncDetailsButton();
            if (resultsTechnicalDetails.open) {
                resultsTechnicalDetails.scrollIntoView({ behavior: getScrollBehavior(), block: "nearest" });
            }
        });

        resultsTechnicalDetails.addEventListener("toggle", syncDetailsButton);
    }

    // Initialize clean zero-default state on load
    clearAssessmentForm();
    showView("intro", null);

}());
