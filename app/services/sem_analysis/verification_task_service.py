"""
app/services/sem_analysis/verification_task_service.py

Controlled AI-Generated Answer Verification Performance Assessment Module.
Component 2: Explainable AI Trust and Verification Assessment Framework (J26-DS-310).

Design Principles:
1. Cross-Disciplinary Undergraduate Accessibility:
   8 accessible scenarios covering General Academic Administration, Campus Regulations,
   Library Source Verification, Scientific Literacy, Quantitative Reasoning, Syllabus Rules,
   Survey Methodology, and Multi-Factor Academic Policies.
   All necessary facts, tables, and policy excerpts are provided in the prompts so no specialized
   mathematics, chemistry, or genetics domain knowledge is required.
2. Controlled Error Topology:
   Contains calculation slips, factual contradictions, hallucinated citations, correlation-causation
   conflations, base-rate neglect, over-generalization from biased samples, and fully sound scientific controls.
3. Researcher-Designed Status:
   All scenarios are researcher-designed instruments pending independent expert panel review.
4. Answer-Key Security:
   Provides sanitized task views to students (masking ground truth and explanations),
   and evaluates submissions against expert answer keys upon completion.
5. Difficulty Mix (Subject to Pilot Validation):
   3 Easy (Scenarios 1, 2, 6), 4 Medium (Scenarios 3, 4, 5, 7), 1 Challenging (Scenario 8).
6. Multidimensional Performance Metrics:
   Measures Accuracy, Error Detection Recall (Sensitivity), Precision, Specificity, F1,
   and Evidence-Based Justification Rubric scores (0-2 scale).
"""

from typing import Any, Dict, List, Optional, Tuple
import copy
from datetime import datetime


# =========================================================================== #
# 1. Bank of 8 Cross-Disciplinary Academic Verification Scenarios              #
# =========================================================================== #

VERIFICATION_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "SCEN_01",
        "domain": "Academic Administration & Data Literacy",
        "topic": "Tutorial Attendance Aggregation & Percentage Calculations",
        "difficulty": "Easy",
        "academic_question": (
            "An undergraduate course administrator compiles the attendance report for three tutorial sections on a given week:\n"
            "- Tutorial Section A: 40 students enrolled, 32 attended (80.0%)\n"
            "- Tutorial Section B: 50 students enrolled, 45 attended (90.0%)\n"
            "- Tutorial Section C: 60 students enrolled, 33 attended (55.0%)\n"
            "Review the simulated AI summary of this attendance data."
        ),
        "simulated_ai_response": (
            "Based on the tutorial records:\n"
            "1. The total course enrollment across all three sections is 150 students, and total attendance is 110 students.\n"
            "2. The overall course attendance rate is calculated by taking the simple average of section percentages: (80.0% + 90.0% + 55.0%) / 3 = 75.0%.\n"
            "3. Tutorial Section A achieved the highest attendance rate among all sections."
        ),
        "reference_truth": (
            "Total enrolled = 40 + 50 + 60 = 150; Total attended = 32 + 45 + 33 = 110 (Claim 1 is CORRECT). "
            "Because sections have unequal sizes, overall attendance must be calculated as a weighted average: 110 / 150 = 73.3%, "
            "not a simple average of 75.0% (Claim 2 is INCORRECT). "
            "Section B had the highest attendance rate at 90.0%, not Section A at 80.0% (Claim 3 is INCORRECT)."
        ),
        "overall_ai_quality": "Partially Correct (Contains Aggregation & Factual Error)",
        "claims": [
            {
                "claim_id": "SCEN_01_C1",
                "claim_text": "The total course enrollment across all three sections is 150 students, and total attendance is 110 students.",
                "statement": "The total course enrollment across all three sections is 150 students, and total attendance is 110 students.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Tally)",
                "explanation": "Summing enrolled: 40 + 50 + 60 = 150. Summing attended: 32 + 45 + 33 = 110. Both totals are mathematically correct.",
                "expert_explanation": "Summing enrolled: 40 + 50 + 60 = 150. Summing attended: 32 + 45 + 33 = 110. Both totals are mathematically correct.",
                "reference_source": "University Course Administration Record Standards (Section Attendance Tally).",
                "reference_citation": "University Course Administration Record Standards (Section Attendance Tally).",
                "rubric_keywords": ["150", "110", "sum", "total", "addition", "enrolled", "attended"],
            },
            {
                "claim_id": "SCEN_01_C2",
                "claim_text": "The overall course attendance rate is calculated by taking the simple average of section percentages: (80.0% + 90.0% + 55.0%) / 3 = 75.0%.",
                "statement": "The overall course attendance rate is calculated by taking the simple average of section percentages: (80.0% + 90.0% + 55.0%) / 3 = 75.0%.",
                "ground_truth": "INCORRECT",
                "error_category": "Numerical Aggregation Error (Unweighted Average on Unequal Group Sizes)",
                "explanation": "Because tutorial section enrollments are unequal (40, 50, 60), simple averaging of percentages introduces aggregation bias. The true overall rate is 110 / 150 = 73.3%, not 75.0%.",
                "expert_explanation": "Because tutorial section enrollments are unequal (40, 50, 60), simple averaging of percentages introduces aggregation bias. The true overall rate is 110 / 150 = 73.3%, not 75.0%.",
                "reference_source": "Freedman, D., Pisani, R., & Purves, R. (2007). Statistics (4th ed.). W. W. Norton & Co., Chapter 4.",
                "reference_citation": "Freedman, D., Pisani, R., & Purves, R. (2007). Statistics (4th ed.). W. W. Norton & Co., Chapter 4.",
                "rubric_keywords": ["weighted", "unweighted", "73.3", "110/150", "unequal", "sample size", "simpson", "denominator"],
            },
            {
                "claim_id": "SCEN_01_C3",
                "claim_text": "Tutorial Section A achieved the highest attendance rate among all sections.",
                "statement": "Tutorial Section A achieved the highest attendance rate among all sections.",
                "ground_truth": "INCORRECT",
                "error_category": "Factual Inconsistency with Provided Data",
                "explanation": "Section B achieved an attendance rate of 90.0% (45/50), which exceeds Section A's 80.0% (32/40) and Section C's 55.0% (33/60).",
                "expert_explanation": "Section B achieved an attendance rate of 90.0% (45/50), which exceeds Section A's 80.0% (32/40) and Section C's 55.0% (33/60).",
                "reference_source": "Course Administrator Attendance Ledger (Table Comparison).",
                "reference_citation": "Course Administrator Attendance Ledger (Table Comparison).",
                "rubric_keywords": ["section b", "90%", "highest", "greater than", "80%"],
            },
        ],
    },
    {
        "id": "SCEN_02",
        "domain": "Campus Regulations & Student Life",
        "topic": "Library Study Room Reservation Policy Rules",
        "difficulty": "Easy",
        "academic_question": (
            "Review the following official university library group-study room booking rules:\n"
            "Rule 1: Group study rooms may be booked for blocks of up to 2 hours per day per student group.\n"
            "Rule 2: Reservations must be claimed within 15 minutes of the start time, after which the room is released to walk-ins.\n"
            "Rule 3: Rooms are reserved strictly for collaborative groups of 2 or more students; single-occupant use is prohibited.\n"
            "Rule 4: Cancellations made at least 1 hour in advance incur no penalty. Late cancellations or no-shows forfeit booking privileges for 7 days.\n"
            "Review the simulated AI response to a student inquiry about booking rules."
        ),
        "simulated_ai_response": (
            "According to the library policy:\n"
            "1. An individual student studying alone may book a group study room for up to 2 hours per day.\n"
            "2. If a group does not arrive within 15 minutes of their reserved start time, the reservation is canceled and made available to other students.\n"
            "3. If your group cancels your booking 2 hours before the start time, you will not lose booking privileges."
        ),
        "reference_truth": (
            "Rule 3 explicitly prohibits single-occupant use of group study rooms (Claim 1 is INCORRECT). "
            "Rule 2 specifies a 15-minute grace period before rooms are released to walk-in students (Claim 2 is CORRECT). "
            "Rule 4 states cancellations made at least 1 hour in advance incur no penalty; 2 hours satisfies this condition (Claim 3 is CORRECT)."
        ),
        "overall_ai_quality": "Partially Correct (Contains Policy Inversion Error)",
        "claims": [
            {
                "claim_id": "SCEN_02_C1",
                "claim_text": "An individual student studying alone may book a group study room for up to 2 hours per day.",
                "statement": "An individual student studying alone may book a group study room for up to 2 hours per day.",
                "ground_truth": "INCORRECT",
                "error_category": "Direct Factual Contradiction of Policy Text",
                "explanation": "Rule 3 explicitly states that group rooms are strictly for 2 or more students and single-occupant use is prohibited.",
                "expert_explanation": "Rule 3 explicitly states that group rooms are strictly for 2 or more students and single-occupant use is prohibited.",
                "reference_source": "University Library Facility Use Policy, Rule 3 (Collaborative Space Regulations).",
                "reference_citation": "University Library Facility Use Policy, Rule 3 (Collaborative Space Regulations).",
                "rubric_keywords": ["rule 3", "2 or more", "prohibited", "single occupant", "individual", "alone"],
            },
            {
                "claim_id": "SCEN_02_C2",
                "claim_text": "If a group does not arrive within 15 minutes of their reserved start time, the reservation is canceled and made available to other students.",
                "statement": "If a group does not arrive within 15 minutes of their reserved start time, the reservation is canceled and made available to other students.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Policy Rule)",
                "explanation": "Rule 2 explicitly specifies that reservations must be claimed within 15 minutes or released to walk-ins.",
                "expert_explanation": "Rule 2 explicitly specifies that reservations must be claimed within 15 minutes or released to walk-ins.",
                "reference_source": "University Library Facility Use Policy, Rule 2.",
                "reference_citation": "University Library Facility Use Policy, Rule 2.",
                "rubric_keywords": ["15 minutes", "rule 2", "walk-in", "released", "grace period"],
            },
            {
                "claim_id": "SCEN_02_C3",
                "claim_text": "If your group cancels your booking 2 hours before the start time, you will not lose booking privileges.",
                "statement": "If your group cancels your booking 2 hours before the start time, you will not lose booking privileges.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Policy Rule)",
                "explanation": "Rule 4 states cancellations made at least 1 hour in advance incur no penalty. A cancellation 2 hours in advance exceeds this minimum threshold.",
                "expert_explanation": "Rule 4 states cancellations made at least 1 hour in advance incur no penalty. A cancellation 2 hours in advance exceeds this minimum threshold.",
                "reference_source": "University Library Facility Use Policy, Rule 4.",
                "reference_citation": "University Library Facility Use Policy, Rule 4.",
                "rubric_keywords": ["rule 4", "1 hour", "at least", "no penalty", "in advance"],
            },
        ],
    },
    {
        "id": "SCEN_03",
        "domain": "Academic Research & Source Evaluation",
        "topic": "Library Catalog Citation Verification",
        "difficulty": "Medium",
        "academic_question": (
            "A student asks an AI research assistant for evidence regarding digital note-taking. The student accesses the university library discovery catalog, which displays the following three verified records:\n"
            "- Record 1: Mueller, P. A., & Oppenheimer, D. M. (2014). 'The pen is mightier than the keyboard: Advantages of longhand over laptop note taking.' Psychological Science, 25(6), 1159-1168.\n"
            "- Record 2: Morehead, K., Dunlosky, J., & Rawson, K. A. (2019). 'How much mightier is the pen than the keyboard for note-taking? A replication and extension.' Educational Psychology Review, 31(3), 753-780.\n"
            "- Record 3: Sana, E., Weston, T., & Cepeda, N. J. (2013). 'Laptop multitasking hinders classroom learning for both users and nearby peers.' Computers & Education, 62, 24-31.\n"
            "Evaluate the simulated AI summary of these scholarly sources."
        ),
        "simulated_ai_response": (
            "Based on the academic literature:\n"
            "1. Mueller and Oppenheimer (2014) investigated differences in student learning outcomes between laptop and longhand note-taking in Psychological Science.\n"
            "2. A 2022 paper by Mueller and Cepeda in Nature titled 'Complete Digital Note Dominance: Why Longhand Writing is Obsolete' established that handwriting reduces memory retention by 80%.\n"
            "3. Sana, Weston, and Cepeda (2013) evaluated the impact of laptop multitasking on both the user and nearby classmates."
        ),
        "reference_truth": (
            "Record 1 validates that Mueller & Oppenheimer (2014) investigated longhand vs. laptop note-taking in Psychological Science (Claim 1 is CORRECT). "
            "Claim 2 cites a non-existent paper ('Complete Digital Note Dominance' in Nature 2022); neither Mueller nor Cepeda published this paper, nor does it appear in the catalog (Claim 2 is UNSUPPORTED / Hallucinated). "
            "Record 3 validates that Sana et al. (2013) in Computers & Education studied multitasking effects on users and nearby peers (Claim 3 is CORRECT)."
        ),
        "overall_ai_quality": "Hallucinated Source / Fabricated Literature Citation",
        "claims": [
            {
                "claim_id": "SCEN_03_C1",
                "claim_text": "Mueller and Oppenheimer (2014) investigated differences in student learning outcomes between laptop and longhand note-taking in Psychological Science.",
                "statement": "Mueller and Oppenheimer (2014) investigated differences in student learning outcomes between laptop and longhand note-taking in Psychological Science.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Citation Match)",
                "explanation": "Directly matches Record 1 from the verified library discovery catalog.",
                "expert_explanation": "Directly matches Record 1 from the verified library discovery catalog.",
                "reference_source": "Mueller, P. A., & Oppenheimer, D. M. (2014). Psychological Science, 25(6), 1159-1168.",
                "reference_citation": "Mueller, P. A., & Oppenheimer, D. M. (2014). Psychological Science, 25(6), 1159-1168.",
                "rubric_keywords": ["record 1", "psychological science", "mueller", "oppenheimer", "verified"],
            },
            {
                "claim_id": "SCEN_03_C2",
                "claim_text": "Mueller and Cepeda published a 2022 paper in Nature titled 'Complete Digital Note Dominance' proving handwriting reduces memory retention by 80%.",
                "statement": "Mueller and Cepeda published a 2022 paper in Nature titled 'Complete Digital Note Dominance' proving handwriting reduces memory retention by 80%.",
                "ground_truth": "UNSUPPORTED",
                "error_category": "Phantom / Hallucinated Academic Citation",
                "explanation": "This citation does not exist in the university library catalog or scholarly indexes; it pairs real author surnames with an invented title, venue, and extreme quantitative claim.",
                "expert_explanation": "This citation does not exist in the university library catalog or scholarly indexes; it pairs real author surnames with an invented title, venue, and extreme quantitative claim.",
                "reference_source": "University Library Discovery System (Index Audit: zero matches for claimed Nature title).",
                "reference_citation": "University Library Discovery System (Index Audit: zero matches for claimed Nature title).",
                "rubric_keywords": ["hallucination", "fabricated", "does not exist", "not in catalog", "phantom", "unsupported"],
            },
            {
                "claim_id": "SCEN_03_C3",
                "claim_text": "Sana, Weston, and Cepeda (2013) evaluated the impact of laptop multitasking on both the user and nearby classmates.",
                "statement": "Sana, Weston, and Cepeda (2013) evaluated the impact of laptop multitasking on both the user and nearby classmates.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Citation Match)",
                "explanation": "Directly matches Record 3 from the verified library discovery catalog in Computers & Education.",
                "expert_explanation": "Directly matches Record 3 from the verified library discovery catalog in Computers & Education.",
                "reference_source": "Sana, E., Weston, T., & Cepeda, N. J. (2013). Computers & Education, 62, 24-31.",
                "reference_citation": "Sana, E., Weston, T., & Cepeda, N. J. (2013). Computers & Education, 62, 24-31.",
                "rubric_keywords": ["record 3", "sana", "multitasking", "peers", "computers & education"],
            },
        ],
    },
    {
        "id": "SCEN_04",
        "domain": "Scientific Literacy & Evidence Interpretation",
        "topic": "Observational Correlation vs. Causal Intervention",
        "difficulty": "Medium",
        "academic_question": (
            "An undergraduate student newspaper published a survey of 500 university students:\n"
            "'A cross-sectional survey conducted during week 8 found a positive correlation (r = +0.38, p < 0.001) "
            "between weekly hours spent exercising at the campus gym and cumulative GPA. "
            "Students exercising over 6 hours weekly reported an average GPA of 3.5, whereas those exercising under 2 hours reported an average GPA of 3.0.'\n"
            "Review the simulated AI response explaining what this finding means."
        ),
        "simulated_ai_response": (
            "Based on this survey data:\n"
            "1. In this sample, students reporting higher weekly exercise hours had a higher average cumulative GPA.\n"
            "2. This study proves that requiring all students to spend 6 hours at the gym will directly increase their GPA by 0.5 points.\n"
            "3. Because the survey was observational and cross-sectional, confounding factors such as time management skills or study discipline cannot be ruled out."
        ),
        "reference_truth": (
            "The survey indeed observed a positive statistical association between exercise and GPA in the sample (Claim 1 is CORRECT). "
            "A cross-sectional observational survey captures simultaneous covariance; it cannot establish a causal effect or prove that mandating gym time will raise grades (Claim 2 is INCORRECT). "
            "Confounding variables (e.g. self-discipline, structured schedules) can explain both higher exercise and higher grades (Claim 3 is CORRECT)."
        ),
        "overall_ai_quality": "Methodologically Fallacious (Causal Attribution in Cross-Sectional Survey)",
        "claims": [
            {
                "claim_id": "SCEN_04_C1",
                "claim_text": "In this surveyed sample, students reporting higher weekly exercise hours showed a higher average cumulative GPA.",
                "statement": "In this surveyed sample, students reporting higher weekly exercise hours showed a higher average cumulative GPA.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Descriptive Summary)",
                "explanation": "Accurately summarizes the reported sample statistics: r = +0.38 and 3.5 GPA vs 3.0 GPA.",
                "expert_explanation": "Accurately summarizes the reported sample statistics: r = +0.38 and 3.5 GPA vs 3.0 GPA.",
                "reference_source": "Student Survey Descriptive Report (Sample Statistics Summary).",
                "reference_citation": "Student Survey Descriptive Report (Sample Statistics Summary).",
                "rubric_keywords": ["descriptive", "sample", "association", "correlation", "average"],
            },
            {
                "claim_id": "SCEN_04_C2",
                "claim_text": "This study proves that requiring all students to spend 6 hours at the gym will directly increase their GPA by 0.5 points.",
                "statement": "This study proves that requiring all students to spend 6 hours at the gym will directly increase their GPA by 0.5 points.",
                "ground_truth": "INCORRECT",
                "error_category": "Causal Inference Fallacy (Correlation Conflated with Causation)",
                "explanation": "Cross-sectional correlational surveys cannot establish causal direction or intervention efficacy. High GPA students might independently maintain structured routines that include exercise.",
                "expert_explanation": "Cross-sectional correlational surveys cannot establish causal direction or intervention efficacy. High GPA students might independently maintain structured routines that include exercise.",
                "reference_source": "Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). Experimental and Quasi-Experimental Designs for Generalized Causal Inference. Houghton Mifflin, Chapter 1.",
                "reference_citation": "Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). Experimental and Quasi-Experimental Designs for Generalized Causal Inference. Houghton Mifflin, Chapter 1.",
                "rubric_keywords": ["correlation is not causation", "cannot prove", "cross-sectional", "observational", "causal fallacy"],
            },
            {
                "claim_id": "SCEN_04_C3",
                "claim_text": "Confounding factors such as student self-discipline and time management skills cannot be ruled out by this cross-sectional survey.",
                "statement": "Confounding factors such as student self-discipline and time management skills cannot be ruled out by this cross-sectional survey.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Methodological Caveat)",
                "explanation": "Observational designs do not control for unobserved third variables (confounders) that may drive both healthy habits and academic success.",
                "expert_explanation": "Observational designs do not control for unobserved third variables (confounders) that may drive both healthy habits and academic success.",
                "reference_source": "Shadish, W. R., et al. (2002). Chapter 2 (Threats to Internal Validity).",
                "reference_citation": "Shadish, W. R., et al. (2002). Chapter 2 (Threats to Internal Validity).",
                "rubric_keywords": ["confounder", "third variable", "self-discipline", "time management", "observational"],
            },
        ],
    },
    {
        "id": "SCEN_05",
        "domain": "Quantitative Reasoning & Practical Logic",
        "topic": "Academic Integrity Screening Tool Performance",
        "difficulty": "Medium",
        "academic_question": (
            "A university tests an automated essay originality detector on 1,000 submitted student essays with verified historical records:\n"
            "- Actual copied/plagiarized essays: 50 (5% true prevalence)\n"
            "- Actual original/honest essays: 950 (95% true prevalence)\n"
            "- Detector accuracy on copied essays: 90% (correctly flags 45; misses 5)\n"
            "- Detector accuracy on original essays: 90% (correctly passes 855; falsely flags 95)\n"
            "- Total essays flagged by the tool: 45 true positives + 95 false positives = 140 flagged essays.\n"
            "Review the simulated AI response interpreting the tool's performance."
        ),
        "simulated_ai_response": (
            "Analyzing the screening tool:\n"
            "1. Across the 1,000 tested essays, the tool flagged a total of 140 essays as potentially copied.\n"
            "2. If an essay is flagged as copied, there is a 90% probability that the student actually committed plagiarism, matching the detector's 90% accuracy.\n"
            "3. The number of false accusations (95) exceeds the number of correctly identified copied essays (45) due to the low base rate of plagiarism."
        ),
        "reference_truth": (
            "Total flagged essays = 45 true positives + 95 false positives = 140 (Claim 1 is CORRECT). "
            "Claim 2 commits the classic base-rate fallacy: out of 140 flagged essays, only 45 are truly copied, so the actual probability is 45 / 140 = 32.1%, not 90.0% (Claim 2 is INCORRECT). "
            "Because plagiarism has a low 5% prevalence, 90% specificity on the 950 original essays generates 95 false alarms, which outnumbers the 45 true detections (Claim 3 is CORRECT)."
        ),
        "overall_ai_quality": "Partially Correct (Contains Base-Rate Neglect Fallacy)",
        "claims": [
            {
                "claim_id": "SCEN_05_C1",
                "claim_text": "The tool flagged a total of 140 essays as potentially copied out of the 1,000 evaluated.",
                "statement": "The tool flagged a total of 140 essays as potentially copied out of the 1,000 evaluated.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Tally)",
                "explanation": "Summing flagged cases: 45 (true positives) + 95 (false positives) = 140 total flagged essays.",
                "expert_explanation": "Summing flagged cases: 45 (true positives) + 95 (false positives) = 140 total flagged essays.",
                "reference_source": "Screening Performance Matrix (45 TP + 95 FP = 140 Flagged).",
                "reference_citation": "Screening Performance Matrix (45 TP + 95 FP = 140 Flagged).",
                "rubric_keywords": ["140", "45", "95", "sum", "true positive", "false positive"],
            },
            {
                "claim_id": "SCEN_05_C2",
                "claim_text": "If an essay is flagged as copied, there is a 90% probability that the student actually committed plagiarism.",
                "statement": "If an essay is flagged as copied, there is a 90% probability that the student actually committed plagiarism.",
                "ground_truth": "INCORRECT",
                "error_category": "Base Rate Neglect / Inverse Fallacy",
                "explanation": "Out of 140 total flagged essays, only 45 are actually copied. The positive predictive value is 45 / 140 = 32.1%, far below the claimed 90%.",
                "expert_explanation": "Out of 140 total flagged essays, only 45 are actually copied. The positive predictive value is 45 / 140 = 32.1%, far below the claimed 90%.",
                "reference_source": "Kahneman, D., & Tversky, A. (1973). On the psychology of prediction. Psychological Review, 80(4), 237-251.",
                "reference_citation": "Kahneman, D., & Tversky, A. (1973). On the psychology of prediction. Psychological Review, 80(4), 237-251.",
                "rubric_keywords": ["32.1%", "45/140", "base rate", "positive predictive value", "false positive rate"],
            },
            {
                "claim_id": "SCEN_05_C3",
                "claim_text": "The number of false accusations (95) exceeds the number of correctly identified copied essays (45) due to the low base rate of plagiarism.",
                "statement": "The number of false accusations (95) exceeds the number of correctly identified copied essays (45) due to the low base rate of plagiarism.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Proportion Comparison)",
                "explanation": "95 false alarms > 45 true positives. When prevalence is low (5%), even a high 90% accuracy rate generates more false positives than true positives.",
                "expert_explanation": "95 false alarms > 45 true positives. When prevalence is low (5%), even a high 90% accuracy rate generates more false positives than true positives.",
                "reference_source": "Diagnostic Screening Interpretation Standards (Low Prevalence Dynamics).",
                "reference_citation": "Diagnostic Screening Interpretation Standards (Low Prevalence Dynamics).",
                "rubric_keywords": ["95 > 45", "low prevalence", "base rate", "false alarms exceed"],
            },
        ],
    },
    {
        "id": "SCEN_06",
        "domain": "Course Policies & Academic Regulations",
        "topic": "Syllabus Grading Policy & Capstone Hurdle (Sound Control)",
        "difficulty": "Easy",
        "academic_question": (
            "Review the grading scheme from an official university course syllabus:\n"
            "'Course Assessment Components:\n"
            "- Term Quizzes (best 4 of 5 administered): 20%\n"
            "- Midterm Examination: 30%\n"
            "- Final Capstone Project: 40%\n"
            "- Seminar Participation: 10%\n"
            "Passing Condition: Students must achieve a minimum score of 50% on the Final Capstone Project to pass the course with a grade of C or above, regardless of cumulative points.'\n"
            "Review the simulated AI advice given to a student asking about their grade."
        ),
        "simulated_ai_response": (
            "Based on the course syllabus:\n"
            "1. The Midterm Exam and Final Capstone Project together constitute 70% of the total course assessment.\n"
            "2. A student who achieves 100% on Quizzes, Midterm, and Participation (60 points total) but receives 40% on the Final Project cannot receive a grade of C or above.\n"
            "3. The Term Quizzes component drops the lowest quiz score and counts only the best 4 scores toward the 20% allocation."
        ),
        "reference_truth": (
            "Midterm (30%) + Final Project (40%) = 70% (Claim 1 is CORRECT). "
            "Even though 60 points + (40% of 40 = 16) = 76 points cumulative, failing to reach 50% on the Final Project triggers the hurdle rule, preventing a grade of C or above (Claim 2 is CORRECT). "
            "Syllabus explicitly specifies 'best 4 of 5 administered' (Claim 3 is CORRECT). All three claims are completely sound."
        ),
        "overall_ai_quality": "Accurate (Fully Sound Academic Explanation)",
        "claims": [
            {
                "claim_id": "SCEN_06_C1",
                "claim_text": "The Midterm Exam and Final Capstone Project together constitute 70% of the total course assessment.",
                "statement": "The Midterm Exam and Final Capstone Project together constitute 70% of the total course assessment.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Addition)",
                "explanation": "30% (Midterm) + 40% (Final Project) = 70% of the overall course grade.",
                "expert_explanation": "30% (Midterm) + 40% (Final Project) = 70% of the overall course grade.",
                "reference_source": "Course Syllabus Grading Specification Table (30% + 40% = 70%).",
                "reference_citation": "Course Syllabus Grading Specification Table (30% + 40% = 70%).",
                "rubric_keywords": ["70%", "30%", "40%", "addition", "sum"],
            },
            {
                "claim_id": "SCEN_06_C2",
                "claim_text": "A student who achieves 100% on Quizzes, Midterm, and Participation but receives 40% on the Final Project cannot receive a grade of C or above.",
                "statement": "A student who achieves 100% on Quizzes, Midterm, and Participation but receives 40% on the Final Project cannot receive a grade of C or above.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Hurdle Interpretation)",
                "explanation": "The syllabus explicitly mandates achieving at least 50% on the Final Project as a condition for receiving a C or above. A score of 40% fails this mandatory prerequisite.",
                "expert_explanation": "The syllabus explicitly mandates achieving at least 50% on the Final Project as a condition for receiving a C or above. A score of 40% fails this mandatory prerequisite.",
                "reference_source": "Course Syllabus Passing Condition Clause (50% Minimum Project Hurdle).",
                "reference_citation": "Course Syllabus Passing Condition Clause (50% Minimum Project Hurdle).",
                "rubric_keywords": ["hurdle", "50% minimum", "mandatory", "prerequisite", "fails requirement"],
            },
            {
                "claim_id": "SCEN_06_C3",
                "claim_text": "The Term Quizzes component drops the lowest quiz score and counts only the best 4 scores toward the 20% allocation.",
                "statement": "The Term Quizzes component drops the lowest quiz score and counts only the best 4 scores toward the 20% allocation.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Syllabus Reading)",
                "explanation": "Directly quotes the syllabus policy: 'best 4 of 5 administered: 20%'.",
                "expert_explanation": "Directly quotes the syllabus policy: 'best 4 of 5 administered: 20%'.",
                "reference_source": "Course Syllabus Quiz Grading Clause.",
                "reference_citation": "Course Syllabus Quiz Grading Clause.",
                "rubric_keywords": ["best 4 of 5", "drops lowest", "quiz policy", "20%"],
            },
        ],
    },
    {
        "id": "SCEN_07",
        "domain": "Research Literacy & Survey Evaluation",
        "topic": "Convenience Sampling & Population Generalizability",
        "difficulty": "Medium",
        "academic_question": (
            "The university student council conducted an online poll regarding campus dining hours:\n"
            "'A poll was posted on the Student Council Instagram stories for 3 hours on a Friday evening (6:00 PM to 9:00 PM), asking whether dining halls should remain open until midnight. "
            "A total of 84 students responded, with 72 (85.7%) voting YES. Residence Hall East accounted for 65 of the 84 responses.'\n"
            "Review the simulated AI analysis of this poll."
        ),
        "simulated_ai_response": (
            "Analyzing the dining survey:\n"
            "1. A total of 84 responses were collected during the 3-hour Friday evening poll window.\n"
            "2. This poll conclusively proves that over 85% of the university's 18,000 undergraduate students demand midnight dining across all campus halls.\n"
            "3. The survey suffers from voluntary response and geographical bias, as the majority of respondents were residents of a single dormitory responding on a Friday night."
        ),
        "reference_truth": (
            "The poll indeed gathered 84 responses during the stated window (Claim 1 is CORRECT). "
            "A convenience sample of 84 students on a Friday night concentrated in one dormitory cannot be generalized to claim 85% of 18,000 students support the policy (Claim 2 is INCORRECT / UNSUPPORTED). "
            "Voluntary response bias and unrepresentative geographic concentration are well-established sampling limitations in survey methodology (Claim 3 is CORRECT)."
        ),
        "overall_ai_quality": "Partially Correct (Contains Over-Generalization Fallacy)",
        "claims": [
            {
                "claim_id": "SCEN_07_C1",
                "claim_text": "A total of 84 responses were collected during the 3-hour Friday evening poll window.",
                "statement": "A total of 84 responses were collected during the 3-hour Friday evening poll window.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Survey Record)",
                "explanation": "Directly matches the reported survey data (84 respondents between 6:00 PM and 9:00 PM).",
                "expert_explanation": "Directly matches the reported survey data (84 respondents between 6:00 PM and 9:00 PM).",
                "reference_source": "Student Council Poll Summary Report.",
                "reference_citation": "Student Council Poll Summary Report.",
                "rubric_keywords": ["84 responses", "3 hours", "poll window", "reported"],
            },
            {
                "claim_id": "SCEN_07_C2",
                "claim_text": "This poll conclusively proves that over 85% of the university's 18,000 undergraduate students demand midnight dining across all campus halls.",
                "statement": "This poll conclusively proves that over 85% of the university's 18,000 undergraduate students demand midnight dining across all campus halls.",
                "ground_truth": "UNSUPPORTED",
                "error_category": "Over-Generalization from Unrepresentative Sample",
                "explanation": "Extrapolating an 84-person convenience sample from one residence hall to an entire 18,000-student university commits a sampling fallacy; confidence intervals would be extremely wide and selection bias is severe.",
                "expert_explanation": "Extrapolating an 84-person convenience sample from one residence hall to an entire 18,000-student university commits a sampling fallacy; confidence intervals would be extremely wide and selection bias is severe.",
                "reference_source": "Groves, R. M., et al. (2009). Survey Methodology (2nd ed.). Wiley, Chapter 2 (Inference and Error in Surveys).",
                "reference_citation": "Groves, R. M., et al. (2009). Survey Methodology (2nd ed.). Wiley, Chapter 2 (Inference and Error in Surveys).",
                "rubric_keywords": ["sampling bias", "unrepresentative", "over-generalization", "convenience sample", "cannot generalize"],
            },
            {
                "claim_id": "SCEN_07_C3",
                "claim_text": "The survey suffers from voluntary response and geographical bias, as the majority of respondents were residents of a single dormitory responding on a Friday night.",
                "statement": "The survey suffers from voluntary response and geographical bias, as the majority of respondents were residents of a single dormitory responding on a Friday night.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Methodological Critique)",
                "explanation": "65 out of 84 respondents (77.4%) were from Residence Hall East alone, and voluntary Instagram participation selects for engaged, active users rather than a random probability sample.",
                "expert_explanation": "65 out of 84 respondents (77.4%) were from Residence Hall East alone, and voluntary Instagram participation selects for engaged, active users rather than a random probability sample.",
                "reference_source": "Groves, R. M., et al. (2009). Chapter 3.",
                "reference_citation": "Groves, R. M., et al. (2009). Chapter 3.",
                "rubric_keywords": ["voluntary response", "geographic bias", "residence hall east", "selection bias"],
            },
        ],
    },
    {
        "id": "SCEN_08",
        "domain": "Academic Rules & Policy Synthesis",
        "topic": "Assignment Late Penalty Tiers & Extension Offsets",
        "difficulty": "Challenging",
        "academic_question": (
            "Review the faculty late submission policy and a specific student case:\n"
            "Policy Rules:\n"
            "- Standard penalty: 5% of maximum assignment marks deducted per 24-hour period (or fraction thereof) late, up to a maximum of 5 days (120 hours / 25% max penalty).\n"
            "- After 120 hours, a mark of zero is recorded unless an exceptional Dean's waiver is granted.\n"
            "- Approved extensions: If an extension is approved, the late period begins from the extended deadline.\n"
            "Student Case:\n"
            "- Assignment Max Marks = 100. Student raw earned mark before penalty = 86.\n"
            "- Student was granted an approved 24-hour extension in advance.\n"
            "- The student submitted their assignment 54 hours after the original deadline (which is 30 hours after the extended deadline).\n"
            "Review the simulated AI response calculating the student's final recorded grade."
        ),
        "simulated_ai_response": (
            "Evaluating the student's submission:\n"
            "1. Measuring from the extended deadline, the submission was 30 hours late, which incurs a 2-day penalty tier (each 24 hours or fraction thereof = 2 periods x 5% = 10% deduction).\n"
            "2. The 10% penalty deducts 10 marks from the raw score of 86, resulting in a recorded grade of 76 out of 100.\n"
            "3. If the student had submitted 125 hours after the original deadline without an extension, their submission would still be eligible for a 25% capped penalty."
        ),
        "reference_truth": (
            "Late duration from extended deadline = 54 - 24 = 30 hours. Because 30 hours spans into the second 24-hour period (24-48h tier), the deduction is 2 x 5% = 10% (Claim 1 is CORRECT). "
            "10% of 100 marks = 10 marks deducted from 86 gives 76 out of 100 (Claim 2 is CORRECT). "
            "125 hours exceeds the 120-hour (5-day) ceiling; the policy strictly mandates a mark of zero after 120 hours unless an exceptional waiver is granted (Claim 3 is INCORRECT)."
        ),
        "overall_ai_quality": "Partially Correct (Contains Policy Threshold Misapplication)",
        "claims": [
            {
                "claim_id": "SCEN_08_C1",
                "claim_text": "Measuring from the extended deadline, the submission was 30 hours late, which incurs a 2-day penalty tier (10% deduction).",
                "statement": "Measuring from the extended deadline, the submission was 30 hours late, which incurs a 2-day penalty tier (10% deduction).",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Penalty Calculation)",
                "explanation": "54 hours total - 24 hours extension = 30 hours late. Since 30 hours is between 24 and 48 hours, it incurs 2 penalty tiers of 5% = 10%.",
                "expert_explanation": "54 hours total - 24 hours extension = 30 hours late. Since 30 hours is between 24 and 48 hours, it incurs 2 penalty tiers of 5% = 10%.",
                "reference_source": "Faculty Assessment Late Submission Guidelines, Section 4.2.",
                "reference_citation": "Faculty Assessment Late Submission Guidelines, Section 4.2.",
                "rubric_keywords": ["30 hours", "54 minus 24", "2 periods", "10%", "tier"],
            },
            {
                "claim_id": "SCEN_08_C2",
                "claim_text": "The 10% penalty deducts 10 marks from the raw score of 86, resulting in a recorded grade of 76 out of 100.",
                "statement": "The 10% penalty deducts 10 marks from the raw score of 86, resulting in a recorded grade of 76 out of 100.",
                "ground_truth": "CORRECT",
                "error_category": "None (Accurate Mark Deduction)",
                "explanation": "10% of maximum 100 marks = 10 marks. 86 raw marks - 10 deduction = 76 recorded marks.",
                "expert_explanation": "10% of maximum 100 marks = 10 marks. 86 raw marks - 10 deduction = 76 recorded marks.",
                "reference_source": "Faculty Assessment Grading Computation Handbook.",
                "reference_citation": "Faculty Assessment Grading Computation Handbook.",
                "rubric_keywords": ["86 - 10", "76", "10 marks", "recorded grade", "deduction"],
            },
            {
                "claim_id": "SCEN_08_C3",
                "claim_text": "If the student had submitted 125 hours after the original deadline without an extension, their submission would still be eligible for a 25% capped penalty.",
                "statement": "If the student had submitted 125 hours after the original deadline without an extension, their submission would still be eligible for a 25% capped penalty.",
                "ground_truth": "INCORRECT",
                "error_category": "Direct Misapplication of Policy Cutoff",
                "explanation": "The policy states that after 5 days (120 hours), a mark of zero is recorded; 125 hours exceeds the 120-hour cutoff, so the submission receives 0 marks rather than the 25% cap.",
                "expert_explanation": "The policy states that after 5 days (120 hours), a mark of zero is recorded; 125 hours exceeds the 120-hour cutoff, so the submission receives 0 marks rather than the 25% cap.",
                "reference_source": "Faculty Assessment Regulations, Rule 4.4 (Zero Mark Post-120 Hours).",
                "reference_citation": "Faculty Assessment Regulations, Rule 4.4 (Zero Mark Post-120 Hours).",
                "rubric_keywords": ["120 hours", "5 days", "mark of zero", "exceeds cutoff", "ineligible for cap"],
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
            "difficulty": sc.get("difficulty", "Medium"),
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
      0 = Absent, trivial (< 12 chars), or reiterates error with no reasoning.
      1 = Partially correct intuition or identifies general issue without detailed computation/rule.
      2 = Sound, evidence-based academic justification citing relevant principles or numbers.
    """
    text = (justification or "").strip().lower()
    if len(text) < 12:
        return 0, "No substantive reasoning or justification provided."

    # Check for trivial dismissive phrases
    trivial_phrases = ["it is wrong", "it's wrong", "this is wrong", "incorrect", "false", "i guess so", "bad math", "dunno"]
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
        "weighted", "unweighted", "average", "rule", "policy", "correlation",
        "causation", "sample", "prevalence", "base rate", "hurdle", "cutoff",
        "hours", "extension", "penalty", "hallucination", "catalog"
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
        sample_keywords = claim_info.get("rubric_keywords", [
            "weighted", "unweighted", "average", "rule", "policy", "correlation",
            "causation", "sample", "prevalence", "base rate", "hurdle", "cutoff"
        ])
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
            "title": "Strengthen Step-by-Step Data & Rule Checking",
            "diagnostic": (
                f"You missed {fn} simulated AI errors (Recall = {recall:.1%}), notably in "
                f"{', '.join(missed_domains[:2]) if missed_domains else 'quantitative or policy tasks'}. "
                "AI responses frequently present flawed conclusions wrapped in fluent and confident prose."
            ),
            "action_strategy": (
                "Do not evaluate AI answers as a single holistic block. Cross-check each specific claim "
                "(e.g., tallying percentages, verifying conditional policies) independently against the provided facts."
            ),
            "action_steps": [
                "Re-calculate key numbers independently rather than accepting the AI's arithmetic.",
                "Verify whether an AI summary contradicts any explicit rule in the provided text.",
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
            "title": "Differentiate Valid Explanations from Intuitive Doubts",
            "diagnostic": (
                f"You rejected {fp} factually sound statements as errors (Precision = {precision:.1%}), "
                f"particularly in {', '.join(false_alarm_domains[:2]) if false_alarm_domains else 'control tasks'}. "
                "Overly aggressive skepticism without verifying the explicit rules can lead to discarding sound work."
            ),
            "action_strategy": (
                "Before flagging an AI statement as flawed, find the exact contradictory clause or calculation. "
                "If no concrete contradiction exists, verify against course guidelines before rejecting the step."
            ),
            "action_steps": [
                "Verify syllabus rules and grading formulas directly against official documentation.",
                "Distinguish unfamiliar wording from an actual factual error.",
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
                "Generative AI models often fabricate plausible-sounding authors, journals, and titles that do not exist."
            ),
            "action_strategy": (
                "Never cite AI-generated references without confirming them in a library catalog or academic database (e.g. Google Scholar, Scopus). "
                "Verify that the authors, year, volume, and article title match genuine publications."
            ),
            "action_steps": [
                "Search the exact paper title in the university library catalog before citing.",
                "Confirm that the cited journal and author actually published the claimed study.",
            ],
            "evidence_trace": "Missed hallucinated citation in literature scenario.",
        })

    # Rule 4: Weak Explanation Quality (Rubric < 60%)
    if rubric_score_pct < 60.0:
        feedback.append({
            "id": "FB_RUBRIC_RATIONALE",
            "category": "Critical Reasoning Articulation",
            "priority": "MEDIUM",
            "title": "Ground Critiques in Specific Evidence",
            "diagnostic": (
                f"Your written justifications earned {rubric_score_pct:.1f}% of available rubric points. "
                "Some responses stated that an answer was 'wrong' or 'incorrect' without pointing to the exact rule or number."
            ),
            "action_strategy": (
                "Practice structuring critiques with evidence: (1) Identify the flawed step; "
                "(2) Quote or cite the correct rule/number from the source; (3) State the corrected outcome."
            ),
            "action_steps": [
                "Reference the specific number or policy rule violated (e.g. 'unweighted average of 75% vs. weighted 73.3%').",
                "Write brief factual reasons rather than subjective impressions.",
            ],
            "evidence_trace": f"Rubric point capture rate = {rubric_score_pct:.1f}% (target >= 75%)",
        })

    # Rule 5: High Mastery Maintenance
    if accuracy >= 0.85 and recall >= 0.85:
        feedback.append({
            "id": "FB_CALIBRATED_MASTERY",
            "category": "Verification Excellence",
            "priority": "LOW",
            "title": "Exemplary Critical Discernment",
            "diagnostic": (
                f"You demonstrated superior evaluative precision ({accuracy:.1%} accuracy, {recall:.1%} recall), "
                "effectively catching subtle arithmetic slips, identifying fabricated citations, and recognizing sound explanations."
            ),
            "action_strategy": (
                "Maintain this rigorous verification routine when integrating generative AI into your coursework and research. "
                "Continue using independent sources to cross-check complex AI outputs."
            ),
            "action_steps": [
                "Serve as a peer reviewer or share verification tips with study partners.",
                "Structure AI prompts to explicitly ask for step-by-step reasoning that you can cross-check.",
            ],
            "evidence_trace": f"Overall Accuracy = {accuracy:.1%}, Recall = {recall:.1%}",
        })

    # Guarantee minimum 2 actionable recommendations
    if len(feedback) < 2:
        feedback.append({
            "id": "FB_GENERAL_TRIANGULATION",
            "category": "Multi-Source Verification",
            "priority": "LOW",
            "title": "Cross-Reference AI Answers with Course Materials",
            "diagnostic": "Effective learning with AI requires checking key answers against reliable primary references.",
            "action_strategy": "Always verify AI-generated summaries, formulas, and recommendations against your course lecture slides and syllabus.",
            "action_steps": ["Keep official course documentation accessible when using AI for coursework."],
            "evidence_trace": "Standard academic verification practice.",
        })

    return feedback
