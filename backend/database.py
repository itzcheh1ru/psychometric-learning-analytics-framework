"""
Database management module for GenAI Learning Evaluation Research Platform.
Provides SQLite database connection and schema initialization for storing
participant demographics, experimental session telemetry, and recall test results.
"""

import os
import sqlite3

# Define relative path to the database file in project/database/research.db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "research.db")


def get_db_connection():
    """Establishes and returns a connection to the SQLite research database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    """
    Initializes the database tables required for the experimental evaluation:
    - participants: Demographics, prior GenAI experience, and consent status
    - experiment_sessions: Telemetry for Brain-Only and GenAI-assisted learning conditions
    - recall_evaluations: Delayed recall test responses and performance metrics
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")

    # 1. Participants Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT UNIQUE NOT NULL,
        age_group TEXT,
        university_name TEXT,
        degree_programme TEXT,
        genai_experience TEXT,
        consent_given INTEGER NOT NULL,
        experiment_group TEXT,
        assigned_sequence TEXT,
        mother_code TEXT,
        birth_year TEXT,
        birth_month TEXT,
        school_code TEXT,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Experiment Sessions / Telemetry Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiment_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT NOT NULL,
        phase_name TEXT NOT NULL,
        condition_type TEXT NOT NULL,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_seconds REAL,
        raw_telemetry_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
    )
    """)

    # 3. Delayed Recall Evaluation Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recall_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT NOT NULL,
        test_phase TEXT NOT NULL,
        question_id TEXT NOT NULL,
        participant_response TEXT,
        is_correct INTEGER,
        score REAL,
        response_time_ms INTEGER,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
    )
    """)

    # 4. Phase 1: Brain-Only Condition Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brain_only_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT NOT NULL,
        topic_id TEXT NOT NULL,
        learning_time REAL NOT NULL,
        mcq_score REAL NOT NULL,
        short_answers TEXT,
        confidence_score INTEGER,
        effort_score INTEGER,
        experiment_group TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
    )
    """)

    # 5. Phase 2: GenAI-Assisted Condition Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genai_assisted_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT NOT NULL,
        topic_id TEXT NOT NULL,
        learning_time REAL NOT NULL,
        mcq_score REAL NOT NULL,
        short_answers TEXT,
        ai_tool TEXT,
        prompt_count INTEGER,
        ai_usage_purpose TEXT,
        confidence_score INTEGER,
        ai_usefulness_score INTEGER,
        effort_score INTEGER,
        explanation_score INTEGER,
        experiment_group TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
    )
    """)

    # 6. Phase 3: Delayed Recall & Retention Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS delayed_recall_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT NOT NULL,
        brain_immediate_score REAL NOT NULL,
        brain_recall_score REAL NOT NULL,
        brain_retention_score REAL NOT NULL,
        genai_immediate_score REAL NOT NULL,
        genai_recall_score REAL,
        genai_retention_score REAL,
        ownership_score INTEGER,
        explanation_score INTEGER,
        dependency_score INTEGER,
        experiment_group TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
    )
    """)

    cursor.execute("PRAGMA table_info(delayed_recall_results)")
    phase3_columns = {row[1]: bool(row[3]) for row in cursor.fetchall()}
    if phase3_columns.get("genai_recall_score") or phase3_columns.get("genai_retention_score"):
        cursor.execute("""
        CREATE TABLE delayed_recall_results_nullable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id TEXT NOT NULL,
            brain_immediate_score REAL NOT NULL,
            brain_recall_score REAL NOT NULL,
            brain_retention_score REAL NOT NULL,
            genai_immediate_score REAL NOT NULL,
            genai_recall_score REAL,
            genai_retention_score REAL,
            ownership_score INTEGER,
            explanation_score INTEGER,
            dependency_score INTEGER,
            experiment_group TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
        )
        """)
        cursor.execute("""
        INSERT INTO delayed_recall_results_nullable (
            id, participant_id, brain_immediate_score, brain_recall_score,
            brain_retention_score, genai_immediate_score, genai_recall_score,
            genai_retention_score, ownership_score, explanation_score,
            dependency_score, experiment_group, created_at
        )
        SELECT id, participant_id, brain_immediate_score, brain_recall_score,
            brain_retention_score, genai_immediate_score, genai_recall_score,
            genai_retention_score, ownership_score, explanation_score,
            dependency_score, experiment_group, created_at
        FROM delayed_recall_results
        """)
        cursor.execute("DROP TABLE delayed_recall_results")
        cursor.execute("ALTER TABLE delayed_recall_results_nullable RENAME TO delayed_recall_results")

    # Dynamic Column Migration for existing databases
    def ensure_column(table_name, col_name, col_type):
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = [row[1] for row in cursor.fetchall()]
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")

    ensure_column("participants", "experiment_group", "TEXT")
    ensure_column("participants", "assigned_sequence", "TEXT")
    ensure_column("participants", "university_name", "TEXT")
    ensure_column("participants", "mother_code", "TEXT")
    ensure_column("participants", "birth_year", "TEXT")
    ensure_column("participants", "birth_month", "TEXT")
    ensure_column("participants", "school_code", "TEXT")
    ensure_column("brain_only_results", "experiment_group", "TEXT")
    ensure_column("genai_assisted_results", "experiment_group", "TEXT")
    ensure_column("delayed_recall_results", "experiment_group", "TEXT")

    conn.commit()
    conn.close()
    print(f"Database initialized and migrated successfully at: {DB_PATH}")


if __name__ == "__main__":
    init_db()
