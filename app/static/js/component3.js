/**
 * component3.js – Client-side logic for Component 3:
 * Longitudinal AI-Assisted Study Pattern Analytics prototype.
 *
 * Responsibilities:
 *   - Client-side validation for weekly study record inputs
 *   - POST submission to /api/component3/validate-weekly-record
 *   - Display validation outcome and sanitised record preview
 *   - Form reset
 *   - Load Component 3 analytical summary
 *   - Load AI-assisted vs independent study-share chart
 *   - Load weekly prompt-frequency chart
 *   - Load study-pattern shift chart
 *
 * CRITICAL RESEARCH INTEGRITY:
 *   - No longitudinal trend calculation in JavaScript
 *   - No AI Study Share calculation as research findings
 *   - No study-pattern classification or mock histories
 *   - All analytical values are obtained from the backend APIs
 */

"use strict";

(function () {

    /* ============================================================
       PART 1 — WEEKLY RECORD VALIDATION
       ============================================================ */

    var VALIDATE_URL = "/api/component3/validate-weekly-record";


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
            id: "academic_period",
            label: "Academic Period",
            errorId: "period_error"
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

        academic_period:
            "Academic Period / Context",

        learning_activity:
            "Main Learning Activity",

        prompt_count:
            "Academic GenAI Prompt Count",

        prompt_purpose:
            "Primary Prompt Purpose"

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

        return {

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

            academic_period:
                document.getElementById(
                    "academic_period"
                ).value.trim(),

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


    function showSuccess(data) {

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


        previewSection.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

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


                if (submitBtn) {

                    submitBtn.disabled =
                        true;

                    submitBtn.textContent =
                        "Validating…";

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

                            showSuccess(
                                result.data
                            );

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
                                "Validate Weekly Record";

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
                        ? "Available"
                        : "Baseline Only";

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
            var countsByWeek = {};

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

                    if (!countsByWeek[weekKey]) {

                        countsByWeek[weekKey] = {};

                    }

                    countsByWeek[weekKey][category] =
                        Number(row.count) || 0;

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

                                    return (
                                        countsByWeek[String(week)][category] || 0
                                    );

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

                                        return (
                                            context.dataset.label +
                                            ": " +
                                            context.parsed.y +
                                            " records"
                                        );

                                    }

                                }

                            }

                        },

                        scales: {

                            x: {

                                stacked: true,

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

                                stacked: true,

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

                                    text: "Weekly records",

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
                " from the processed dataset.";

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

                        return item.total_prompts;

                    }
                );


            new Chart(
                canvas,
                {

                    type: "bar",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Total Academic Prompts",

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
                                        "Number of Prompts"

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

            console.error(
                "Study shift chart error:",
                error
            );

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

        }
    );

})();