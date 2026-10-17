"""
generate_synthetic_dataset.py
----------------------------------------------------------------------------
Generates a realistic, academically sound synthetic research dataset of 300
participants for Component 4:
GenAI-Assisted Cognitive Engagement & Learning Retention Evaluation.

Produces:
1. component4_master_dataset_300.csv (Merged dataset for statistical tools: SPSS, R, Python, JASP)
2. participants_300.csv (Participant demographics, group assignments)
3. brain_only_results_300.csv (Phase 1 Brain-Only condition telemetry & NLP essays)
4. genai_assisted_results_300.csv (Phase 2 GenAI-Assisted condition telemetry & NLP essays)
5. delayed_recall_results_300.csv (Phase 3 Immediate vs. Delayed Retention & Likert scales)
----------------------------------------------------------------------------
"""

import os
import csv
import json
import random
import datetime

# Seed for reproducibility
random.seed(42)

TOTAL_ROWS = 300

# Metadata distributions
UNIVERSITIES = [
    "Sri Lanka Institute of Information Technology (SLIIT)",
    "University of Colombo - UCSC",
    "University of Moratuwa",
    "University of Kelaniya",
    "Sri Lanka Technological Campus (SLTC)",
    "Informatics Institute of Technology (IIT)",
]
UNIVERSITY_WEIGHTS = [0.55, 0.15, 0.10, 0.08, 0.07, 0.05]

DEGREES = [
    "BSc (Hons) in Information Technology",
    "BSc (Hons) in Computer Science",
    "BSc (Hons) in Data Science",
    "BSc (Hons) in Software Engineering",
    "BSc (Hons) in Artificial Intelligence",
    "BBA (Hons) in Business Analytics",
]
DEGREE_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.05, 0.05]

AGE_GROUPS = ["18-24", "25-30"]
AGE_WEIGHTS = [0.88, 0.12]

GENAI_EXPERIENCES = ["Daily", "Weekly", "Occasionally", "Never"]
GENAI_EXP_WEIGHTS = [0.45, 0.35, 0.16, 0.04]

AI_TOOLS = [
    "ChatGPT (GPT-4)",
    "ChatGPT (GPT-3.5)",
    "Claude 3.5 Sonnet",
    "Google Gemini",
    "Microsoft Copilot",
]
AI_TOOL_WEIGHTS = [0.42, 0.22, 0.15, 0.13, 0.08]

AI_PURPOSES = [
    "Explanation, Summarization",
    "Concept Clarification, Code Examples",
    "Summarization, Idea Brainstorming",
    "Direct Answer Lookup, Revision",
    "Simplifying Complex Definitions",
]

# Text snippets for authentic student short-answer responses
BO_Q11_TEXTS = [
    "Technology has facilitated continuous online access to study materials through learning portals, and collaborative digital workspaces have allowed peer-to-peer discussion regardless of location.",
    "First, students can access digital textbooks and recorded lectures at any time. Second, automated testing and interactive modules give instant feedback without waiting for tutors.",
    "Distance education and remote lectures provide flexibility for working students, while online databases and scholarly search engines make research much quicker than physical libraries.",
    "E-learning platforms provide self-paced video lectures, while digital simulation tools help engineering and computing students experiment with practical concepts online.",
    "Access to vast repositories of research papers via Google Scholar has accelerated literature review, and mobile applications allow micro-learning during daily commutes.",
    "Cloud storage makes assignment sharing effortless across project teams, and online discussion forums enable students to resolve academic queries asynchronously.",
    "Interactive quiz platforms like Kahoot promote active classroom participation, and digital note-taking applications allow seamless indexing of lecture transcripts.",
    "High-speed internet access allows students to follow global academic conferences, and open educational resources (OER) reduce financial barriers to textbook access."
]

BO_Q12_TEXTS = [
    "Critical thinking prevents accepting incorrect information at face value, enabling students to evaluate credibility, detect bias, and make well-reasoned analytical choices.",
    "It is vital because misleading data and unverified sources can lead to flawed conclusions. Critical reflection allows one to cross-verify facts before making decisions.",
    "Without critical evaluation, learners become passive consumers of information. Critical thinking ensures sound judgment and systematic problem-solving in complex academic problems.",
    "Evaluating claims objectively helps identify logical fallacies, biases, and unstated assumptions, leading to robust evidence-based reasoning in research projects.",
    "Critical thinking enables students to synthesize conflicting perspectives, verify empirical evidence, and form justifiable personal stances rather than memorizing dogma.",
    "It allows learners to question assumptions, test alternative hypotheses, and select the most reliable methodology when faced with ambiguous real-world problems."
]

GA_Q11_TEXTS = [
    "Generative AI provides instant conversational explanations tailored to a student's knowledge level, and intelligent tutoring systems deliver adaptive practice exercises.",
    "Modern digital technology enables automated concept summarization through LLMs and centralized LMS platforms that monitor personal progress metrics in real time.",
    "AI assistants can break down complex mathematical proofs step-by-step, while digital collaborative tools allow real-time co-authoring of project documentation.",
    "Personalized AI learning companions generate customized flashcards and quizzes, and global video platforms allow learners to study diverse instructional perspectives.",
    "Students can use GenAI to debug programming code interactively, and online cloud laboratories make expensive hardware unnecessary for computer science experiments.",
    "Automated transcription software converts recorded lectures into searchable notes, and AI synthesis tools quickly highlight key takeaways from long research articles."
]

GA_Q12_TEXTS = [
    "Critical thinking is crucial when interacting with AI outputs because large language models can hallucinate persuasive but factually inaccurate responses.",
    "When evaluating synthetic information, critical scrutiny ensures students verify citations, check logical consistency, and avoid over-relying on automated suggestions.",
    "It prevents algorithmic bias from skewing decisions and encourages verification against peer-reviewed empirical evidence rather than blindly trusting machine output.",
    "Critical thinking maintains cognitive independence, ensuring the human learner retains intellectual agency and ownership of analytical conclusions.",
    "Because AI models generate generic or confident-sounding fabrications, rigorous critical evaluation is essential to confirm academic validity before submission."
]

def generate_dataset():
    participants = []
    brain_only = []
    genai_assisted = []
    delayed_recall = []
    master_records = []

    start_date = datetime.datetime(2026, 9, 1, 9, 0, 0)

    for i in range(1, TOTAL_ROWS + 1):
        pid = f"PID-{i:04d}"
        
        # 50% Group A (Brain-Only first), 50% Group B (GenAI-assisted first / counterbalanced)
        group = "A" if i % 2 == 1 else "B"
        sequence = "brain_only_first" if group == "A" else "genai_first"
        
        uni = random.choices(UNIVERSITIES, weights=UNIVERSITY_WEIGHTS)[0]
        degree = random.choices(DEGREES, weights=DEGREE_WEIGHTS)[0]
        age = random.choices(AGE_GROUPS, weights=AGE_WEIGHTS)[0]
        genai_exp = random.choices(GENAI_EXPERIENCES, weights=GENAI_EXP_WEIGHTS)[0]
        consent = 1
        
        mother_code = random.choice(["KA", "MA", "SA", "NU", "CH", "DI", "AN", "RO", "TH", "VI"])
        birth_year = str(random.randint(2001, 2005))
        birth_month = f"{random.randint(1, 12):02d}"
        school_code = random.choice(["AC", "DS", "RC", "TC", "MC", "VC", "KC", "IC"])
        
        reg_time = start_date + datetime.timedelta(days=(i // 15), minutes=random.randint(5, 500))
        reg_time_str = reg_time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Participant Record
        participants.append({
            "id": i,
            "participant_id": pid,
            "experiment_group": group,
            "assigned_sequence": sequence,
            "mother_code": mother_code,
            "birth_year": birth_year,
            "birth_month": birth_month,
            "school_code": school_code,
            "university_name": uni,
            "age_group": age,
            "degree_programme": degree,
            "genai_experience": genai_exp,
            "consent_given": consent,
            "registered_at": reg_time_str,
        })

        # --- Phase 1: Brain-Only Condition Metrics ---
        # Baseline study time: mean ~ 230 sec (std ~ 35)
        bo_time = round(max(120.0, min(360.0, random.gauss(225.0, 32.0))), 1)
        # Immediate Brain-only MCQ score (out of 10): mean ~ 8.1
        bo_mcq = round(max(4.0, min(10.0, random.gauss(8.1, 1.2))), 1)
        # Confidence score (1-5): mean ~ 3.8
        bo_conf = max(1, min(5, int(round(random.gauss(3.8, 0.8)))))
        # Mental effort invested (1-5): Higher in human-only mode, mean ~ 3.9
        bo_effort = max(1, min(5, int(round(random.gauss(3.9, 0.7)))))
        
        # Essays
        bo_q11 = random.choice(BO_Q11_TEXTS)
        bo_q12 = random.choice(BO_Q12_TEXTS)
        bo_answers = json.dumps({"q11": bo_q11, "q12": bo_q12})
        bo_words = len(bo_q11.split()) + len(bo_q12.split())
        bo_ttr = round(len(set((bo_q11 + " " + bo_q12).lower().split())) / bo_words, 3)

        brain_only.append({
            "id": i,
            "participant_id": pid,
            "experiment_group": group,
            "assigned_sequence": sequence,
            "topic_id": "blockchain_intro_01",
            "learning_time": bo_time,
            "mcq_score": bo_mcq,
            "short_answers": bo_answers,
            "confidence_score": bo_conf,
            "effort_score": bo_effort,
            "created_at": reg_time_str,
        })

        # --- Phase 2: GenAI-Assisted Condition Metrics ---
        # AI study time: Faster due to AI assistance, mean ~ 170 sec
        ga_time = round(max(90.0, min(300.0, random.gauss(170.0, 28.0))), 1)
        # Immediate GenAI MCQ score: High immediate success, mean ~ 8.8
        ga_mcq = round(max(5.0, min(10.0, random.gauss(8.8, 1.0))), 1)
        
        ai_tool = random.choices(AI_TOOLS, weights=AI_TOOL_WEIGHTS)[0]
        prompts = max(1, min(8, int(round(random.gauss(3.2, 1.3)))))
        purpose = random.choice(AI_PURPOSES)
        
        ga_conf = max(2, min(5, int(round(random.gauss(4.3, 0.6)))))
        ga_usefulness = max(2, min(5, int(round(random.gauss(4.4, 0.6)))))
        # Lower mental effort due to cognitive offloading, mean ~ 2.4
        ga_effort = max(1, min(4, int(round(random.gauss(2.4, 0.7)))))
        ga_explanation = max(2, min(5, int(round(random.gauss(3.9, 0.7)))))
        
        ga_q11 = random.choice(GA_Q11_TEXTS)
        ga_q12 = random.choice(GA_Q12_TEXTS)
        ga_answers = json.dumps({"q11": ga_q11, "q12": ga_q12})
        ga_words = len(ga_q11.split()) + len(ga_q12.split())
        ga_ttr = round(len(set((ga_q11 + " " + ga_q12).lower().split())) / ga_words, 3)

        genai_assisted.append({
            "id": i,
            "participant_id": pid,
            "experiment_group": group,
            "assigned_sequence": sequence,
            "topic_id": "blockchain_advanced_02",
            "learning_time": ga_time,
            "mcq_score": ga_mcq,
            "short_answers": ga_answers,
            "ai_tool": ai_tool,
            "prompt_count": prompts,
            "ai_usage_purpose": purpose,
            "confidence_score": ga_conf,
            "ai_usefulness_score": ga_usefulness,
            "effort_score": ga_effort,
            "explanation_score": ga_explanation,
            "created_at": reg_time_str,
        })

        # --- Phase 3: Delayed Recall & Cognitive Retention Evaluation ---
        # Immediate scores
        brain_imm = bo_mcq
        genai_imm = ga_mcq

        # Cognitive Ownership & Agency Likert items (1 to 5)
        # Brain condition generates higher perceived ownership and deeper reflection
        ownership = max(1, min(5, int(round(random.gauss(4.1, 0.7)))))
        explanation_autonomy = max(1, min(5, int(round(random.gauss(3.8, 0.8)))))
        # GenAI dependency (higher in students who offload more)
        dependency = max(1, min(5, int(round(random.gauss(3.6, 0.9)))))

        # Retention modeling grounded in Cognitive Offloading Theory:
        # Retention correlates with active mental effort, perceived ownership, dependency, and time
        effort_factor = (ga_effort - 2.5) * 0.06
        ownership_factor = (ownership - 3.0) * 0.05
        dep_penalty = (dependency - 3.0) * 0.08
        time_factor = ((ga_time - 170.0) / 100.0) * 0.04
        noise = random.gauss(0.0, 0.03)

        genai_retention_ratio = 0.70 + effort_factor + ownership_factor - dep_penalty + time_factor + noise
        genai_retention_ratio = max(0.40, min(0.95, genai_retention_ratio))
        genai_recall = round(max(2.0, min(genai_imm, genai_imm * genai_retention_ratio)), 1)
        genai_retention_pct = round((genai_recall / genai_imm) * 100.0, 1) if genai_imm > 0 else 0.0

        brain_recall_raw = brain_imm * max(0.60, min(1.0, random.gauss(0.85, 0.06)))
        brain_recall = round(max(3.0, min(brain_imm, brain_recall_raw)), 1)
        brain_retention_pct = round((brain_recall / brain_imm) * 100.0, 1) if brain_imm > 0 else 0.0

        # Additional cognitive effort & reflection Likert items (1-5)
        active_thought = max(1, min(5, int(round(random.gauss(3.9, 0.8)))))
        understand_concepts = max(1, min(5, int(round(random.gauss(4.0, 0.7)))))
        careful_consideration = max(1, min(5, int(round(random.gauss(3.8, 0.8)))))
        active_involvement = max(1, min(5, int(round(random.gauss(3.9, 0.7)))))
        reflected_learning = max(1, min(5, int(round(random.gauss(3.7, 0.8)))))
        mental_effort_required = max(1, min(5, int(round(random.gauss(3.6, 0.8)))))
        careful_thinking = max(1, min(5, int(round(random.gauss(3.8, 0.7)))))
        concentration = max(1, min(5, int(round(random.gauss(3.9, 0.8)))))
        mentally_demanding = max(1, min(5, int(round(random.gauss(3.4, 0.9)))))
        considerable_mental_effort = max(1, min(5, int(round(random.gauss(3.5, 0.8)))))

        delayed_recall.append({
            "id": i,
            "participant_id": pid,
            "experiment_group": group,
            "assigned_sequence": sequence,
            "brain_immediate_score": brain_imm,
            "brain_recall_score": brain_recall,
            "brain_retention_score": brain_retention_pct,
            "genai_immediate_score": genai_imm,
            "genai_recall_score": genai_recall,
            "genai_retention_score": genai_retention_pct,
            "ownership_score": ownership,
            "explanation_score": explanation_autonomy,
            "dependency_score": dependency,
            "active_thought_score": active_thought,
            "understand_concepts_score": understand_concepts,
            "careful_consideration_score": careful_consideration,
            "active_involvement_score": active_involvement,
            "reflected_learning_score": reflected_learning,
            "mental_effort_required_score": mental_effort_required,
            "careful_thinking_score": careful_thinking,
            "concentration_score": concentration,
            "mentally_demanding_score": mentally_demanding,
            "considerable_mental_effort_score": considerable_mental_effort,
            "created_at": reg_time_str,
        })

        # --- Comprehensive Master Research Row ---
        retention_diff = round(brain_retention_pct - genai_retention_pct, 1)
        master_records.append({
            "participant_id": pid,
            "experiment_group": group,
            "assigned_sequence": sequence,
            "university": uni,
            "degree_programme": degree,
            "age_group": age,
            "genai_prior_experience": genai_exp,
            "bo_learning_time_sec": bo_time,
            "bo_immediate_mcq": bo_mcq,
            "bo_confidence": bo_conf,
            "bo_mental_effort": bo_effort,
            "bo_word_count": bo_words,
            "bo_lexical_diversity_ttr": bo_ttr,
            "ga_learning_time_sec": ga_time,
            "ga_immediate_mcq": ga_mcq,
            "ga_ai_tool": ai_tool,
            "ga_prompt_count": prompts,
            "ga_ai_purpose": purpose,
            "ga_confidence": ga_conf,
            "ga_ai_usefulness": ga_usefulness,
            "ga_mental_effort": ga_effort,
            "ga_explanation_ease": ga_explanation,
            "ga_word_count": ga_words,
            "ga_lexical_diversity_ttr": ga_ttr,
            "brain_immediate_score": brain_imm,
            "brain_delayed_recall_score": brain_recall,
            "brain_retention_rate_pct": brain_retention_pct,
            "genai_immediate_score": genai_imm,
            "genai_delayed_recall_score": genai_recall,
            "genai_retention_rate_pct": genai_retention_pct,
            "retention_differential_bo_minus_ga": retention_diff,
            "cognitive_ownership_score": ownership,
            "explanation_autonomy_score": explanation_autonomy,
            "perceived_ai_dependency_score": dependency,
            "active_thought_score": active_thought,
            "understand_concepts_score": understand_concepts,
            "careful_consideration_score": careful_consideration,
            "active_involvement_score": active_involvement,
            "reflected_learning_score": reflected_learning,
            "mental_effort_required_score": mental_effort_required,
            "careful_thinking_score": careful_thinking,
            "concentration_score": concentration,
            "mentally_demanding_score": mentally_demanding,
            "considerable_mental_effort_score": considerable_mental_effort,
        })

    return participants, brain_only, genai_assisted, delayed_recall, master_records


def write_csv(filepath, rows, fieldnames):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Written: {filepath} ({len(rows)} rows)")
    except PermissionError:
        alt_path = filepath.replace(".csv", "_v2.csv")
        with open(alt_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Notice: {filepath} is open in Excel. Written to: {alt_path} ({len(rows)} rows)")


if __name__ == "__main__":
    p_data, bo_data, ga_data, dr_data, master_data = generate_dataset()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "data", "processed")
    raw_dir = os.path.join(base_dir, "data", "raw")

    # Output paths in current project
    write_csv(os.path.join(out_dir, "component4_master_dataset_300.csv"), master_data, list(master_data[0].keys()))
    write_csv(os.path.join(raw_dir, "participants_300.csv"), p_data, list(p_data[0].keys()))
    write_csv(os.path.join(raw_dir, "brain_only_results_300.csv"), bo_data, list(bo_data[0].keys()))
    write_csv(os.path.join(raw_dir, "genai_assisted_results_300.csv"), ga_data, list(ga_data[0].keys()))
    write_csv(os.path.join(raw_dir, "delayed_recall_results_300.csv"), dr_data, list(dr_data[0].keys()))

    # Also save to Research Project folder in Downloads for seamless convenience
    alt_dir = r"c:\Users\USER\Downloads\Research Project (1)\Research Project\database\synthetic_data_300"
    os.makedirs(alt_dir, exist_ok=True)
    write_csv(os.path.join(alt_dir, "component4_master_dataset_300.csv"), master_data, list(master_data[0].keys()))
    write_csv(os.path.join(alt_dir, "participants_300.csv"), p_data, list(p_data[0].keys()))
    write_csv(os.path.join(alt_dir, "brain_only_results_300.csv"), bo_data, list(bo_data[0].keys()))
    write_csv(os.path.join(alt_dir, "genai_assisted_results_300.csv"), ga_data, list(ga_data[0].keys()))
    write_csv(os.path.join(alt_dir, "delayed_recall_results_300.csv"), dr_data, list(dr_data[0].keys()))

    print("\nSuccessfully generated all 300-row synthetic datasets!")
