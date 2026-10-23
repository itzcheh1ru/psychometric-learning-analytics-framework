/**
 * component2.js – Client-side script for Component 2:
 * Algorithmic Trust & Verification Analysis (CFA & SEM).
 *
 * Responsibilities:
 * - Handle file selection, drag-and-drop, and upload validation
 * - Execute CFA and SEM estimation pipelines via AJAX
 * - Render 10 structured analysis sections dynamically
 * - Render interactive Plotly diagrams
 * - Handle report export (CSV and JSON) and APA narrative copying
 * - Preserve research integrity: show awaiting-data state when unanalyzed
 */

"use strict";

(function () {
    var STATUS_URL = "/api/component2/status";
    var SPECIFICATION_URL = "/api/component2/specification";
    var ANALYZE_URL = "/api/component2/analyze";
    var LOAD_DEMO_URL = "/api/component2/load-demo";
    var EXPORT_URL = "/api/component2/export";

    // Global in-memory cache for export
    var currentAnalysisData = null;

    document.addEventListener("DOMContentLoaded", function () {
        initStatusCheck();
        initUploadForm();
        initDemoButton();
        initResetButton();
        initExportButtons();
    });

    /**
     * Check pipeline status from the backend service.
     */
    function initStatusCheck() {
        fetch(STATUS_URL)
            .then(function (res) {
                return res.ok ? res.json() : null;
            })
            .then(function (data) {
                if (data) {
                    var statusEl = document.getElementById("pipelineStatusBadge");
                    if (statusEl && !data.sem_results_available) {
                        statusEl.setAttribute("title", "SEM Status: Pipeline Ready for Survey Data");
                    }
                }
            })
            .catch(function (err) {
                console.warn("Component 2 status query note:", err.message);
            });
    }

    /**
     * Initialize file upload and drag-and-drop.
     */
    function initUploadForm() {
        var uploadForm = document.getElementById("datasetUploadForm");
        var fileInput = document.getElementById("datasetFile");
        var dropZone = document.getElementById("dropZone");

        if (!uploadForm || !fileInput || !dropZone) return;

        // Drag and drop events
        ["dragenter", "dragover"].forEach(function (eventName) {
            dropZone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add("drop-zone--dragover");
            });
        });

        ["dragleave", "drop"].forEach(function (eventName) {
            dropZone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove("drop-zone--dragover");
            });
        });

        dropZone.addEventListener("drop", function (e) {
            if (e.dataTransfer && e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                updateDropZoneLabel(fileInput.files[0].name);
            }
        });

        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                updateDropZoneLabel(fileInput.files[0].name);
            }
        });

        uploadForm.addEventListener("submit", function (e) {
            e.preventDefault();
            var file = fileInput.files[0];
            if (!file) {
                showFeedback("error", "Please select a survey dataset (.csv or .xlsx) before proceeding.");
                return;
            }

            var formData = new FormData();
            formData.append("file", file);

            showFeedback("loading", "Estimating CFA measurement model and SEM structural equations... Please wait.");
            disableButtons(true);

            fetch(ANALYZE_URL, {
                method: "POST",
                body: formData,
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        if (!response.ok) {
                            throw new Error(data.error || "Statistical estimation failed.");
                        }
                        return data;
                    });
                })
                .then(function (data) {
                    currentAnalysisData = data;
                    showFeedback("success", "Analysis completed: " + data.message);
                    renderDashboard(data);
                    disableButtons(false);
                })
                .catch(function (error) {
                    showFeedback("error", error.message);
                    disableButtons(false);
                });
        });
    }

    /**
     * Initialize Load Demonstration Dataset button.
     */
    function initDemoButton() {
        var btnLoadDemo = document.getElementById("btnLoadDemo");
        if (!btnLoadDemo) return;

        btnLoadDemo.addEventListener("click", function () {
            showFeedback("loading", "Loading synthetic benchmark dataset (N=250) and estimating CFA/SEM models...");
            disableButtons(true);

            fetch(LOAD_DEMO_URL, {
                method: "POST",
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        if (!response.ok) {
                            throw new Error(data.error || "Failed to load demonstration dataset.");
                        }
                        return data;
                    });
                })
                .then(function (data) {
                    currentAnalysisData = data;
                    showFeedback("success", data.message);
                    renderDashboard(data);
                    disableButtons(false);
                })
                .catch(function (error) {
                    showFeedback("error", error.message);
                    disableButtons(false);
                });
        });
    }

    /**
     * Reset analysis state.
     */
    function initResetButton() {
        var btnReset = document.getElementById("btnResetData");
        if (!btnReset) return;

        btnReset.addEventListener("click", function () {
            currentAnalysisData = null;
            document.getElementById("resultsDashboardContainer").style.display = "none";
            document.getElementById("emptyAnalyticsContainer").style.display = "block";
            document.getElementById("uploadResult").style.display = "none";
            btnReset.style.display = "none";
            updateDropZoneLabel("");
            var fileInput = document.getElementById("datasetFile");
            if (fileInput) fileInput.value = "";
        });
    }

    /**
     * Initialize export actions.
     */
    function initExportButtons() {
        var btnCsv = document.getElementById("btnDownloadCsv");
        var btnJson = document.getElementById("btnDownloadJson");
        var btnCopyApa = document.getElementById("btnCopyApa");

        if (btnCsv) {
            btnCsv.addEventListener("click", function () {
                if (!currentAnalysisData || !currentAnalysisData.csv_report) {
                    alert("No analysis report is available to export.");
                    return;
                }
                downloadFile(currentAnalysisData.csv_report, "Component2_SEM_Analysis_Report.csv", "text/csv");
            });
        }

        if (btnJson) {
            btnJson.addEventListener("click", function () {
                if (!currentAnalysisData) {
                    alert("No analysis data is available to export.");
                    return;
                }
                var jsonStr = JSON.stringify(currentAnalysisData, null, 2);
                downloadFile(jsonStr, "Component2_SEM_Analysis_Package.json", "application/json");
            });
        }

        if (btnCopyApa) {
            btnCopyApa.addEventListener("click", function () {
                if (!currentAnalysisData || !currentAnalysisData.apa_summary) return;
                navigator.clipboard.writeText(currentAnalysisData.apa_summary)
                    .then(function () {
                        btnCopyApa.textContent = "Copied!";
                        setTimeout(function () {
                            btnCopyApa.textContent = "Copy Narrative";
                        }, 2000);
                    })
                    .catch(function () {
                        alert("Could not copy to clipboard. Please copy manually.");
                    });
            });
        }
    }

    /**
     * Render the complete results dashboard.
     */
    function renderDashboard(data) {
        // Toggle containers
        document.getElementById("emptyAnalyticsContainer").style.display = "none";
        document.getElementById("resultsDashboardContainer").style.display = "block";
        document.getElementById("btnResetData").style.display = "inline-flex";

        // Show/hide demonstration banner
        var demoBanner = document.getElementById("demoDataBanner");
        if (demoBanner) {
            demoBanner.style.display = data.is_demo ? "flex" : "none";
        }

        // 1. Render Descriptives
        renderDescriptivesTable(data.dataset_summary.descriptive_statistics);

        // 2. Render CFA Loadings
        renderLoadingsTable(data.cfa_results.loadings);

        // 3. Render Validity & Reliability
        renderValidityTables(data.cfa_results);

        // 4. Render SEM Structural Paths & R2
        renderSemTables(data.sem_results);

        // 5. Render Hypotheses Testing Summary
        renderHypothesesTable(data.sem_results.hypotheses_evaluation);

        // 6. Render Model Fit Grid
        renderFitGrid(data.sem_results.model_fit);

        // 7. Render Plotly Charts
        renderPlotlyCharts(data.charts);

        // 8. Render APA Summary
        renderApaSummary(data.apa_summary);
    }

    /**
     * Render Section 3: Descriptive Statistics.
     */
    function renderDescriptivesTable(descriptives) {
        var tbody = document.getElementById("descriptivesTableBody");
        if (!tbody || !descriptives || !descriptives.items) return;
        tbody.innerHTML = "";

        var items = descriptives.items;
        Object.keys(items).forEach(function (code) {
            var s = items[code];
            var tr = document.createElement("tr");

            var constructCode = code.startsWith("T") ? "AT" :
                (code.startsWith("PU") ? "PU" :
                (code.startsWith("V") ? "VB" :
                (code.startsWith("AD") ? "AD" :
                (code.startsWith("LC") ? "LC" : "-"))));

            tr.innerHTML =
                "<td><code>" + code + "</code></td>" +
                "<td><strong>" + constructCode + "</strong></td>" +
                "<td>" + s.mean.toFixed(2) + "</td>" +
                "<td>" + s.sd.toFixed(2) + "</td>" +
                "<td>" + s.median.toFixed(1) + "</td>" +
                "<td>" + s.min + "</td>" +
                "<td>" + s.max + "</td>" +
                "<td>" + s.skewness.toFixed(2) + "</td>" +
                "<td>" + s.kurtosis.toFixed(2) + "</td>" +
                "<td>" + s.n + "</td>";
            tbody.appendChild(tr);
        });
    }

    /**
     * Render Section 4: CFA Factor Loadings.
     */
    function renderLoadingsTable(loadingsByConstruct) {
        var tbody = document.getElementById("loadingsTableBody");
        if (!tbody || !loadingsByConstruct) return;
        tbody.innerHTML = "";

        Object.keys(loadingsByConstruct).forEach(function (cCode) {
            var items = loadingsByConstruct[cCode];
            items.forEach(function (item) {
                var tr = document.createElement("tr");
                var badgeClass = item.passed ? "badge--success" : (item.std_loading >= 0.50 ? "badge--warning" : "badge--danger");

                tr.innerHTML =
                    "<td><strong>" + item.construct + "</strong></td>" +
                    "<td><code>" + item.indicator + "</code></td>" +
                    "<td style='max-width:280px;font-size:0.78rem;'>" + item.wording + "</td>" +
                    "<td><strong>" + item.std_loading.toFixed(3) + "</strong></td>" +
                    "<td>" + item.unstandardized.toFixed(3) + "</td>" +
                    "<td>" + item.se + "</td>" +
                    "<td>" + item.z_value + "</td>" +
                    "<td>" + item.p_value + "</td>" +
                    "<td>" + item.r2_communality.toFixed(3) + "</td>" +
                    "<td><span class='badge " + badgeClass + "'>" + item.status + "</span></td>";
                tbody.appendChild(tr);
            });
        });
    }

    /**
     * Render Section 5: Reliability & Validity.
     */
    function renderValidityTables(cfaResults) {
        // 1. Reliability & Convergent Validity
        var valTbody = document.getElementById("validityTableBody");
        if (valTbody && cfaResults.construct_validity) {
            valTbody.innerHTML = "";
            Object.keys(cfaResults.construct_validity).forEach(function (cCode) {
                var v = cfaResults.construct_validity[cCode];
                var tr = document.createElement("tr");

                var alphaBadge = v.alpha_passed ? "badge--success" : "badge--danger";
                var crBadge = v.cr_passed ? "badge--success" : "badge--danger";
                var aveBadge = v.ave_passed ? "badge--success" : "badge--danger";

                tr.innerHTML =
                    "<td><strong>" + v.construct + "</strong></td>" +
                    "<td>" + v.name + "</td>" +
                    "<td>" + v.items_count + "</td>" +
                    "<td><span class='badge " + alphaBadge + "'>" + v.cronbach_alpha.toFixed(3) + "</span></td>" +
                    "<td><span class='badge " + crBadge + "'>" + v.composite_reliability.toFixed(3) + "</span></td>" +
                    "<td><span class='badge " + aveBadge + "'>" + v.ave.toFixed(3) + "</span></td>" +
                    "<td>" + v.sqrt_ave.toFixed(3) + "</td>" +
                    "<td><span class='badge " + (v.convergent_validity === "Established" ? "badge--success" : "badge--warning") + "'>" + v.convergent_validity + "</span></td>";
                valTbody.appendChild(tr);
            });
        }

        // 2. Fornell-Larcker Matrix
        var fornellHead = document.getElementById("fornellTableHead");
        var fornellBody = document.getElementById("fornellTableBody");
        if (fornellHead && fornellBody && cfaResults.fornell_larcker && cfaResults.fornell_larcker.length > 0) {
            var fRows = cfaResults.fornell_larcker;
            var constructCodes = Object.keys(cfaResults.construct_validity || {});

            var headHtml = "<tr><th>Construct</th><th>Name</th>";
            constructCodes.forEach(function (c) {
                headHtml += "<th>" + c + "</th>";
            });
            headHtml += "</tr>";
            fornellHead.innerHTML = headHtml;

            fornellBody.innerHTML = "";
            fRows.forEach(function (row) {
                var trHtml = "<tr><td><strong>" + row.construct + "</strong></td><td>" + row.name + "</td>";
                constructCodes.forEach(function (c) {
                    var val = row[c] || "-";
                    trHtml += "<td>" + val + "</td>";
                });
                trHtml += "</tr>";
                fornellBody.innerHTML += trHtml;
            });
        }

        // 3. HTMT Matrix
        var htmtHead = document.getElementById("htmtTableHead");
        var htmtBody = document.getElementById("htmtTableBody");
        if (htmtHead && htmtBody && cfaResults.htmt_matrix && cfaResults.htmt_matrix.length > 0) {
            var hRows = cfaResults.htmt_matrix;
            var cCodes = Object.keys(cfaResults.construct_validity || {});

            var hHeadHtml = "<tr><th>Construct</th><th>Name</th>";
            cCodes.forEach(function (c) {
                hHeadHtml += "<th>" + c + "</th>";
            });
            hHeadHtml += "</tr>";
            htmtHead.innerHTML = hHeadHtml;

            htmtBody.innerHTML = "";
            hRows.forEach(function (row) {
                var trHtml = "<tr><td><strong>" + row.construct + "</strong></td><td>" + row.name + "</td>";
                cCodes.forEach(function (c) {
                    var val = row[c];
                    if (val === "-" || val === undefined) {
                        trHtml += "<td>-</td>";
                    } else {
                        var fVal = parseFloat(val);
                        var badge = fVal < 0.85 ? "badge--success" : (fVal < 0.90 ? "badge--warning" : "badge--danger");
                        trHtml += "<td><span class='badge " + badge + "'>" + fVal.toFixed(3) + "</span></td>";
                    }
                });
                trHtml += "</tr>";
                htmtBody.innerHTML += trHtml;
            });
        }
    }

    /**
     * Render Section 6: SEM Structural Paths, R2, and Mediation.
     */
    function renderSemTables(semResults) {
        // 1. R2 Badges
        var r2Container = document.getElementById("r2Container");
        if (r2Container && semResults.variance_explained_r2) {
            r2Container.innerHTML = "";
            var r2 = semResults.variance_explained_r2;
            Object.keys(r2).forEach(function (code) {
                var val = r2[code];
                var card = document.createElement("div");
                card.className = "r2-card";
                card.innerHTML =
                    "<span class='r2-card__label'>Variance Explained (" + code + " R&sup2;):</span>" +
                    "<span class='r2-card__val'>" + (val * 100).toFixed(1) + "%</span>";
                r2Container.appendChild(card);
            });
        }

        // 2. Direct Paths Table
        var dBody = document.getElementById("directPathsTableBody");
        if (dBody && semResults.direct_paths) {
            dBody.innerHTML = "";
            semResults.direct_paths.forEach(function (p) {
                var tr = document.createElement("tr");
                var badge = p.significant ? "badge--success" : "badge--neutral";

                tr.innerHTML =
                    "<td><strong>" + p.predictor + "</strong></td>" +
                    "<td><strong>" + p.outcome + "</strong></td>" +
                    "<td><code>" + p.path + "</code></td>" +
                    "<td><strong>" + p.std_beta.toFixed(3) + "</strong></td>" +
                    "<td>" + p.unstandardized.toFixed(3) + "</td>" +
                    "<td>" + p.se + "</td>" +
                    "<td>" + p.z_value + "</td>" +
                    "<td>" + p.p_value + "</td>" +
                    "<td><span class='badge " + badge + "'>" + (p.significant ? "Significant (p < 0.05)" : "Not Significant") + "</span></td>";
                dBody.appendChild(tr);
            });
        }

        // 3. Mediation Table
        var mBody = document.getElementById("mediationTableBody");
        if (mBody && semResults.indirect_effects) {
            mBody.innerHTML = "";
            semResults.indirect_effects.forEach(function (m) {
                var tr = document.createElement("tr");
                var badge = m.bootstrap_significant ? "badge--success" : "badge--neutral";

                tr.innerHTML =
                    "<td><code>" + m.hypothesis_id + "</code></td>" +
                    "<td><strong>" + m.path + "</strong></td>" +
                    "<td><strong>" + m.indirect_beta.toFixed(3) + "</strong></td>" +
                    "<td>" + m.sobel_z.toFixed(2) + "</td>" +
                    "<td>" + m.sobel_p + "</td>" +
                    "<td><code>" + m.bootstrap_ci_95 + "</code></td>" +
                    "<td>" + m.direct_beta.toFixed(3) + "</td>" +
                    "<td>" + m.total_effect.toFixed(3) + "</td>" +
                    "<td><span class='badge " + badge + "'>" + m.mediation_status + "</span></td>";
                mBody.appendChild(tr);
            });
        }
    }

    /**
     * Render Section 7: Hypotheses Testing Summary.
     */
    function renderHypothesesTable(hypotheses) {
        var tbody = document.getElementById("hypothesesTableBody");
        if (!tbody || !hypotheses) return;
        tbody.innerHTML = "";

        hypotheses.forEach(function (h) {
            var tr = document.createElement("tr");
            var badge = h.supported ? "badge--success" : "badge--danger";

            tr.innerHTML =
                "<td><code>" + h.id + "</code></td>" +
                "<td><strong>" + h.path + "</strong></td>" +
                "<td>" + h.type + "</td>" +
                "<td>" + h.expected_direction + "</td>" +
                "<td><strong>" + h.estimate.toFixed(3) + "</strong></td>" +
                "<td>" + h.p_value + "</td>" +
                "<td>" + (h.supported ? "Yes" : "No / Inconclusive") + "</td>" +
                "<td><span class='badge " + badge + "'>" + h.status_label + "</span></td>";
            tbody.appendChild(tr);
        });
    }

    /**
     * Render Section 8: Model Fit Grid.
     */
    function renderFitGrid(fit) {
        var grid = document.getElementById("fitGridContainer");
        if (!grid || !fit) return;
        grid.innerHTML = "";

        var metrics = [
            { name: "Chi-Square (χ²)", val: fit.chi2.toFixed(2), bench: "p = " + fit.chi2_p, status: fit.chi2_df_status },
            { name: "Degrees of Freedom (df)", val: fit.df, bench: "-", status: "-" },
            { name: "χ²/df Ratio", val: fit.chi2_df_ratio.toFixed(2), bench: "≤ 3.0 (good)", status: fit.chi2_df_status },
            { name: "Comparative Fit Index (CFI)", val: fit.cfi.toFixed(3), bench: "≥ 0.95 (good)", status: fit.cfi_status },
            { name: "Tucker-Lewis Index (TLI)", val: fit.tli.toFixed(3), bench: "≥ 0.95 (good)", status: fit.tli_status },
            { name: "RMSEA", val: fit.rmsea.toFixed(3), bench: "≤ 0.05 (good)", status: fit.rmsea_status },
            { name: "SRMR", val: fit.srmr.toFixed(3), bench: "≤ 0.08 (good)", status: fit.srmr_status },
            { name: "Overall Model Fit", val: fit.overall_fit, bench: "Hu & Bentler (1999)", status: fit.overall_fit + " Fit" },
        ];

        metrics.forEach(function (m) {
            var card = document.createElement("div");
            card.className = "fit-card";
            var badgeClass = m.status.indexOf("Good") !== -1 ? "badge--success" : (m.status.indexOf("Acceptable") !== -1 ? "badge--warning" : "badge--neutral");

            card.innerHTML =
                "<span class='fit-card__title'>" + m.name + "</span>" +
                "<span class='fit-card__val'>" + m.val + "</span>" +
                "<span class='fit-card__bench'>Criteria: " + m.bench + "</span>" +
                (m.status !== "-" ? "<span class='badge fit-card__status " + badgeClass + "'>" + m.status + "</span>" : "");
            grid.appendChild(card);
        });
    }

    /**
     * Render Section 9: Plotly Interactive Visualizations.
     */
    function renderPlotlyCharts(charts) {
        if (typeof Plotly === "undefined" || !charts) {
            console.warn("Plotly library not loaded or no chart configurations found.");
            return;
        }

        var config = { responsive: true, displayModeBar: false };

        if (charts.path_diagram && document.getElementById("plotlyPathDiagram")) {
            Plotly.newPlot("plotlyPathDiagram", charts.path_diagram.data, charts.path_diagram.layout, config);
        }

        if (charts.loadings && document.getElementById("plotlyLoadings")) {
            Plotly.newPlot("plotlyLoadings", charts.loadings.data, charts.loadings.layout, config);
        }

        if (charts.htmt && document.getElementById("plotlyHtmt")) {
            Plotly.newPlot("plotlyHtmt", charts.htmt.data, charts.htmt.layout, config);
        }

        if (charts.effects_chart && document.getElementById("plotlyEffects")) {
            Plotly.newPlot("plotlyEffects", charts.effects_chart.data, charts.effects_chart.layout, config);
        }
    }

    /**
     * Render Section 10: APA Summary Text.
     */
    function renderApaSummary(apaText) {
        var container = document.getElementById("apaReportContainer");
        if (!container || !apaText) return;

        // Simple markdown line formatter
        var formatted = apaText.replace(/### (.*)/g, "<h4>$1</h4>")
            .replace(/#### (.*)/g, "<h5>$1</h5>")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/\n\n/g, "<p>")
            .replace(/\n- (.*)/g, "<li>$1</li>");

        container.innerHTML = formatted;
    }

    /**
     * Helper to show alert feedback banner.
     */
    function showFeedback(type, message) {
        var el = document.getElementById("uploadResult");
        if (!el) return;
        el.className = "upload-feedback upload-feedback--" + type;
        el.textContent = message;
        el.style.display = "block";
    }

    /**
     * Helper to disable/enable action buttons during execution.
     */
    function disableButtons(disabled) {
        var btnUpload = document.getElementById("btnValidateUpload");
        var btnDemo = document.getElementById("btnLoadDemo");
        if (btnUpload) btnUpload.disabled = disabled;
        if (btnDemo) btnDemo.disabled = disabled;
    }

    /**
     * Update dropzone label text.
     */
    function updateDropZoneLabel(fileName) {
        var label = document.querySelector(".drop-zone__label");
        if (!label) return;
        if (fileName) {
            label.innerHTML = "Selected file: <strong>" + fileName + "</strong>";
        } else {
            label.innerHTML = "<strong>Choose a file</strong> or drag and drop here";
        }
    }

    /**
     * File download trigger.
     */
    function downloadFile(content, fileName, contentType) {
        var blob = new Blob([content], { type: contentType });
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
})();
