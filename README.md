# GenAI-Assisted Cognitive Engagement, Recall, and Learning Retention Evaluation

A web-based experimental research data collection platform developed as an undergraduate final-year research prototype.

---

## 1. Project Overview

This platform investigates the cognitive differences between autonomous learning and Generative AI (GenAI)-assisted learning. Specifically, the study measures:
- **Cognitive Engagement**: How deeply participants interact with learning material under different modalities.
- **Immediate Recall**: The volume and fidelity of information retained immediately following the learning intervention.
- **Delayed Retention**: Long-term conceptual retention and transfer evaluated after a designated interval.

> **Note**: This system is designed strictly as an empirical data collection prototype for university research, not a commercial application.

---

## 2. Project Directory Structure

```text
project/
│
├── frontend/
│   ├── index.html          # Study overview & participant information landing page
│   ├── register.html       # Participant demographics, GenAI background & consent form
│   ├── dashboard.html      # Experiment session manager & phase condition cards
│   ├── brain_only.html     # Phase 1: Brain-Only Learning Condition (Reading, Timer, Quiz, Likert)
│   ├── genai_assisted.html # Phase 2: GenAI-Assisted Learning Condition (Reading, AI Telemetry, Quiz, Likert)
│   ├── delayed_recall.html # Phase 3: Delayed Recall & Retention Evaluation (Recall Tests, Metrics, Ownership)
│   ├── css/
│   │   └── style.css       # Clean, professional academic research interface stylesheet
│   └── js/
│       └── app.js          # Client-side navigation, session manager & dashboard state controller
│
├── backend/
│   ├── app.py              # Flask server with REST API routes (including /api/delayed-recall-result)
│   └── database.py         # SQLite connection manager & table schema (including delayed_recall_results)
│
├── database/
│   └── research.db         # SQLite database file storing participants, Phase 1, Phase 2, & Phase 3 data
│
└── README.md               # Project documentation and architectural overview
```

---

## 3. Platform Architecture & Modules

### Frontend
- **Academic Research Interface**: Designed with an accessible, high-contrast, clean academic palette (deep slate navy, lab white, subtle borders) suited for formal participant evaluations.
- **Study Overview (`index.html`)**: Summarizes the research protocol, background, ethics statement, and study roadmap.
- **Participant Registration (`register.html`)**: Collects baseline demographic data and research consent.
- **Experiment Dashboard (`dashboard.html`)**: Displays the 3-phase experimental structure, tracking completion states, unlocking successive stages, and showing comparative progress.
- **Phase 1: Brain-Only Condition (`brain_only.html`)**:
  - Independent reading passage (~340 words) on foundational blockchain principles.
  - Active study timer logging duration.
  - 10 MCQs + 2 short-answer synthesis questions with automatic grading.
  - 1–5 Likert scale self-report measures (confidence, Paas mental effort, independent explanation ability).
  - Persistence via `POST /api/brain-only-result`.
- **Phase 2: GenAI-Assisted Condition (`genai_assisted.html`)**:
  - Reading passage (~340 words) on advanced blockchain concepts (Scalability Trilemma, Rollups, Sharding, Oracles).
  - GenAI interaction telemetry logging: AI tool used, prompt count, and usage purposes.
  - Study timer logging total AI-assisted learning duration.
  - 10 MCQs + 2 short-answer synthesis questions with automatic grading.
  - 1–5 Likert scale measures: comprehension confidence, AI helpfulness, AI support, mental effort, and explanation ability without AI.
  - Within-subjects comparative overview (Phase 1 vs. Phase 2) and persistence via `POST /api/genai-assisted-result`.
- **Phase 3: Delayed Recall & Retention Evaluation (`delayed_recall.html`)**:
  - One Brain-Only delayed recall section (10 MCQs + 2 short answers matching Phase 1).
  - Cognitive reflection and ownership measures.
  - Brain-Only retention score: `(Delayed Recall / Immediate Score) * 100`; GenAI delayed recall is not assessed.
  - Cognitive reflection & ownership measures (1–5 Likert scales: explanation autonomy, memory recall, personal knowledge ownership, cognitive dependency).
  - Retention comparison dashboard with percentage retention rates and delta metrics.
  - Persistence via `POST /api/delayed-recall-result`.

### Backend & Database
- **Flask REST API (`backend/app.py`)**:
  - Exposes JSON endpoints:
    - `POST /api/register` (demographics ingestion)
    - `POST /api/brain-only-result` (Phase 1 results ingestion)
    - `GET /api/brain-only-results` (Phase 1 export and inspection)
    - `POST /api/genai-assisted-result` (Phase 2 results & AI telemetry ingestion)
    - `GET /api/genai-assisted-results` (Phase 2 export and inspection)
    - `POST /api/delayed-recall-result` (Phase 3 retention results ingestion)
    - `GET /api/delayed-recall-results` (Phase 3 export and inspection)
    - `GET /api/participants` (participant list)
    - `GET /api/health` (service health check)
- **SQLite Database (`database/research.db` & `backend/database.py`)**:
  - `participants`: Stores pseudonymized IDs, demographic cohorts, and consent records.
  - `brain_only_results`: Stores baseline human-only condition metrics.
  - `genai_assisted_results`: Stores AI-augmented condition metrics, tool selections, prompt counts, and cognitive load ratings.
  - `delayed_recall_results`: Stores immediate vs. delayed scores, retention percentages, ownership, and dependency ratings.

---

## 4. Getting Started

### Option A: Static Frontend Preview (Quickest)
You can directly open any of the HTML pages in your web browser without running a server:
- Open `frontend/index.html`, `frontend/register.html`, `frontend/dashboard.html`, `frontend/brain_only.html`, `frontend/genai_assisted.html`, or `frontend/delayed_recall.html` in your browser.

### Option B: Running with the Python Backend
To run the full client-server environment:

1. **(Optional) Install Flask**:
   ```bash
   pip install flask
   ```

2. **Initialize Database**:
   ```bash
   python3 backend/database.py
   ```
   *(Creates or updates `database/research.db` with all tables)*

3. **Start the Research Server**:
   ```bash
   python3 backend/app.py
   ```

4. **Access the Application**:
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 5. Development Roadmap

- [x] **Step 1: Scaffolding & Initial Layout**
  - Clean project folder hierarchy
  - Academic research UI theme (HTML/CSS/JS)
  - Participant registration interface with required demographic fields
  - Experiment dashboard displaying the three experimental conditions
- [x] **Step 2: Phase 1 (Brain-Only Learning Condition)**
  - Academic reading passage on Blockchain Technology
  - Study duration timer and auto-tracking
  - 10 MCQs + 2 short-answer questions with automated scoring
  - 1–5 Likert self-report cognitive load & confidence measures
  - `POST /api/brain-only-result` backend API and `brain_only_results` SQLite table
- [x] **Step 3: Phase 2 (GenAI-Assisted Learning Condition)**
  - Academic reading passage on Advanced Blockchain Concepts
  - GenAI tool usage tracking (tool used, prompt count, purpose)
  - Active study duration timer
  - 10 MCQs + 2 short-answer questions with automated scoring
  - 1–5 Likert self-report measures (confidence, AI helpfulness, AI support, mental effort, explanation ability)
  - `POST /api/genai-assisted-result` backend API and `genai_assisted_results` SQLite table
  - Within-subjects comparative overview (Phase 1 vs. Phase 2)
- [x] **Step 4: Phase 3 (Delayed Recall and Retention Evaluation)**
  - One delayed recall section for Brain-Only (10 MCQs + 2 short answers)
  - Brain-Only retention score calculation: `(Delayed Recall / Immediate Score) * 100`; GenAI recall metrics are stored as not assessed
  - Cognitive reflection & ownership measures (explanation autonomy, memory recall, knowledge ownership, dependency)
  - Comparative retention dashboard displaying retention percentages and differential metrics
  - `POST /api/delayed-recall-result` backend API and `delayed_recall_results` SQLite table
- [x] **Step 5: Fixed Experimental Sequence**
  - All new participants follow Step 01 Brain-Only, Step 02 GenAI-Assisted, and Step 03 Delayed Recall
  - Fixed sequence flow tracker banner and phase cards on the dashboard
  - All numbered phases remain accessible from the dashboard
  - Registration guard protects experiment pages
  - Complete database schema migration adding `experiment_group` and `assigned_sequence` to `participants` and experimental result tables
- [x] **Step 6: Researcher Admin Dashboard & Standardized CSV Exports** *(Completed)*
  - Dedicated researcher administration portal (`/admin_dashboard.html` / `/admin`)
  - Real-time participant overview metrics (total enrolled, completed count, cohort balance, completion %)
  - Live participant data table with search, group filter, and multi-phase progression status tracking
  - Experimental results telemetry summary comparing Brain-Only vs. GenAI-Assisted learning time, scores, prompt count, and longitudinal retention
  - One-click CSV dataset export endpoints formatted to RFC 4180 with recorded participant groups and sequences

---

## 6. Experimental Design: Fixed Sequence

All participants follow the same within-subjects sequence:

| Step | Condition |
|---|---|
| **Step 01** | Brain-Only Learning Condition |
| **Step 02** | GenAI-Assisted Learning Condition |
| **Step 03** | Delayed Recall Test |

New registrations are assigned `brain_only_first`. Existing records retain their original group and sequence values for historical reporting. All numbered phases remain accessible from the dashboard.

### Phase Access
1. **Open Phase Access**: Participants may open any numbered phase from the dashboard without completing earlier phases first.
2. **Registration Guard**: Direct access to experiment pages still requires participant registration.
3. **Data Integrity for Statistical Modeling**: Every data record stores `experiment_group` and `assigned_sequence`. Since the current protocol uses a fixed order, this design does not counterbalance order effects.

---

## 7. Researcher Data Management & Export Pipeline

The platform provides a dedicated, restricted researcher portal (`/admin_dashboard.html` or `/admin`) for monitoring participant flow and exporting experimental datasets for downstream statistical analysis.

### Dashboard Modules
1. **Section 1: Participant Overview**: High-level KPIs displaying total registered sample size, fully completed protocols (all 3 phases), Group A vs. Group B sample balance, and overall completion rate.
2. **Section 2: Participant Data Table**: Live table displaying all participants with:
   - `Participant ID`
  - `Experiment Group` (recorded group assignment)
  - `Assigned Sequence` (recorded sequence; new registrations use `brain_only_first`)
   - `Registration Date`
   - `Phase 1 Status` (Completion badge, score, learning time)
   - `Phase 2 Status` (Completion badge, score, learning time, AI tool)
   - `Phase 3 Status` (Completion badge, Brain retention %, GenAI retention %)
   - Real-time client-side search by ID/Degree and filtering by Group and Completion Status.
3. **Section 3: Experimental Results Summary**: Aggregated analytical comparison:
   - **Brain-Only Results**: Total attempts, mean MCQ score (/10), mean learning duration.
   - **GenAI-Assisted Results**: Total attempts, mean MCQ score (/10), mean learning duration, mean prompt count.
   - **Retention Results**: Mean Brain-Only retention score (%), mean GenAI-assisted retention score (%), and comparative progress indicators.

### REST API Endpoints for Researchers
| Endpoint | Method | Response Format | Purpose |
|---|---|---|---|
| `/api/admin/summary` | GET | JSON | Aggregated research telemetry & condition performance metrics |
| `/api/admin/participants` | GET | JSON | Comprehensive participant list with multi-phase statuses |
| `/api/export/participants` | GET | CSV (`participants.csv`) | Demographics, recorded group, sequence, consent |
| `/api/export/brain-only` | GET | CSV (`brain_only_results.csv`) | Phase 1 scores, learning duration, Likert ratings |
| `/api/export/genai-assisted` | GET | CSV (`genai_assisted_results.csv`) | Phase 2 scores, duration, prompt counts, tools, purposes |
| `/api/export/delayed-recall` | GET | CSV (`delayed_recall_results.csv`) | Phase 3 immediate/recall scores, retention %, ownership |

> **Ready for Statistical Software**: All CSV exports strictly adhere to RFC 4180 standards and include `participant_id`, `experiment_group`, and `assigned_sequence`, enabling import into SPSS, R, Python (`pandas`), Stata, or JASP for repeated-measures analysis.

