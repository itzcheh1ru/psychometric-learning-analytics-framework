/**
 * main.js – Minimal JavaScript for the
 * Psychometric Learning Analytics Framework (J26-DS-310).
 *
 * Prototype scaffold: no analytical logic is present here.
 * Chart.js and analytical interactions will be added in later features.
 */

"use strict";

document.addEventListener("DOMContentLoaded", function () {
    /* Highlight the active navigation link based on current path */
    const currentPath = window.location.pathname;
    document.querySelectorAll(".nav-link").forEach(function (link) {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("nav-link--active");
        }
    });
});
