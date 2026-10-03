"""
Backend server for GenAI-Assisted Cognitive Engagement Evaluation Platform.
Provides RESTful API endpoints for participant registration, session tracking,
Phase 1 (Brain-Only) results ingestion, and static delivery of the research frontend.
Supports standard Flask server and includes a zero-dependency fallback server.
"""

import os
import sys
import json
import random
import csv
import io
import socket
import sqlite3
import hmac
try:
    from backend.database import get_db_connection, init_db
except ImportError:
    from database import get_db_connection, init_db

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# --- Admin Credentials (loaded from .env or environment variables) ---
def _load_dotenv(path):
    """Minimal .env loader — no external dependencies required."""
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Only set if not already present in environment
            if key and key not in os.environ:
                os.environ[key] = value

_load_dotenv(os.path.join(BASE_DIR, ".env"))

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "research_admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ResearchAdmin@2026")

try:
    from flask import Flask, request, jsonify, send_from_directory, Response
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


# --- Research Export SQL Queries ---
QUERY_EXPORT_PARTICIPANTS = """
SELECT 
    id,
    participant_id,
    experiment_group,
    assigned_sequence,
    mother_code,
    birth_year,
    birth_month,
    school_code,
    university_name,
    age_group,
    degree_programme,
    genai_experience,
    consent_given,
    registered_at
FROM participants
ORDER BY id DESC
"""

QUERY_EXPORT_BRAIN_ONLY = """
SELECT 
    b.id,
    b.participant_id,
    b.experiment_group,
    COALESCE(p.assigned_sequence, CASE WHEN b.experiment_group = 'A' THEN 'brain_only_first' ELSE 'genai_first' END) AS assigned_sequence,
    b.topic_id,
    b.learning_time,
    b.mcq_score,
    b.short_answers,
    b.confidence_score,
    b.effort_score,
    b.created_at
FROM brain_only_results b
LEFT JOIN participants p ON b.participant_id = p.participant_id
ORDER BY b.id DESC
"""

QUERY_EXPORT_GENAI_ASSISTED = """
SELECT 
    g.id,
    g.participant_id,
    g.experiment_group,
    COALESCE(p.assigned_sequence, CASE WHEN g.experiment_group = 'A' THEN 'brain_only_first' ELSE 'genai_first' END) AS assigned_sequence,
    g.topic_id,
    g.learning_time,
    g.mcq_score,
    g.short_answers,
    g.ai_tool,
    g.prompt_count,
    g.ai_usage_purpose,
    g.confidence_score,
    g.ai_usefulness_score,
    g.effort_score,
    g.explanation_score,
    g.created_at
FROM genai_assisted_results g
LEFT JOIN participants p ON g.participant_id = p.participant_id
ORDER BY g.id DESC
"""

QUERY_EXPORT_DELAYED_RECALL = """
SELECT 
    d.id,
    d.participant_id,
    d.experiment_group,
    COALESCE(p.assigned_sequence, CASE WHEN d.experiment_group = 'A' THEN 'brain_only_first' ELSE 'genai_first' END) AS assigned_sequence,
    d.brain_immediate_score,
    d.brain_recall_score,
    d.brain_retention_score,
    d.genai_immediate_score,
    d.genai_recall_score,
    d.genai_retention_score,
    d.ownership_score,
    d.explanation_score,
    d.dependency_score,
    d.created_at
FROM delayed_recall_results d
LEFT JOIN participants p ON d.participant_id = p.participant_id
ORDER BY d.id DESC
"""


def generate_csv_string(query, params=None):
    """Executes query against SQLite and formats result rows as an RFC 4180 CSV string."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description] if cursor.description else []
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(list(r))
        return output.getvalue()
    finally:
        conn.close()


def get_admin_summary_data():
    """Aggregates high-level research telemetry and condition statistics for admin dashboard."""
    conn = get_db_connection()
    try:
        total_participants = conn.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
        group_a_count = conn.execute("SELECT COUNT(*) FROM participants WHERE experiment_group = 'A'").fetchone()[0]
        group_b_count = conn.execute("SELECT COUNT(*) FROM participants WHERE experiment_group = 'B'").fetchone()[0]

        completed_count = conn.execute("""
            SELECT COUNT(DISTINCT p.participant_id)
            FROM participants p
            INNER JOIN brain_only_results b ON p.participant_id = b.participant_id
            INNER JOIN genai_assisted_results g ON p.participant_id = g.participant_id
            INNER JOIN delayed_recall_results d ON p.participant_id = d.participant_id
        """).fetchone()[0]

        completion_rate = round((completed_count / total_participants * 100), 1) if total_participants > 0 else 0.0

        bo = conn.execute("""
            SELECT 
                COUNT(*) as count,
                AVG(mcq_score) as avg_mcq,
                AVG(learning_time) as avg_time
            FROM brain_only_results
        """).fetchone()

        ga = conn.execute("""
            SELECT 
                COUNT(*) as count,
                AVG(mcq_score) as avg_mcq,
                AVG(learning_time) as avg_time,
                AVG(prompt_count) as avg_prompts
            FROM genai_assisted_results
        """).fetchone()

        dr = conn.execute("""
            SELECT 
                COUNT(*) as count,
                AVG(brain_retention_score) as avg_brain_retention,
                AVG(genai_retention_score) as avg_genai_retention
            FROM delayed_recall_results
        """).fetchone()

        return {
            "participant_overview": {
                "total_participants": total_participants,
                "completed_experiments": completed_count,
                "group_a_count": group_a_count,
                "group_b_count": group_b_count,
                "completion_rate": completion_rate
            },
            "brain_only_results": {
                "attempts": bo["count"] if bo else 0,
                "average_mcq_score": round(bo["avg_mcq"], 2) if bo and bo["avg_mcq"] is not None else 0.0,
                "average_learning_time": round(bo["avg_time"], 1) if bo and bo["avg_time"] is not None else 0.0
            },
            "genai_assisted_results": {
                "attempts": ga["count"] if ga else 0,
                "average_mcq_score": round(ga["avg_mcq"], 2) if ga and ga["avg_mcq"] is not None else 0.0,
                "average_learning_time": round(ga["avg_time"], 1) if ga and ga["avg_time"] is not None else 0.0,
                "average_prompt_count": round(ga["avg_prompts"], 2) if ga and ga["avg_prompts"] is not None else 0.0
            },
            "retention_results": {
                "attempts": dr["count"] if dr else 0,
                "average_brain_retention": round(dr["avg_brain_retention"], 1) if dr and dr["avg_brain_retention"] is not None else 0.0,
                "average_genai_retention": round(dr["avg_genai_retention"], 1) if dr and dr["avg_genai_retention"] is not None else None
            }
        }
    finally:
        conn.close()


def get_admin_participants_data():
    """Returns all participant records with completion statuses across Phase 1, Phase 2, and Phase 3."""
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT 
                p.id,
                p.participant_id,
                p.age_group,
                p.university_name,
                p.degree_programme,
                p.genai_experience,
                p.consent_given,
                p.experiment_group,
                p.assigned_sequence,
                p.registered_at,
                CASE WHEN b.id IS NOT NULL THEN 1 ELSE 0 END AS phase1_completed,
                b.mcq_score AS phase1_score,
                b.learning_time AS phase1_time,
                CASE WHEN g.id IS NOT NULL THEN 1 ELSE 0 END AS phase2_completed,
                g.mcq_score AS phase2_score,
                g.learning_time AS phase2_time,
                g.ai_tool AS phase2_tool,
                CASE WHEN d.id IS NOT NULL THEN 1 ELSE 0 END AS phase3_completed,
                d.brain_retention_score,
                d.genai_retention_score
            FROM participants p
            LEFT JOIN (
                SELECT participant_id, id, mcq_score, learning_time
                FROM brain_only_results
                WHERE id IN (SELECT MAX(id) FROM brain_only_results GROUP BY participant_id)
            ) b ON p.participant_id = b.participant_id
            LEFT JOIN (
                SELECT participant_id, id, mcq_score, learning_time, ai_tool
                FROM genai_assisted_results
                WHERE id IN (SELECT MAX(id) FROM genai_assisted_results GROUP BY participant_id)
            ) g ON p.participant_id = g.participant_id
            LEFT JOIN (
                SELECT participant_id, id, brain_retention_score, genai_retention_score
                FROM delayed_recall_results
                WHERE id IN (SELECT MAX(id) FROM delayed_recall_results GROUP BY participant_id)
            ) d ON p.participant_id = d.participant_id
            ORDER BY p.id DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


if HAS_FLASK:
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

    @app.route("/")
    def index():
        """Serves the study overview landing page."""
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/register.html")
    def register_page():
        """Serves the participant registration page."""
        return send_from_directory(FRONTEND_DIR, "register.html")

    @app.route("/dashboard.html")
    def dashboard_page():
        """Serves the experiment dashboard page."""
        return send_from_directory(FRONTEND_DIR, "dashboard.html")

    @app.route("/brain_only.html")
    def brain_only_page():
        """Serves the Phase 1 Brain-Only learning condition page."""
        return send_from_directory(FRONTEND_DIR, "brain_only.html")

    @app.route("/genai_assisted.html")
    def genai_assisted_page():
        """Serves the Phase 2 GenAI-Assisted learning condition page."""
        return send_from_directory(FRONTEND_DIR, "genai_assisted.html")

    @app.route("/delayed_recall.html")
    def delayed_recall_page():
        """Serves the Phase 3 Delayed Recall and Retention evaluation page."""
        return send_from_directory(FRONTEND_DIR, "delayed_recall.html")

    @app.route("/admin_dashboard.html")
    @app.route("/admin")
    def admin_dashboard_page():
        """Serves the researcher admin dashboard page."""
        return send_from_directory(FRONTEND_DIR, "admin_dashboard.html")

    @app.route("/admin_login.html")
    @app.route("/admin/login")
    def admin_login_page():
        """Serves the researcher admin login page."""
        return send_from_directory(FRONTEND_DIR, "admin_login.html")

    @app.route("/api/admin/login", methods=["POST"])
    def admin_login():
        """
        Authenticates researcher admin credentials.
        Expected JSON: { "username": "...", "password": "..." }
        Returns: { "success": true } or { "success": false, "message": "..." }
        Credentials are loaded from environment variables / .env — never hardcoded in JS.
        """
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        username_match = hmac.compare_digest(username, ADMIN_USERNAME)
        password_match = hmac.compare_digest(password, ADMIN_PASSWORD)

        if username_match and password_match:
            return jsonify({"success": True, "message": "Admin authenticated successfully."}), 200
        else:
            return jsonify({"success": False, "message": "Invalid username or password."}), 401

    @app.route("/api/admin/logout", methods=["POST"])
    def admin_logout():
        """Admin logout endpoint — session state is managed client-side (sessionStorage)."""
        return jsonify({"success": True, "message": "Logged out successfully."}), 200

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint confirming backend and database status."""
        return jsonify({
            "status": "operational",
            "project": "GenAI-Assisted Cognitive Engagement, Recall, and Learning Retention Evaluation",
            "phase": "All Phases Active (Phase 1, 2 & 3 Completed)",
            "framework": "Flask"
        }), 200

    @app.route("/api/register", methods=["POST"])
    def register_participant():
        """Registers a new participant for the fixed Brain-Only-first sequence."""
        data = request.get_json() or {}
        participant_id = (data.get("participant_id") or "").strip().lower()
        mother_code = (data.get("mother_code") or "").strip().lower()
        birth_year = str(data.get("birth_year") or "").strip()
        birth_month = str(data.get("birth_month") or "").strip().zfill(2) if data.get("birth_month") else ""
        school_code = (data.get("school_code") or "").strip().lower()

        if not participant_id and mother_code and birth_year and birth_month and school_code:
            participant_id = f"{mother_code}{birth_year}{birth_month}{school_code}"

        age_group = data.get("age_group")
        university_name = (data.get("university_name") or "").strip()
        degree_programme = data.get("degree_programme")
        genai_experience = data.get("genai_experience")
        consent_given = 1 if data.get("consent_given") else 0

        experiment_group = "A"
        assigned_sequence = "brain_only_first"

        if not participant_id or not university_name or not consent_given:
            return jsonify({"error": "Please complete all required fields before continuing."}), 400

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO participants (
                    participant_id, age_group, university_name, degree_programme, genai_experience,
                    consent_given, experiment_group, assigned_sequence,
                    mother_code, birth_year, birth_month, school_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (participant_id, age_group, university_name, degree_programme, genai_experience, consent_given, experiment_group, assigned_sequence, mother_code, birth_year, birth_month, school_code))
            conn.commit()

            return jsonify({
                "success": True,
                "message": f"Participant {participant_id} registered successfully in Group {experiment_group}.",
                "participant_id": participant_id,
                "experiment_group": experiment_group,
                "assigned_sequence": assigned_sequence,
                "mother_code": mother_code,
                "birth_year": birth_year,
                "birth_month": birth_month,
                "school_code": school_code
            }), 201
        except sqlite3.IntegrityError:
            if conn:
                try: conn.close()
                except Exception: pass
            conn = get_db_connection()
            existing = conn.execute("SELECT * FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
            if existing:
                return jsonify({
                    "success": True,
                    "message": f"Participant {participant_id} already registered. Resuming experimental session.",
                    "participant_id": existing["participant_id"],
                    "experiment_group": existing["experiment_group"],
                    "assigned_sequence": existing["assigned_sequence"],
                    "mother_code": existing["mother_code"],
                    "birth_year": existing["birth_year"],
                    "birth_month": existing["birth_month"],
                    "school_code": existing["school_code"]
                }), 200
            return jsonify({"error": "Database integrity constraint violation."}), 500
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    @app.route("/api/participants", methods=["GET"])
    def list_participants():
        """Returns list of registered participants for research export."""
        conn = get_db_connection()
        participants = conn.execute("SELECT * FROM participants ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in participants]), 200

    @app.route("/api/brain-only-result", methods=["POST"])
    def save_brain_only_result():
        """
        Records assessment and self-report metrics for Phase 1: Brain-Only condition.
        Expected JSON payload:
        {
            "participant_id": "PID-1042",
            "topic_id": "blockchain_intro_01",
            "learning_time": 245.5,
            "mcq_score": 9,
            "short_answers": "{\"q11\": \"...\", \"q12\": \"...\"}",
            "confidence_score": 4,
            "effort_score": 3
        }
        """
        data = request.get_json() or {}
        participant_id = data.get("participant_id")
        topic_id = data.get("topic_id", "blockchain_intro_01")
        learning_time = data.get("learning_time", 0)
        mcq_score = data.get("mcq_score", 0)
        short_answers = data.get("short_answers", "")
        confidence_score = data.get("confidence_score")
        effort_score = data.get("effort_score")
        experiment_group = data.get("experiment_group")

        if not participant_id:
            return jsonify({"error": "participant_id is required."}), 400

        if isinstance(short_answers, (dict, list)):
            short_answers_str = json.dumps(short_answers)
        else:
            short_answers_str = str(short_answers)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if not experiment_group:
                p_row = conn.execute("SELECT experiment_group FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
                experiment_group = p_row["experiment_group"] if p_row and p_row["experiment_group"] else "A"

            cursor.execute("""
                INSERT INTO brain_only_results (
                    participant_id, topic_id, learning_time, mcq_score,
                    short_answers, confidence_score, effort_score, experiment_group
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                participant_id,
                topic_id,
                float(learning_time),
                float(mcq_score),
                short_answers_str,
                int(confidence_score) if confidence_score is not None else None,
                int(effort_score) if effort_score is not None else None,
                experiment_group
            ))
            result_id = cursor.lastrowid
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Brain-Only condition results successfully recorded.",
                "result_id": result_id,
                "participant_id": participant_id,
                "experiment_group": experiment_group
            }), 201
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    @app.route("/api/brain-only-results", methods=["GET"])
    def list_brain_only_results():
        """Returns all recorded brain-only experimental trials for researcher verification."""
        conn = get_db_connection()
        results = conn.execute("SELECT * FROM brain_only_results ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in results]), 200

    @app.route("/api/genai-assisted-result", methods=["POST"])
    def save_genai_assisted_result():
        """
        Records assessment, AI telemetry, and self-report metrics for Phase 2: GenAI-Assisted condition.
        Expected JSON payload:
        {
            "participant_id": "PID-1042",
            "topic_id": "blockchain_advanced_02",
            "learning_time": 240.0,
            "mcq_score": 9.0,
            "short_answers": "{\"q11\": \"...\", \"q12\": \"...\"}",
            "ai_tool": "ChatGPT (GPT-4)",
            "prompt_count": 3,
            "ai_usage_purpose": "Explanation, Summarization",
            "confidence_score": 5,
            "ai_usefulness_score": 4,
            "effort_score": 2,
            "explanation_score": 4
        }
        """
        data = request.get_json() or {}
        participant_id = data.get("participant_id")
        topic_id = data.get("topic_id", "blockchain_advanced_02")
        learning_time = data.get("learning_time", 0)
        mcq_score = data.get("mcq_score", 0)
        short_answers = data.get("short_answers", "")
        ai_tool = data.get("ai_tool", "")
        prompt_count = data.get("prompt_count")
        ai_usage_purpose = data.get("ai_usage_purpose", "")
        confidence_score = data.get("confidence_score")
        ai_usefulness_score = data.get("ai_usefulness_score")
        effort_score = data.get("effort_score")
        explanation_score = data.get("explanation_score")
        experiment_group = data.get("experiment_group")

        if not participant_id:
            return jsonify({"error": "participant_id is required."}), 400

        short_answers_str = json.dumps(short_answers) if isinstance(short_answers, (dict, list)) else str(short_answers)
        purpose_str = ", ".join(ai_usage_purpose) if isinstance(ai_usage_purpose, list) else str(ai_usage_purpose)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if not experiment_group:
                p_row = conn.execute("SELECT experiment_group FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
                experiment_group = p_row["experiment_group"] if p_row and p_row["experiment_group"] else "A"

            cursor.execute("""
                INSERT INTO genai_assisted_results (
                    participant_id, topic_id, learning_time, mcq_score,
                    short_answers, ai_tool, prompt_count, ai_usage_purpose,
                    confidence_score, ai_usefulness_score, effort_score,
                    explanation_score, experiment_group
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                participant_id,
                topic_id,
                float(learning_time),
                float(mcq_score),
                short_answers_str,
                str(ai_tool),
                int(prompt_count) if prompt_count is not None else None,
                purpose_str,
                int(confidence_score) if confidence_score is not None else None,
                int(ai_usefulness_score) if ai_usefulness_score is not None else None,
                int(effort_score) if effort_score is not None else None,
                int(explanation_score) if explanation_score is not None else None,
                experiment_group
            ))
            result_id = cursor.lastrowid
            conn.commit()

            return jsonify({
                "success": True,
                "message": "GenAI-Assisted condition results successfully recorded.",
                "result_id": result_id,
                "participant_id": participant_id,
                "experiment_group": experiment_group
            }), 201
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    @app.route("/api/genai-assisted-results", methods=["GET"])
    def list_genai_assisted_results():
        """Returns all recorded GenAI-assisted experimental trials."""
        conn = get_db_connection()
        results = conn.execute("SELECT * FROM genai_assisted_results ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in results]), 200

    @app.route("/api/delayed-recall-result", methods=["POST"])
    def save_delayed_recall_result():
        """
        Records retention scores and cognitive ownership measures for Phase 3: Delayed Recall.
        Expected JSON payload:
        {
            "participant_id": "PID-1042",
            "brain_immediate_score": 8.0,
            "brain_recall_score": 7.0,
            "brain_retention_score": 87.5,
            "genai_immediate_score": 9.0,
            "genai_recall_score": 6.0,
            "genai_retention_score": 66.7,
            "ownership_score": 4,
            "explanation_score": 4,
            "dependency_score": 2
        }
        """
        data = request.get_json() or {}
        participant_id = data.get("participant_id")
        brain_immediate_score = data.get("brain_immediate_score", 0.0)
        brain_recall_score = data.get("brain_recall_score", 0.0)
        brain_retention_score = data.get("brain_retention_score", 0.0)
        genai_immediate_score = data.get("genai_immediate_score", 0.0)
        genai_recall_score = data.get("genai_recall_score")
        genai_retention_score = data.get("genai_retention_score")
        ownership_score = data.get("ownership_score")
        explanation_score = data.get("explanation_score")
        dependency_score = data.get("dependency_score")
        experiment_group = data.get("experiment_group")

        if not participant_id:
            return jsonify({"error": "participant_id is required."}), 400

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if not experiment_group:
                p_row = conn.execute("SELECT experiment_group FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
                experiment_group = p_row["experiment_group"] if p_row and p_row["experiment_group"] else "A"

            cursor.execute("""
                INSERT INTO delayed_recall_results (
                    participant_id, brain_immediate_score, brain_recall_score,
                    brain_retention_score, genai_immediate_score, genai_recall_score,
                    genai_retention_score, ownership_score, explanation_score,
                    dependency_score, experiment_group
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                participant_id,
                float(brain_immediate_score),
                float(brain_recall_score),
                float(brain_retention_score),
                float(genai_immediate_score),
                float(genai_recall_score) if genai_recall_score is not None else None,
                float(genai_retention_score) if genai_retention_score is not None else None,
                int(ownership_score) if ownership_score is not None else None,
                int(explanation_score) if explanation_score is not None else None,
                int(dependency_score) if dependency_score is not None else None,
                experiment_group
            ))
            result_id = cursor.lastrowid
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Delayed recall and retention results successfully recorded.",
                "result_id": result_id,
                "participant_id": participant_id,
                "experiment_group": experiment_group
            }), 201
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    @app.route("/api/delayed-recall-results", methods=["GET"])
    def list_delayed_recall_results():
        """Returns all recorded delayed recall experimental trials."""
        conn = get_db_connection()
        results = conn.execute("SELECT * FROM delayed_recall_results ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in results]), 200

    @app.route("/api/admin/summary", methods=["GET"])
    def admin_summary():
        """Returns aggregated telemetry and condition metrics for researcher admin dashboard."""
        return jsonify(get_admin_summary_data()), 200

    @app.route("/api/admin/participants", methods=["GET"])
    def admin_participants():
        """Returns detailed participant records with completion statuses across all phases."""
        return jsonify(get_admin_participants_data()), 200

    @app.route("/api/export/participants", methods=["GET"])
    def export_participants():
        """Exports all participant demographic and assignment data as CSV."""
        csv_data = generate_csv_string(QUERY_EXPORT_PARTICIPANTS)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=participants.csv"}
        )

    @app.route("/api/export/brain-only", methods=["GET"])
    def export_brain_only():
        """Exports Phase 1 Brain-Only learning condition data as CSV."""
        csv_data = generate_csv_string(QUERY_EXPORT_BRAIN_ONLY)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=brain_only_results.csv"}
        )

    @app.route("/api/export/genai-assisted", methods=["GET"])
    def export_genai_assisted():
        """Exports Phase 2 GenAI-Assisted learning condition data as CSV."""
        csv_data = generate_csv_string(QUERY_EXPORT_GENAI_ASSISTED)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=genai_assisted_results.csv"}
        )

    @app.route("/api/export/delayed-recall", methods=["GET"])
    def export_delayed_recall():
        """Exports Phase 3 Delayed Recall and Retention evaluation data as CSV."""
        csv_data = generate_csv_string(QUERY_EXPORT_DELAYED_RECALL)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=delayed_recall_results.csv"}
        )

else:
    # Zero-dependency Built-in HTTP Server Fallback (when Flask is not yet installed)
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import urllib.parse

    class ResearchHTTPHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

        def _send_json(self, status_code, data):
            payload = json.dumps(data).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(payload)

        def _send_csv(self, filename, csv_content):
            payload = csv_content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.end_headers()
            self.wfile.write(payload)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path).path
            if parsed_path == "/admin":
                self.send_response(302)
                self.send_header("Location", "/admin_dashboard.html")
                self.end_headers()
            elif parsed_path == "/admin/login":
                self.send_response(302)
                self.send_header("Location", "/admin_login.html")
                self.end_headers()
            elif parsed_path == "/api/health":
                self._send_json(200, {
                    "status": "operational",
                    "project": "GenAI-Assisted Cognitive Engagement Evaluation",
                    "framework": "Python Built-in HTTP Server (Flask Fallback)"
                })
            elif parsed_path == "/api/brain-only-results":
                conn = get_db_connection()
                results = conn.execute("SELECT * FROM brain_only_results ORDER BY id DESC").fetchall()
                conn.close()
                self._send_json(200, [dict(row) for row in results])
            elif parsed_path == "/api/genai-assisted-results":
                conn = get_db_connection()
                results = conn.execute("SELECT * FROM genai_assisted_results ORDER BY id DESC").fetchall()
                conn.close()
                self._send_json(200, [dict(row) for row in results])
            elif parsed_path == "/api/delayed-recall-results":
                conn = get_db_connection()
                results = conn.execute("SELECT * FROM delayed_recall_results ORDER BY id DESC").fetchall()
                conn.close()
                self._send_json(200, [dict(row) for row in results])
            elif parsed_path == "/api/participants":
                conn = get_db_connection()
                participants = conn.execute("SELECT * FROM participants ORDER BY id DESC").fetchall()
                conn.close()
                self._send_json(200, [dict(row) for row in participants])
            elif parsed_path == "/api/admin/summary":
                self._send_json(200, get_admin_summary_data())
            elif parsed_path == "/api/admin/participants":
                self._send_json(200, get_admin_participants_data())
            elif parsed_path == "/api/export/participants":
                self._send_csv("participants.csv", generate_csv_string(QUERY_EXPORT_PARTICIPANTS))
            elif parsed_path == "/api/export/brain-only":
                self._send_csv("brain_only_results.csv", generate_csv_string(QUERY_EXPORT_BRAIN_ONLY))
            elif parsed_path == "/api/export/genai-assisted":
                self._send_csv("genai_assisted_results.csv", generate_csv_string(QUERY_EXPORT_GENAI_ASSISTED))
            elif parsed_path == "/api/export/delayed-recall":
                self._send_csv("delayed_recall_results.csv", generate_csv_string(QUERY_EXPORT_DELAYED_RECALL))
            else:
                super().do_GET()

        def do_POST(self):
            parsed_path = urllib.parse.urlparse(self.path).path
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body) if body else {}
            except Exception:
                data = {}

            if parsed_path == "/api/admin/login":
                username = (data.get("username") or "").strip()
                password = (data.get("password") or "").strip()
                username_match = hmac.compare_digest(username, ADMIN_USERNAME)
                password_match = hmac.compare_digest(password, ADMIN_PASSWORD)
                if username_match and password_match:
                    self._send_json(200, {"success": True, "message": "Admin authenticated successfully."})
                else:
                    self._send_json(401, {"success": False, "message": "Invalid username or password."})

            elif parsed_path == "/api/admin/logout":
                self._send_json(200, {"success": True, "message": "Logged out successfully."})

            elif parsed_path == "/api/register":
                participant_id = (data.get("participant_id") or "").strip().lower()
                mother_code = (data.get("mother_code") or "").strip().lower()
                birth_year = str(data.get("birth_year") or "").strip()
                birth_month = str(data.get("birth_month") or "").strip().zfill(2) if data.get("birth_month") else ""
                school_code = (data.get("school_code") or "").strip().lower()

                if not participant_id and mother_code and birth_year and birth_month and school_code:
                    participant_id = f"{mother_code}{birth_year}{birth_month}{school_code}"

                age_group = data.get("age_group")
                university_name = (data.get("university_name") or "").strip()
                degree_programme = data.get("degree_programme")
                genai_experience = data.get("genai_experience")
                consent_given = 1 if data.get("consent_given") else 0

                # New participants follow the fixed Brain-Only-first sequence.
                experiment_group = "A"
                assigned_sequence = "brain_only_first"

                if not participant_id or not university_name or not consent_given:
                    self._send_json(400, {"error": "Please complete all required fields before continuing."})
                    return

                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO participants (
                            participant_id, age_group, university_name, degree_programme, genai_experience,
                            consent_given, experiment_group, assigned_sequence,
                            mother_code, birth_year, birth_month, school_code
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (participant_id, age_group, university_name, degree_programme, genai_experience, consent_given, experiment_group, assigned_sequence, mother_code, birth_year, birth_month, school_code))
                    conn.commit()
                    conn.close()

                    self._send_json(201, {
                        "success": True,
                        "message": f"Participant {participant_id} registered successfully in Group {experiment_group}.",
                        "participant_id": participant_id,
                        "experiment_group": experiment_group,
                        "assigned_sequence": assigned_sequence,
                        "mother_code": mother_code,
                        "birth_year": birth_year,
                        "birth_month": birth_month,
                        "school_code": school_code
                    })
                except sqlite3.IntegrityError:
                    conn = get_db_connection()
                    existing = conn.execute("SELECT * FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
                    conn.close()
                    if existing:
                        self._send_json(200, {
                            "success": True,
                            "message": f"Participant {participant_id} already registered. Resuming experimental session.",
                            "participant_id": existing["participant_id"],
                            "experiment_group": existing["experiment_group"],
                            "assigned_sequence": existing["assigned_sequence"],
                            "mother_code": existing["mother_code"],
                            "birth_year": existing["birth_year"],
                            "birth_month": existing["birth_month"],
                            "school_code": existing["school_code"]
                        })
                        return
                    self._send_json(500, {"error": "Database integrity constraint violation."})
                except Exception as e:
                    self._send_json(500, {"error": f"Database error: {str(e)}"})

            elif parsed_path == "/api/brain-only-result":
                participant_id = data.get("participant_id")
                topic_id = data.get("topic_id", "blockchain_intro_01")
                learning_time = data.get("learning_time", 0)
                mcq_score = data.get("mcq_score", 0)
                short_answers = data.get("short_answers", "")
                confidence_score = data.get("confidence_score")
                effort_score = data.get("effort_score")
                experiment_group = data.get("experiment_group")

                if not participant_id:
                    self._send_json(400, {"error": "participant_id is required."})
                    return

                short_answers_str = json.dumps(short_answers) if isinstance(short_answers, (dict, list)) else str(short_answers)

                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    if not experiment_group:
                        p_row = conn.execute("SELECT experiment_group FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
                        experiment_group = p_row["experiment_group"] if p_row and p_row["experiment_group"] else "A"

                    cursor.execute("""
                        INSERT INTO brain_only_results (
                            participant_id, topic_id, learning_time, mcq_score,
                            short_answers, confidence_score, effort_score, experiment_group
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        participant_id,
                        topic_id,
                        float(learning_time),
                        float(mcq_score),
                        short_answers_str,
                        int(confidence_score) if confidence_score is not None else None,
                        int(effort_score) if effort_score is not None else None,
                        experiment_group
                    ))
                    result_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    self._send_json(201, {
                        "success": True,
                        "message": "Brain-Only condition results successfully recorded.",
                        "result_id": result_id,
                        "participant_id": participant_id,
                        "experiment_group": experiment_group
                    })
                except Exception as e:
                    self._send_json(500, {"error": f"Database error: {str(e)}"})

            elif parsed_path == "/api/genai-assisted-result":
                participant_id = data.get("participant_id")
                topic_id = data.get("topic_id", "blockchain_advanced_02")
                learning_time = data.get("learning_time", 0)
                mcq_score = data.get("mcq_score", 0)
                short_answers = data.get("short_answers", "")
                ai_tool = data.get("ai_tool", "")
                prompt_count = data.get("prompt_count")
                ai_usage_purpose = data.get("ai_usage_purpose", "")
                confidence_score = data.get("confidence_score")
                ai_usefulness_score = data.get("ai_usefulness_score")
                effort_score = data.get("effort_score")
                explanation_score = data.get("explanation_score")
                experiment_group = data.get("experiment_group")

                if not participant_id:
                    self._send_json(400, {"error": "participant_id is required."})
                    return

                short_answers_str = json.dumps(short_answers) if isinstance(short_answers, (dict, list)) else str(short_answers)
                purpose_str = ", ".join(ai_usage_purpose) if isinstance(ai_usage_purpose, list) else str(ai_usage_purpose)

                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    if not experiment_group:
                        p_row = conn.execute("SELECT experiment_group FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
                        experiment_group = p_row["experiment_group"] if p_row and p_row["experiment_group"] else "A"

                    cursor.execute("""
                        INSERT INTO genai_assisted_results (
                            participant_id, topic_id, learning_time, mcq_score,
                            short_answers, ai_tool, prompt_count, ai_usage_purpose,
                            confidence_score, ai_usefulness_score, effort_score,
                            explanation_score, experiment_group
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        participant_id,
                        topic_id,
                        float(learning_time),
                        float(mcq_score),
                        short_answers_str,
                        str(ai_tool),
                        int(prompt_count) if prompt_count is not None else None,
                        purpose_str,
                        int(confidence_score) if confidence_score is not None else None,
                        int(ai_usefulness_score) if ai_usefulness_score is not None else None,
                        int(effort_score) if effort_score is not None else None,
                        int(explanation_score) if explanation_score is not None else None,
                        experiment_group
                    ))
                    result_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    self._send_json(201, {
                        "success": True,
                        "message": "GenAI-Assisted condition results successfully recorded.",
                        "result_id": result_id,
                        "participant_id": participant_id,
                        "experiment_group": experiment_group
                    })
                except Exception as e:
                    self._send_json(500, {"error": f"Database error: {str(e)}"})

            elif parsed_path == "/api/delayed-recall-result":
                participant_id = data.get("participant_id")
                brain_immediate_score = data.get("brain_immediate_score", 0.0)
                brain_recall_score = data.get("brain_recall_score", 0.0)
                brain_retention_score = data.get("brain_retention_score", 0.0)
                genai_immediate_score = data.get("genai_immediate_score", 0.0)
                genai_recall_score = data.get("genai_recall_score", 0.0)
                genai_retention_score = data.get("genai_retention_score", 0.0)
                ownership_score = data.get("ownership_score")
                explanation_score = data.get("explanation_score")
                dependency_score = data.get("dependency_score")
                experiment_group = data.get("experiment_group")

                if not participant_id:
                    self._send_json(400, {"error": "participant_id is required."})
                    return

                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    if not experiment_group:
                        p_row = conn.execute("SELECT experiment_group FROM participants WHERE participant_id = ?", (participant_id,)).fetchone()
                        experiment_group = p_row["experiment_group"] if p_row and p_row["experiment_group"] else "A"

                    cursor.execute("""
                        INSERT INTO delayed_recall_results (
                            participant_id, brain_immediate_score, brain_recall_score,
                            brain_retention_score, genai_immediate_score, genai_recall_score,
                            genai_retention_score, ownership_score, explanation_score,
                            dependency_score, experiment_group
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        participant_id,
                        float(brain_immediate_score),
                        float(brain_recall_score),
                        float(brain_retention_score),
                        float(genai_immediate_score),
                        float(genai_recall_score),
                        float(genai_retention_score),
                        int(ownership_score) if ownership_score is not None else None,
                        int(explanation_score) if explanation_score is not None else None,
                        int(dependency_score) if dependency_score is not None else None,
                        experiment_group
                    ))
                    result_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    self._send_json(201, {
                        "success": True,
                        "message": "Delayed recall results successfully recorded.",
                        "result_id": result_id,
                        "participant_id": participant_id,
                        "experiment_group": experiment_group
                    })
                except Exception as e:
                    self._send_json(500, {"error": f"Database error: {str(e)}"})
            else:
                self._send_json(404, {"error": f"Endpoint {parsed_path} not found."})


def find_available_port(preferred_port=5000):
    """Finds an open port starting from preferred_port, avoiding macOS AirPlay Receiver conflicts on 5000."""
    candidates = [preferred_port, 5001, 5050, 8000, 8080]
    for p in candidates:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", p))
                return p
        except OSError:
            continue
    return preferred_port


def run_server(port=None):
    """Initializes the database and runs the research server."""
    init_db()
    if port is None:
        port = int(os.environ.get("PORT", 0)) or find_available_port(5000)

    if HAS_FLASK:
        print(f"Starting Flask research server on http://127.0.0.1:{port} ...")
        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    else:
        print(f"Flask not installed in current environment.")
        print(f"Starting standard Python HTTP research server on http://127.0.0.1:{port} ...")
        print(f"(To use Flask: pip install flask)")
        server = HTTPServer(("127.0.0.1", port), ResearchHTTPHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            print("\nServer stopped.")


if __name__ == "__main__":
    target_port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    run_server(target_port)
