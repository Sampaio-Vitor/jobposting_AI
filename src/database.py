import sqlite3
import os
from contextlib import contextmanager
from src import config


def _ensure_dir():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)


@contextmanager
def get_db():
    _ensure_dir()
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                link TEXT,
                description TEXT,
                date_posted TEXT,
                salary_min REAL,
                salary_max REAL,
                salary_currency TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                is_relevant BOOLEAN,
                is_remote BOOLEAN,
                is_international BOOLEAN,
                role_category TEXT,
                seniority TEXT,
                summary TEXT,
                salary_range TEXT,
                analyzed_at TIMESTAMP,

                notified BOOLEAN DEFAULT 0,
                notified_at TIMESTAMP
            )
        """)
        # Migration: add salary columns to existing DBs
        for col, typ in [("salary_min", "REAL"), ("salary_max", "REAL"), ("salary_currency", "TEXT")]:
            try:
                conn.execute(f"ALTER TABLE jobs ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError:
                pass  # column already exists


def upsert_jobs(jobs: list[dict]) -> int:
    """Insert new jobs, skip duplicates. Returns count of new jobs inserted."""
    new_count = 0
    with get_db() as conn:
        for job in jobs:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO jobs
                   (id, title, company, location, link, description, date_posted,
                    salary_min, salary_max, salary_currency)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (job["id"], job["title"], job["company"], job["location"],
                 job["link"], job["description"], job.get("date_posted"),
                 job.get("salary_min"), job.get("salary_max"), job.get("salary_currency")),
            )
            if cursor.rowcount > 0:
                new_count += 1
    return new_count


def get_unanalyzed() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, title, company, location, link, description FROM jobs WHERE analyzed_at IS NULL"
        ).fetchall()
        return [dict(row) for row in rows]


def save_analysis(job_id: str, analysis: dict):
    with get_db() as conn:
        conn.execute(
            """UPDATE jobs SET
                is_relevant = ?, is_international = ?,
                role_category = ?, seniority = ?, summary = ?, salary_range = ?,
                analyzed_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (analysis["is_relevant"], analysis["is_international"],
             analysis["role_category"], analysis["seniority"], analysis["summary"],
             analysis.get("salary_range"), job_id),
        )


def get_unnotified_matches() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM jobs
               WHERE is_relevant = 1 AND is_international = 1
                 AND notified = 0"""
        ).fetchall()
        return [dict(row) for row in rows]


def mark_notified(job_ids: list[str]):
    with get_db() as conn:
        conn.executemany(
            "UPDATE jobs SET notified = 1, notified_at = CURRENT_TIMESTAMP WHERE id = ?",
            [(jid,) for jid in job_ids],
        )
