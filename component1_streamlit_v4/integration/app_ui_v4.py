"""
app_ui_v4.py
============
Student-Friendly Interactive Self-Reflection Application for Component 1 (Version 4):
Explainable Cognitive Offloading Risk Model Among Undergraduate Students (J26-DS-310).

Usage:
------
    python3 -m streamlit run app_ui_v4.py --server.port 8501
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd
import numpy as np

# Ensure integration service is discoverable
INTEGRATION_DIR = Path(__file__).resolve().parent
if str(INTEGRATION_DIR) not in sys.path:
    sys.path.append(str(INTEGRATION_DIR))

from integration_service_v4 import (
    get_predictor_v4,
    DISCLAIMER,
    FEATURE_HUMAN_LABELS,
    FEATURE_PLAIN_EXPLANATIONS
)

# -----------------------------------------------------------------------------
# Streamlit App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-Assisted Learning Self-Reflection | J26-DS-310",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Clean Modern Styling (CSS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Main container and typography */
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header hero styling */
    .hero-container {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #cbd5e1;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.4rem;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 0.8rem;
    }
    
    /* Step progress bar container */
    .step-pill {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .step-active {
        background-color: #2563eb;
        color: #ffffff;
    }
    .step-done {
        background-color: #e2e8f0;
        color: #334155;
    }
    .step-pending {
        background-color: #f1f5f9;
        color: #94a3b8;
    }
    
    /* Question card */
    .question-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .question-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.3rem;
    }
    .question-desc {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 0.8rem;
    }

    /* Result Cards */
    .result-card-low {
        background-color: #f0fdf4;
        border: 2px solid #86efac;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
    }
    .result-card-med {
        background-color: #fffbeb;
        border: 2px solid #fde047;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
    }
    .result-card-high {
        background-color: #fef2f2;
        border: 2px solid #fca5a5;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
    }
    
    /* SHAP factor badge */
    .factor-badge-mitigate {
        border-left: 4px solid #16a34a;
        background-color: #f0fdf4;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin-bottom: 0.6rem;
    }
    .factor-badge-increase {
        border-left: 4px solid #dc2626;
        background-color: #fef2f2;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin-bottom: 0.6rem;
    }
    
    /* Footer research note */
    .research-note {
        font-size: 0.82rem;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        padding-top: 1rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Singleton Model Loader
# -----------------------------------------------------------------------------
@st.cache_resource
def load_predictor():
    return get_predictor_v4()

predictor = load_predictor()

# -----------------------------------------------------------------------------
# Presets Data for Quick Evaluation / Testing
# -----------------------------------------------------------------------------
PRESETS_DATA = {
    "Low-Risk Student Profile": {
        "degree_field": "Natural & Applied Sciences",
        "academic_year": 3,
        "age_group": 2,
        "ai_usage_freq": 1,
        "ai_time_per_week": 1,
        "tools_used": ["ChatGPT"],
        "Q20_task_delegation_freq": 1,
        "tasks_delegated": ["Explaining difficult concepts"],
        "Q1_direct_use_freq": 1,
        "Q22_effort_on_ai_answers": 5,
        "Q2_verify_info": 5,
        "Q3_compare_sources": 5,
        "Q4_check_accuracy": 5,
        "Q5_understand_reasoning": 5,
        "Q6_modify_content": 5,
        "Q7_attempt_independently": 5,
        "Q8_complete_without_ai": 5,
        "Q9_learning_assistant": 5,
        "Q30_trust_accuracy": 2,
        "Q33_trust_appropriate_support": 2
    },
    "Medium-Risk Student Profile": {
        "degree_field": "Computer Science / IT",
        "academic_year": 2,
        "age_group": 2,
        "ai_usage_freq": 2,
        "ai_time_per_week": 3,
        "tools_used": ["ChatGPT", "Google Gemini"],
        "Q20_task_delegation_freq": 3,
        "tasks_delegated": ["Explaining difficult concepts", "Summarising reading materials"],
        "Q1_direct_use_freq": 3,
        "Q22_effort_on_ai_answers": 3,
        "Q2_verify_info": 3,
        "Q3_compare_sources": 3,
        "Q4_check_accuracy": 3,
        "Q5_understand_reasoning": 3,
        "Q6_modify_content": 3,
        "Q7_attempt_independently": 3,
        "Q8_complete_without_ai": 3,
        "Q9_learning_assistant": 3,
        "Q30_trust_accuracy": 3,
        "Q33_trust_appropriate_support": 3
    },
    "High-Risk Student Profile (Extreme)": {
        "degree_field": "Business / Economics",
        "academic_year": 1,
        "age_group": 1,
        "ai_usage_freq": 4,
        "ai_time_per_week": 5,
        "tools_used": ["ChatGPT", "Claude", "Perplexity AI"],
        "Q20_task_delegation_freq": 5,
        "tasks_delegated": [
            "Writing assignments or essays",
            "Summarising reading materials",
            "Programming and coding solutions",
            "Mathematical and calculation problems"
        ],
        "Q1_direct_use_freq": 5,
        "Q22_effort_on_ai_answers": 1,
        "Q2_verify_info": 1,
        "Q3_compare_sources": 1,
        "Q4_check_accuracy": 1,
        "Q5_understand_reasoning": 1,
        "Q6_modify_content": 1,
        "Q7_attempt_independently": 1,
        "Q8_complete_without_ai": 1,
        "Q9_learning_assistant": 1,
        "Q30_trust_accuracy": 5,
        "Q33_trust_appropriate_support": 5
    },
    "Borderline Low/Medium (Score ~2.59)": {
        "degree_field": "Natural & Applied Sciences",
        "academic_year": 2,
        "age_group": 2,
        "ai_usage_freq": 2,
        "ai_time_per_week": 2,
        "tools_used": ["ChatGPT"],
        "Q20_task_delegation_freq": 2,
        "tasks_delegated": ["Explaining difficult concepts"],
        "Q1_direct_use_freq": 2,
        "Q22_effort_on_ai_answers": 3,
        "Q2_verify_info": 4,
        "Q3_compare_sources": 4,
        "Q4_check_accuracy": 4,
        "Q5_understand_reasoning": 4,
        "Q6_modify_content": 4,
        "Q7_attempt_independently": 4,
        "Q8_complete_without_ai": 3,
        "Q9_learning_assistant": 4,
        "Q30_trust_accuracy": 3,
        "Q33_trust_appropriate_support": 3
    },
    "Borderline Medium/High (Score ~3.39)": {
        "degree_field": "Computer Science / IT",
        "academic_year": 3,
        "age_group": 2,
        "ai_usage_freq": 3,
        "ai_time_per_week": 4,
        "tools_used": ["ChatGPT", "Microsoft Copilot"],
        "Q20_task_delegation_freq": 4,
        "tasks_delegated": ["Writing assignments or essays", "Programming and coding solutions"],
        "Q1_direct_use_freq": 3,
        "Q22_effort_on_ai_answers": 3,
        "Q2_verify_info": 3,
        "Q3_compare_sources": 3,
        "Q4_check_accuracy": 3,
        "Q5_understand_reasoning": 3,
        "Q6_modify_content": 3,
        "Q7_attempt_independently": 3,
        "Q8_complete_without_ai": 3,
        "Q9_learning_assistant": 3,
        "Q30_trust_accuracy": 4,
        "Q33_trust_appropriate_support": 3
    },
    "Simulate Incomplete / Empty Input": {},
    "Simulate Dirty Input (NaN/Inf/Out-of-Range)": {
        "ai_usage_freq": "daily",
        "Q1_direct_use_freq": 99.0,
        "Q8_complete_without_ai": -10.0,
        "Q20_task_delegation_freq": "unparseable_text_token",
        "ai_time_per_week": float("inf"),
        "idx_delegation_intensity": float("nan")
    }
}

# -----------------------------------------------------------------------------
# UI-Only Input Keys (Preserved for review/display, isolated from ML model)
# -----------------------------------------------------------------------------
UI_ONLY_KEYS = {"specific_degree_programme", "other_academic_field"}

def get_model_inputs(answers_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out UI-only fields before sending payload to the inference service."""
    return {k: v for k, v in answers_dict.items() if k not in UI_ONLY_KEYS}

# -----------------------------------------------------------------------------
# Blank Initial State & Validation Helpers
# -----------------------------------------------------------------------------
# Every questionnaire input begins completely unanswered.
# No plausible defaults, implicit answers, or hardcoded values are preselected.
BLANK_ANSWERS = {
    # Section 1: AI Usage Habits & Academic Context
    "degree_field": None,
    "specific_degree_programme": "",
    "other_academic_field": "",
    "academic_year": None,
    "age_group": None,
    "ai_usage_freq": None,
    "ai_time_per_week": None,
    "tools_used": [],
    # Section 2: Task Delegation & Content Use
    "Q20_task_delegation_freq": None,
    "tasks_delegated": [],
    "Q1_direct_use_freq": None,
    "Q22_effort_on_ai_answers": None,
    # Section 3: Verification & Critical Thinking
    "Q2_verify_info": None,
    "Q3_compare_sources": None,
    "Q4_check_accuracy": None,
    "Q5_understand_reasoning": None,
    "Q6_modify_content": None,
    # Section 4: Independent Learning & Trust in AI
    "Q7_attempt_independently": None,
    "Q8_complete_without_ai": None,
    "Q9_learning_assistant": None,
    "Q30_trust_accuracy": None,
    "Q33_trust_appropriate_support": None
}

# DEFAULT_ANSWERS is aliased to BLANK_ANSWERS so tests and fresh sessions start genuinely blank
DEFAULT_ANSWERS = dict(BLANK_ANSWERS)

# Sample profile for explicit evaluation testing (used only when requested via Load Sample Profile)
SAMPLE_STUDENT_PROFILE = dict(PRESETS_DATA["Medium-Risk Student Profile"])

LIKERT_5_AGREEMENT = {
    1: "1 — Strongly Disagree",
    2: "2 — Disagree",
    3: "3 — Neutral",
    4: "4 — Agree",
    5: "5 — Strongly Agree"
}

def render_likert_radio(label: str, desc: str, key_name: str, cur_val: Optional[int]) -> Optional[int]:
    """Render a 5-point Likert scale radio question with no default selection."""
    opt_keys = list(LIKERT_5_AGREEMENT.keys())
    cur_idx = opt_keys.index(cur_val) if cur_val in opt_keys else None
    st.markdown(f"**{label} ***")
    st.caption(desc)
    return st.radio(
        label=f"Rating for {key_name}",
        options=opt_keys,
        format_func=lambda x: LIKERT_5_AGREEMENT[x],
        index=cur_idx,
        horizontal=True,
        key=f"radio_{key_name}",
        label_visibility="collapsed"
    )

def get_missing_required_fields(answers: Dict[str, Any]) -> List[str]:
    """Identify any required questionnaire inputs that have not been answered."""
    missing = []
    if not answers.get("degree_field"):
        missing.append("Section 1: Academic Field / Discipline")
    if answers.get("academic_year") is None:
        missing.append("Section 1: Current Academic Year")
    if answers.get("age_group") is None:
        missing.append("Section 1: Age Bracket")
    if answers.get("ai_usage_freq") is None:
        missing.append("Section 1: AI Usage Frequency")
    if answers.get("ai_time_per_week") is None:
        missing.append("Section 1: Weekly AI Usage Time")
    if not answers.get("tools_used"):
        missing.append("Section 1: Generative AI Tools Used (at least one tool)")

    if answers.get("Q20_task_delegation_freq") is None:
        missing.append("Section 2: Task Delegation Frequency")
    if answers.get("Q1_direct_use_freq") is None:
        missing.append("Section 2: Direct Use / Copying Frequency")
    if answers.get("Q22_effort_on_ai_answers") is None:
        missing.append("Section 2: Effort Spent Reviewing AI Answers")

    if answers.get("Q2_verify_info") is None:
        missing.append("Section 3: External Source Verification")
    if answers.get("Q3_compare_sources") is None:
        missing.append("Section 3: Coursework & Lecture Comparison")
    if answers.get("Q4_check_accuracy") is None:
        missing.append("Section 3: Accuracy Checking")
    if answers.get("Q5_understand_reasoning") is None:
        missing.append("Section 3: Understanding Underlying Reasoning")
    if answers.get("Q6_modify_content") is None:
        missing.append("Section 3: Content Personalization & Synthesis")

    if answers.get("Q7_attempt_independently") is None:
        missing.append("Section 4: Attempting Coursework Independently First")
    if answers.get("Q8_complete_without_ai") is None:
        missing.append("Section 4: Confidence in Completing Work Without AI")
    if answers.get("Q9_learning_assistant") is None:
        missing.append("Section 4: Assistant vs Replacement Mindset")
    if answers.get("Q30_trust_accuracy") is None:
        missing.append("Section 4: Belief in AI Factual Accuracy")
    if answers.get("Q33_trust_appropriate_support") is None:
        missing.append("Section 4: Trust in AI Academic Guidance")

    return missing

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "answers" not in st.session_state:
    st.session_state.answers = dict(BLANK_ANSWERS)

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

# -----------------------------------------------------------------------------
# Sidebar: Examiner & Testing Tools (Collapsed Expander)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Evaluation Panel")
    with st.expander("🧪 Examiner & Research Tools", expanded=False):
        st.markdown(
            "Quickly load test profiles or simulate edge cases to inspect "
            "model responses, thresholds, clamping, and SHAP outputs."
        )
        selected_preset = st.selectbox(
            "Select Benchmark Scenario",
            options=list(PRESETS_DATA.keys()),
            index=0
        )
        col_load, col_eval = st.columns(2)
        with col_load:
            if st.button("Load Profile", use_container_width=True):
                st.session_state.answers = dict(PRESETS_DATA[selected_preset])
                st.session_state.page = "review"
                st.rerun()
        with col_eval:
            if st.button("Evaluate Now", type="primary", use_container_width=True):
                st.session_state.answers = dict(PRESETS_DATA[selected_preset])
                model_payload = get_model_inputs(st.session_state.answers)
                res = predictor.predict(model_payload, top_factors_count=5)
                st.session_state.prediction_result = res
                st.session_state.page = "results"
                st.rerun()

        st.markdown("---")
        st.caption(
            "**Architecture:** Thresholded Ridge (Ordinal)\n"
            "- Cross-validation: 25-fold Repeated Stratified CV\n"
            "- Thresholds: cut1=2.667, cut2=3.500\n"
            "- Latent bound: [1.0, 5.0]\n"
            "- Explainability: LinearSHAP exact attribution"
        )

# -----------------------------------------------------------------------------
# Reusable UI Helpers
# -----------------------------------------------------------------------------
def render_progress(step_index: int):
    """Render a clean multi-step breadcrumb bar."""
    steps = [
        ("1", "AI Usage Habits"),
        ("2", "Task Delegation"),
        ("3", "Verification & Critical Thinking"),
        ("4", "Independent Learning"),
        ("Review", "Summary"),
        ("Results", "Self-Reflection")
    ]
    cols = st.columns(len(steps))
    for idx, (s_num, s_name) in enumerate(steps):
        with cols[idx]:
            if idx == step_index:
                st.markdown(f"<span class='step-pill step-active'>{s_num}. {s_name}</span>", unsafe_allow_html=True)
            elif idx < step_index:
                st.markdown(f"<span class='step-pill step-done'>✓ {s_name}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='step-pill step-pending'>{s_num}. {s_name}</span>", unsafe_allow_html=True)
    st.progress((step_index + 1) / len(steps))

# =============================================================================
# PAGE: HOME / WELCOME
# =============================================================================
if st.session_state.page == "home":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🎓 AI-Assisted Learning Self-Reflection</div>
        <div class="hero-subtitle">
            Understand your generative AI study habits, maintain your cognitive autonomy, and build deeper problem-solving skills.
        </div>
        <div style="font-size: 0.95rem; color: #475569; line-height: 1.5;">
            Generative AI tools like ChatGPT, Gemini, and Copilot can be powerful study companions. 
            However, research shows that relying on AI to perform analytical thinking for you—a process known as 
            <b>cognitive offloading</b>—can inadvertently bypass the productive mental effort needed for long-term learning.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="question-card">
            <h4>⏱️ Quick & Simple</h4>
            <p style="color:#64748b; font-size:0.9rem;">
                Takes approximately <b>3 minutes</b> to complete across 4 structured sections.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="question-card">
            <h4>🔒 Anonymous & Safe</h4>
            <p style="color:#64748b; font-size:0.9rem;">
                No names, emails, or student IDs are collected. Your answers are processed in memory for immediate personal feedback.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="question-card">
            <h4>💡 Actionable Insights</h4>
            <p style="color:#64748b; font-size:0.9rem;">
                Receive transparent feedback on which specific habits support your independence and ideas to strengthen your critical thinking.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    c_btn1, c_btn2, _ = st.columns([1.5, 1.5, 3])
    with c_btn1:
        if st.button("🚀 Begin Reflection", type="primary", use_container_width=True):
            st.session_state.page = "section_1"
            st.rerun()
    with c_btn2:
        if st.button("📋 Load Sample Profile", use_container_width=True):
            st.session_state.answers = dict(PRESETS_DATA["Medium-Risk Student Profile"])
            st.session_state.page = "section_1"
            st.rerun()

    st.markdown(f"<div class='research-note'><b>Research Notice:</b> {DISCLAIMER}</div>", unsafe_allow_html=True)

# =============================================================================
# PAGE: SECTION 1 — AI USAGE HABITS
# =============================================================================
elif st.session_state.page == "section_1":
    render_progress(0)
    st.subheader("Section 1 of 4: AI Usage Habits & Academic Context")
    st.caption("Tell us a little about your university studies and how often you interact with Generative AI.")

    ans = st.session_state.answers

    # 1. Academic Field / Discipline (Required)
    degree_options = [
        "Computer Science / IT",
        "Engineering",
        "Business / Economics",
        "Natural & Applied Sciences",
        "Humanities / Social Sciences / Health",
        "Other"
    ]
    cur_deg = ans.get("degree_field")
    deg_idx = degree_options.index(cur_deg) if cur_deg in degree_options else None
    sel_degree = st.selectbox(
        "1. Academic Field / Discipline *",
        options=degree_options,
        index=deg_idx,
        placeholder="Select your academic field...",
        help="Select the broad field that best matches your studies or faculty."
    )

    # Optional: If "Other" is selected, display a text input to specify their academic field
    if sel_degree == "Other":
        cur_other_field = ans.get("other_academic_field", "")
        sel_other_field = st.text_input(
            "Specify Academic Field (Optional)",
            value=cur_other_field,
            placeholder="e.g., Law, Architecture, Education, Design",
            help="Optional: Specify your academic field or faculty."
        )
    else:
        sel_other_field = ""

    # Optional: Separate text input for specific degree programme
    cur_specific_degree = ans.get("specific_degree_programme", "")
    sel_specific_degree = st.text_input(
        "Specific Degree Programme (Optional)",
        value=cur_specific_degree,
        placeholder="e.g., BSc in Data Science, BSc in Software Engineering",
        help="Optional: Enter your specific degree or major title."
    )

    # Year & Age (Required)
    c_yr, c_age = st.columns(2)
    with c_yr:
        year_options = {
            1: "1st Year (Freshman)",
            2: "2nd Year (Sophomore)",
            3: "3rd Year (Junior)",
            4: "4th Year (Senior)",
            5: "5th Year",
            6: "Postgraduate"
        }
        cur_yr = ans.get("academic_year")
        yr_idx = list(year_options.keys()).index(cur_yr) if cur_yr in year_options else None
        sel_year = st.selectbox(
            "2. Current Academic Year *",
            options=list(year_options.keys()),
            format_func=lambda x: year_options[x],
            index=yr_idx,
            placeholder="Select academic year..."
        )

    with c_age:
        age_options = {
            1: "18–20 years",
            2: "21–23 years",
            3: "24–26 years",
            4: "27 or above"
        }
        cur_age = ans.get("age_group")
        age_idx = list(age_options.keys()).index(cur_age) if cur_age in age_options else None
        sel_age = st.selectbox(
            "3. Age Bracket *",
            options=list(age_options.keys()),
            format_func=lambda x: age_options[x],
            index=age_idx,
            placeholder="Select age bracket..."
        )

    # Usage frequency (Required)
    freq_options = {
        1: "Rarely (less than once a week)",
        2: "Sometimes (1–3 times per week)",
        3: "Frequently (4–6 times per week)",
        4: "Daily"
    }
    cur_freq = ans.get("ai_usage_freq")
    freq_idx = list(freq_options.keys()).index(cur_freq) if cur_freq in freq_options else None
    sel_freq = st.radio(
        "4. How often do you typically use Generative AI tools for your academic studies? *",
        options=list(freq_options.keys()),
        format_func=lambda x: freq_options[x],
        index=freq_idx
    )

    # Weekly time (Required)
    time_options = {
        1: "Less than 1 hour per week",
        2: "1–3 hours per week",
        3: "4–6 hours per week",
        4: "7–10 hours per week",
        5: "More than 10 hours per week"
    }
    cur_time = ans.get("ai_time_per_week")
    time_idx = list(time_options.keys()).index(cur_time) if cur_time in time_options else None
    sel_time = st.selectbox(
        "5. Approximately how much time do you spend using AI tools per week? *",
        options=list(time_options.keys()),
        format_func=lambda x: time_options[x],
        index=time_idx,
        placeholder="Select weekly time..."
    )

    # Tools used (Multi-select, Required: at least one tool)
    all_tools = ["ChatGPT", "Google Gemini", "Microsoft Copilot", "Claude", "Perplexity AI"]
    cur_tools = ans.get("tools_used") or []
    sel_tools = st.multiselect(
        "6. Which Generative AI tools do you actively use? * (Select all that apply)",
        options=all_tools,
        default=[t for t in cur_tools if t in all_tools],
        placeholder="Select all AI tools you use..."
    )

    # Navigation buttons
    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_next = st.columns([1, 1])
    with c_back:
        if st.button("⬅️ Back to Home"):
            # Preserve current answers
            st.session_state.answers["degree_field"] = sel_degree
            st.session_state.answers["other_academic_field"] = sel_other_field.strip() if sel_other_field else ""
            st.session_state.answers["specific_degree_programme"] = sel_specific_degree.strip() if sel_specific_degree else ""
            st.session_state.answers["academic_year"] = sel_year
            st.session_state.answers["age_group"] = sel_age
            st.session_state.answers["ai_usage_freq"] = sel_freq
            st.session_state.answers["ai_time_per_week"] = sel_time
            st.session_state.answers["tools_used"] = sel_tools
            st.session_state.page = "home"
            st.rerun()
    with c_next:
        if st.button("Next: Task Delegation ➡️", type="primary"):
            # Preserve current answers
            st.session_state.answers["degree_field"] = sel_degree
            st.session_state.answers["other_academic_field"] = sel_other_field.strip() if sel_other_field else ""
            st.session_state.answers["specific_degree_programme"] = sel_specific_degree.strip() if sel_specific_degree else ""
            st.session_state.answers["academic_year"] = sel_year
            st.session_state.answers["age_group"] = sel_age
            st.session_state.answers["ai_usage_freq"] = sel_freq
            st.session_state.answers["ai_time_per_week"] = sel_time
            st.session_state.answers["tools_used"] = sel_tools

            # Validate Section 1 required fields
            missing_in_s1 = []
            if not sel_degree:
                missing_in_s1.append("1. Academic Field / Discipline")
            if sel_year is None:
                missing_in_s1.append("2. Current Academic Year")
            if sel_age is None:
                missing_in_s1.append("3. Age Bracket")
            if sel_freq is None:
                missing_in_s1.append("4. AI Usage Frequency")
            if sel_time is None:
                missing_in_s1.append("5. Weekly AI Usage Time")
            if not sel_tools:
                missing_in_s1.append("6. Generative AI Tools Used (select at least one tool)")

            if missing_in_s1:
                st.error("⚠️ **Please answer the following required question(s) before proceeding:**\n\n" + "\n".join(f"- {item}" for item in missing_in_s1))
            else:
                st.session_state.page = "section_2"
                st.rerun()

# =============================================================================
# PAGE: SECTION 2 — ACADEMIC TASK DELEGATION
# =============================================================================
elif st.session_state.page == "section_2":
    render_progress(1)
    st.subheader("Section 2 of 4: Academic Task Delegation & Content Use")
    st.caption("Investigate how tasks are shared between you and AI tools during assignments.")

    ans = st.session_state.answers

    # 1. Task delegation frequency (Required)
    likert_5_freq = {
        1: "Never (1)",
        2: "Rarely (2)",
        3: "Sometimes (3)",
        4: "Often (4)",
        5: "Very Often (5)"
    }
    cur_q20 = ans.get("Q20_task_delegation_freq")
    q20_idx = list(likert_5_freq.keys()).index(cur_q20) if cur_q20 in likert_5_freq else None
    sel_q20 = st.radio(
        "1. How often do you ask Generative AI to solve or complete entire coursework tasks for you? *",
        options=list(likert_5_freq.keys()),
        format_func=lambda x: likert_5_freq[x],
        index=q20_idx,
        help="Delegating entire tasks shifts active reasoning from you to the software."
    )

    # 2. Delegated task types (Multi-select, Optional)
    all_tasks = [
        "Writing assignments or essays",
        "Explaining difficult concepts",
        "Summarising reading materials",
        "Creating presentation slides",
        "Programming and coding solutions",
        "Mathematical and calculation problems"
    ]
    cur_tasks = ans.get("tasks_delegated") or []
    sel_tasks = st.multiselect(
        "2. Which kinds of coursework tasks do you ask AI to assist with? (Optional — select all that apply)",
        options=all_tasks,
        default=[t for t in cur_tasks if t in all_tasks],
        placeholder="Select tasks you delegate (optional)..."
    )

    # 3. Direct use frequency (Required)
    direct_options = {
        1: "Never (1) — I always write in my own words",
        2: "Rarely (2) — I heavily edit and rewrite",
        3: "Sometimes (3) — I combine AI text with my own writing",
        4: "Often (4) — I use AI output with minor edits",
        5: "Always (5) — I copy and submit directly"
    }
    cur_q1 = ans.get("Q1_direct_use_freq")
    q1_idx = list(direct_options.keys()).index(cur_q1) if cur_q1 in direct_options else None
    sel_q1 = st.radio(
        "3. How often do you directly use or submit AI-generated answers with minimal or no editing? *",
        options=list(direct_options.keys()),
        format_func=lambda x: direct_options[x],
        index=q1_idx
    )

    # 4. Effort reviewing answers (Required)
    effort_options = {
        1: "No effort (1) — Accept answer without review",
        2: "Little effort (2) — Quick skim read",
        3: "Moderate effort (3) — Read through and check main points",
        4: "High effort (4) — Thoroughly check details and rewrite sections",
        5: "Very high effort (5) — Rigorously audit, test, and verify every point"
    }
    cur_q22 = ans.get("Q22_effort_on_ai_answers")
    q22_idx = list(effort_options.keys()).index(cur_q22) if cur_q22 in effort_options else None
    sel_q22 = st.radio(
        "4. How much effort do you invest in analyzing, verifying, and improving AI answers? *",
        options=list(effort_options.keys()),
        format_func=lambda x: effort_options[x],
        index=q22_idx
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_next = st.columns([1, 1])
    with c_back:
        if st.button("⬅️ Back to Section 1"):
            # Preserve current Section 2 inputs
            st.session_state.answers["Q20_task_delegation_freq"] = sel_q20
            st.session_state.answers["tasks_delegated"] = sel_tasks
            st.session_state.answers["Q1_direct_use_freq"] = sel_q1
            st.session_state.answers["Q22_effort_on_ai_answers"] = sel_q22
            st.session_state.page = "section_1"
            st.rerun()
    with c_next:
        if st.button("Next: Critical Thinking ➡️", type="primary"):
            # Preserve current Section 2 inputs
            st.session_state.answers["Q20_task_delegation_freq"] = sel_q20
            st.session_state.answers["tasks_delegated"] = sel_tasks
            st.session_state.answers["Q1_direct_use_freq"] = sel_q1
            st.session_state.answers["Q22_effort_on_ai_answers"] = sel_q22

            # Validate Section 2 required fields
            missing_in_s2 = []
            if sel_q20 is None:
                missing_in_s2.append("1. Task Delegation Frequency (delegating complete tasks)")
            if sel_q1 is None:
                missing_in_s2.append("3. Direct Use / Copying Frequency")
            if sel_q22 is None:
                missing_in_s2.append("4. Effort Spent Reviewing and Improving AI Answers")

            if missing_in_s2:
                st.error("⚠️ **Please answer the following required question(s) before proceeding:**\n\n" + "\n".join(f"- {item}" for item in missing_in_s2))
            else:
                st.session_state.page = "section_3"
                st.rerun()

# =============================================================================
# PAGE: SECTION 3 — VERIFICATION & CRITICAL THINKING
# =============================================================================
elif st.session_state.page == "section_3":
    render_progress(2)
    st.subheader("Section 3 of 4: Verification & Critical Thinking")
    st.caption("Active verification is the strongest protection against cognitive offloading.")

    ans = st.session_state.answers
    sel_q2 = render_likert_radio(
        "1. External Source Verification",
        "I actively verify facts and claims made by AI against external textbooks, lecture slides, or papers.",
        "Q2_verify_info",
        ans.get("Q2_verify_info")
    )

    sel_q3 = render_likert_radio(
        "2. Coursework Comparison",
        "I cross-reference AI-generated solutions with my official course syllabus and lecture materials.",
        "Q3_compare_sources",
        ans.get("Q3_compare_sources")
    )

    sel_q4 = render_likert_radio(
        "3. Accuracy Checking",
        "I actively check whether AI formulas, calculations, or code outputs are factually correct.",
        "Q4_check_accuracy",
        ans.get("Q4_check_accuracy")
    )

    sel_q5 = render_likert_radio(
        "4. Understanding the Reasoning",
        "Before using an AI output, I make sure I personally understand the underlying logic and steps.",
        "Q5_understand_reasoning",
        ans.get("Q5_understand_reasoning")
    )

    sel_q6 = render_likert_radio(
        "5. Content Personalization & Synthesis",
        "I adapt and rewrite AI outputs into my own academic voice and perspective.",
        "Q6_modify_content",
        ans.get("Q6_modify_content")
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_next = st.columns([1, 1])
    with c_back:
        if st.button("⬅️ Back to Section 2"):
            # Preserve current Section 3 inputs
            st.session_state.answers["Q2_verify_info"] = sel_q2
            st.session_state.answers["Q3_compare_sources"] = sel_q3
            st.session_state.answers["Q4_check_accuracy"] = sel_q4
            st.session_state.answers["Q5_understand_reasoning"] = sel_q5
            st.session_state.answers["Q6_modify_content"] = sel_q6
            st.session_state.page = "section_2"
            st.rerun()
    with c_next:
        if st.button("Next: Independent Learning ➡️", type="primary"):
            # Preserve current Section 3 inputs
            st.session_state.answers["Q2_verify_info"] = sel_q2
            st.session_state.answers["Q3_compare_sources"] = sel_q3
            st.session_state.answers["Q4_check_accuracy"] = sel_q4
            st.session_state.answers["Q5_understand_reasoning"] = sel_q5
            st.session_state.answers["Q6_modify_content"] = sel_q6

            # Validate Section 3 required fields
            missing_in_s3 = []
            if sel_q2 is None:
                missing_in_s3.append("1. External Source Verification")
            if sel_q3 is None:
                missing_in_s3.append("2. Coursework Comparison")
            if sel_q4 is None:
                missing_in_s3.append("3. Accuracy Checking")
            if sel_q5 is None:
                missing_in_s3.append("4. Understanding the Reasoning")
            if sel_q6 is None:
                missing_in_s3.append("5. Content Personalization & Synthesis")

            if missing_in_s3:
                st.error("⚠️ **Please answer the following required question(s) before proceeding:**\n\n" + "\n".join(f"- {item}" for item in missing_in_s3))
            else:
                st.session_state.page = "section_4"
                st.rerun()

# =============================================================================
# PAGE: SECTION 4 — INDEPENDENT LEARNING & AUTONOMY
# =============================================================================
elif st.session_state.page == "section_4":
    render_progress(3)
    st.subheader("Section 4 of 4: Independent Learning & Trust in AI")
    st.caption("Examine your confidence in working independently and how much you trust AI outputs.")

    ans = st.session_state.answers

    sel_q7 = render_likert_radio(
        "1. Independent Problem-Solving First",
        "I always attempt to solve coursework questions or draft ideas on my own before opening an AI tool.",
        "Q7_attempt_independently",
        ans.get("Q7_attempt_independently")
    )

    sel_q8 = render_likert_radio(
        "2. Confidence in Completing Work Without AI",
        "If AI tools were completely unavailable tomorrow, I am confident I could complete all my assignments successfully.",
        "Q8_complete_without_ai",
        ans.get("Q8_complete_without_ai")
    )

    sel_q9 = render_likert_radio(
        "3. Assistant vs. Replacement Mindset",
        "I view generative AI strictly as an auxiliary assistant, never as a replacement for my own critical thinking.",
        "Q9_learning_assistant",
        ans.get("Q9_learning_assistant")
    )

    sel_q30 = render_likert_radio(
        "4. Belief in AI Accuracy",
        "I generally assume that information generated by generative AI is accurate and trustworthy.",
        "Q30_trust_accuracy",
        ans.get("Q30_trust_accuracy")
    )

    sel_q33 = render_likert_radio(
        "5. Trust in AI Guidance",
        "I trust that generative AI gives me the most appropriate academic guidance for my coursework.",
        "Q33_trust_appropriate_support",
        ans.get("Q33_trust_appropriate_support")
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_next = st.columns([1, 1])
    with c_back:
        if st.button("⬅️ Back to Section 3"):
            # Preserve current Section 4 inputs
            st.session_state.answers["Q7_attempt_independently"] = sel_q7
            st.session_state.answers["Q8_complete_without_ai"] = sel_q8
            st.session_state.answers["Q9_learning_assistant"] = sel_q9
            st.session_state.answers["Q30_trust_accuracy"] = sel_q30
            st.session_state.answers["Q33_trust_appropriate_support"] = sel_q33
            st.session_state.page = "section_3"
            st.rerun()
    with c_next:
        if st.button("Review Your Answers ➡️", type="primary"):
            # Preserve current Section 4 inputs
            st.session_state.answers["Q7_attempt_independently"] = sel_q7
            st.session_state.answers["Q8_complete_without_ai"] = sel_q8
            st.session_state.answers["Q9_learning_assistant"] = sel_q9
            st.session_state.answers["Q30_trust_accuracy"] = sel_q30
            st.session_state.answers["Q33_trust_appropriate_support"] = sel_q33

            # Validate Section 4 required fields
            missing_in_s4 = []
            if sel_q7 is None:
                missing_in_s4.append("1. Independent Problem-Solving First")
            if sel_q8 is None:
                missing_in_s4.append("2. Confidence in Completing Work Without AI")
            if sel_q9 is None:
                missing_in_s4.append("3. Assistant vs. Replacement Mindset")
            if sel_q30 is None:
                missing_in_s4.append("4. Belief in AI Accuracy")
            if sel_q33 is None:
                missing_in_s4.append("5. Trust in AI Guidance")

            if missing_in_s4:
                st.error("⚠️ **Please answer the following required question(s) before proceeding:**\n\n" + "\n".join(f"- {item}" for item in missing_in_s4))
            else:
                st.session_state.page = "review"
                st.rerun()

# =============================================================================
# PAGE: REVIEW SUMMARY SCREEN
# =============================================================================
elif st.session_state.page == "review":
    render_progress(4)
    st.subheader("📋 Review Your Answers Before Submitting")
    st.caption("Check your responses below. You can return to any section to make adjustments before generating your reflection.")

    ans = st.session_state.answers

    def fmt_display(val: Any, mapping: Optional[Dict[Any, str]] = None, is_required: bool = True) -> str:
        """Format an answer cleanly, highlighting missing required values in red."""
        if val is None or val == "" or val == []:
            if is_required:
                return "<span style='color:#dc2626; font-weight:600;'>⚠️ Not Answered (Required)</span>"
            return "<span style='color:#64748b; font-style:italic;'>Not specified (Optional)</span>"
        if mapping and val in mapping:
            return mapping[val]
        if isinstance(val, list):
            if not val:
                return "<span style='color:#dc2626; font-weight:600;'>⚠️ None Selected (Required)</span>" if is_required else "<span style='color:#64748b; font-style:italic;'>None (Optional)</span>"
            return ", ".join(str(x) for x in val)
        return str(val)

    # Check for any missing required fields across all sections
    missing_all = get_missing_required_fields(ans)
    if missing_all:
        st.warning(
            f"⚠️ **Incomplete Questionnaire ({len(missing_all)} questions remaining):** "
            "Some required questions have not been answered yet. "
            "Please click the Edit buttons to complete them before generating your reflection."
        )

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("""
        <div class="question-card">
            <h4>Section 1: AI Usage Habits</h4>
        """, unsafe_allow_html=True)
        display_field = ans.get("degree_field")
        if display_field == "Other" and ans.get("other_academic_field", "").strip():
            display_field = f"Other ({ans['other_academic_field'].strip()})"
        st.markdown(f"- **Academic Field:** {fmt_display(display_field, is_required=True)}", unsafe_allow_html=True)

        specific_deg = ans.get("specific_degree_programme", "").strip()
        if specific_deg:
            st.markdown(f"- **Specific Degree:** {fmt_display(specific_deg, is_required=False)}", unsafe_allow_html=True)

        yr_map = {1: "1st Year (Freshman)", 2: "2nd Year (Sophomore)", 3: "3rd Year (Junior)", 4: "4th Year (Senior)", 5: "5th Year", 6: "Postgraduate"}
        st.markdown(f"- **Academic Year:** {fmt_display(ans.get('academic_year'), yr_map, is_required=True)}", unsafe_allow_html=True)

        age_map = {1: "18–20 years", 2: "21–23 years", 3: "24–26 years", 4: "27 or above"}
        st.markdown(f"- **Age Bracket:** {fmt_display(ans.get('age_group'), age_map, is_required=True)}", unsafe_allow_html=True)

        freq_map = {1: "Rarely (< 1/wk)", 2: "Sometimes (1–3/wk)", 3: "Frequently (4–6/wk)", 4: "Daily"}
        st.markdown(f"- **Usage Frequency:** {fmt_display(ans.get('ai_usage_freq'), freq_map, is_required=True)}", unsafe_allow_html=True)

        time_map = {1: "< 1 hr/wk", 2: "1–3 hrs/wk", 3: "4–6 hrs/wk", 4: "7–10 hrs/wk", 5: "> 10 hrs/wk"}
        st.markdown(f"- **Weekly AI Usage Time:** {fmt_display(ans.get('ai_time_per_week'), time_map, is_required=True)}", unsafe_allow_html=True)

        st.markdown(f"- **Tools Used:** {fmt_display(ans.get('tools_used'), is_required=True)}", unsafe_allow_html=True)
        if st.button("✏️ Edit Section 1", key="btn_edit_1"):
            st.session_state.page = "section_1"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="question-card">
            <h4>Section 2: Task Delegation & Copying</h4>
        """, unsafe_allow_html=True)
        q20_map = {1: "Never (1)", 2: "Rarely (2)", 3: "Sometimes (3)", 4: "Often (4)", 5: "Very Often (5)"}
        st.markdown(f"- **Delegate Whole Tasks:** {fmt_display(ans.get('Q20_task_delegation_freq'), q20_map, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Delegated Tasks:** {fmt_display(ans.get('tasks_delegated'), is_required=False)}", unsafe_allow_html=True)
        q1_map = {
            1: "Never (1) — Always own words",
            2: "Rarely (2) — Heavily edit",
            3: "Sometimes (3) — Combine AI & own",
            4: "Often (4) — Minor edits",
            5: "Always (5) — Direct copy"
        }
        st.markdown(f"- **Direct Use / Copying:** {fmt_display(ans.get('Q1_direct_use_freq'), q1_map, is_required=True)}", unsafe_allow_html=True)
        q22_map = {
            1: "No effort (1)",
            2: "Little effort (2)",
            3: "Moderate effort (3)",
            4: "High effort (4)",
            5: "Very high effort (5)"
        }
        st.markdown(f"- **Review Effort:** {fmt_display(ans.get('Q22_effort_on_ai_answers'), q22_map, is_required=True)}", unsafe_allow_html=True)
        if st.button("✏️ Edit Section 2", key="btn_edit_2"):
            st.session_state.page = "section_2"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        st.markdown("""
        <div class="question-card">
            <h4>Section 3: Verification & Critical Thinking</h4>
        """, unsafe_allow_html=True)
        likert_lbl = {1: "1 — Strongly Disagree", 2: "2 — Disagree", 3: "3 — Neutral", 4: "4 — Agree", 5: "5 — Strongly Agree"}
        st.markdown(f"- **Verify Against Sources:** {fmt_display(ans.get('Q2_verify_info'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Compare with Lectures:** {fmt_display(ans.get('Q3_compare_sources'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Check Accuracy:** {fmt_display(ans.get('Q4_check_accuracy'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Understand Logic:** {fmt_display(ans.get('Q5_understand_reasoning'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Personalize Content:** {fmt_display(ans.get('Q6_modify_content'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        if st.button("✏️ Edit Section 3", key="btn_edit_3"):
            st.session_state.page = "section_3"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="question-card">
            <h4>Section 4: Independent Learning & Autonomy</h4>
        """, unsafe_allow_html=True)
        st.markdown(f"- **Attempt First Independently:** {fmt_display(ans.get('Q7_attempt_independently'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Able to Complete Without AI:** {fmt_display(ans.get('Q8_complete_without_ai'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **View AI as Assistant:** {fmt_display(ans.get('Q9_learning_assistant'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Trust in AI Accuracy:** {fmt_display(ans.get('Q30_trust_accuracy'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        st.markdown(f"- **Trust in AI Guidance:** {fmt_display(ans.get('Q33_trust_appropriate_support'), likert_lbl, is_required=True)}", unsafe_allow_html=True)
        if st.button("✏️ Edit Section 4", key="btn_edit_4"):
            st.session_state.page = "section_4"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_submit = st.columns([1, 1.5])
    with c_back:
        if st.button("⬅️ Back to Section 4"):
            st.session_state.page = "section_4"
            st.rerun()
    with c_submit:
        if st.button("🚀 Submit & Generate My Reflection", type="primary", use_container_width=True):
            missing_at_submit = get_missing_required_fields(st.session_state.answers)
            if missing_at_submit:
                st.error(
                    "❌ **Submission Blocked:** All required questions must be answered before generating your self-reflection. "
                    "Please click the Edit buttons to complete the following:\n\n"
                    + "\n".join(f"- {m}" for m in missing_at_submit)
                )
            else:
                with st.spinner("Analyzing study habits using research model..."):
                    model_payload = get_model_inputs(st.session_state.answers)
                    res = predictor.predict(model_payload, top_factors_count=5)
                    st.session_state.prediction_result = res
                    st.session_state.page = "results"
                    st.rerun()

# =============================================================================
# PAGE: RESULTS & SELF-REFLECTION
# =============================================================================
elif st.session_state.page == "results":
    render_progress(5)
    res = st.session_state.prediction_result

    # Handle edge case where prediction is missing or triggered validation error
    if not res or res.get("status") == "validation_error":
        st.error(f"❌ {res.get('message', 'Validation error occurred.') if res else 'No results found.'}")
        st.info("Please complete the self-reflection questions or load a sample student profile.")
        if st.button("⬅️ Return to Questionnaire", type="primary"):
            st.session_state.page = "home"
            st.rerun()
    else:
        cat = res["predicted_category"]
        score = res["continuous_risk_score"]
        conf = res["confidence"]
        probs = res["probabilities"]

        # 1. Hero Result Card
        if cat == "Low":
            card_class = "result-card-low"
            cat_icon = "🟢"
            cat_title = "Low Cognitive Offloading Tendency"
            cat_tagline = "Balanced & Independent AI Learner"
            summary_desc = (
                "Your responses show strong academic autonomy. You actively verify information, "
                "attempt coursework on your own first, and view AI as a supportive study companion rather than "
                "a substitute for your own critical thinking. Keep up this disciplined approach!"
            )
        elif cat == "Medium":
            card_class = "result-card-med"
            cat_icon = "🟡"
            cat_title = "Moderate Cognitive Offloading Tendency"
            cat_tagline = "Emerging Reliance — Great Opportunity to Strengthen Verification"
            summary_desc = (
                "You use Generative AI productively in many areas, but there are signs that certain tasks "
                "(such as writing, coding, or problem-solving) are occasionally delegated without full independent struggle "
                "or rigorous source checking. Small adjustments can significantly reinforce your long-term learning."
            )
        else:
            card_class = "result-card-high"
            cat_icon = "🔴"
            cat_title = "High Cognitive Offloading Tendency"
            cat_tagline = "Elevated Task Delegation — Action Recommended to Protect Independent Skills"
            summary_desc = (
                "Your responses suggest a strong pattern of delegating core academic reasoning directly to AI tools. "
                "While AI provides rapid solutions, bypassing early problem-solving struggle and fact-checking can weaken "
                "your independent analytical mastery and exam readiness over time."
            )

        st.markdown(f"""
        <div class="{card_class}">
            <div style="font-size: 1.8rem; font-weight: 700; color: #1e293b; margin-bottom: 0.2rem;">
                {cat_icon} {cat_title}
            </div>
            <div style="font-size: 1.15rem; font-weight: 600; color: #475569; margin-bottom: 0.8rem;">
                {cat_tagline}
            </div>
            <div style="font-size: 0.98rem; color: #334155; line-height: 1.5; margin-bottom: 1.2rem;">
                {summary_desc}
            </div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">
                Estimated Offloading Score: <b>{score:.2f} / 5.0</b>
                <span style="font-size: 0.88rem; font-weight: normal; color: #64748b; margin-left: 0.8rem;">
                    (Scale: 1.0 = Highly Autonomous & Verified, 5.0 = Heavy Automated Offloading)
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Clamping transparency notice
        raw_val = res.get("raw_regression_score", score)
        if raw_val > 5.0 or raw_val < 1.0:
            st.info(
                f"ℹ️ **Score Range Transparency Note:** The raw latent linear regression estimate ({raw_val:.3f}) "
                f"fell outside the theoretical Likert construct scale [1.0, 5.0] and was defensively constrained to **{score:.2f}**. "
                f"The raw statistical estimate is preserved for academic audit."
            )

        # 2. What Influenced Your Result? (LinearSHAP Factors)
        st.subheader("🔍 What Influenced Your Reflection? (Key Habits)")
        st.caption(
            "Our explainable model uses LinearSHAP to calculate the exact contribution of each habit toward "
            "protecting or increasing your cognitive offloading score compared to the university peer cohort."
        )

        factors = res.get("top_contributing_factors", [])
        if factors:
            col_f1, col_f2 = st.columns(2)
            mitigating_factors = [f for f in factors if f["effect"] == "mitigates predicted risk"]
            increasing_factors = [f for f in factors if f["effect"] == "increases predicted risk"]

            with col_f1:
                st.markdown("##### 🛡️ Habits Protecting Your Independent Learning")
                if mitigating_factors:
                    for f in mitigating_factors:
                        lbl = f.get("human_label", f["feature_name"])
                        expl = f.get("plain_explanation", "Protects your independent critical thinking.")
                        st.markdown(f"""
                        <div class="factor-badge-mitigate">
                            <b>{lbl}</b><br>
                            <span style="font-size: 0.88rem; color: #15803d;">{expl}</span>
                            <div style="font-size: 0.78rem; color: #166534; margin-top: 0.3rem;">
                                Model impact: {f['linear_shap_contribution']:+.3f} points
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No significant mitigating habits detected in this profile.")

            with col_f2:
                st.markdown("##### ⚠️ Habits Contributing to Higher Offloading")
                if increasing_factors:
                    for f in increasing_factors:
                        lbl = f.get("human_label", f["feature_name"])
                        expl = f.get("plain_explanation", "Increases reliance on automated outputs.")
                        st.markdown(f"""
                        <div class="factor-badge-increase">
                            <b>{lbl}</b><br>
                            <span style="font-size: 0.88rem; color: #b91c1c;">{expl}</span>
                            <div style="font-size: 0.78rem; color: #991b1b; margin-top: 0.3rem;">
                                Model impact: {f['linear_shap_contribution']:+.3f} points
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("No major risk-elevating habits detected!")
        else:
            st.info("No feature contribution breakdown available.")

        # 3. Model-Estimated Category Distribution
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Model-Estimated Category Likelihoods")
        st.caption(
            "These probabilities represent the statistical likelihood distribution generated by our calibrated residual density model. "
            "They reflect how peer students with similar responses distributed across categories, rather than absolute certainty."
        )

        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            st.metric("Low Offloading Probability", f"{probs['low']*100:.1f}%")
            st.progress(float(probs['low']))
        with c_p2:
            st.metric("Medium Offloading Probability", f"{probs['medium']*100:.1f}%")
            st.progress(float(probs['medium']))
        with c_p3:
            st.metric("High Offloading Probability", f"{probs['high']*100:.1f}%")
            st.progress(float(probs['high']))

        # 4. Actionable Ideas for Learning (Recommendations)
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💡 Actionable Ideas for Your Studies")
        
        if cat == "Low":
            recs = [
                ("Maintain Your 15-Minute Rule", "Continue attempting assignments and problem sets independently first before consulting AI for hints."),
                ("Teach the AI", "Prompt AI by saying: 'Here is my proposed solution and reasoning. Critique it and identify any logical gaps.'"),
                ("Deepen Socratic Inquiry", "Ask AI for alternative theoretical frameworks or edge cases to challenge your existing understanding.")
            ]
        elif cat == "Medium":
            recs = [
                ("The Draft-First Habit", "Spend at least 15 to 20 minutes drafting an outline, pseudocode, or initial paragraph before opening an AI tool."),
                ("Dual-Source Rule", "Whenever an AI tool provides an explanation, formula, or code snippet, cross-check it against your lecture slides or recommended textbook."),
                ("Rewrite in Your Own Words", "Avoid copying sentences directly. Summarize the AI explanation in your own handwriting or notes to trigger memory encoding.")
            ]
        else:
            recs = [
                ("Step Away from Full-Task Delegation", "Break assignments into parts and only use AI for conceptual clarification on specific obstacles, never the final answer."),
                ("Active Verification Routine", "Assume every AI output contains subtle factual errors or hallucinations until verified against official coursework notes."),
                ("Simulate Exam Conditions", "Practice solving past exam questions completely disconnected from AI tools to build confidence and mental endurance.")
            ]

        c_r1, c_r2, c_r3 = st.columns(3)
        for idx, (title, text) in enumerate(recs):
            with [c_r1, c_r2, c_r3][idx]:
                st.markdown(f"""
                <div class="question-card" style="height: 100%;">
                    <h5 style="color:#1e293b; margin-bottom: 0.4rem;">📌 {title}</h5>
                    <p style="color:#475569; font-size:0.88rem; line-height: 1.4;">{text}</p>
                </div>
                """, unsafe_allow_html=True)

        # 5. Navigation & Reset Buttons
        st.markdown("<br>", unsafe_allow_html=True)
        c_nav1, c_nav2, c_nav3 = st.columns([1, 1, 1])
        with c_nav1:
            if st.button("📝 Review My Answers", use_container_width=True):
                st.session_state.page = "review"
                st.rerun()
        with c_nav2:
            if st.button("🔄 Start New Assessment", use_container_width=True):
                st.session_state.answers = dict(BLANK_ANSWERS)
                st.session_state.prediction_result = None
                st.session_state.page = "home"
                st.rerun()
        with c_nav3:
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

        # Preprocessing warnings expander (if any)
        if res.get("warnings"):
            with st.expander(f"Data Preprocessing & Validation Notes ({len(res['warnings'])} notices)"):
                for w in res["warnings"]:
                    st.write(f"- {w}")

# -----------------------------------------------------------------------------
# Research & Evaluation Methodology Footnote
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div class='research-note'>"
    "<b>Research Project:</b> Explainable Cognitive Offloading Risk Model Among Undergraduate Students (J26-DS-310 | Component 1)<br>"
    "<b>Champion Architecture:</b> Calibrated Thresholded Ridge Regressor (Ordinal) defensibly selected strictly via "
    "25-fold Repeated Stratified Cross-Validation on the training partition (N=300). Historical exposed holdout split (N=75) "
    "is preserved for auditing and not used for model selection.<br>"
    "<b>Explainability Engine:</b> Exact LinearSHAP (Linear Shapley Additive Explanations) computing feature contributions "
    "relative to peer cohort baseline means."
    "</div>",
    unsafe_allow_html=True
)
