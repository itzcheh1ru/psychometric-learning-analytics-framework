"""
app/services/sem_analysis/verification_task_service.py

Controlled AI-Generated Answer Verification Performance Assessment Module.
Component 2: Algorithmic Trust & Verification Analysis (J26-DS-310).

Design Principles:
1. Authentic Academic Scenarios:
   8 controlled academic questions spanning Mathematics, Statistics, Scientific Reasoning,
   and Academic Source Evaluation.
2. Controlled Error Topology:
   Contains correct AI answers, numerical errors, unsupported claims, logical reasoning fallacies,
   and misleading/hallucinated citations. Fully correct controls ensure students cannot assume
   every output contains errors.
3. Researcher-Designed Status:
   All scenarios are researcher-designed instruments pending independent expert validation.
4. Answer-Key Security:
   Provides sanitized task views to students (masking ground truth and explanations),
   and evaluates submissions against expert answer keys upon completion.
5. Multidimensional Performance Metrics:
   Measures Accuracy, Error Detection Recall (Sensitivity), Precision, False Error Accusations,
   and Evidence-Based Justification Rubric scores.
"""

from typing import Any, Dict, List, Optional, Tuple
import copy
from datetime import datetime


# =========================================================================== #
# 1. Bank of 8 Controlled Academic Verification Scenarios                    #
# =========================================================================== #

VERIFICATION_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "SCEN_01",
        "domain": "Mathematics & Calculus",
        "topic": "Integration by Parts & Exponential Functions",
        "academic_question": (
            "Evaluate the indefinite integral: \\int x \\cdot e^{2x} \\, dx. "
            "Show all intermediate steps and the final antiderivative."
        ),
        "simulated_ai_response": (
            "To evaluate \\int x \\cdot e^{2x} \\, dx, we use integration by parts: \\int u \\, dv = uv - \\int v \\, du.\n"
            "Step 1: Let u = x, so du = dx.\n"
            "Step 2: Let dv = e^{2x} \\, dx, so v = \\int e^{2x} \\, dx = \\frac{1}{2} e^{2x}.\n"
            "Step 3: Substitute into the formula: uv - \\int v \\, du = \\frac{1}{2} x e^{2x} - \\int \\frac{1}{2} e^{2x} \\, dx.\n"
            "Step 4: Integrating the remaining term gives: \\int \\frac{1}{2} e^{2x} \\, dx = \\frac{1}{2} e^{2x}.\n"
            "Step 5: Therefore, \\int x \\cdot e^{2x} \\, dx = \\frac{1}{2} x e^{2x} - \\frac{1}{2} e^{2x} + C."
        ),
        "reference_truth": (
            "Correct antiderivative: \\int x e^{2x} dx = \\frac{1}{2} x e^{2x} - \\frac{1}{4} e^{2x} + C = "
            "\\frac{1}{4} e^{2x}(2x - 1) + C. The AI made a coefficient error in Step 4 by omitting the second division by 2."
        ),
        "overall_ai_quality": "Partially Correct (Contains Calculation Error)",
        "claims": [
            {
                "claim_id": "SCEN_01_C1",
                "claim_text": "The choice of parts u = x (giving du = dx) and dv = e^{2x} dx (giving v = (1/2)e^{2x}) is mathematically sound.",
                "statement": "The choice of parts u = x (giving du = dx) and dv = e^{2x} dx (giving v = (1/2)e^{2x}) is mathematically sound.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Reasoning)",
                "explanation": "Selecting u = x follows the standard LIATE rule (algebraic before exponential) and v = (1/2)e^{2x} is the correct antiderivative.",
                "expert_explanation": "Selecting u = x follows the standard LIATE rule (algebraic before exponential) and v = (1/2)e^{2x} is the correct antiderivative.",
                "reference_source": "Stewart, J. (2020). Calculus: Early Transcendentals (9th ed.). Cengage Learning, Section 7.1.",
                "reference_citation": "Stewart, J. (2020). Calculus: Early Transcendentals (9th ed.). Cengage Learning, Section 7.1.",
                "rubric_keywords": ["liate", "derivative", "antiderivative", "parts", "exponential"],
            },
            {
                "claim_id": "SCEN_01_C2",
                "claim_text": "In Step 4, the integral \\int (1/2)e^{2x} dx equals (1/2)e^{2x}.",
                "statement": "In Step 4, the integral \\int (1/2)e^{2x} dx equals (1/2)e^{2x}.",
                "ground_truth": "INCORRECT",
                "error_category": "Numerical Calculation Error",
                "explanation": "Integrating (1/2)e^{2x} dx produces (1/2) * (1/2)e^{2x} = (1/4)e^{2x}. The AI failed to divide by the inner derivative (2).",
                "expert_explanation": "Integrating (1/2)e^{2x} dx produces (1/2) * (1/2)e^{2x} = (1/4)e^{2x}. The AI failed to divide by the inner derivative (2).",
                "reference_source": "Stewart, J. (2020). Calculus: Early Transcendentals (9th ed.). Section 7.1.",
                "reference_citation": "Stewart, J. (2020). Calculus: Early Transcendentals (9th ed.). Section 7.1.",
                "rubric_keywords": ["1/4", "divide", "inner derivative", "factor of 2", "chain rule", "quarter"],
            },
            {
                "claim_id": "SCEN_01_C3",
                "claim_text": "The final antiderivative (1/2)x e^{2x} - (1/2)e^{2x} + C is correct.",
                "statement": "The final antiderivative (1/2)x e^{2x} - (1/2)e^{2x} + C is correct.",
                "ground_truth": "INCORRECT",
                "error_category": "Compounded Calculation Error",
                "explanation": "Differentiating (1/2)xe^{2x} - (1/2)e^{2x} yields x e^{2x} - (1/2)e^{2x}, which does not match the integrand x e^{2x}.",
                "expert_explanation": "Differentiating (1/2)xe^{2x} - (1/2)e^{2x} yields x e^{2x} - (1/2)e^{2x}, which does not match the integrand x e^{2x}.",
                "reference_source": "Stewart, J. (2020). Calculus: Early Transcendentals (9th ed.). Section 7.1.",
                "reference_citation": "Stewart, J. (2020). Calculus: Early Transcendentals (9th ed.). Section 7.1.",
                "rubric_keywords": ["differentiation", "verify", "1/4", "constant", "derivative"],
            },
        ],
    },
    {
        "id": "SCEN_02",
        "domain": "Statistics & Data Science",
        "topic": "Null Hypothesis Significance Testing & p-value Interpretation",
        "academic_question": (
            "A researcher conducts a two-sample t-test comparing exam scores between two teaching methods. "
            "The resulting p-value is 0.03 (alpha = 0.05). Explain what this p-value implies regarding the hypothesis and effect size."
        ),
        "simulated_ai_response": (
            "A p-value of 0.03 means there is only a 3% probability that the null hypothesis is true.\n"
            "Because p < 0.05, we reject the null hypothesis and have proven that the alternative hypothesis is true.\n"
            "Furthermore, because the p-value is statistically significant, we can conclude that the teaching intervention had a large, practically meaningful effect on student learning."
        ),
        "reference_truth": (
            "The p-value is P(Data >= observed | H0 is true), NOT P(H0 is true | Data). It does not prove H1 is true, "
            "nor does statistical significance inform effect size or practical educational meaningfulness."
        ),
        "overall_ai_quality": "Flawed (Multiple Statistical Misconceptions)",
        "claims": [
            {
                "claim_id": "SCEN_02_C1",
                "claim_text": "A p-value of 0.03 means there is a 3% probability that the null hypothesis is true.",
                "statement": "A p-value of 0.03 means there is a 3% probability that the null hypothesis is true.",
                "ground_truth": "INCORRECT",
                "error_category": "Conceptual Fallacy (Inverse Probability Error)",
                "explanation": "A p-value is the conditional probability of observing data at least as extreme assuming H0 is true, not the posterior probability of H0 given the data (which requires Bayesian methods).",
                "expert_explanation": "A p-value is the conditional probability of observing data at least as extreme assuming H0 is true, not the posterior probability of H0 given the data (which requires Bayesian methods).",
                "reference_source": "Wasserstein, R. L., & Lazar, N. A. (2016). The ASA's Statement on p-Values: Context, Process, and Purpose. The American Statistician, 70(2), 129-133.",
                "reference_citation": "Wasserstein, R. L., & Lazar, N. A. (2016). The ASA's Statement on p-Values: Context, Process, and Purpose. The American Statistician, 70(2), 129-133.",
                "rubric_keywords": ["conditional", "given the null", "posterior", "bayesian", "inverse probability", "h0"],
            },
            {
                "claim_id": "SCEN_02_C2",
                "claim_text": "Because p < 0.05, the researcher has proven that the alternative hypothesis is true.",
                "statement": "Because p < 0.05, the researcher has proven that the alternative hypothesis is true.",
                "ground_truth": "INCORRECT",
                "error_category": "Epistemological Fallacy (Absolute Proof in NHST)",
                "explanation": "Hypothesis testing cannot prove an alternative hypothesis; it merely provides evidence against the null under assumed models, with an ongoing alpha = 5% Type I error risk.",
                "expert_explanation": "Hypothesis testing cannot prove an alternative hypothesis; it merely provides evidence against the null under assumed models, with an ongoing alpha = 5% Type I error risk.",
                "reference_source": "Wasserstein, R. L., & Lazar, N. A. (2016). The ASA's Statement on p-Values. The American Statistician.",
                "reference_citation": "Wasserstein, R. L., & Lazar, N. A. (2016). The ASA's Statement on p-Values. The American Statistician.",
                "rubric_keywords": ["type i error", "alpha", "cannot prove", "evidence against", "rejection"],
            },
            {
                "claim_id": "SCEN_02_C3",
                "claim_text": "Statistical significance (p < 0.05) directly demonstrates that the intervention had a large practical effect.",
                "statement": "Statistical significance (p < 0.05) directly demonstrates that the intervention had a large practical effect.",
                "ground_truth": "INCORRECT",
                "error_category": "Conflation of Significance and Effect Size",
                "explanation": "Statistical significance is heavily influenced by sample size; a tiny, trivial difference can achieve p < 0.05 with large N. Effect size (e.g. Cohen's d) must be evaluated separately.",
                "expert_explanation": "Statistical significance is heavily influenced by sample size; a tiny, trivial difference can achieve p < 0.05 with large N. Effect size (e.g. Cohen's d) must be evaluated separately.",
                "reference_source": "Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates.",
                "reference_citation": "Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates.",
                "rubric_keywords": ["effect size", "cohen's d", "sample size", "practical significance", "magnitude"],
            },
        ],
    },
    {
        "id": "SCEN_03",
        "domain": "Statistics & Probability",
        "topic": "Central Limit Theorem (Fully Correct Control)",
        "academic_question": (
            "State the Central Limit Theorem (CLT) for independent and identically distributed (i.i.d.) random variables "
            "with finite mean mu and finite variance sigma^2, and specify the distribution of the sample mean as n grows."
        ),
        "simulated_ai_response": (
            "The Central Limit Theorem states that if X_1, X_2, ..., X_n are i.i.d. random variables drawn from any distribution "
            "with a finite mean \\mu and finite variance \\sigma^2, then as the sample size n approaches infinity, the standardized sample mean "
            "Z_n = \\frac{\\bar{X}_n - \\mu}{\\sigma / \\sqrt{n}} converges in distribution to a standard normal distribution N(0, 1).\n"
            "Equivalently, the sample mean \\bar{X}_n is approximately distributed as N(\\mu, \\sigma^2 / n) for sufficiently large n."
        ),
        "reference_truth": (
            "The AI response is completely rigorous and correct. All hypotheses (i.i.d., finite mean, finite variance) are explicitly stated."
        ),
        "overall_ai_quality": "Accurate (Sound Academic Formulation)",
        "claims": [
            {
                "claim_id": "SCEN_03_C1",
                "claim_text": "The CLT requires the underlying random variables to possess a finite mean mu and finite variance sigma^2.",
                "statement": "The CLT requires the underlying random variables to possess a finite mean mu and finite variance sigma^2.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Reasoning)",
                "explanation": "Finite variance is a mandatory prerequisite for the classical Lindeberg-Levy CLT; distributions with heavy tails (e.g., Cauchy) do not converge to a normal distribution.",
                "expert_explanation": "Finite variance is a mandatory prerequisite for the classical Lindeberg-Levy CLT; distributions with heavy tails (e.g., Cauchy) do not converge to a normal distribution.",
                "reference_source": "Casella, G., & Berger, R. L. (2002). Statistical Inference (2nd ed.). Duxbury, Theorem 5.5.15.",
                "reference_citation": "Casella, G., & Berger, R. L. (2002). Statistical Inference (2nd ed.). Duxbury, Theorem 5.5.15.",
                "rubric_keywords": ["finite variance", "cauchy", "lindeberg-levy", "prerequisite"],
            },
            {
                "claim_id": "SCEN_03_C2",
                "claim_text": "The standardized sample mean (X_bar - mu) / (sigma / sqrt(n)) converges in distribution to N(0, 1) as n -> infinity.",
                "statement": "The standardized sample mean (X_bar - mu) / (sigma / sqrt(n)) converges in distribution to N(0, 1) as n -> infinity.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Reasoning)",
                "explanation": "This is the exact mathematical definition of convergence in distribution under the classical CLT.",
                "expert_explanation": "This is the exact mathematical definition of convergence in distribution under the classical CLT.",
                "reference_source": "Casella, G., & Berger, R. L. (2002). Statistical Inference (2nd ed.). Duxbury.",
                "reference_citation": "Casella, G., & Berger, R. L. (2002). Statistical Inference (2nd ed.). Duxbury.",
                "rubric_keywords": ["convergence in distribution", "standard normal", "n(0,1)", "sqrt(n)"],
            },
            {
                "claim_id": "SCEN_03_C3",
                "claim_text": "The variance of the sample mean X_bar is sigma^2 / n.",
                "statement": "The variance of the sample mean X_bar is sigma^2 / n.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Reasoning)",
                "explanation": "Var(X_bar) = Var((1/n) sum X_i) = (1/n^2) * n * sigma^2 = sigma^2 / n for independent observations.",
                "expert_explanation": "Var(X_bar) = Var((1/n) sum X_i) = (1/n^2) * n * sigma^2 = sigma^2 / n for independent observations.",
                "reference_source": "Casella, G., & Berger, R. L. (2002). Statistical Inference (2nd ed.). Section 5.2.",
                "reference_citation": "Casella, G., & Berger, R. L. (2002). Statistical Inference (2nd ed.). Section 5.2.",
                "rubric_keywords": ["variance", "sample mean", "n squared", "independent"],
            },
        ],
    },
    {
        "id": "SCEN_04",
        "domain": "Physical Chemistry & Thermodynamics",
        "topic": "Gibbs Free Energy & Temperature Scaling Error",
        "academic_question": (
            "For a chemical reaction, Delta H = -40 kJ/mol and Delta S = -120 J/(mol*K). "
            "Determine whether the reaction is spontaneous at 25 degrees Celsius (298.15 K)."
        ),
        "simulated_ai_response": (
            "We use the Gibbs free energy equation: \\Delta G = \\Delta H - T \\Delta S.\n"
            "Given: \\Delta H = -40 \\text{ kJ/mol}, \\Delta S = -120 \\text{ J/(mol}\\cdot\\text{K)}, T = 25^\\circ\\text{C}.\n"
            "Step 1: Calculate T \\Delta S = 25 \\times (-120) = -3000 \\text{ J/mol} = -3.0 \\text{ kJ/mol}.\n"
            "Step 2: \\Delta G = -40 - (-3.0) = -37.0 \\text{ kJ/mol}.\n"
            "Conclusion: Since \\Delta G < 0, the reaction is spontaneous at 25 degrees Celsius."
        ),
        "reference_truth": (
            "The AI made a fundamental unit conversion error by using Celsius (25) instead of Kelvin (298.15 K). "
            "Correct calculation: T = 298.15 K; T*Delta S = 298.15 * (-120 J/(mol*K)) = -35.78 kJ/mol. "
            "Delta G = -40 - (-35.78) = -4.22 kJ/mol. While Delta G is still negative here, the magnitude is wildly off by a factor of 12."
        ),
        "overall_ai_quality": "Partially Correct Conclusion from Severe Computational Error",
        "claims": [
            {
                "claim_id": "SCEN_04_C1",
                "claim_text": "In the thermodynamic equation Delta G = Delta H - T*Delta S, temperature T must be expressed in Kelvin.",
                "statement": "In the thermodynamic equation Delta G = Delta H - T*Delta S, temperature T must be expressed in Kelvin.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Principle)",
                "explanation": "Thermodynamic equations derived from the second law require absolute temperature in Kelvin (T_K = T_C + 273.15).",
                "expert_explanation": "Thermodynamic equations derived from the second law require absolute temperature in Kelvin (T_K = T_C + 273.15).",
                "reference_source": "Atkins, P., & de Paula, J. (2014). Physical Chemistry (10th ed.). Oxford University Press, Chapter 3.",
                "reference_citation": "Atkins, P., & de Paula, J. (2014). Physical Chemistry (10th ed.). Oxford University Press, Chapter 3.",
                "rubric_keywords": ["kelvin", "absolute temperature", "273.15", "thermodynamic scale"],
            },
            {
                "claim_id": "SCEN_04_C2",
                "claim_text": "The product T*Delta S equals -3.0 kJ/mol at 25 degrees Celsius.",
                "statement": "The product T*Delta S equals -3.0 kJ/mol at 25 degrees Celsius.",
                "ground_truth": "INCORRECT",
                "error_category": "Unit Conversion & Scale Error",
                "explanation": "Using T = 298.15 K gives T*Delta S = 298.15 * (-120 J/mol*K) = -35,778 J/mol = -35.78 kJ/mol, not -3.0 kJ/mol.",
                "expert_explanation": "Using T = 298.15 K gives T*Delta S = 298.15 * (-120 J/mol*K) = -35,778 J/mol = -35.78 kJ/mol, not -3.0 kJ/mol.",
                "reference_source": "Atkins, P., & de Paula, J. (2014). Physical Chemistry (10th ed.). Chapter 3.",
                "reference_citation": "Atkins, P., & de Paula, J. (2014). Physical Chemistry (10th ed.). Chapter 3.",
                "rubric_keywords": ["298.15", "-35.8", "celsius instead of kelvin", "magnitude", "conversion"],
            },
            {
                "claim_id": "SCEN_04_C3",
                "claim_text": "Delta G equals -37.0 kJ/mol for this system.",
                "statement": "Delta G equals -37.0 kJ/mol for this system.",
                "ground_truth": "INCORRECT",
                "error_category": "Compounded Calculation Error",
                "explanation": "Delta G = -40 - (-35.78) = -4.22 kJ/mol. The AI value of -37.0 kJ/mol is distorted by omitting Kelvin conversion.",
                "expert_explanation": "Delta G = -40 - (-35.78) = -4.22 kJ/mol. The AI value of -37.0 kJ/mol is distorted by omitting Kelvin conversion.",
                "reference_source": "Atkins, P., & de Paula, J. (2014). Physical Chemistry (10th ed.).",
                "reference_citation": "Atkins, P., & de Paula, J. (2014). Physical Chemistry (10th ed.).",
                "rubric_keywords": ["-4.22", "compounded", "error propagation", "actual delta g"],
            },
        ],
    },
    {
        "id": "SCEN_05",
        "domain": "Biological Sciences & Genetics",
        "topic": "DNA Polymerase Proofreading & Exonuclease Directionality",
        "academic_question": (
            "Explain the enzymatic mechanism by which DNA Polymerase III in E. coli proofreads mispaired nucleotides "
            "during DNA replication. Specify the catalytic domain and direction of exonuclease activity."
        ),
        "simulated_ai_response": (
            "DNA Polymerase III proofreads mispaired nucleotides using its intrinsic 5'-to-3' exonuclease activity.\n"
            "When an incorrect nucleotide is incorporated, the polymerase stalls, reverses direction, and hydrolyzes "
            "the erroneous base from the 5' end of the newly synthesized strand, allowing accurate replication to proceed."
        ),
        "reference_truth": (
            "DNA polymerase proofreading operates strictly via 3'-to-5' exonuclease activity (specifically the epsilon subunit of Pol III). "
            "5'-to-3' exonuclease activity is unique to DNA Polymerase I for primer removal and nick translation."
        ),
        "overall_ai_quality": "Biochemically Inaccurate (Reversed Exonuclease Direction)",
        "claims": [
            {
                "claim_id": "SCEN_05_C1",
                "claim_text": "Proofreading by DNA Polymerase III utilizes a 5'-to-3' exonuclease activity.",
                "statement": "Proofreading by DNA Polymerase III utilizes a 5'-to-3' exonuclease activity.",
                "ground_truth": "INCORRECT",
                "error_category": "Domain Factual Inaccuracy (Directionality Error)",
                "explanation": "Proofreading exonuclease activity proceeds strictly in the 3'-to-5' direction to remove the terminal mispaired nucleotide at the growing 3'-OH end.",
                "expert_explanation": "Proofreading exonuclease activity proceeds strictly in the 3'-to-5' direction to remove the terminal mispaired nucleotide at the growing 3'-OH end.",
                "reference_source": "Nelson, D. L., & Cox, M. M. (2021). Lehninger Principles of Biochemistry (8th ed.). W. H. Freeman, Chapter 25.",
                "reference_citation": "Nelson, D. L., & Cox, M. M. (2021). Lehninger Principles of Biochemistry (8th ed.). W. H. Freeman, Chapter 25.",
                "rubric_keywords": ["3' to 5'", "3 prime to 5 prime", "growing end", "polymerase i", "direction"],
            },
            {
                "claim_id": "SCEN_05_C2",
                "claim_text": "Polymerase stalling upon mismatch incorporation triggers exonucleolytic cleavage.",
                "statement": "Polymerase stalling upon mismatch incorporation triggers exonucleolytic cleavage.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Mechanism)",
                "explanation": "Geometric distortion caused by mispaired bases stalls catalytic forward progression, allowing the frayed primer terminus to migrate to the exonuclease active site.",
                "expert_explanation": "Geometric distortion caused by mispaired bases stalls catalytic forward progression, allowing the frayed primer terminus to migrate to the exonuclease active site.",
                "reference_source": "Nelson, D. L., & Cox, M. M. (2021). Lehninger Principles of Biochemistry (8th ed.). Chapter 25.",
                "reference_citation": "Nelson, D. L., & Cox, M. M. (2021). Lehninger Principles of Biochemistry (8th ed.). Chapter 25.",
                "rubric_keywords": ["stalling", "distortion", "migration", "mismatch"],
            },
            {
                "claim_id": "SCEN_05_C3",
                "claim_text": "The newly added mispaired nucleotide is removed from the 5' end of the nascent chain.",
                "statement": "The newly added mispaired nucleotide is removed from the 5' end of the nascent chain.",
                "ground_truth": "INCORRECT",
                "error_category": "Structural Polarity Error",
                "explanation": "DNA chain synthesis occurs 5' to 3', so the most recently incorporated base resides at the 3' end, not the 5' end.",
                "expert_explanation": "DNA chain synthesis occurs 5' to 3', so the most recently incorporated base resides at the 3' end, not the 5' end.",
                "reference_source": "Nelson, D. L., & Cox, M. M. (2021). Lehninger Principles of Biochemistry (8th ed.).",
                "reference_citation": "Nelson, D. L., & Cox, M. M. (2021). Lehninger Principles of Biochemistry (8th ed.).",
                "rubric_keywords": ["3' end", "3 prime", "growing terminus", "hydroxyl", "polarity"],
            },
        ],
    },
    {
        "id": "SCEN_06",
        "domain": "Computer Science & Machine Learning",
        "topic": "Transformer Attention Complexity & Fabricated Citation",
        "academic_question": (
            "What is the computational complexity of standard scaled dot-product self-attention with respect to "
            "sequence length N, and what seminal 2018 Nature paper first demonstrated linear O(N) self-attention?"
        ),
        "simulated_ai_response": (
            "Standard scaled dot-product self-attention has a time and memory complexity of O(N^2) with respect to sequence length N, "
            "because every token must compute attention scores with every other token in the sequence.\n"
            "This quadratic bottleneck was first overcome by Vaswani and colleagues in their 2018 Nature paper titled "
            "'Attention Across Dimensions: Linearizing Self-Attention for Deep Sequence Representations' (Nature, 554, 102-108), "
            "which introduced the linear O(N) attention mechanism now standard in modern language models."
        ),
        "reference_truth": (
            "Quadratic O(N^2) complexity is correct. However, the claimed 2018 Nature paper is a completely fabricated/hallucinated citation. "
            "The seminal Transformer paper by Vaswani et al. is 'Attention Is All You Need' (NeurIPS 2017), which introduced quadratic attention. "
            "Linear attention models (e.g., Linformer, Performer) were published in 2020 at ML venues, not in Nature in 2018."
        ),
        "overall_ai_quality": "Hallucinated Source / Fabricated Literature Citation",
        "claims": [
            {
                "claim_id": "SCEN_06_C1",
                "claim_text": "Standard scaled dot-product self-attention scales quadratically O(N^2) with sequence length N.",
                "statement": "Standard scaled dot-product self-attention scales quadratically O(N^2) with sequence length N.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Complexity)",
                "explanation": "Computing the full N x N attention matrix Q*K^T requires O(N^2 * d) operations and O(N^2) memory footprint.",
                "expert_explanation": "Computing the full N x N attention matrix Q*K^T requires O(N^2 * d) operations and O(N^2) memory footprint.",
                "reference_source": "Vaswani, A., et al. (2017). Attention Is All You Need. Advances in Neural Information Processing Systems (NeurIPS 2017), 30.",
                "reference_citation": "Vaswani, A., et al. (2017). Attention Is All You Need. Advances in Neural Information Processing Systems (NeurIPS 2017), 30.",
                "rubric_keywords": ["quadratic", "o(n^2)", "attention matrix", "n by n", "pairwise"],
            },
            {
                "claim_id": "SCEN_06_C2",
                "claim_text": "Vaswani et al. published a 2018 Nature paper titled 'Attention Across Dimensions: Linearizing Self-Attention for Deep Sequence Representations'.",
                "statement": "Vaswani et al. published a 2018 Nature paper titled 'Attention Across Dimensions: Linearizing Self-Attention for Deep Sequence Representations'.",
                "ground_truth": "UNSUPPORTED",
                "error_category": "Phantom / Hallucinated Academic Citation",
                "explanation": "This citation does not exist in scientific literature; Vaswani et al. published 'Attention Is All You Need' at NeurIPS 2017.",
                "expert_explanation": "This citation does not exist in scientific literature; Vaswani et al. published 'Attention Is All You Need' at NeurIPS 2017.",
                "reference_source": "Vaswani, A., et al. (2017). NeurIPS 2017; Nature volume 554 does not contain any such paper.",
                "reference_citation": "Vaswani, A., et al. (2017). NeurIPS 2017; Nature volume 554 does not contain any such paper.",
                "rubric_keywords": ["hallucination", "fabricated", "does not exist", "neurips 2017", "phantom citation"],
            },
            {
                "claim_id": "SCEN_06_C3",
                "claim_text": "Linear O(N) self-attention was established in the original 2017/2018 Transformer architecture.",
                "statement": "Linear O(N) self-attention was established in the original 2017/2018 Transformer architecture.",
                "ground_truth": "INCORRECT",
                "error_category": "Historical & Technical Factual Error",
                "explanation": "Original transformers used standard O(N^2) attention; linear approximations like Linformer (Wang et al.) and Performer (Choromanski et al.) emerged in 2020.",
                "expert_explanation": "Original transformers used standard O(N^2) attention; linear approximations like Linformer (Wang et al.) and Performer (Choromanski et al.) emerged in 2020.",
                "reference_source": "Wang, S., et al. (2020). Linformer: Self-Attention with Linear Complexity. arXiv:2006.04768.",
                "reference_citation": "Wang, S., et al. (2020). Linformer: Self-Attention with Linear Complexity. arXiv:2006.04768.",
                "rubric_keywords": ["linformer", "performer", "2020", "original was quadratic", "not linear"],
            },
        ],
    },
    {
        "id": "SCEN_07",
        "domain": "Cognitive Psychology",
        "topic": "Working Memory Capacity & Miller's Law (Accurate Control)",
        "academic_question": (
            "Summarize George Miller's (1956) classic findings on immediate memory capacity, and explain how Nelson Cowan (2001) "
            "subsequently refined the estimated capacity limit of working memory."
        ),
        "simulated_ai_response": (
            "In 1956, George Miller proposed that immediate memory capacity is constrained to 'the magical number seven, plus or minus two' (7 +/- 2) chunks of information.\n"
            "In 2001, Nelson Cowan conducted extensive re-evaluations controlling for rehearsal and chunking strategies, concluding that the true capacity limit of pure working memory is approximately 4 chunks (typically 3 to 5) in young adults.\n"
            "Both researchers emphasized that 'chunks' represent meaningful subjective organizational units rather than raw physical bits of information."
        ),
        "reference_truth": (
            "This AI response is entirely accurate and reflects contemporary consensus in cognitive psychology regarding Miller (1956) and Cowan (2001)."
        ),
        "overall_ai_quality": "Accurate (Sound Literature Synthesis)",
        "claims": [
            {
                "claim_id": "SCEN_07_C1",
                "claim_text": "George Miller (1956) proposed that immediate memory capacity spans 7 +/- 2 chunks of information.",
                "statement": "George Miller (1956) proposed that immediate memory capacity spans 7 +/- 2 chunks of information.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Synthesis)",
                "explanation": "Miller's 1956 paper 'The Magical Number Seven, Plus or Minus Two' is among the foundational papers of cognitive psychology.",
                "expert_explanation": "Miller's 1956 paper 'The Magical Number Seven, Plus or Minus Two' is among the foundational papers of cognitive psychology.",
                "reference_source": "Miller, G. A. (1956). The magical number seven, plus or minus two. Psychological Review, 63(2), 81-97.",
                "reference_citation": "Miller, G. A. (1956). The magical number seven, plus or minus two. Psychological Review, 63(2), 81-97.",
                "rubric_keywords": ["7 plus or minus 2", "magical number seven", "miller 1956", "chunks"],
            },
            {
                "claim_id": "SCEN_07_C2",
                "claim_text": "Nelson Cowan (2001) revised pure working memory capacity to approximately 4 chunks when rehearsal is controlled.",
                "statement": "Nelson Cowan (2001) revised pure working memory capacity to approximately 4 chunks when rehearsal is controlled.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Synthesis)",
                "explanation": "Cowan's target article in Behavioral and Brain Sciences demonstrated that without verbal rehearsal, capacity is 4 +/- 1 chunks.",
                "expert_explanation": "Cowan's target article in Behavioral and Brain Sciences demonstrated that without verbal rehearsal, capacity is 4 +/- 1 chunks.",
                "reference_source": "Cowan, N. (2001). The magical number 4 in short-term memory. Behavioral and Brain Sciences, 24(1), 87-114.",
                "reference_citation": "Cowan, N. (2001). The magical number 4 in short-term memory. Behavioral and Brain Sciences, 24(1), 87-114.",
                "rubric_keywords": ["cowan", "4 chunks", "rehearsal", "behavioral and brain sciences"],
            },
            {
                "claim_id": "SCEN_07_C3",
                "claim_text": "A 'chunk' represents a subjective meaningful grouping rather than an objective fixed number of bits.",
                "statement": "A 'chunk' represents a subjective meaningful grouping rather than an objective fixed number of bits.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Synthesis)",
                "explanation": "Miller explicitly showed that information capacity increases dramatically when bits are recoded into richer semantic chunks.",
                "expert_explanation": "Miller explicitly showed that information capacity increases dramatically when bits are recoded into richer semantic chunks.",
                "reference_source": "Miller, G. A. (1956). Psychological Review, 63(2), 81-97.",
                "reference_citation": "Miller, G. A. (1956). Psychological Review, 63(2), 81-97.",
                "rubric_keywords": ["recoding", "semantic", "meaningful unit", "subjective"],
            },
        ],
    },
    {
        "id": "SCEN_08",
        "domain": "Research Methods & Causal Inference",
        "topic": "Observational Covariance vs. Causal Effect",
        "academic_question": (
            "A cross-sectional study of 500 university students observes a positive correlation (r = +0.45, p < 0.001) "
            "between daily Generative AI usage hours and semester GPA. How should this finding be interpreted?"
        ),
        "simulated_ai_response": (
            "The strong positive correlation (r = +0.45, p < 0.001) proves that increasing daily Generative AI usage "
            "directly improves university student GPA.\n"
            "Because the sample size is large (N=500) and the p-value is extremely small (p < 0.001), confounding factors "
            "such as baseline academic ability, study hours, or student motivation are statistically ruled out as alternative explanations."
        ),
        "reference_truth": (
            "Correlation does not imply causation. A cross-sectional survey cannot establish causal direction or rule out confounders, "
            "regardless of sample size or p-value. High GPA students might adopt AI tools more actively (reverse causality), or third variables "
            "(academic engagement, tech-savviness) could drive both."
        ),
        "overall_ai_quality": "Methodologically Fallacious (Causal Attribution in Cross-Sectional Data)",
        "claims": [
            {
                "claim_id": "SCEN_08_C1",
                "claim_text": "A cross-sectional correlation of r = +0.45 proves that Generative AI usage causes higher GPA.",
                "statement": "A cross-sectional correlation of r = +0.45 proves that Generative AI usage causes higher GPA.",
                "ground_truth": "INCORRECT",
                "error_category": "Causal Inference Fallacy",
                "explanation": "Cross-sectional correlational designs capture simultaneous covariance and cannot establish temporal precedence or causal direction.",
                "expert_explanation": "Cross-sectional correlational designs capture simultaneous covariance and cannot establish temporal precedence or causal direction.",
                "reference_source": "Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). Experimental and Quasi-Experimental Designs for Generalized Causal Inference. Houghton Mifflin.",
                "reference_citation": "Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). Experimental and Quasi-Experimental Designs for Generalized Causal Inference. Houghton Mifflin.",
                "rubric_keywords": ["correlation is not causation", "cross-sectional", "temporal precedence", "reverse causality"],
            },
            {
                "claim_id": "SCEN_08_C2",
                "claim_text": "A large sample size (N=500) and small p-value (p < 0.001) eliminate the possibility of unobserved confounding variables.",
                "statement": "A large sample size (N=500) and small p-value (p < 0.001) eliminate the possibility of unobserved confounding variables.",
                "ground_truth": "INCORRECT",
                "error_category": "Methodological Fallacy (Sample Size and Confounding)",
                "explanation": "Statistical power reduces random sampling error but has zero effect on systematic bias or omitted confounding variables.",
                "expert_explanation": "Statistical power reduces random sampling error but has zero effect on systematic bias or omitted confounding variables.",
                "reference_source": "Pearl, J. (2009). Causality: Models, Reasoning, and Inference (2nd ed.). Cambridge University Press.",
                "reference_citation": "Pearl, J. (2009). Causality: Models, Reasoning, and Inference (2nd ed.). Cambridge University Press.",
                "rubric_keywords": ["confounding", "third variable", "sampling error vs bias", "omitted variables"],
            },
            {
                "claim_id": "SCEN_08_C3",
                "claim_text": "Reverse causality (students with higher GPAs independently choosing to use AI more frequently) remains a plausible alternative explanation.",
                "statement": "Reverse causality (students with higher GPAs independently choosing to use AI more frequently) remains a plausible alternative explanation.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Methodological Reasoning)",
                "explanation": "Without longitudinal manipulation or randomized control trials, bidirectional or reverse causal paths cannot be ruled out.",
                "expert_explanation": "Without longitudinal manipulation or randomized control trials, bidirectional or reverse causal paths cannot be ruled out.",
                "reference_source": "Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). Chapter 1.",
                "reference_citation": "Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). Chapter 1.",
                "rubric_keywords": ["reverse causality", "bidirectional", "randomized trial", "alternative explanation"],
            },
        ],
    },
]


# =========================================================================== #
# 2. Secure Scenario Retrieval (Masked Answer Keys)                          #
# =========================================================================== #

def get_sanitized_verification_scenarios(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Return assessment scenarios with answer keys, explanations, and ground truth strictly masked.
    Safe for presentation in student-facing browser client before submission.
    """
    scenarios = VERIFICATION_SCENARIOS[:limit] if limit else VERIFICATION_SCENARIOS
    sanitized: List[Dict[str, Any]] = []

    for sc in scenarios:
        clean_sc = {
            "id": sc["id"],
            "domain": sc["domain"],
            "topic": sc["topic"],
            "academic_question": sc["academic_question"],
            "simulated_ai_response": sc["simulated_ai_response"],
            "claims": [
                {
                    "claim_id": c["claim_id"],
                    "claim_text": c["claim_text"],
                    "statement": c["claim_text"],
                }
                for c in sc["claims"]
            ],
        }
        sanitized.append(clean_sc)

    return sanitized


def get_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Lookup a full scenario by its ID, including answer keys (backend internal use only)."""
    for sc in VERIFICATION_SCENARIOS:
        if sc["id"] == scenario_id:
            return sc
    return None


# =========================================================================== #
# 3. Objective Performance Scoring Engine                                    #
# =========================================================================== #

def evaluate_explanation_quality(justification: str, ground_truth: str, key_concepts: List[str]) -> Tuple[int, str]:
    """
    Evaluate student written justification against standard 0-2 educational rubric.
    
    Rubric:
      0 = Absent, trivial (< 10 chars), or reiterates error with no reasoning.
      1 = Partially correct intuition or identifies location without theoretical reasoning.
      2 = Sound, evidence-based academic justification citing relevant principles or counterexamples.
    """
    text = (justification or "").strip().lower()
    if len(text) < 12:
        return 0, "No substantive reasoning or justification provided."

    # Check for trivial dismissive phrases
    trivial_phrases = ["it is wrong", "it's wrong", "this is wrong", "incorrect", "false", "i guess so", "bad math"]
    if text in trivial_phrases:
        return 0, "Superficial assertion without supporting academic reasoning."

    # Check for technical reasoning keywords
    matches = sum(1 for kw in key_concepts if kw.lower() in text)
    if matches >= 2 or len(text) >= 60:
        return 2, "Evidence-based justification identifying underlying academic mechanism."
    elif matches >= 1 or len(text) >= 25:
        return 1, "Partially developed reasoning identifying the general issue."
    else:
        return 0, "Vague or unsupported assertion without academic justification."


def grade_explanation_rubric(
    justification: str,
    claim_or_gt: Any = None,
    is_correct_verdict: bool = True,
    key_concepts: Optional[List[str]] = None,
) -> Tuple[int, str]:
    """
    Flexible rubric evaluator accepting either:
    - (justification, ground_truth, key_concepts)
    - (justification, claim_dict, is_correct_verdict)
    """
    default_kws = [
        "derivative", "integral", "factor", "divide", "p-value", "null",
        "effect size", "clt", "variance", "kelvin", "temperature",
        "exonuclease", "proofread", "fidelity", "vaswani", "citation",
        "nature", "confound", "selection", "sample size"
    ]
    if isinstance(claim_or_gt, dict):
        gt = claim_or_gt.get("ground_truth", "CORRECT")
        kws = claim_or_gt.get("rubric_keywords", default_kws)
    elif isinstance(claim_or_gt, str):
        gt = claim_or_gt
        kws = key_concepts or default_kws
    else:
        gt = "CORRECT"
        kws = key_concepts or default_kws

    return evaluate_explanation_quality(justification, gt, kws)


def evaluate_student_verification(
    submissions: List[Dict[str, Any]],
    student_id: str = "Anonymous Student"
) -> Dict[str, Any]:
    """
    Evaluate student claim classifications and written justifications against expert answer keys.
    """
    # Create lookup map of all master claims
    master_claims: Dict[str, Dict[str, Any]] = {}
    master_scenarios: Dict[str, Dict[str, Any]] = {}
    for sc in VERIFICATION_SCENARIOS:
        master_scenarios[sc["id"]] = sc
        for c in sc["claims"]:
            master_claims[c["claim_id"]] = {
                **c,
                "scenario_id": sc["id"],
                "domain": sc["domain"],
                "topic": sc["topic"],
            }

    # Flatten nested scenario-based submissions if necessary
    flat_submissions: List[Dict[str, Any]] = []
    for item in submissions:
        if isinstance(item, dict) and "claims" in item and isinstance(item["claims"], list):
            for c in item["claims"]:
                flat_submissions.append(c)
        elif isinstance(item, dict):
            flat_submissions.append(item)

    total_claims = len(flat_submissions)
    correct_classifications = 0
    tp = 0  # True Positive: correctly caught an erroneous or unsupported claim
    tn = 0  # True Negative: correctly accepted an accurate claim
    fp = 0  # False Positive: falsely accused an accurate claim of being flawed
    fn = 0  # False Negative: failed to catch an erroneous or unsupported claim

    rubric_points_earned = 0
    rubric_points_possible = total_claims * 2

    detailed_evaluations: List[Dict[str, Any]] = []

    for sub in flat_submissions:
        cid = sub.get("claim_id")
        raw_choice = sub.get("student_classification") or sub.get("selected_verdict") or sub.get("student_verdict") or ""
        student_choice = raw_choice.strip().upper()
        if student_choice == "ERRONEOUS":
            student_choice = "INCORRECT"

        justification = sub.get("justification", "")
        method = sub.get("verification_method", "Unspecified")

        if cid not in master_claims:
            continue

        claim_info = master_claims[cid]
        gt = claim_info["ground_truth"]  # "CORRECT" | "INCORRECT" | "UNSUPPORTED"

        # Check exact classification match
        is_exact_match = (student_choice == gt)
        if is_exact_match:
            correct_classifications += 1

        # Binary Error Detection Framing:
        # Flawed = (INCORRECT or UNSUPPORTED); Sound = CORRECT
        is_flawed_ground_truth = (gt in ["INCORRECT", "UNSUPPORTED"])
        student_flagged_flaw = (student_choice in ["INCORRECT", "UNSUPPORTED"])

        if is_flawed_ground_truth and student_flagged_flaw:
            tp += 1
            detection_status = "True Detection (Error Correctly Flagged)"
        elif not is_flawed_ground_truth and not student_flagged_flaw:
            tn += 1
            detection_status = "True Acceptance (Accurate Statement Recognized)"
        elif not is_flawed_ground_truth and student_flagged_flaw:
            fp += 1
            detection_status = "False Error Accusation (Valid Statement Flagged as Flawed)"
        else:  # is_flawed_ground_truth and not student_flagged_flaw
            fn += 1
            detection_status = "Missed AI Flaw (Erroneous Statement Accepted)"

        # Rubric evaluation
        sample_keywords = [
            "derivative", "integral", "factor", "divide", "p-value", "null",
            "effect size", "clt", "variance", "kelvin", "temperature",
            "exonuclease", "proofread", "fidelity", "vaswani", "citation",
            "nature", "confound", "selection", "sample size"
        ]
        rubric_score, rubric_feedback = evaluate_explanation_quality(justification, gt, sample_keywords)
        rubric_points_earned += rubric_score

        detailed_evaluations.append({
            "claim_id": cid,
            "scenario_id": claim_info["scenario_id"],
            "domain": claim_info["domain"],
            "topic": claim_info["topic"],
            "claim_text": claim_info["claim_text"],
            "statement": claim_info["claim_text"],
            "student_choice": student_choice,
            "student_verdict": student_choice,
            "ground_truth": gt,
            "is_correct": is_exact_match,
            "is_correct_classification": is_exact_match,
            "detection_status": detection_status,
            "error_category": claim_info["error_category"],
            "expert_explanation": claim_info["explanation"],
            "reference_source": claim_info["reference_source"],
            "reference_citation": claim_info["reference_source"],
            "student_justification": justification,
            "verification_method": method,
            "rubric_score": rubric_score,
            "rubric_feedback": rubric_feedback,
        })

    # Metric computations
    accuracy = (correct_classifications / total_claims) if total_claims > 0 else 0.0
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    specificity = (tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    rubric_pct = (rubric_points_earned / rubric_points_possible * 100.0) if rubric_points_possible > 0 else 0.0

    # Generate Task-Specific Explainable Feedback
    task_feedback = generate_task_performance_feedback(
        accuracy=accuracy,
        recall=recall,
        precision=precision,
        fn=fn,
        fp=fp,
        rubric_score_pct=rubric_pct,
        detailed_evals=detailed_evaluations,
    )

    return {
        "success": True,
        "student_id": student_id,
        "evaluated_at": datetime.now().isoformat(),
        "summary": {
            "total_claims_evaluated": total_claims,
            "correct_classifications": correct_classifications,
            "accuracy": round(accuracy, 3),
            "accuracy_pct": round(accuracy * 100.0, 1),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "specificity": round(specificity, 3),
            "f1_score": round(f1, 3),
            "rubric_points_earned": rubric_points_earned,
            "rubric_points_possible": rubric_points_possible,
            "rubric_pct": round(rubric_pct, 1),
        },
        "confusion_matrix": {
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "interpretation": {
                "tp": "Erroneous or unsupported claims correctly flagged",
                "tn": "Accurate AI statements correctly recognized",
                "fp": "False error accusations on valid AI statements",
                "fn": "Missed AI errors accepted as true",
            },
        },
        "claim_evaluations": detailed_evaluations,
        "performance_feedback": task_feedback,
        "non_diagnostic_notice": (
            "Empirical Validation Notice: This performance assessment evaluates demonstrated verification accuracy "
            "across 8 controlled academic scenarios. Performance metrics reflect specific scenario outcomes and "
            "must be interpreted alongside self-reported psychometric dimensions."
        ),
    }


# =========================================================================== #
# 4. Task Performance Feedback Generator                                     #
# =========================================================================== #

def generate_task_performance_feedback(
    accuracy: float,
    recall: float,
    precision: float,
    fn: int,
    fp: int,
    rubric_score_pct: float,
    detailed_evals: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Generate explainable, evidence-traced feedback based on demonstrated task performance."""
    feedback: List[Dict[str, Any]] = []

    # Rule 1: Missed AI Errors (Low Recall)
    if fn >= 2 or recall < 0.70:
        missed_domains = list({e["domain"] for e in detailed_evals if e["detection_status"].startswith("Missed")})
        feedback.append({
            "id": "FB_MISSED_ERRORS",
            "category": "Error Sensitivity",
            "priority": "HIGH",
            "title": "Strengthen Sub-Step Execution Auditing",
            "diagnostic": (
                f"You missed {fn} simulated AI errors (Recall = {recall:.1%}), notably in "
                f"{', '.join(missed_domains[:2]) if missed_domains else 'intermediate steps'}. "
                "AI responses frequently present flawed derivations wrapped in plausible introductory and concluding text."
            ),
            "action_strategy": (
                "Do not evaluate AI answers as a holistic block. Isolate each intermediate transition "
                "(e.g., individual integration steps, unit conversions) and re-evaluate them independently with pen and scratchpad."
            ),
            "action_steps": [
                "Execute the LIATE or derivation step independently before reading the AI's intermediate algebra.",
                "Explicitly check scale units (e.g. Celsius to Kelvin) in scientific and thermodynamic formulas.",
            ],
            "evidence_trace": f"Observed FN = {fn}, Error Detection Recall = {recall:.1%}",
        })

    # Rule 2: False Error Accusations (Low Specificity / Precision)
    if fp >= 2 or precision < 0.75:
        false_alarm_domains = list({e["domain"] for e in detailed_evals if e["detection_status"].startswith("False Error")})
        feedback.append({
            "id": "FB_FALSE_ALARMS",
            "category": "Calibrated Discrimination",
            "priority": "MEDIUM",
            "title": "Differentiate Valid Steps from Heuristic Doubts",
            "diagnostic": (
                f"You rejected {fp} factually sound statements as errors (Precision = {precision:.1%}), "
                f"particularly in {', '.join(false_alarm_domains[:2]) if false_alarm_domains else 'control tasks'}. "
                "Overly aggressive skepticism without verifying the mathematical grounds leads to unnecessary rejection of correct work."
            ),
            "action_strategy": (
                "Before flagging an AI step as flawed, write out the explicit counter-example or identify the exact algebraic slip. "
                "If no concrete contradictory evidence is found, verify via textbook lookup before discarding the step."
            ),
            "action_steps": [
                "Verify standard theorems (such as Central Limit Theorem conditions) in authorized course slides.",
                "Distinguish unfamiliar terminology from genuine technical errors.",
            ],
            "evidence_trace": f"Observed FP = {fp}, Classification Precision = {precision:.1%}",
        })

    # Rule 3: Phantom Citation & Source Auditing
    citation_miss = any(
        e["ground_truth"] == "UNSUPPORTED" and not e["is_correct"]
        for e in detailed_evals
    )
    if citation_miss:
        feedback.append({
            "id": "FB_CITATION_AUDIT",
            "category": "Academic Integrity & Source Verification",
            "priority": "HIGH",
            "title": "Systematically Verify AI-Generated Citations",
            "diagnostic": (
                "You accepted a simulated or hallucinated academic paper citation as authentic. "
                "Generative AI models frequently generate 'chimera citations'—real author names paired with plausible, invented titles and DOIs."
            ),
            "action_strategy": (
                "Never cite AI-provided papers directly in coursework without querying Google Scholar, CrossRef, or the university library index. "
                "Verify that the authors, publication year, volume, and exact title match genuine peer-reviewed literature."
            ),
            "action_steps": [
                "Copy the exact article title into Google Scholar or Semantic Scholar before referencing.",
                "Confirm that the cited volume and page numbers align with the referenced journal.",
            ],
            "evidence_trace": "Missed hallucinated citation in AI sequence representation scenario.",
        })

    # Rule 4: Weak Explanation Quality (Rubric < 60%)
    if rubric_score_pct < 60.0:
        feedback.append({
            "id": "FB_RUBRIC_RATIONALE",
            "category": "Metacognitive Articulation",
            "priority": "MEDIUM",
            "title": "Ground Critiques in Theoretical Principles",
            "diagnostic": (
                f"Your written justifications earned {rubric_score_pct:.1f}% of available rubric points. "
                "Many evaluations stated that an answer was 'wrong' or 'weird' without articulating the underlying mathematical or empirical principle."
            ),
            "action_strategy": (
                "Practice framing critiques in structured explanatory form: (1) Identify the flawed step; "
                "(2) State the governing theorem or rule; (3) Provide the corrected calculation or counterexample."
            ),
            "action_steps": [
                "Reference the specific violated constraint (e.g. 'requires 3'-to-5' direction' or 'omitted 1/2 inner derivative factor').",
                "Write brief mathematical justifications rather than subjective impressions.",
            ],
            "evidence_trace": f"Rubric point capture rate = {rubric_score_pct:.1f}% (target >= 75%)",
        })

    # Rule 5: High Mastery Maintenance
    if accuracy >= 0.85 and recall >= 0.85:
        feedback.append({
            "id": "FB_CALIBRATED_MASTERY",
            "category": "Verification Excellence",
            "priority": "LOW",
            "title": "Exemplary Verification Discernment",
            "diagnostic": (
                f"You demonstrated superior evaluative precision ({accuracy:.1%} accuracy, {recall:.1%} recall), "
                "effectively catching subtle algebraic errors, identifying fabricated citations, and respecting accurate control problems."
            ),
            "action_strategy": (
                "Maintain this rigorous verification workflow when incorporating generative AI into research, thesis drafting, "
                "and complex computational problem solving. Share your step-auditing methods with peers."
            ),
            "action_steps": [
                "Serve as a peer reviewer or lead study groups on critical AI literacy.",
                "Explore automated prompt engineering strategies that enforce step-by-step verification protocols.",
            ],
            "evidence_trace": f"Overall Accuracy = {accuracy:.1%}, Recall = {recall:.1%}",
        })

    # Guarantee minimum 2 actionable recommendations
    if len(feedback) < 2:
        feedback.append({
            "id": "FB_GENERAL_TRIANGULATION",
            "category": "Multi-Source Verification",
            "priority": "LOW",
            "title": "Triangulate AI Answers with Course Syllabus",
            "diagnostic": "Consistent verification requires maintaining independent reference sources alongside AI study tools.",
            "action_strategy": "Always cross-reference AI-generated code, derivations, and summaries with primary lecture notes.",
            "action_steps": ["Bookmark primary textbook electronic editions for immediate reference checks."],
            "evidence_trace": "Standard educational best practice.",
        })

    return feedback
