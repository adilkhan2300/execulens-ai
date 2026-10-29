"""
ExecuLens AI - Database Layer (SQLite)
Manages persistence for action items, audit trails, user annotations, and ingestion history.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config.settings import DATABASE_PATH

def get_connection() -> sqlite3.Connection:
    """Create a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables with appropriate schemas and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Management Actions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS management_actions (
                action_id TEXT PRIMARY KEY,
                date_created TEXT NOT NULL,
                related_kpi TEXT,
                related_financial_outcome TEXT,
                action_description TEXT NOT NULL,
                owner TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                expected_impact TEXT,
                actual_impact TEXT,
                review_date TEXT,
                updated_at TEXT
            )
        """)
        
        # Audit Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                user_role TEXT DEFAULT 'Executive',
                details TEXT,
                metadata_json TEXT
            )
        """)
        
        # Dataset Ingestion History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                dataset_type TEXT NOT NULL,
                row_count INTEGER,
                status TEXT NOT NULL,
                validation_summary TEXT
            )
        """)
        
        # User Scenarios Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_scenarios (
                scenario_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                base_period TEXT,
                assumptions_json TEXT NOT NULL,
                projected_results_json TEXT NOT NULL
            )
        """)
        
        conn.commit()

def log_audit_event(action_type: str, details: str, metadata: Optional[Dict[str, Any]] = None, user_role: str = "Executive"):
    """Record an audit trail event for compliance, model governance, and accountability."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_logs (timestamp, action_type, user_role, details, metadata_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    action_type,
                    user_role,
                    details,
                    json.dumps(metadata or {})
                )
            )
            conn.commit()
    except Exception as e:
        # Avoid crashing app if logging fails
        print(f"Warning: Audit log failed: {e}")

def get_audit_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve recent audit logs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

def upsert_action(action: Dict[str, Any]):
    """Insert or update a management action record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO management_actions (
                action_id, date_created, related_kpi, related_financial_outcome,
                action_description, owner, priority, status, expected_impact,
                actual_impact, review_date, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(action_id) DO UPDATE SET
                related_kpi=excluded.related_kpi,
                related_financial_outcome=excluded.related_financial_outcome,
                action_description=excluded.action_description,
                owner=excluded.owner,
                priority=excluded.priority,
                status=excluded.status,
                expected_impact=excluded.expected_impact,
                actual_impact=excluded.actual_impact,
                review_date=excluded.review_date,
                updated_at=excluded.updated_at
            """,
            (
                action["action_id"],
                action.get("date_created", datetime.now().strftime("%Y-%m-%d")),
                action.get("related_kpi", ""),
                action.get("related_financial_outcome", ""),
                action["action_description"],
                action.get("owner", "Unassigned"),
                action.get("priority", "Medium"),
                action.get("status", "Proposed"),
                action.get("expected_impact", ""),
                action.get("actual_impact", ""),
                action.get("review_date", ""),
                datetime.now().isoformat()
            )
        )
        conn.commit()
        log_audit_event("UPSERT_ACTION", f"Action {action['action_id']} updated with status {action.get('status')}")

def get_all_actions() -> List[Dict[str, Any]]:
    """Retrieve all management actions ordered by priority and date."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM management_actions ORDER BY date_created DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_action(action_id: str):
    """Delete a management action by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM management_actions WHERE action_id = ?", (action_id,))
        conn.commit()
        log_audit_event("DELETE_ACTION", f"Action {action_id} deleted")

# Initialize database upon import
init_db()
