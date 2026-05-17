from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Optional

from job_helper.schemas import JobFitAnalysis


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    experience_level TEXT,
    technical_fit_score INTEGER,
    hiring_competitiveness_score INTEGER,
    apply_priority TEXT,
    sponsorship_risk TEXT,
    ats_keyword_match INTEGER,
    status TEXT DEFAULT 'Found',
    job_url TEXT,
    notes TEXT,
    analysis_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(db_path: str) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()


def save_analysis(db_path: str, analysis: JobFitAnalysis, job_url: Optional[str] = None) -> int:
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO jobs (
                company, title, location, experience_level,
                technical_fit_score, hiring_competitiveness_score,
                apply_priority, sponsorship_risk, ats_keyword_match,
                status, job_url, notes, analysis_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis.company,
                analysis.title,
                analysis.location,
                analysis.experience_level,
                analysis.technical_fit_score,
                analysis.hiring_competitiveness_score,
                analysis.apply_priority,
                analysis.sponsorship_risk,
                analysis.ats_keyword_match,
                "Found",
                job_url,
                analysis.short_reasoning,
                analysis.model_dump_json(indent=2),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_jobs(db_path: str, limit: int = 30) -> list[dict]:
    with connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, company, title, location, technical_fit_score,
                   hiring_competitiveness_score, apply_priority,
                   sponsorship_risk, status, created_at
            FROM jobs
            ORDER BY technical_fit_score DESC, hiring_competitiveness_score DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_job(db_path: str, job_id: int) -> dict | None:
    with connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None


def update_status(db_path: str, job_id: int, status: str) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, job_id),
        )
        conn.commit()


def export_csv(db_path: str, csv_path: str) -> None:
    rows = list_jobs(db_path, limit=10000)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id", "company", "title", "location", "technical_fit_score",
                "hiring_competitiveness_score", "apply_priority",
                "sponsorship_risk", "status", "created_at"
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
