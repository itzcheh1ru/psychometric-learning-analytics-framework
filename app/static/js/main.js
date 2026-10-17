/**
 * main.js – Minimal JavaScript for the
 * Psychometric Learning Analytics Framework (J26-DS-310).
 *
 * Feature 002: sidebar mobile toggle, footer year.
 * No analytical logic is present here.
 */

"use strict";

document.addEventListener("DOMContentLoaded", function () {

    /* ------------------------------------------------------------------
       Sidebar mobile toggle
    ------------------------------------------------------------------ */
    var toggle   = document.getElementById("sidebarToggle");
    var sidebar  = document.getElementById("appSidebar");
    var overlay  = document.getElementById("sidebarOverlay");

    function openSidebar() {
        sidebar.classList.add("sidebar--open");
        overlay.classList.add("overlay--visible");
        overlay.removeAttribute("aria-hidden");
        toggle.setAttribute("aria-expanded", "true");
        sidebar.focus();
    }

    function closeSidebar() {
        sidebar.classList.remove("sidebar--open");
        overlay.classList.remove("overlay--visible");
        overlay.setAttribute("aria-hidden", "true");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
    }

    if (toggle && sidebar && overlay) {
        toggle.addEventListener("click", function () {
            var isOpen = sidebar.classList.contains("sidebar--open");
            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });

        /* Close on overlay click */
        overlay.addEventListener("click", closeSidebar);

        /* Close on Escape key */
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && sidebar.classList.contains("sidebar--open")) {
                closeSidebar();
            }
        });

        /* Close sidebar when a nav link is clicked (mobile UX) */
        sidebar.querySelectorAll(".sidebar-link").forEach(function (link) {
            link.addEventListener("click", function () {
                if (window.innerWidth <= 720) {
                    closeSidebar();
                }
            });
        });
    }

    /* ------------------------------------------------------------------
       Footer: current year
    ------------------------------------------------------------------ */
    var yearEl = document.getElementById("footerYear");
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }

});
