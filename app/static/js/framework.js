/**
 * app/static/js/framework.js
 *
 * Client-side behaviour for the Framework Integration page (/framework/).
 *
 * Responsibilities:
 * - Fetches /api/framework/status and renders readiness badges.
 * - Does NOT combine component scores.
 * - Does NOT compute an overall risk level or framework-level prediction.
 * - Does NOT show fake analytical findings.
 *
 * Psychometric Learning Analytics Framework – J26-DS-310
 * Prototype stage – data collection in progress.
 */

"use strict";

(function () {

  /**
   * Fetch framework status from the API and update readiness indicators.
   * Only updates visual badge states; does not aggregate scores.
   */
  function loadFrameworkStatus() {
    const container = document.getElementById("frameworkReadinessContainer");
    if (!container) return;

    fetch("/api/framework/status")
      .then(function (response) {
        if (!response.ok) throw new Error("Status API error: " + response.status);
        return response.json();
      })
      .then(function (data) {
        renderReadinessIndicators(data, container);
      })
      .catch(function (err) {
        // Non-blocking: readiness state is already shown server-side.
        console.warn("[framework.js] Could not load framework status:", err.message);
      });
  }

  /**
   * Render per-component readiness indicators based on API response.
   * Does NOT compute or display a combined / aggregated score.
   *
   * @param {Object} data   – Response from /api/framework/status
   * @param {Element} root  – Container element to update
   */
  function renderReadinessIndicators(data, root) {
    var components = (data && Array.isArray(data.components)) ? data.components : [];

    components.forEach(function (comp) {
      var el = root.querySelector('[data-component-id="' + comp.id + '"]');
      if (!el) return;

      var analysisPill = el.querySelector(".js-analysis-pill");
      var prototypePill = el.querySelector(".js-prototype-pill");

      if (prototypePill) {
        prototypePill.textContent = comp.prototype_ready ? "Ready" : "Pending";
        prototypePill.className =
          "readiness-pill " +
          (comp.prototype_ready ? "readiness-pill--ready" : "readiness-pill--pending");
      }

      if (analysisPill) {
        analysisPill.textContent = comp.analysis_ready ? "Available" : "Pending data";
        analysisPill.className =
          "readiness-pill " +
          (comp.analysis_ready ? "readiness-pill--ready" : "readiness-pill--pending");
      }
    });
  }

  // Run when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadFrameworkStatus);
  } else {
    loadFrameworkStatus();
  }

})();
