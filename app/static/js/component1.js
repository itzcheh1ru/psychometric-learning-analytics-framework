/**
 * component1.js – Client-side logic for Component 1:
 * Explainable Cognitive Offloading Risk Model (Version 4).
 * Psychometric Learning Analytics Framework – J26-DS-310
 *
 * Responsibilities:
 *   - Multi-step questionnaire wizard navigation (Steps 1–4)
 *   - Step progress tracker and visual progress bar
 *   - Rigorous client-side section validation with clear warning banners
 *   - Guaranteed unselected initial state (no default preselection)
 *   - Demonstration presets (Low, Medium, High risk) as explicit optional tools
 *   - Interactive prediction & exact LinearSHAP attribution via POST /api/component1/predict
 *   - Latent score spectrum visualizer & category likelihood meters
 *   - Two-column LinearSHAP factor rendering (Mitigating vs Elevating)
 *   - Actionable study recommendations based on predicted risk tier
 */

"use strict";

(function () {

    /* ==================================================================
       1. Endpoints & Constants
    ================================================================== */
    var PREDICT_URL = "/api/component1/predict";

    // Required questions per wizard section
    var SECTION_REQUIREMENTS = {
        1: [
            { id: "pred_degree_field", type: "select", cardId: "card_degree_field", errId: "err_degree_field", label: "Academic Field / Discipline" },
            { id: "pred_academic_year", type: "select", cardId: "card_academic_year", errId: "err_academic_year", label: "Current Academic Year" },
            { id: "pred_age_group", type: "select", cardId: "card_age_group", errId: "err_age_group", label: "Age Bracket" },
            { name: "ai_usage_freq", type: "radio", cardId: "card_ai_usage_freq", errId: "err_ai_usage_freq", label: "AI Usage Frequency" },
            { id: "pred_ai_time_per_week", type: "select", cardId: "card_ai_time_per_week", errId: "err_ai_time_per_week", label: "Weekly AI Study Time" },
            { name: "tools_used", type: "checkbox", cardId: "card_tools_used", errId: "err_tools_used", label: "Generative AI Tools Used (select at least one)" }
        ],
        2: [
            { name: "Q20_task_delegation_freq", type: "radio", cardId: "card_Q20", errId: "err_Q20", label: "Task Delegation Frequency (Q20)" },
            { name: "Q1_direct_use_freq", type: "radio", cardId: "card_Q1", errId: "err_Q1", label: "Direct Use / Copying Frequency (Q1)" },
            { name: "Q22_effort_on_ai_answers", type: "radio", cardId: "card_Q22", errId: "err_Q22", label: "Cognitive Effort on AI Answers (Q22)" }
        ],
        3: [
            { name: "Q2_verify_info", type: "radio", cardId: "card_Q2", errId: "err_Q2", label: "External Source Verification (Q2)" },
            { name: "Q3_compare_sources", type: "radio", cardId: "card_Q3", errId: "err_Q3", label: "Coursework Comparison (Q3)" },
            { name: "Q4_check_accuracy", type: "radio", cardId: "card_Q4", errId: "err_Q4", label: "Accuracy Checking (Q4)" },
            { name: "Q5_understand_reasoning", type: "radio", cardId: "card_Q5", errId: "err_Q5", label: "Understanding Reasoning (Q5)" },
            { name: "Q6_modify_content", type: "radio", cardId: "card_Q6", errId: "err_Q6", label: "Content Personalization (Q6)" }
        ],
        4: [
            { name: "Q7_attempt_independently", type: "radio", cardId: "card_Q7", errId: "err_Q7", label: "Independent Problem-Solving First (Q7)" },
            { name: "Q8_complete_without_ai", type: "radio", cardId: "card_Q8", errId: "err_Q8", label: "Confidence Without AI (Q8)" },
            { name: "Q9_learning_assistant", type: "radio", cardId: "card_Q9", errId: "err_Q9", label: "Assistant vs Replacement Mindset (Q9)" },
            { name: "Q30_trust_accuracy", type: "radio", cardId: "card_Q30", errId: "err_Q30", label: "Belief in AI Accuracy (Q30)" },
            { name: "Q33_trust_appropriate_support", type: "radio", cardId: "card_Q33", errId: "err_Q33", label: "Trust in AI Guidance (Q33)" }
        ]
    };

    // Synthetic Demonstration Profiles
    var PRESETS = {
        low: {
            degree_field: "Natural_Applied_Sciences",
            academic_year: "3",
            age_group: "2",
            ai_usage_freq: "1",
            ai_time_per_week: "1",
            tools_used: ["ChatGPT"],
            Q20_task_delegation_freq: "1",
            tasks_delegated: ["Explaining difficult concepts"],
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
        },
        med: {
            degree_field: "Computing_IT",
            academic_year: "2",
            age_group: "2",
            ai_usage_freq: "2",
            ai_time_per_week: "3",
            tools_used: ["ChatGPT", "Google Gemini"],
            Q20_task_delegation_freq: "3",
            tasks_delegated: ["Explaining difficult concepts", "Summarising reading materials"],
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
        },
        high: {
            degree_field: "Business_Economics",
            academic_year: "1",
            age_group: "1",
            ai_usage_freq: "4",
            ai_time_per_week: "5",
            tools_used: ["ChatGPT", "Claude", "Perplexity AI"],
            Q20_task_delegation_freq: "5",
            tasks_delegated: [
                "Writing assignments or essays",
                "Summarising reading materials",
                "Programming and coding solutions",
                "Mathematical and calculation problems"
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
    };

    // Actionable Study Recommendations per Predicted Risk Tier
    var ACTIONABLE_IDEAS = {
        low: [
            {
                title: "Maintain First-Principles Problem Solving",
                text: "Continue attempting coursework challenges independently before consulting AI. This productive struggle builds durable synaptic connections and exam readiness."
            },
            {
                title: "Use AI as a Socratic Dialogue Partner",
                text: "Prompt the AI to critique your own written logic or challenge your assumptions rather than asking it to generate answers directly."
            },
            {
                title: "Audit Algorithmic Claims",
                text: "Keep verifying citations and numerical proofs against peer-reviewed literature and course texts to prevent hallucination acceptance."
            }
        ],
        medium: [
            {
                title: "Establish a 15-Minute Independence Window",
                text: "Spend at least 15 minutes drafting your outline, code architecture, or conceptual proof on paper before opening ChatGPT or Copilot."
            },
            {
                title: "Transform Every AI Output in Your Own Words",
                text: "Never copy and paste generated text directly. Read, close the window, and re-synthesize the explanation in your personal academic voice."
            },
            {
                title: "Cross-Reference With Course Slides",
                text: "Ensure the concepts and notation suggested by AI align strictly with the methodology taught by your lecturer."
            }
        ],
        high: [
            {
                title: "Reclaim Cognitive Agency on Core Tasks",
                text: "Identify assignments where AI was delegated the entire task (e.g. coding or essay drafting) and commit to solving the core reasoning steps yourself."
            },
            {
                title: "Implement Systematic Fact-Checking",
                text: "Assume every AI fact or equation is unverified until corroborated by an authoritative textbook, syllabus document, or academic paper."
            },
            {
                title: "Conduct Weekly 'Offline' Practice Tests",
                text: "Test your ability to solve typical exam problems under timed conditions without access to any generative AI assistant."
            }
        ]
    };

    // Risk Category Interpretation Summaries
    var RISK_INTERPRETATION = {
        low: "Your self-reflection reflects strong cognitive autonomy. You actively verify facts, attempt problem-solving on your own before turning to AI, and utilize Generative AI strictly as an auxiliary sounding board. This approach maximizes both your efficiency and deep conceptual learning.",
        medium: "You use Generative AI productively in many areas, but there are signs that certain tasks (such as writing, coding, or problem-solving) are occasionally delegated without full independent struggle or rigorous source checking. Small adjustments can significantly reinforce your long-term learning.",
        high: "Your responses suggest a strong pattern of delegating core academic reasoning directly to AI tools. While AI provides rapid solutions, bypassing early problem-solving struggle and fact-checking can weaken your independent analytical mastery and exam readiness over time."
    };

    /* ==================================================================
       2. DOM Element References
    ================================================================== */
    var assessmentForm          = document.getElementById("reflectionAssessmentForm");
    var sectionErrorBanner      = document.getElementById("sectionValidationError");
    var sectionErrorList        = document.getElementById("sectionValidationErrorList");

    var c1ProgressBarFill       = document.getElementById("c1ProgressBarFill");
    var stepPill1               = document.getElementById("stepPill1");
    var stepPill2               = document.getElementById("stepPill2");
    var stepPill3               = document.getElementById("stepPill3");
    var stepPill4               = document.getElementById("stepPill4");

    var formStep1               = document.getElementById("formStep1");
    var formStep2               = document.getElementById("formStep2");
    var formStep3               = document.getElementById("formStep3");
    var formStep4               = document.getElementById("formStep4");

    var btnNextStep1            = document.getElementById("btnNextStep1");
    var btnPrevStep2            = document.getElementById("btnPrevStep2");
    var btnNextStep2            = document.getElementById("btnNextStep2");
    var btnPrevStep3            = document.getElementById("btnPrevStep3");
    var btnNextStep3            = document.getElementById("btnNextStep3");
    var btnPrevStep4            = document.getElementById("btnPrevStep4");

    var btnCalculatePrediction  = document.getElementById("btnCalculatePrediction");
    var btnResetAssessment      = document.getElementById("btnResetAssessment");

    var btnPresetLow            = document.getElementById("btnPresetLow");
    var btnPresetMed            = document.getElementById("btnPresetMed");
    var btnPresetHigh           = document.getElementById("btnPresetHigh");
    var btnClearProfile         = document.getElementById("btnClearProfile");

    // Results Panel Elements
    var reflectionResultSec     = document.getElementById("reflectionResultSection");
    var predictionResultCard    = document.getElementById("predictionResultCard");
    var riskCategoryBadge       = document.getElementById("riskCategoryBadge");
    var continuousScoreVal      = document.getElementById("continuousScoreVal");
    var scoreSpectrumMarker     = document.getElementById("scoreSpectrumMarker");
    var riskInterpretationSummary = document.getElementById("riskInterpretationSummary");

    var probBarLow              = document.getElementById("probBarLow");
    var probValLow              = document.getElementById("probValLow");
    var probBarMed              = document.getElementById("probBarMed");
    var probValMed              = document.getElementById("probValMed");
    var probBarHigh             = document.getElementById("probBarHigh");
    var probValHigh             = document.getElementById("probValHigh");

    var mitigatingContainer     = document.getElementById("mitigatingFactorsContainer");
    var elevatingContainer      = document.getElementById("elevatingFactorsContainer");
    var actionableIdeasGrid     = document.getElementById("actionableIdeasGrid");

    var currentStep = 1;

    /* ==================================================================
       3. Wizard Navigation & Step Display
    ================================================================== */
    function showStep(stepNumber) {
        currentStep = stepNumber;

        // Toggle step containers
        var steps = [formStep1, formStep2, formStep3, formStep4];
        var pills = [stepPill1, stepPill2, stepPill3, stepPill4];

        steps.forEach(function (stepEl, idx) {
            if (!stepEl) return;
            var num = idx + 1;
            if (num === stepNumber) {
                stepEl.removeAttribute("hidden");
            } else {
                stepEl.setAttribute("hidden", "");
            }
        });

        // Update pills
        pills.forEach(function (pillEl, idx) {
            if (!pillEl) return;
            var num = idx + 1;
            pillEl.classList.remove("step-active", "step-completed", "step-pending");
            if (num === stepNumber) {
                pillEl.classList.add("step-active");
            } else if (num < stepNumber) {
                pillEl.classList.add("step-completed");
            } else {
                pillEl.classList.add("step-pending");
            }
        });

        // Update progress bar
        if (c1ProgressBarFill) {
            c1ProgressBarFill.style.width = (stepNumber * 25) + "%";
        }

        // Hide validation banner on step transition
        hideSectionValidationBanner();

        // Scroll step heading into view smoothly on manual user navigation
        var curStepEl = steps[stepNumber - 1];
        if (curStepEl && stepNumber > 1) {
            curStepEl.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    /* ==================================================================
       4. Section Validation Logic
    ================================================================== */
    function clearCardErrors(cardId, errId) {
        var card = document.getElementById(cardId);
        if (card) card.classList.remove("question-card--error");

        var errEl = document.getElementById(errId);
        if (errEl) {
            errEl.textContent = "";
            errEl.setAttribute("hidden", "");
        }
    }

    function showCardError(cardId, errId, message) {
        var card = document.getElementById(cardId);
        if (card) card.classList.add("question-card--error");

        var errEl = document.getElementById(errId);
        if (errEl) {
            errEl.textContent = message;
            errEl.removeAttribute("hidden");
        }
    }

    function showSectionValidationBanner(missingItems) {
        if (!sectionErrorBanner || !sectionErrorList) return;
        sectionErrorList.innerHTML = "";

        missingItems.forEach(function (item) {
            var li = document.createElement("li");
            li.textContent = item.label;
            sectionErrorList.appendChild(li);
        });

        sectionErrorBanner.removeAttribute("hidden");
        sectionErrorBanner.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function hideSectionValidationBanner() {
        if (!sectionErrorBanner) return;
        sectionErrorBanner.setAttribute("hidden", "");
        if (sectionErrorList) sectionErrorList.innerHTML = "";
    }

    function validateSection(stepNumber) {
        var reqs = SECTION_REQUIREMENTS[stepNumber] || [];
        var missing = [];

        reqs.forEach(function (req) {
            clearCardErrors(req.cardId, req.errId);

            if (req.type === "select") {
                var selectEl = document.getElementById(req.id);
                if (!selectEl || !selectEl.value || selectEl.value.trim() === "") {
                    missing.push(req);
                    showCardError(req.cardId, req.errId, "This question requires an explicit selection.");
                }
            } else if (req.type === "radio") {
                var checked = document.querySelector('input[name="' + req.name + '"]:checked');
                if (!checked) {
                    missing.push(req);
                    showCardError(req.cardId, req.errId, "Please select an answer on the provided scale.");
                }
            } else if (req.type === "checkbox") {
                var checkedBoxes = document.querySelectorAll('input[name="' + req.name + '"]:checked');
                if (!checkedBoxes || checkedBoxes.length === 0) {
                    missing.push(req);
                    showCardError(req.cardId, req.errId, "Select at least one tool that you use.");
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
                showStep(s);
                return false;
            }
        }
        return true;
    }

    /* ==================================================================
       5. Build Form Payload
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

        // Section 1
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

        // Section 2
        var q20 = getSelectedRadioValue("Q20_task_delegation_freq");
        if (q20 !== null) payload.Q20_task_delegation_freq = q20;

        payload.tasks_delegated = getSelectedCheckboxes("tasks_delegated");

        var q1 = getSelectedRadioValue("Q1_direct_use_freq");
        if (q1 !== null) payload.Q1_direct_use_freq = q1;

        var q22 = getSelectedRadioValue("Q22_effort_on_ai_answers");
        if (q22 !== null) payload.Q22_effort_on_ai_answers = q22;

        // Section 3
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

        // Section 4
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
       6. Form State & Profile Management
    ================================================================== */
    function syncSelectionClasses() {
        if (!assessmentForm) return;

        // Likert options
        var likertOptions = assessmentForm.querySelectorAll(".likert-option");
        likertOptions.forEach(function (opt) {
            var radio = opt.querySelector('input[type="radio"]');
            if (radio && radio.checked) {
                opt.classList.add("likert-option--selected");
            } else {
                opt.classList.remove("likert-option--selected");
            }
        });

        // Radio card labels
        var radioCards = assessmentForm.querySelectorAll(".radio-card-label");
        radioCards.forEach(function (card) {
            var radio = card.querySelector('input[type="radio"]');
            if (radio && radio.checked) {
                card.classList.add("radio-card-label--selected");
            } else {
                card.classList.remove("radio-card-label--selected");
            }
        });

        // Checkbox cards
        var checkboxCards = assessmentForm.querySelectorAll(".checkbox-card-label");
        checkboxCards.forEach(function (card) {
            var cb = card.querySelector('input[type="checkbox"]');
            if (cb && cb.checked) {
                card.classList.add("checkbox-card-label--selected");
            } else {
                card.classList.remove("checkbox-card-label--selected");
            }
        });
    }

    function clearAssessmentForm() {
        if (!assessmentForm) return;

        try {
            assessmentForm.reset();
        } catch (e) {
            // Ignore if reset fails
        }

        // Reset selects
        var selects = assessmentForm.querySelectorAll("select");
        selects.forEach(function (s) {
            s.selectedIndex = 0;
            s.value = "";
        });

        // Uncheck all radios & checkboxes
        var inputs = assessmentForm.querySelectorAll('input[type="radio"], input[type="checkbox"]');
        inputs.forEach(function (inp) {
            inp.checked = false;
        });

        // Clear all card error borders
        var errorCards = assessmentForm.querySelectorAll(".question-card--error");
        errorCards.forEach(function (c) {
            c.classList.remove("question-card--error");
        });

        // Hide all field error texts
        var errMsgs = assessmentForm.querySelectorAll(".field-error-msg");
        errMsgs.forEach(function (m) {
            m.textContent = "";
            m.setAttribute("hidden", "");
        });

        hideSectionValidationBanner();

        // Hide results panel
        if (reflectionResultSec) {
            reflectionResultSec.setAttribute("hidden", "");
        }

        syncSelectionClasses();
        showStep(1);
    }

    function applyPresetProfile(profileData) {
        clearAssessmentForm();

        // Populate selects
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

        // Populate radios
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

        // Populate checkboxes
        if (Array.isArray(profileData.tools_used)) {
            profileData.tools_used.forEach(function (toolVal) {
                var cb = document.querySelector('input[name="tools_used"][value="' + toolVal + '"]');
                if (cb) cb.checked = true;
            });
        }

        if (Array.isArray(profileData.tasks_delegated)) {
            profileData.tasks_delegated.forEach(function (taskVal) {
                var cb = document.querySelector('input[name="tasks_delegated"][value="' + taskVal + '"]');
                if (cb) cb.checked = true;
            });
        }

        syncSelectionClasses();
        showStep(1);
    }

    /* ==================================================================
       7. Prediction & LinearSHAP Rendering
    ================================================================== */
    function renderActionableIdeas(category) {
        if (!actionableIdeasGrid) return;
        actionableIdeasGrid.innerHTML = "";

        var ideas = ACTIONABLE_IDEAS[category] || ACTIONABLE_IDEAS.medium;
        ideas.forEach(function (idea) {
            var card = document.createElement("div");
            card.className = "recommendation-card";

            var titleEl = document.createElement("h5");
            titleEl.className = "recommendation-card__title";
            titleEl.textContent = "📌 " + idea.title;

            var textEl = document.createElement("p");
            textEl.className = "recommendation-card__text";
            textEl.textContent = idea.text;

            card.appendChild(titleEl);
            card.appendChild(textEl);
            actionableIdeasGrid.appendChild(card);
        });
    }

    function renderShapFactors(factors) {
        if (!mitigatingContainer || !elevatingContainer) return;
        mitigatingContainer.innerHTML = "";
        elevatingContainer.innerHTML = "";

        var mitigating = [];
        var elevating = [];

        factors.forEach(function (f) {
            var contrib = parseFloat(f.linear_shap_contribution);
            var isMitigating = contrib <= 0 || (f.effect && f.effect.indexOf("mitigates") !== -1);
            if (isMitigating) {
                mitigating.push(f);
            } else {
                elevating.push(f);
            }
        });

        // Render Mitigating
        if (mitigating.length === 0) {
            var emptyMit = document.createElement("div");
            emptyMit.className = "factor-card factor-card--empty";
            emptyMit.textContent = "No significant risk-mitigating habits detected in this profile.";
            mitigatingContainer.appendChild(emptyMit);
        } else {
            mitigating.forEach(function (f) {
                var card = document.createElement("div");
                card.className = "factor-card factor-card--mitigate";

                var nameEl = document.createElement("div");
                nameEl.className = "factor-card__name";
                nameEl.textContent = f.human_label || f.feature_name;

                var explEl = document.createElement("div");
                explEl.className = "factor-card__explanation";
                explEl.textContent = f.plain_explanation || "Protects independent learning.";

                var metaEl = document.createElement("div");
                metaEl.className = "factor-card__meta";
                var contribVal = parseFloat(f.linear_shap_contribution);
                metaEl.textContent = "Model impact: " + (contribVal > 0 ? "+" : "") + contribVal.toFixed(3) + " points";

                card.appendChild(nameEl);
                card.appendChild(explEl);
                card.appendChild(metaEl);
                mitigatingContainer.appendChild(card);
            });
        }

        // Render Elevating
        if (elevating.length === 0) {
            var emptyElev = document.createElement("div");
            emptyElev.className = "factor-card factor-card--empty";
            emptyElev.textContent = "No major risk-elevating habits detected in this profile!";
            elevatingContainer.appendChild(emptyElev);
        } else {
            elevating.forEach(function (f) {
                var card = document.createElement("div");
                card.className = "factor-card factor-card--elevate";

                var nameEl = document.createElement("div");
                nameEl.className = "factor-card__name";
                nameEl.textContent = f.human_label || f.feature_name;

                var explEl = document.createElement("div");
                explEl.className = "factor-card__explanation";
                explEl.textContent = f.plain_explanation || "Elevates reliance on automated outputs.";

                var metaEl = document.createElement("div");
                metaEl.className = "factor-card__meta";
                var contribVal = parseFloat(f.linear_shap_contribution);
                metaEl.textContent = "Model impact: " + (contribVal > 0 ? "+" : "") + contribVal.toFixed(3) + " points";

                card.appendChild(nameEl);
                card.appendChild(explEl);
                card.appendChild(metaEl);
                elevatingContainer.appendChild(card);
            });
        }
    }

    function renderPredictionResult(data) {
        if (!reflectionResultSec || !predictionResultCard) return;

        reflectionResultSec.removeAttribute("hidden");

        var rawCategory = (data.predicted_category || "Medium").toLowerCase();
        var catKey = rawCategory === "low" ? "low" : (rawCategory === "high" ? "high" : "medium");

        // Set card styling
        predictionResultCard.classList.remove("result-card-low", "result-card-med", "result-card-high");
        predictionResultCard.classList.add("result-card-" + (catKey === "medium" ? "med" : catKey));

        // Risk Category Badge
        if (riskCategoryBadge) {
            riskCategoryBadge.classList.remove("risk-badge--low", "risk-badge--med", "risk-badge--high");
            riskCategoryBadge.classList.add("risk-badge--" + (catKey === "medium" ? "med" : catKey));

            if (catKey === "low") {
                riskCategoryBadge.textContent = "🟢 Low Cognitive Offloading Tendency";
            } else if (catKey === "high") {
                riskCategoryBadge.textContent = "🔴 High Cognitive Offloading Tendency";
            } else {
                riskCategoryBadge.textContent = "🟡 Moderate Cognitive Offloading Tendency";
            }
        }

        // Continuous Latent Score
        if (continuousScoreVal && data.continuous_risk_score !== null && data.continuous_risk_score !== undefined) {
            var sc = parseFloat(data.continuous_risk_score);
            continuousScoreVal.textContent = sc.toFixed(3);

            // Update spectrum marker (Scale: 1.0 to 5.0)
            if (scoreSpectrumMarker) {
                var spectrumPct = Math.max(0, Math.min(100, ((sc - 1.0) / 4.0) * 100));
                scoreSpectrumMarker.style.left = spectrumPct.toFixed(1) + "%";
            }
        }

        // Interpretation Summary
        if (riskInterpretationSummary) {
            riskInterpretationSummary.textContent = RISK_INTERPRETATION[catKey];
        }

        // Calibrated Probabilities
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

        // LinearSHAP Factors
        var factors = data.top_contributing_factors || [];
        renderShapFactors(factors);

        // Actionable Recommendations
        renderActionableIdeas(catKey);

        // Smooth scroll to results
        reflectionResultSec.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    /* ==================================================================
       8. Event Listeners – Wizard & Form
    ================================================================== */
    // Step navigation buttons
    if (btnNextStep1) {
        btnNextStep1.addEventListener("click", function () {
            if (validateSection(1)) {
                showStep(2);
            }
        });
    }

    if (btnPrevStep2) {
        btnPrevStep2.addEventListener("click", function () {
            showStep(1);
        });
    }

    if (btnNextStep2) {
        btnNextStep2.addEventListener("click", function () {
            if (validateSection(2)) {
                showStep(3);
            }
        });
    }

    if (btnPrevStep3) {
        btnPrevStep3.addEventListener("click", function () {
            showStep(2);
        });
    }

    if (btnNextStep3) {
        btnNextStep3.addEventListener("click", function () {
            if (validateSection(3)) {
                showStep(4);
            }
        });
    }

    if (btnPrevStep4) {
        btnPrevStep4.addEventListener("click", function () {
            showStep(3);
        });
    }

    // Step pill header buttons (with forward validation)
    [
        { pill: stepPill1, step: 1 },
        { pill: stepPill2, step: 2 },
        { pill: stepPill3, step: 3 },
        { pill: stepPill4, step: 4 }
    ].forEach(function (item) {
        if (item.pill) {
            item.pill.addEventListener("click", function () {
                if (item.step > currentStep) {
                    for (var s = currentStep; s < item.step; s++) {
                        if (!validateSection(s)) return;
                    }
                }
                showStep(item.step);
            });
        }
    });

    // Calculate Prediction Button
    if (btnCalculatePrediction) {
        btnCalculatePrediction.addEventListener("click", function () {
            if (!validateAllSections()) {
                return;
            }

            var payload = buildAssessmentPayload();

            btnCalculatePrediction.disabled = true;
            btnCalculatePrediction.textContent = "Calculating Prediction & LinearSHAP…";

            fetch(PREDICT_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(function (res) {
                return res.json().then(function (data) {
                    return { ok: res.ok, status: res.status, data: data };
                });
            })
            .then(function (result) {
                if (result.ok && result.data && result.data.status === "success") {
                    renderPredictionResult(result.data);
                } else {
                    var errorMsg = (result.data && result.data.message)
                        ? result.data.message
                        : "Could not calculate prediction. Please verify your responses.";
                    alert("Assessment Error: " + errorMsg);
                }
            })
            .catch(function () {
                alert("Connection Error: Could not reach the Component 1 prediction service. Please ensure the local Flask server is running.");
            })
            .finally(function () {
                btnCalculatePrediction.disabled = false;
                btnCalculatePrediction.textContent = "Submit Assessment & Calculate Prediction";
            });
        });
    }

    // Reset Buttons
    if (btnResetAssessment) {
        btnResetAssessment.addEventListener("click", function () {
            clearAssessmentForm();
        });
    }

    if (btnClearProfile) {
        btnClearProfile.addEventListener("click", function () {
            clearAssessmentForm();
        });
    }

    // Preset Profile Buttons
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

    // Listen for form input changes to update selected styling and clear inline errors dynamically
    if (assessmentForm) {
        assessmentForm.addEventListener("change", function (e) {
            syncSelectionClasses();
            var target = e.target;
            if (target) {
                var card = target.closest(".question-card");
                if (card && card.classList.contains("question-card--error")) {
                    card.classList.remove("question-card--error");
                    var errEl = card.querySelector(".field-error-msg");
                    if (errEl) {
                        errEl.textContent = "";
                        errEl.setAttribute("hidden", "");
                    }
                }
            }
        });
    }

    // Initialize to Step 1 on page load (form begins blank with no preselected answers)
    clearAssessmentForm();
    showStep(1);

}());
