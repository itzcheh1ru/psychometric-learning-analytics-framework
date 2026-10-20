/**
 * component3.js – Client-side logic for Component 3:
 * Longitudinal AI-Assisted Study Pattern Analytics prototype.
 *
 * Responsibilities:
 *   - Client-side validation for weekly study record inputs
 *   - Validate weekly records through /api/component3/validate-weekly-record
 *   - Save validated prototype records in browser-local storage
 *   - Render participant-specific charts separately from imported-dataset charts
 *   - Form reset
 *   - Load Component 3 analytical summary
 *   - Load AI-assisted vs independent study-share chart
 *   - Load weekly prompt-frequency chart
 *   - Load study-pattern shift chart
 *
 * CRITICAL RESEARCH INTEGRITY:
 *   - Imported-dataset analytical values are obtained from backend APIs
 *   - Browser-local user charts are descriptive previews, not research findings
 *   - User-entered records are never sent to or merged with the imported dataset
 */

"use strict";

(function () {

    /* ============================================================
       PART 1 — WEEKLY RECORD VALIDATION
       ============================================================ */

    var VALIDATE_URL = "/api/component3/validate-weekly-record";
    var USER_RECORDS_KEY = "component3.userWeeklyRecords.v1";
    var activeUserParticipant = null;
    var userCharts = [];


    var REQUIRED_FIELDS = [
        {
            id: "participant_reference",
            label: "Participant Reference ID",
            errorId: "ref_error"
        },
        {
            id: "study_week",
            label: "Study Week",
            errorId: "week_error"
        },
        {
            id: "ai_study_hours",
            label: "AI-Assisted Study Hours",
            errorId: "ai_hours_error"
        },
        {
            id: "independent_study_hours",
            label: "Independent Study Hours",
            errorId: "ind_hours_error"
        },
        {
            id: "learning_activity",
            label: "Learning Activity",
            errorId: "activity_error"
        },
        {
            id: "prompt_count",
            label: "Prompt Count",
            errorId: "prompt_count_error"
        },
        {
            id: "prompt_purpose",
            label: "Primary Prompt Purpose",
            errorId: "purpose_error"
        }
    ];


    var FIELD_LABELS = {

        participant_reference:
            "Participant Reference ID",

        study_week:
            "Study Week",

        ai_study_hours:
            "AI-Assisted Study Hours",

        independent_study_hours:
            "Independent Study Hours",

        learning_activity:
            "Main Learning Activity",

        prompt_count:
            "Academic GenAI Prompt Count",

        prompt_purpose:
            "Primary Prompt Purpose",

        study_methods:
            "Study Methods",

        perceived_productivity:
            "Perceived Productivity",

        workload_pressure:
            "Workload / Deadline Pressure",

        prompt_detail:
            "Self-Reported Prompt Detail Rating"

    };


    /* ============================================================
       PART 2 — EXISTING WEEKLY RECORD FORM ELEMENTS
       ============================================================ */

    var form =
        document.getElementById("weeklyRecordForm");

    var submitBtn =
        document.getElementById("validateWeeklyBtn");

    var resetBtn =
        document.getElementById("resetWeeklyBtn");

    var previewSection =
        document.getElementById(
            "validationPreviewSection"
        );

    var successBlock =
        document.getElementById(
            "validationSuccessBlock"
        );

    var errorBlock =
        document.getElementById(
            "validationErrorBlock"
        );

    var summaryBody =
        document.getElementById(
            "weeklyRecordSummaryBody"
        );

    var errorList =
        document.getElementById(
            "weeklyErrorList"
        );

    var userDataSection =
        document.querySelector(".c3-user-data");

    var userDataStatus =
        document.getElementById("userDataStatus");

    var userParticipantTabs =
        document.getElementById("userParticipantTabs");

    var userParticipantCharts =
        document.getElementById("userParticipantCharts");

    var clearUserDataBtn =
        document.getElementById("clearUserDataBtn");


    function readUserRecords() {

        var stored =
            window.localStorage.getItem(USER_RECORDS_KEY);

        if (stored === null) {
            return [];
        }

        var records =
            JSON.parse(stored);

        if (
            !Array.isArray(records) ||
            records.some(function (record) {
                return !record ||
                    typeof record !== "object" ||
                    typeof record.participant_reference !== "string" ||
                    typeof record.study_week !== "string";
            })
        ) {
            throw new Error("Saved browser data has an invalid format.");
        }

        return records;

    }


    function weekNumber(record) {

        var match =
            String(record.study_week || "").match(/\d+/);

        return match ? Number(match[0]) : 0;

    }


    function destroyUserCharts() {

        userCharts.forEach(function (chart) {
            chart.destroy();
        });

        userCharts = [];

    }


    function renderUserDashboard(selectedParticipant) {

        if (!userDataStatus || !userParticipantTabs || !userParticipantCharts) {
            return;
        }

        var records;

        try {
            records = readUserRecords();
        } catch (error) {
            userDataStatus.textContent =
                "Saved browser data could not be read. Clear the saved user data and try again.";
            userDataStatus.classList.add("is-error");
            if (clearUserDataBtn) {
                clearUserDataBtn.disabled = false;
            }
            console.error("User-entered Component 3 data error:", error);
            return;
        }

        userDataStatus.classList.remove("is-error");
        if (clearUserDataBtn) {
            clearUserDataBtn.disabled = records.length === 0;
        }

        if (records.length === 0) {
            activeUserParticipant = null;
            userParticipantTabs.hidden = true;
            userParticipantTabs.replaceChildren();
            destroyUserCharts();
            userParticipantCharts.innerHTML =
                '<p class="c3-user-data__empty">Save a weekly record below to create a participant tab and view its charts.</p>';
            userDataStatus.textContent =
                "No user-entered records saved in this browser yet.";
            return;
        }

        var participantCodes =
            Array.from(new Set(records.map(function (record) {
                return String(record.participant_reference);
            }))).sort(function (left, right) {
                return left.localeCompare(right, undefined, {
                    numeric: true,
                    sensitivity: "base"
                });
            });

        var activeCode =
            selectedParticipant || activeUserParticipant;

        if (participantCodes.indexOf(activeCode) === -1) {
            activeCode = participantCodes[0];
        }

        activeUserParticipant = activeCode;
        userParticipantTabs.hidden = false;
        userParticipantTabs.replaceChildren();

        participantCodes.forEach(function (participantCode, index) {
            var tab = document.createElement("button");
            tab.type = "button";
            tab.id = "userParticipantTab" + index;
            tab.className = "c3-user-data__tab";
            tab.setAttribute("role", "tab");
            tab.setAttribute("aria-selected", String(participantCode === activeCode));
            tab.setAttribute(
                "tabindex",
                participantCode === activeCode ? "0" : "-1"
            );
            tab.setAttribute(
                "aria-controls",
                "userParticipantCharts"
            );
            tab.textContent = participantCode;
            tab.addEventListener("click", function () {
                renderUserDashboard(participantCode);
            });
            tab.addEventListener("keydown", function (event) {
                var currentIndex =
                    participantCodes.indexOf(participantCode);
                var nextIndex = currentIndex;

                if (event.key === "ArrowRight") {
                    nextIndex = (currentIndex + 1) % participantCodes.length;
                } else if (event.key === "ArrowLeft") {
                    nextIndex =
                        (currentIndex - 1 + participantCodes.length) %
                        participantCodes.length;
                } else if (event.key === "Home") {
                    nextIndex = 0;
                } else if (event.key === "End") {
                    nextIndex = participantCodes.length - 1;
                } else {
                    return;
                }

                event.preventDefault();
                renderUserDashboard(participantCodes[nextIndex]);
                var selectedTab =
                    document.getElementById("userParticipantTab" + nextIndex);
                if (selectedTab) {
                    selectedTab.focus();
                }
            });
            userParticipantTabs.appendChild(tab);
            if (participantCode === activeCode) {
                userParticipantCharts.setAttribute(
                    "aria-labelledby",
                    tab.id
                );
            }
        });

        var participantRecords =
            records.filter(function (record) {
                return String(record.participant_reference) === activeCode;
            }).sort(function (left, right) {
                return weekNumber(left) - weekNumber(right);
            });

        userDataStatus.textContent =
            participantCodes.length +
            " participant " +
            (participantCodes.length === 1 ? "code" : "codes") +
            " saved in this browser; showing " +
            participantRecords.length +
            " weekly " +
            (participantRecords.length === 1 ? "record" : "records") +
            " for " +
            activeCode +
            ".";

        renderUserParticipantCharts(activeCode, participantRecords);

    }


    function renderUserParticipantCharts(participantCode, records) {

        destroyUserCharts();
        userParticipantCharts.replaceChildren();

        var title = document.createElement("h3");
        title.className = "subsection-heading";
        title.textContent = "Weekly charts for " + participantCode;
        userParticipantCharts.appendChild(title);

        var note = document.createElement("p");
        note.className = "c3-chart-description";
        note.textContent =
            "Charts use only this participant code's saved entries. A shift value appears only when a valid previous-week study-share comparison exists.";
        userParticipantCharts.appendChild(note);

        var chartDefinitions = [
            {
                id: "userStudyShareChart",
                title: "Study-hour allocation",
                type: "line",
                datasets: [
                    {
                        label: "AI-assisted study share (%)",
                        color: "#2563eb",
                        values: records.map(function (record) {
                            var total = Number(record.ai_study_hours) +
                                Number(record.independent_study_hours);
                            return total > 0
                                ? Number(record.ai_study_hours) / total * 100
                                : null;
                        })
                    },
                    {
                        label: "Independent study share (%)",
                        color: "#7c3aed",
                        values: records.map(function (record) {
                            var total = Number(record.ai_study_hours) +
                                Number(record.independent_study_hours);
                            return total > 0
                                ? Number(record.independent_study_hours) / total * 100
                                : null;
                        })
                    }
                ],
                axisTitle: "Share of reported study hours (%)"
            },
            {
                id: "userPromptFrequencyChart",
                title: "Academic prompt count",
                type: "bar",
                datasets: [
                    {
                        label: "Prompts",
                        color: "#0f766e",
                        values: records.map(function (record) {
                            return Number(record.prompt_count);
                        })
                    }
                ],
                axisTitle: "Prompts per week"
            },
            {
                id: "userShiftChart",
                title: "Study Pattern Shift",
                type: "line",
                datasets: [
                    {
                        label: "Average absolute share change (percentage points)",
                        color: "#d97706",
                        values: getUserShiftValues(records)
                    }
                ],
                axisTitle: "Average absolute percentage-point change"
            },
            {
                id: "userPromptDetailChart",
                title: "Self-reported prompt detail",
                type: "line",
                datasets: [
                    {
                        label: "Prompt detail rating (1–5)",
                        color: "#db2777",
                        values: records.map(function (record) {
                            return record.prompt_detail === undefined
                                ? null
                                : Number(record.prompt_detail);
                        })
                    }
                ],
                axisTitle: "Self-reported rating (1–5)"
            }
        ];

        var grid = document.createElement("div");
        grid.className = "c3-user-data__grid";

        chartDefinitions.forEach(function (definition) {
            var card = document.createElement("section");
            card.className = "c3-user-data__chart-card";

            var heading = document.createElement("h4");
            heading.textContent = definition.title;
            card.appendChild(heading);

            var chartWrap = document.createElement("div");
            chartWrap.className = "c3-user-data__chart-wrap";

            var canvas = document.createElement("canvas");
            canvas.id = definition.id;
            canvas.setAttribute("role", "img");
            canvas.setAttribute(
                "aria-label",
                definition.title + " for participant " + participantCode
            );
            chartWrap.appendChild(canvas);
            card.appendChild(chartWrap);
            grid.appendChild(card);

            var chartDatasets =
                definition.datasets.map(function (dataset) {
                    return {
                        label: dataset.label,
                        data: dataset.values,
                        borderColor: dataset.color,
                        backgroundColor: dataset.color,
                        pointRadius: 4,
                        borderWidth: 2,
                        tension: 0.25,
                        spanGaps: false,
                        fill: false,
                        borderRadius: definition.type === "bar" ? 4 : 0
                    };
                });

            userCharts.push(new Chart(canvas, {
                type: definition.type,
                data: {
                    labels: records.map(function (record) {
                        return record.study_week;
                    }),
                    datasets: chartDatasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: chartDatasets.length > 1,
                            position: "bottom"
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    var value = Number(context.parsed.y);
                                    return context.dataset.label + ": " +
                                        (Number.isFinite(value)
                                            ? value.toFixed(1)
                                            : "Not available");
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            title: { display: true, text: "Observation week" }
                        },
                        y: {
                            beginAtZero: true,
                            suggestedMax: definition.id === "userPromptDetailChart"
                                ? 5
                                : undefined,
                            title: { display: true, text: definition.axisTitle }
                        }
                    }
                }
            }));

            if (
                definition.id === "userShiftChart" &&
                definition.datasets[0].values.every(function (value) {
                    return value === null;
                })
            ) {
                var shiftNote = document.createElement("p");
                shiftNote.className = "c3-data-note";
                shiftNote.textContent =
                    "Study Pattern Shift needs at least two weeks with non-zero total study hours for this participant.";
                card.appendChild(shiftNote);
            }
        });

        userParticipantCharts.appendChild(grid);

        var detailsSection = document.createElement("section");
        detailsSection.className = "c3-user-data__details";

        var detailsHeading = document.createElement("h4");
        detailsHeading.className = "c3-user-data__details-heading";
        detailsHeading.textContent = "Weekly record details";
        detailsSection.appendChild(detailsHeading);

        var detailsIntro = document.createElement("p");
        detailsIntro.className = "c3-user-data__details-intro";
        detailsIntro.textContent =
            "Review the values saved for each observation week. Optional items are marked when they were not reported.";
        detailsSection.appendChild(detailsIntro);

        records.forEach(function (record) {
            var weekCard = document.createElement("article");
            weekCard.className = "c3-user-data__week-card";

            var weekHeading = document.createElement("h5");
            weekHeading.className = "c3-user-data__week-heading";
            weekHeading.textContent = record.study_week;
            weekCard.appendChild(weekHeading);

            var fields = [
                {
                    label: "AI-assisted study",
                    value: record.ai_study_hours + " hours",
                    group: "study"
                },
                {
                    label: "Independent study",
                    value: record.independent_study_hours + " hours",
                    group: "study"
                },
                {
                    label: "Academic prompts",
                    value: record.prompt_count,
                    group: "prompts"
                },
                {
                    label: "Primary prompt purpose",
                    value: record.prompt_purpose,
                    group: "prompts"
                },
                {
                    label: "Study methods",
                    value: Array.isArray(record.study_methods) &&
                        record.study_methods.length
                        ? record.study_methods.join(", ")
                        : "Not reported",
                    group: "additional"
                },
                {
                    label: "Perceived productivity",
                    value: record.perceived_productivity || "Not reported",
                    group: "additional"
                },
                {
                    label: "Workload pressure",
                    value: record.workload_pressure || "Not reported",
                    group: "additional"
                },
                {
                    label: "Prompt detail rating",
                    value: record.prompt_detail === undefined
                        ? "Not reported"
                        : record.prompt_detail + " / 5",
                    group: "additional"
                }
            ];

            [
                { key: "study", title: "Study time" },
                { key: "prompts", title: "Prompt activity" },
                { key: "additional", title: "Additional measures" }
            ].forEach(function (group) {
                var groupSection = document.createElement("section");
                groupSection.className = "c3-user-data__detail-group";

                var groupHeading = document.createElement("h6");
                groupHeading.textContent = group.title;
                groupSection.appendChild(groupHeading);

                var fieldGrid = document.createElement("dl");
                fieldGrid.className = "c3-user-data__field-grid";

                fields.filter(function (field) {
                    return field.group === group.key;
                }).forEach(function (field) {
                    var fieldItem = document.createElement("div");
                    fieldItem.className = "c3-user-data__field";

                    var label = document.createElement("dt");
                    label.textContent = field.label;

                    var value = document.createElement("dd");
                    value.textContent = String(field.value);
                    if (field.value === "Not reported") {
                        value.className = "c3-user-data__not-reported";
                    }

                    fieldItem.appendChild(label);
                    fieldItem.appendChild(value);
                    fieldGrid.appendChild(fieldItem);
                });

                groupSection.appendChild(fieldGrid);
                weekCard.appendChild(groupSection);
            });

            detailsSection.appendChild(weekCard);
        });
        userParticipantCharts.appendChild(detailsSection);

    }


    function getUserShiftValues(records) {

        var previousShares = null;

        return records.map(function (record) {
            var total =
                Number(record.ai_study_hours) +
                Number(record.independent_study_hours);

            if (!(total > 0)) {
                return null;
            }

            var aiShare =
                Number(record.ai_study_hours) / total * 100;
            var independentShare =
                Number(record.independent_study_hours) / total * 100;
            var shift = previousShares === null
                ? null
                : (
                    Math.abs(aiShare - previousShares.ai) +
                    Math.abs(independentShare - previousShares.independent)
                ) / 2;

            previousShares = {
                ai: aiShare,
                independent: independentShare
            };

            return shift;
        });

    }


    function saveUserRecord(record) {

        var records =
            readUserRecords();
        var existingIndex =
            records.findIndex(function (savedRecord) {
                return String(savedRecord.participant_reference) ===
                        String(record.participant_reference) &&
                    String(savedRecord.study_week) ===
                        String(record.study_week);
            });

        if (existingIndex === -1) {
            records.push(record);
        } else {
            records[existingIndex] = record;
        }

        window.localStorage.setItem(
            USER_RECORDS_KEY,
            JSON.stringify(records)
        );

    }


    /* ============================================================
       PART 3 — VALIDATION FUNCTIONS
       ============================================================ */

    function showFieldError(errorId, message) {

        var el =
            document.getElementById(errorId);

        if (el) {

            el.textContent = message;

            el.removeAttribute("hidden");

        }

    }


    function clearFieldError(errorId, inputId) {

        var el =
            document.getElementById(errorId);

        if (el) {

            el.textContent = "";

            el.setAttribute(
                "hidden",
                ""
            );

        }


        var input =
            document.getElementById(inputId);

        if (input) {

            input.classList.remove(
                "input--error"
            );

        }

    }


    function clearAllErrors() {

        REQUIRED_FIELDS.forEach(
            function (field) {

                clearFieldError(
                    field.errorId,
                    field.id
                );

            }
        );

    }


    function clientValidate() {

        var isValid = true;

        clearAllErrors();


        REQUIRED_FIELDS.forEach(
            function (field) {

                var input =
                    document.getElementById(
                        field.id
                    );


                if (!input) {

                    return;

                }


                var val =
                    input.value.trim();


                if (!val) {

                    showFieldError(
                        field.errorId,
                        field.label +
                            " is required."
                    );

                    input.classList.add(
                        "input--error"
                    );

                    isValid = false;

                }

                else if (
                    field.id ===
                        "ai_study_hours" ||

                    field.id ===
                        "independent_study_hours"
                ) {

                    var num =
                        parseFloat(val);


                    if (
                        isNaN(num) ||
                        num < 0 ||
                        num > 168
                    ) {

                        showFieldError(
                            field.errorId,
                            field.label +
                                " must be between 0 and 168 hours."
                        );

                        input.classList.add(
                            "input--error"
                        );

                        isValid = false;

                    }

                }

                else if (
                    field.id ===
                    "prompt_count"
                ) {

                    var pCount =
                        Number(val);


                    if (
                        !Number.isInteger(
                            pCount
                        ) ||
                        pCount < 0
                    ) {

                        showFieldError(
                            field.errorId,
                            "Prompt count must be a non-negative whole number."
                        );

                        input.classList.add(
                            "input--error"
                        );

                        isValid = false;

                    }

                }

            }
        );


        return isValid;

    }


    function buildPayload() {

        var payload = {

            participant_reference:
                document.getElementById(
                    "participant_reference"
                ).value.trim(),

            study_week:
                document.getElementById(
                    "study_week"
                ).value.trim(),

            ai_study_hours:
                parseFloat(
                    document.getElementById(
                        "ai_study_hours"
                    ).value.trim()
                ),

            independent_study_hours:
                parseFloat(
                    document.getElementById(
                        "independent_study_hours"
                    ).value.trim()
                ),

            learning_activity:
                document.getElementById(
                    "learning_activity"
                ).value.trim(),

            prompt_count:
                parseInt(
                    document.getElementById(
                        "prompt_count"
                    ).value.trim(),
                    10
                ),

            prompt_purpose:
                document.getElementById(
                    "prompt_purpose"
                ).value.trim()

        };

        var studyMethods =
            Array.from(
                document.getElementById("study_methods").selectedOptions
            ).map(function (option) {
                return option.value;
            });

        if (studyMethods.length > 0) {
            payload.study_methods = studyMethods;
        }

        [
            "perceived_productivity",
            "workload_pressure"
        ].forEach(function (field) {
            var value =
                document.getElementById(field).value.trim();

            if (value) {
                payload[field] = value;
            }
        });

        var promptDetail =
            document.getElementById("prompt_detail").value;

        if (promptDetail) {
            payload.prompt_detail = parseInt(promptDetail, 10);
        }

        return payload;

    }


    function renderSummary(
        validatedRecord
    ) {

        if (!summaryBody) {

            return;

        }


        summaryBody.innerHTML = "";


        Object.keys(FIELD_LABELS)
            .forEach(
                function (key) {

                    if (
                        validatedRecord[key] !==
                            undefined &&

                        validatedRecord[key] !==
                            null
                    ) {

                        var tr =
                            document.createElement(
                                "tr"
                            );


                        var th =
                            document.createElement(
                                "td"
                            );


                        th.textContent =
                            FIELD_LABELS[key];


                        var td =
                            document.createElement(
                                "td"
                            );


                        td.textContent =
                            String(
                                validatedRecord[key]
                            );


                        tr.appendChild(th);

                        tr.appendChild(td);

                        summaryBody.appendChild(tr);

                    }

                }
            );

    }


    function showSuccess(data, skipScroll) {

        if (!previewSection) {

            return;

        }


        previewSection.removeAttribute(
            "hidden"
        );


        if (successBlock) {

            successBlock.removeAttribute(
                "hidden"
            );

        }


        if (errorBlock) {

            errorBlock.setAttribute(
                "hidden",
                ""
            );

        }


        if (data.validated_record) {

            renderSummary(
                data.validated_record
            );

        }


        if (!skipScroll) {
            previewSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }

    }


    function showErrors(errors) {

        if (!previewSection) {

            return;

        }


        previewSection.removeAttribute(
            "hidden"
        );


        if (errorBlock) {

            errorBlock.removeAttribute(
                "hidden"
            );

        }


        if (successBlock) {

            successBlock.setAttribute(
                "hidden",
                ""
            );

        }


        if (errorList) {

            errorList.innerHTML = "";


            errors.forEach(
                function (msg) {

                    var li =
                        document.createElement(
                            "li"
                        );


                    li.textContent = msg;


                    errorList.appendChild(li);

                }
            );

        }


        previewSection.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }


    /* ============================================================
       PART 4 — WEEKLY RECORD FORM SUBMISSION
       ============================================================ */

    if (form) {

        form.addEventListener(
            "submit",
            function (e) {

                e.preventDefault();


                if (!clientValidate()) {

                    var firstErr =
                        form.querySelector(
                            ".form-input.input--error, " +
                            ".form-select.input--error"
                        );


                    if (firstErr) {

                        firstErr.focus();

                    }


                    return;

                }


                var payload =
                    buildPayload();

                var savedRecords;
                try {
                    savedRecords = readUserRecords();
                } catch (error) {
                    showErrors([
                        "Saved user data could not be read. Clear the browser-saved user data before submitting a new record."
                    ]);
                    console.error("Could not read user-entered records:", error);
                    return;
                }

                var duplicate =
                    savedRecords.some(function (record) {
                        return String(record.participant_reference) ===
                                String(payload.participant_reference) &&
                            String(record.study_week) ===
                                String(payload.study_week);
                    });

                if (
                    duplicate &&
                    !window.confirm(
                        "A record for this participant and week already exists in this browser. Replace that saved entry?"
                    )
                ) {
                    showErrors([
                        "The existing participant-week record was kept unchanged."
                    ]);
                    return;
                }

                if (submitBtn) {

                    submitBtn.disabled =
                        true;

                    submitBtn.textContent =
                        "Validating and saving…";

                }


                fetch(
                    VALIDATE_URL,
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )

                    }
                )

                .then(
                    function (res) {

                        return res.json()
                            .then(
                                function (data) {

                                    return {
                                        ok: res.ok,
                                        data: data
                                    };

                                }
                            );

                    }
                )

                .then(
                    function (result) {

                        if (result.ok) {

                            try {
                                saveUserRecord(result.data.validated_record);
                            } catch (error) {
                                showErrors([
                                    "The record passed validation, but could not be saved in this browser. Check browser storage settings and try again."
                                ]);
                                console.error("Could not save user-entered record:", error);
                                return;
                            }

                            showSuccess(result.data, true);
                            renderUserDashboard(
                                result.data.validated_record.participant_reference
                            );

                            if (userDataSection) {
                                userDataSection.scrollIntoView({
                                    behavior: "smooth",
                                    block: "start"
                                });
                            }

                        }

                        else {

                            var errors =
                                (
                                    result.data &&
                                    result.data.errors
                                )
                                    ? result.data.errors
                                    : [
                                        "Validation failed."
                                    ];


                            showErrors(
                                errors
                            );

                        }

                    }
                )

                .catch(
                    function () {

                        showErrors(
                            [
                                "Could not reach the validation service. Please check your network connection."
                            ]
                        );

                    }
                )

                .finally(
                    function () {

                        if (submitBtn) {

                            submitBtn.disabled =
                                false;

                            submitBtn.textContent =
                                "Save Weekly Record & Update Charts";

                        }

                    }
                );

            }
        );

    }


    /* ============================================================
       PART 5 — WEEKLY RECORD FORM RESET
       ============================================================ */

    if (resetBtn && form) {

        resetBtn.addEventListener(
            "click",
            function () {

                form.reset();

                clearAllErrors();


                if (previewSection) {

                    previewSection.setAttribute(
                        "hidden",
                        ""
                    );

                }


                if (successBlock) {

                    successBlock.setAttribute(
                        "hidden",
                        ""
                    );

                }


                if (errorBlock) {

                    errorBlock.setAttribute(
                        "hidden",
                        ""
                    );

                }

            }
        );

    }


    if (clearUserDataBtn) {
        clearUserDataBtn.addEventListener("click", function () {
            if (!window.confirm(
                "Clear all weekly records entered in this browser? Imported-dataset charts will not be affected."
            )) {
                return;
            }

            try {
                window.localStorage.removeItem(USER_RECORDS_KEY);
                renderUserDashboard();
                if (form) {
                    form.reset();
                    clearAllErrors();
                }
                if (previewSection) {
                    previewSection.setAttribute("hidden", "");
                }
            } catch (error) {
                userDataStatus.textContent =
                    "User-entered data could not be cleared from this browser.";
                userDataStatus.classList.add("is-error");
                console.error("Could not clear user-entered records:", error);
            }
        });
    }


    /* ============================================================
       PART 6 — COMPONENT 3 SUMMARY
       ============================================================ */

    async function loadComponent3Summary() {

        try {

            var response =
                await fetch(
                    "/api/component3/summary"
                );


            if (!response.ok) {

                throw new Error(
                    "Summary API returned " +
                    response.status
                );

            }


            var data =
                await response.json();


            var participants =
                document.getElementById(
                    "c3-participants"
                );

            var repeatedParticipants =
                document.getElementById(
                    "c3-repeated-participants"
                );


            var weeks =
                document.getElementById(
                    "c3-weeks"
                );


            var records =
                document.getElementById(
                    "c3-records"
                );


            var status =
                document.getElementById(
                    "c3-analysis-status"
                );


            if (participants) {

                participants.textContent =
                    data.participants ??
                    0;

            }

            if (repeatedParticipants) {

                repeatedParticipants.textContent =
                    data.repeated_participants ??
                    0;

            }


            if (weeks) {

                weeks.textContent =
                    data.weeks ??
                    0;

            }


            if (records) {

                records.textContent =
                    data.records ??
                    0;

            }


            if (status) {

                status.textContent =
                    data.trend_analysis_available
                        ? "Repeat-week comparisons available"
                        : "Baseline only — awaiting repeat weeks";

            }

        }

        catch (error) {

            console.error(
                "Component 3 summary error:",
                error
            );

        }

    }


    /* ============================================================
       PART 7 — AI STUDY SHARE CHART
       ============================================================ */

    async function loadStudyShareChart() {

        try {

            var canvas =
                document.getElementById(
                    "studyShareChart"
                );

            var status =
                document.getElementById(
                    "studyShareChartStatus"
                );

            if (!canvas) {

                return;

            }


            var response =
                await fetch(
                    "/api/component3/study-share"
                );


            if (!response.ok) {

                throw new Error(
                    "Study share API returned " +
                    response.status
                );

            }


            var data =
                await response.json();

            if (!Array.isArray(data) || data.length === 0) {

                if (status) {

                    status.textContent =
                        "Study-share data is not yet available because no records contain valid study-hour totals.";

                }

                return;

            }


            var labels =
                data.map(
                    function (item) {

                        return (
                            "Week " +
                            item.study_week
                        );

                    }
                );


            var aiShare =
                data.map(
                    function (item) {

                        return item.ai_study_share;

                    }
                );


            var independentShare =
                data.map(
                    function (item) {

                        return item.independent_study_share;

                    }
                );

            if (status) {

                status.textContent =
                    "Shares are weighted by reported study hours. Sample sizes are shown in the chart tooltips.";

            }


            new Chart(
                canvas,
                {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "AI Study Share (%)",

                                data:
                                    aiShare,

                                borderColor:
                                    "#2563eb",

                                backgroundColor:
                                    "rgba(37, 99, 235, 0.12)",

                                pointBackgroundColor:
                                    "#2563eb",

                                pointBorderColor:
                                    "#ffffff",

                                pointBorderWidth:
                                    2,

                                pointRadius:
                                    5,

                                pointHoverRadius:
                                    7,

                                borderWidth:
                                    3,

                                tension:
                                    0.3

                            },

                            {

                                label:
                                    "Independent Study Share (%)",

                                data:
                                    independentShare,

                                borderColor:
                                    "#7c3aed",

                                backgroundColor:
                                    "rgba(124, 58, 237, 0.12)",

                                pointBackgroundColor:
                                    "#7c3aed",

                                pointBorderColor:
                                    "#ffffff",

                                pointBorderWidth:
                                    2,

                                pointRadius:
                                    5,

                                pointHoverRadius:
                                    7,

                                borderWidth:
                                    3,

                                tension:
                                    0.3

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        interaction: {

                            intersect: false,

                            mode: "index"

                        },

                        plugins: {

                            legend: {

                                position: "top",

                                labels: {

                                    usePointStyle: true,

                                    boxWidth: 9,

                                    boxHeight: 9,

                                    padding: 18,

                                    color: "#344054",

                                    font: {

                                        size: 12,

                                        weight: "600"

                                    }

                                }

                            },

                            tooltip: {

                                callbacks: {

                                    afterBody: function (items) {

                                        var item =
                                            data[items[0].dataIndex];

                                        return [
                                            "Valid records: " + item.records,
                                            "Participants: " + item.participants,
                                            "Reported study hours: " +
                                                Number(item.total_study_hours).toFixed(1)
                                        ];

                                    }

                                }

                            }

                        },

                        scales: {

                            y: {

                                beginAtZero: true,

                                max: 100,

                                grid: {

                                    color: "rgba(148, 163, 184, 0.2)"

                                },

                                ticks: {

                                    color: "#667085",

                                    font: {

                                        size: 11

                                    },

                                    callback: function (value) {

                                        return value + "%";

                                    }

                                },

                                title: {

                                    display: true,

                                    text:
                                        "Study Share (%)"

                                }

                            },

                            x: {

                                grid: {

                                    display: false

                                },

                                ticks: {

                                    color: "#475467",

                                    font: {

                                        size: 11,

                                        weight: "600"

                                    }

                                },

                                title: {

                                    display: true,

                                    text:
                                        "Study Week"

                                }

                            }

                        }

                    }

                }
            );

        }

        catch (error) {

            var status =
                document.getElementById(
                    "studyShareChartStatus"
                );

            if (status) {

                status.textContent =
                    "Study-share data could not be loaded. Please check the dataset and refresh the page.";

                status.classList.add("is-error");

            }

            console.error(
                "Study share chart error:",
                error
            );

        }

    }


    /* ============================================================
       PART 8 — WEEKLY PROMPT FREQUENCY CHART
       ============================================================ */

    async function loadPromptPurposeChart() {

        var canvas =
            document.getElementById(
                "promptPurposeChart"
            );

        var status =
            document.getElementById(
                "promptPurposeChartStatus"
            );

        if (!canvas || !status) {

            return;

        }

        try {

            var response =
                await fetch(
                    "/api/component3/prompt-purposes"
                );

            if (!response.ok) {

                throw new Error(
                    "Prompt-purpose API returned " +
                    response.status
                );

            }

            var rows =
                await response.json();

            if (!Array.isArray(rows)) {

                throw new Error(
                    "Prompt-purpose API returned an invalid dataset."
                );

            }

            if (rows.length === 0) {

                status.textContent =
                    "No prompt-purpose data is available in the processed dataset yet.";

                return;

            }

            var weeks = [];
            var categories = [];
            var purposeByWeek = {};
            var purposeWeekTotals = {};

            rows.forEach(
                function (row) {

                    var week =
                        Number(row.study_week);

                    var category =
                        String(row.prompt_purpose || "").trim();

                    if (!Number.isFinite(week) || !category) {

                        return;

                    }

                    if (weeks.indexOf(week) === -1) {

                        weeks.push(week);

                    }

                    if (categories.indexOf(category) === -1) {

                        categories.push(category);

                    }

                    var weekKey =
                        String(week);

                    if (!purposeByWeek[weekKey]) {

                        purposeByWeek[weekKey] = {};

                    }

                    purposeByWeek[weekKey][category] = row;
                    purposeWeekTotals[weekKey] =
                        Number(row.valid_records) || 0;

                }
            );

            weeks.sort(
                function (left, right) {

                    return left - right;

                }
            );

            categories.sort();

            if (weeks.length === 0 || categories.length === 0) {

                status.textContent =
                    "The processed dataset contains no valid weekly prompt-purpose records.";

                return;

            }

            var palette = [
                "#2563eb",
                "#7c3aed",
                "#0f766e",
                "#d97706",
                "#db2777",
                "#4f46e5",
                "#64748b"
            ];

            var datasets =
                categories.map(
                    function (category, index) {

                        return {

                            label: category,

                            data: weeks.map(
                                function (week) {

                                    var item =
                                        purposeByWeek[String(week)][category];

                                    return item
                                        ? Number(item.percentage)
                                        : 0;

                                }
                            ),

                            backgroundColor:
                                palette[index % palette.length],

                            borderRadius: 4,

                            maxBarThickness: 52

                        };

                    }
                );

            new Chart(
                canvas,
                {

                    type: "bar",

                    data: {

                        labels: weeks.map(
                            function (week) {

                                return "Week " + week;

                            }
                        ),

                        datasets: datasets

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        interaction: {

                            intersect: false,

                            mode: "index"

                        },

                        plugins: {

                            legend: {

                                position: "bottom",

                                labels: {

                                    usePointStyle: true,

                                    boxWidth: 9,

                                    boxHeight: 9,

                                    padding: 14,

                                    color: "#344054",

                                    font: {

                                        size: 11

                                    }

                                }

                            },

                            tooltip: {

                                callbacks: {

                                    label: function (context) {

                                        var weekKey =
                                            String(weeks[context.dataIndex]);
                                        var item =
                                            purposeByWeek[weekKey][
                                                context.dataset.label
                                            ];

                                        return (
                                            context.dataset.label +
                                            ": " +
                                            Number(context.parsed.y).toFixed(1) +
                                            "% (" +
                                            (item ? item.count : 0) +
                                            " of " +
                                            purposeWeekTotals[weekKey] +
                                            " records)"
                                        );

                                    }

                                }

                            }

                        },

                        scales: {

                            x: {

                                stacked: false,

                                grid: {

                                    display: false

                                },

                                ticks: {

                                    color: "#475467",

                                    font: {

                                        size: 11,

                                        weight: "600"

                                    }

                                },

                                title: {

                                    display: true,

                                    text: "Study Week",

                                    color: "#475467"

                                }

                            },

                            y: {

                                stacked: false,

                                beginAtZero: true,

                                ticks: {

                                    precision: 0,

                                    color: "#667085"

                                },

                                grid: {

                                    color: "rgba(148, 163, 184, 0.2)"

                                },

                                title: {

                                    display: true,

                                    text: "Share of valid-purpose records (%)",

                                    color: "#475467"

                                }

                            }

                        }

                    }

                }
            );

            status.textContent =
                "Showing " +
                weeks.length +
                " study week" +
                (weeks.length === 1 ? "" : "s") +
                " from the processed dataset. Category percentages can sum above 100% because responses overlap.";

        }

        catch (error) {

            status.textContent =
                "Prompt-purpose data could not be loaded. Please check the dataset and try refreshing the page.";

            status.classList.add("is-error");

            console.error(
                "Prompt-purpose chart error:",
                error
            );

        }

    }


    async function loadPromptFrequencyChart() {

        try {

            var canvas =
                document.getElementById(
                    "promptFrequencyChart"
                );


            if (!canvas) {

                return;

            }


            var response =
                await fetch(
                    "/api/component3/prompt-frequency"
                );


            if (!response.ok) {

                throw new Error(
                    "Prompt frequency API returned " +
                    response.status
                );

            }


            var data =
                await response.json();

            var status =
                document.getElementById(
                    "promptFrequencyChartStatus"
                );

            if (!Array.isArray(data) || data.length === 0) {

                if (status) {

                    status.textContent =
                        "Prompt-frequency data is not yet available in the processed dataset.";

                }

                return;

            }


            var labels =
                data.map(
                    function (item) {

                        return (
                            "Week " +
                            item.study_week
                        );

                    }
                );


            var values =
                data.map(
                    function (item) {

                        return item.average_prompts;

                    }
                );

            if (status) {

                status.textContent =
                    "Bars show average prompts per weekly record. Total prompts and sample sizes are available in each tooltip.";

            }


            new Chart(
                canvas,
                {

                    type: "bar",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Average Prompts per Record",

                                data:
                                    values,

                                backgroundColor:
                                    "rgba(37, 99, 235, 0.72)",

                                hoverBackgroundColor:
                                    "#1d4ed8",

                                borderColor:
                                    "#2563eb",

                                borderWidth:
                                    1,

                                borderRadius:
                                    6,

                                maxBarThickness:
                                    56

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        plugins: {

                            legend: {

                                position: "top",

                                labels: {

                                    usePointStyle: true,

                                    boxWidth: 9,

                                    boxHeight: 9,

                                    padding: 18,

                                    color: "#344054",

                                    font: {

                                        size: 12,

                                        weight: "600"

                                    }

                                }

                            },

                            tooltip: {

                                callbacks: {

                                    label: function (context) {

                                        return (
                                            "Average: " +
                                            Number(context.parsed.y).toFixed(1) +
                                            " prompts per record"
                                        );

                                    },

                                    afterBody: function (items) {

                                        var item =
                                            data[items[0].dataIndex];

                                        return [
                                            "Total prompts: " + item.total_prompts,
                                            "Records: " + item.records,
                                            "Participants: " + item.participants
                                        ];

                                    }

                                }

                            }

                        },

                        scales: {

                            y: {

                                beginAtZero: true,

                                grid: {

                                    color: "rgba(148, 163, 184, 0.2)"

                                },

                                ticks: {

                                    color: "#667085",

                                    precision: 0,

                                    font: {

                                        size: 11

                                    }

                                },

                                title: {

                                    display: true,

                                    text:
                                        "Average prompts per record"

                                }

                            },

                            x: {

                                grid: {

                                    display: false

                                },

                                ticks: {

                                    color: "#475467",

                                    font: {

                                        size: 11,

                                        weight: "600"

                                    }

                                },

                                title: {

                                    display: true,

                                    text:
                                        "Study Week"

                                }

                            }

                        }

                    }

                }
            );

        }

        catch (error) {

            var status =
                document.getElementById(
                    "promptFrequencyChartStatus"
                );

            if (status) {

                status.textContent =
                    "Prompt-frequency data could not be loaded. Please check the dataset and refresh the page.";

                status.classList.add("is-error");

            }

            console.error(
                "Prompt chart error:",
                error
            );

        }

    }


    /* ============================================================
       PART 9 — STUDY PATTERN SHIFT CHART
       ============================================================ */

    async function loadStudyShiftChart() {

        try {

            var canvas =
                document.getElementById(
                    "studyShiftChart"
                );

            var status =
                document.getElementById(
                    "studyShiftChartStatus"
                );


            if (!canvas) {

                return;

            }


            var response =
                await fetch(
                    "/api/component3/study-shift"
                );


            if (!response.ok) {

                throw new Error(
                    "Study shift API returned " +
                    response.status
                );

            }


            var data =
                await response.json();

            if (!Array.isArray(data) || data.length === 0) {

                if (status) {

                    status.textContent =
                        "Study pattern shift is not yet available. At least two study weeks for the same participant are required.";

                }

                return;

            }

            if (status) {

                status.textContent =
                    "Showing week-to-week comparisons. The shift value is the average absolute percentage-point change across AI-assisted and independent study shares; sample sizes are shown in tooltips.";

            }


            var labels =
                data.map(
                    function (item) {

                        return (
                            "Week " +
                            item.study_week
                        );

                    }
                );


            var values =
                data.map(
                    function (item) {

                        return item.average_shift;

                    }
                );


            new Chart(
                canvas,
                {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Average Study Pattern Shift",

                                data:
                                    values,

                                borderColor:
                                    "#7c3aed",

                                backgroundColor:
                                    "rgba(124, 58, 237, 0.12)",

                                pointBackgroundColor:
                                    "#7c3aed",

                                pointBorderColor:
                                    "#ffffff",

                                pointBorderWidth:
                                    2,

                                pointRadius:
                                    5,

                                pointHoverRadius:
                                    7,

                                borderWidth:
                                    3,

                                tension:
                                    0.3,

                                fill:
                                    true

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        interaction: {

                            intersect: false,

                            mode: "index"

                        },

                        plugins: {

                            legend: {

                                position: "top",

                                labels: {

                                    usePointStyle: true,

                                    boxWidth: 9,

                                    boxHeight: 9,

                                    padding: 18,

                                    color: "#344054",

                                    font: {

                                        size: 12,

                                        weight: "600"

                                    }

                                },

                                tooltip: {

                                    callbacks: {

                                        label: function (context) {

                                            return (
                                                "Average shift: " +
                                                Number(context.parsed.y).toFixed(1) +
                                                " percentage points"
                                            );

                                        },

                                        afterBody: function (items) {

                                            var item =
                                                data[items[0].dataIndex];

                                            return [
                                                "Comparisons: " + item.records,
                                                "Participants: " + item.participants,
                                                "Median shift: " +
                                                    Number(item.median_shift).toFixed(1) +
                                                    " percentage points"
                                            ];

                                        }

                                    }

                                }

                            }

                        },

                        scales: {

                            y: {

                                beginAtZero: true,

                                grid: {

                                    color: "rgba(148, 163, 184, 0.2)"

                                },

                                ticks: {

                                    color: "#667085",

                                    font: {

                                        size: 11

                                    }

                                },

                                title: {

                                    display: true,

                                    text:
                                        "Average Study Pattern Shift"

                                }

                            },

                            x: {

                                grid: {

                                    display: false

                                },

                                ticks: {

                                    color: "#475467",

                                    font: {

                                        size: 11,

                                        weight: "600"

                                    }

                                },

                                title: {

                                    display: true,

                                    text:
                                        "Study Week"

                                }

                            }

                        }

                    }

                }
            );

        }

        catch (error) {

            var status =
                document.getElementById(
                    "studyShiftChartStatus"
                );

            if (status) {

                status.textContent =
                    "Study-shift data could not be loaded. Please check the dataset and refresh the page.";

                status.classList.add("is-error");

            }

            console.error(
                "Study shift chart error:",
                error
            );

        }

    }

    async function loadStudyMethodsChart() {

        var canvas = document.getElementById("studyMethodsChart");
        var status = document.getElementById("studyMethodsChartStatus");

        if (!canvas || !status) {
            return;
        }

        try {
            var response = await fetch("/api/component3/study-methods");
            if (!response.ok) {
                throw new Error("Study-method API returned " + response.status);
            }

            var rows = await response.json();
            if (!Array.isArray(rows) || rows.length === 0) {
                status.textContent = "Study-method data is not yet available.";
                return;
            }

            var weeks = Array.from(new Set(rows.map(function (row) {
                return Number(row.study_week);
            }))).sort(function (a, b) { return a - b; });
            var methods = Array.from(new Set(rows.map(function (row) {
                return row.study_method;
            }))).sort();
            var validRecordsByWeek = {};
            rows.forEach(function (row) {
                validRecordsByWeek[String(row.study_week)] =
                    Number(row.valid_records) || 0;
            });
            var palette = ["#2563eb", "#7c3aed", "#0f766e", "#d97706", "#db2777", "#4f46e5", "#64748b", "#0891b2", "#65a30d"];
            var datasets = methods.map(function (method, index) {
                return {
                    label: method,
                    data: weeks.map(function (week) {
                        var item = rows.find(function (row) {
                            return Number(row.study_week) === week && row.study_method === method;
                        });
                        return item ? item.percentage : 0;
                    }),
                    records: weeks.map(function (week) {
                        var item = rows.find(function (row) {
                            return Number(row.study_week) === week && row.study_method === method;
                        });
                        return item ? item.records : 0;
                    }),
                    validRecords: weeks.map(function (week) {
                        var item = rows.find(function (row) {
                            return Number(row.study_week) === week && row.study_method === method;
                        });
                        return item ? item.valid_records : 0;
                    }),
                    backgroundColor: palette[index % palette.length],
                    borderRadius: 4,
                    maxBarThickness: 46
                };
            });

            new Chart(canvas, {
                type: "bar",
                data: {
                    labels: weeks.map(function (week) { return "Week " + week; }),
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { intersect: false, mode: "index" },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    var item = rows.find(function (row) {
                                        return Number(row.study_week) === weeks[context.dataIndex]
                                            && row.study_method === context.dataset.label;
                                    });
                                    return context.dataset.label + ": "
                                        + Number(context.parsed.y).toFixed(1) + "% ("
                                        + (item ? item.records : 0) + " of "
                                        + (validRecordsByWeek[
                                            String(weeks[context.dataIndex])
                                        ] || 0) + " records)";
                                }
                            }
                        }
                    },
                    scales: {
                        x: { grid: { display: false }, title: { display: true, text: "Study Week" } },
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            title: { display: true, text: "Share of records reporting method (%)" }
                        }
                    }
                }
            });

            status.textContent = "Method percentages use valid method responses and may sum above 100% because participants may report multiple methods.";
        } catch (error) {
            status.textContent = "Study-method data could not be loaded. Please refresh the page.";
            status.classList.add("is-error");
            console.error("Study-method chart error:", error);
        }
    }

    async function loadProductivityChart() {

        var canvas = document.getElementById("productivityChart");
        var status = document.getElementById("productivityChartStatus");

        if (!canvas || !status) {
            return;
        }

        try {
            var response = await fetch("/api/component3/productivity");
            if (!response.ok) {
                throw new Error("Productivity API returned " + response.status);
            }

            var rows = await response.json();
            if (!Array.isArray(rows) || rows.length === 0) {
                status.textContent = "Perceived-productivity data is not yet available.";
                return;
            }

            var weeks = Array.from(new Set(rows.map(function (row) {
                return Number(row.study_week);
            }))).sort(function (a, b) { return a - b; });
            var ratings = [
                "Very unproductive",
                "Somewhat unproductive",
                "Neutral",
                "Somewhat productive",
                "Very productive"
            ];
            var palette = ["#b42318", "#f79009", "#98a2b3", "#12b76a", "#039855"];
            var datasets = ratings.map(function (rating, index) {
                return {
                    label: rating,
                    data: weeks.map(function (week) {
                        var item = rows.find(function (row) {
                            return Number(row.study_week) === week
                                && row.perceived_productivity === rating;
                        });
                        return item ? item.percentage : 0;
                    }),
                    records: weeks.map(function (week) {
                        var item = rows.find(function (row) {
                            return Number(row.study_week) === week
                                && row.perceived_productivity === rating;
                        });
                        return item ? item.records : 0;
                    }),
                    backgroundColor: palette[index]
                };
            });

            new Chart(canvas, {
                type: "bar",
                data: {
                    labels: weeks.map(function (week) { return "Week " + week; }),
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { intersect: false, mode: "index" },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return context.dataset.label + ": "
                                        + Number(context.parsed.y).toFixed(1) + "% ("
                                        + context.dataset.records[context.dataIndex] + " records)";
                                }
                            }
                        }
                    },
                    scales: {
                        x: { stacked: true, grid: { display: false }, title: { display: true, text: "Study Week" } },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            max: 100,
                            ticks: { callback: function (value) { return value + "%"; } },
                            title: { display: true, text: "Share of valid weekly ratings" }
                        }
                    }
                }
            });

            status.textContent = "Each week is normalised to the respondents who provided a productivity rating.";
        } catch (error) {
            status.textContent = "Perceived-productivity data could not be loaded. Please refresh the page.";
            status.classList.add("is-error");
            console.error("Productivity chart error:", error);
        }
    }

    async function loadPromptDetailChart() {

        var canvas = document.getElementById("promptDetailChart");
        var status = document.getElementById("promptDetailChartStatus");

        if (!canvas || !status) {
            return;
        }

        try {
            var response = await fetch("/api/component3/prompt-detail");
            if (!response.ok) {
                throw new Error("Prompt-detail API returned " + response.status);
            }

            var rows = await response.json();
            if (!Array.isArray(rows) || rows.length === 0) {
                status.textContent = "Prompt-detail ratings are not yet available.";
                return;
            }

            new Chart(canvas, {
                type: "line",
                data: {
                    labels: rows.map(function (row) { return "Week " + row.study_week; }),
                    datasets: [{
                        label: "Average self-reported detail rating",
                        data: rows.map(function (row) { return row.average_prompt_detail; }),
                        borderColor: "#0f766e",
                        backgroundColor: "rgba(15, 118, 110, 0.12)",
                        pointBackgroundColor: "#0f766e",
                        pointRadius: 5,
                        borderWidth: 3,
                        tension: 0.25,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                afterBody: function (items) {
                                    var row = rows[items[0].dataIndex];
                                    return ["Rated records: " + row.records, "Participants: " + row.participants];
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            min: 1,
                            max: 5,
                            ticks: { stepSize: 1 },
                            title: { display: true, text: "Self-reported rating (1–5)" }
                        },
                        x: { grid: { display: false }, title: { display: true, text: "Study Week" } }
                    }
                }
            });

            status.textContent = "Rating sample sizes are shown in tooltips; this is a self-report measure, not a text-derived complexity score.";
        } catch (error) {
            status.textContent = "Prompt-detail data could not be loaded. Please refresh the page.";
            status.classList.add("is-error");
            console.error("Prompt-detail chart error:", error);
        }
    }

    async function loadWorkloadComparisonCharts() {

        var status = document.getElementById("workloadComparisonChartStatus");
        var studyHoursCanvas = document.getElementById("workloadStudyHoursChart");
        var promptCountCanvas = document.getElementById("workloadPromptCountChart");

        if (!status || !studyHoursCanvas || !promptCountCanvas) {
            return;
        }

        try {
            var response = await fetch("/api/component3/workload-comparison");
            if (!response.ok) {
                throw new Error("Workload comparison API returned " + response.status);
            }

            var rows = await response.json();
            if (!Array.isArray(rows) || rows.length === 0) {
                status.textContent = "Workload comparisons are not yet available for the collected weekly records.";
                return;
            }

            var pressures = ["Low", "Moderate", "High"];
            var weeks = Array.from(new Set(rows.map(function (row) {
                return Number(row.study_week);
            }))).sort(function (a, b) { return a - b; });
            var palette = ["#2563eb", "#7c3aed", "#0f766e", "#d97706", "#db2777", "#4f46e5"];

            function drawMetric(canvas, field, title) {
                var datasets = weeks.map(function (week, index) {
                    return {
                        label: "Week " + week,
                        data: pressures.map(function (pressure) {
                            var item = rows.find(function (row) {
                                return Number(row.study_week) === week
                                    && row.workload_pressure === pressure;
                            });
                            return item && item[field] !== null ? item[field] : null;
                        }),
                        backgroundColor: palette[index % palette.length],
                        borderColor: palette[index % palette.length],
                        borderWidth: 2,
                        borderRadius: 4,
                        maxBarThickness: 48
                    };
                });

                new Chart(canvas, {
                    type: "bar",
                    data: { labels: pressures, datasets: datasets },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: { intersect: false, mode: "index" },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    afterBody: function (items) {
                                        var week = weeks[items[0].datasetIndex];
                                        var row = rows.find(function (item) {
                                            return Number(item.study_week) === week
                                                && item.workload_pressure === pressures[items[0].dataIndex];
                                        });
                                        return row
                                            ? [
                                                "Records with this measure: " +
                                                    (field === "average_prompts"
                                                        ? row.prompt_records
                                                        : row.ai_hours_records),
                                                "Participants in workload group: " + row.participants
                                            ]
                                            : [];
                                    }
                                }
                            }
                        },
                        scales: {
                            x: { grid: { display: false }, title: { display: true, text: "Self-reported workload / deadline pressure" } },
                            y: { beginAtZero: true, title: { display: true, text: title } }
                        }
                    }
                });
            }

            drawMetric(studyHoursCanvas, "average_ai_study_hours", "Average hours per record");
            drawMetric(promptCountCanvas, "average_prompts", "Average prompts per record");
            status.textContent = "Hover for sample sizes. Categories may have different participants and group sizes; interpret as descriptive, not causal.";
        } catch (error) {
            status.textContent = "Workload comparisons could not be loaded. Please refresh the page.";
            status.classList.add("is-error");
            console.error("Workload comparison chart error:", error);
        }
    }


    /* ============================================================
       PART 10 — PAGE INITIALIZATION
       ============================================================ */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            /*
             * Load only data provided by the backend.
             * JavaScript does not calculate research findings.
             */

            loadComponent3Summary();

            loadStudyShareChart();

            loadPromptFrequencyChart();

            loadPromptPurposeChart();

            loadStudyShiftChart();

            loadStudyMethodsChart();

            loadProductivityChart();

            loadPromptDetailChart();

            loadWorkloadComparisonCharts();

            renderUserDashboard();

        }
    );

})();