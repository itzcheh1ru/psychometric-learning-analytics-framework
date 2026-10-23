"""
app/services/sem_analysis/report_service.py

Exportable research report and academic APA summary service for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).
"""

from typing import Any, Dict, List
import io
import csv


def generate_results_csv(
    cfa_results: Dict[str, Any],
    sem_results: Dict[str, Any],
    descriptives: Dict[str, Any],
) -> str:
    """
    Format complete psychometric analytical results into an RFC 4180 CSV string
    containing: Descriptives, Loadings, Reliability/Validity, Hypotheses, and Fit Indices.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Header & Metadata
    writer.writerow(["# COMPONENT 2: ALGORITHMIC TRUST & VERIFICATION ANALYSIS (CFA & SEM)"])
    writer.writerow(["# Research Project: J26-DS-310 | Psychometric Learning Analytics Framework"])
    writer.writerow([])

    # 2. Descriptive Statistics
    writer.writerow(["--- SECTION 1: DESCRIPTIVE STATISTICS (SURVEY INDICATORS) ---"])
    writer.writerow(["Item", "Mean", "Std Dev", "Median", "Min", "Max", "Skewness", "Kurtosis", "N"])
    item_stats = descriptives.get("items", {})
    for item, s in item_stats.items():
        writer.writerow([
            item, s.get("mean"), s.get("sd"), s.get("median"),
            s.get("min"), s.get("max"), s.get("skewness"), s.get("kurtosis"), s.get("n")
        ])
    writer.writerow([])

    # 3. CFA Factor Loadings
    writer.writerow(["--- SECTION 2: CONFIRMATORY FACTOR ANALYSIS (CFA) FACTOR LOADINGS ---"])
    writer.writerow(["Construct", "Indicator", "Standardized Loading (λ)", "Unstandardized", "SE", "z-value", "p-value", "Communality (R²)", "Evaluation"])
    loadings_by_c = cfa_results.get("loadings", {})
    for c_code, items in loadings_by_c.items():
        for it in items:
            writer.writerow([
                c_code, it.get("indicator"), it.get("std_loading"), it.get("unstandardized"),
                it.get("se"), it.get("z_value"), it.get("p_value"), it.get("r2_communality"), it.get("status")
            ])
    writer.writerow([])

    # 4. Construct Reliability & Convergent Validity
    writer.writerow(["--- SECTION 3: CONSTRUCT RELIABILITY & CONVERGENT VALIDITY ---"])
    writer.writerow(["Construct", "Name", "Items", "Cronbach Alpha (α ≥ 0.70)", "Composite Reliability (CR ≥ 0.70)", "AVE (AVE ≥ 0.50)", "sqrt(AVE)", "Status"])
    validity = cfa_results.get("construct_validity", {})
    for c_code, v in validity.items():
        writer.writerow([
            c_code, v.get("name"), v.get("items_count"), v.get("cronbach_alpha"),
            v.get("composite_reliability"), v.get("ave"), v.get("sqrt_ave"), v.get("convergent_validity")
        ])
    writer.writerow([])

    # 5. SEM Structural Path Model & Hypothesis Testing
    writer.writerow(["--- SECTION 4: STRUCTURAL MODEL PATH ESTIMATES & HYPOTHESIS TESTING ---"])
    writer.writerow(["Hypothesis", "Path", "Type", "Estimate (β)", "SE", "z-value", "p-value", "Expected Direction", "Status"])
    hypotheses = sem_results.get("hypotheses_evaluation", [])
    for h in hypotheses:
        writer.writerow([
            h.get("id"), h.get("path"), h.get("type"), h.get("estimate"),
            h.get("se"), h.get("z_value"), h.get("p_value"), h.get("expected_direction"), h.get("status_label")
        ])
    writer.writerow([])

    # 6. Mediation Analysis (Indirect Effects)
    writer.writerow(["--- SECTION 5: MEDIATION ANALYSIS VIA VERIFICATION BEHAVIOUR ---"])
    writer.writerow(["Hypothesis", "Mediated Path", "Indirect Effect (β)", "Sobel z", "Sobel p", "95% Bootstrap CI", "Mediation Type"])
    indirects = sem_results.get("indirect_effects", [])
    for ind in indirects:
        writer.writerow([
            ind.get("hypothesis_id"), ind.get("path"), ind.get("indirect_beta"),
            ind.get("sobel_z"), ind.get("sobel_p"), ind.get("bootstrap_ci_95"), ind.get("mediation_status")
        ])
    writer.writerow([])

    # 7. Model Fit Summary
    writer.writerow(["--- SECTION 6: MODEL FIT EVALUATION ---"])
    writer.writerow(["Metric", "Threshold Criteria", "Observed Value", "Status Evaluation"])
    fit = sem_results.get("model_fit", {})
    writer.writerow(["Chi-Square (χ²)", "-", fit.get("chi2"), f"p = {fit.get('chi2_p')}"])
    writer.writerow(["Degrees of Freedom (df)", "-", fit.get("df"), "-"])
    writer.writerow(["χ²/df Ratio", "≤ 3.0 (good), ≤ 5.0 (acceptable)", fit.get("chi2_df_ratio"), fit.get("chi2_df_status")])
    writer.writerow(["Comparative Fit Index (CFI)", "≥ 0.90 (acceptable), ≥ 0.95 (good)", fit.get("cfi"), fit.get("cfi_status")])
    writer.writerow(["Tucker-Lewis Index (TLI)", "≥ 0.90 (acceptable), ≥ 0.95 (good)", fit.get("tli"), fit.get("tli_status")])
    writer.writerow(["RMSEA", "≤ 0.08 (acceptable), ≤ 0.05 (good)", fit.get("rmsea"), fit.get("rmsea_status")])
    writer.writerow(["SRMR", "≤ 0.08 (good)", fit.get("srmr"), fit.get("srmr_status")])

    return output.getvalue()


def generate_apa_summary(
    cfa_results: Dict[str, Any],
    sem_results: Dict[str, Any],
    sample_size: int,
) -> str:
    """Generate an APA-formatted academic text report for research dissemination."""
    fit = sem_results.get("model_fit", {})
    hypotheses = sem_results.get("hypotheses_evaluation", [])
    validity = cfa_results.get("construct_validity", {})

    lines = [
        "### Empirical Findings Summary (APA 7th Edition Style)",
        "",
        f"A Confirmatory Factor Analysis (CFA) and Structural Equation Model (SEM) were estimated using a sample of N = {sample_size} undergraduate students. "
        f"Evaluation of goodness-of-fit demonstrated {fit.get('overall_fit', 'acceptable').lower()} model fit to the empirical data: "
        f"χ²({fit.get('df')}) = {fit.get('chi2')}, p {fit.get('chi2_p')}, χ²/df = {fit.get('chi2_df_ratio')}, "
        f"CFI = {fit.get('cfi')}, TLI = {fit.get('tli')}, RMSEA = {fit.get('rmsea')}, and SRMR = {fit.get('srmr')}.",
        "",
        "#### Measurement Model Evaluation",
        "Construct reliability was established across all latent dimensions: ",
    ]

    for c_code, v in validity.items():
        lines.append(f"- **{v['name']} ({c_code})**: Cronbach's α = {v['cronbach_alpha']}, Composite Reliability (CR) = {v['composite_reliability']}, and AVE = {v['ave']}.")

    lines.extend([
        "",
        "#### Structural Path & Hypothesis Testing",
        "Examination of hypothesized structural pathways revealed the following outcomes:",
    ])

    for h in hypotheses:
        lines.append(f"- **{h['id']} ({h['path']})**: β = {h['estimate']}, z = {h['z_value']}, p = {h['p_value']} — *{h['status_label']}*.")

    return "\n".join(lines)
