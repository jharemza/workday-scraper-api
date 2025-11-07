"""Generate a LinkedIn-style post highlighting three SQL roles at financial institutions."""

from __future__ import annotations

import os
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from app.config import JOBS_DB_PATH


def _connect(db_path: str) -> sqlite3.Connection:
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"jobs.db file not found at {db_path}. Ensure the database exists before running this script."
        )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _load_unique_jobs(conn: sqlite3.Connection) -> Dict[str, Dict[str, sqlite3.Row]]:
    """Return job postings grouped by company with unique job_req_id entries."""
    rows = conn.execute(
        """
        SELECT company, job_req_id, title, url
        FROM job_postings
        WHERE company IS NOT NULL AND TRIM(company) != ''
          AND job_req_id IS NOT NULL AND TRIM(job_req_id) != ''
          AND title IS NOT NULL AND TRIM(title) != ''
          AND url IS NOT NULL AND TRIM(url) != ''
        """
    ).fetchall()

    grouped: Dict[str, Dict[str, sqlite3.Row]] = {}
    for row in rows:
        company = row["company"].strip()
        job_req_id = row["job_req_id"].strip()
        grouped.setdefault(company, {})
        # Only keep the first occurrence of a given (company, job_req_id)
        grouped[company].setdefault(job_req_id, row)

    # Filter out companies without any unique job_req_id entries
    return {company: entries for company, entries in grouped.items() if entries}


def _choose_random_jobs(grouped_jobs: Dict[str, Dict[str, sqlite3.Row]], count: int = 3) -> List[sqlite3.Row]:
    available_companies = list(grouped_jobs.keys())
    if len(available_companies) < count:
        raise ValueError(
            f"Not enough companies with unique job_req_id entries to select {count} jobs."
        )

    selected_jobs: List[sqlite3.Row] = []
    for company in random.sample(available_companies, count):
        jobs_for_company = list(grouped_jobs[company].values())
        selected_jobs.append(random.choice(jobs_for_company))
    return selected_jobs


def _format_post(jobs: List[sqlite3.Row]) -> str:
    lines = [
        "💼 SQL Roles at Financial Institutions",
        "",
        "I came across a few openings that might be helpful for anyone currently on the job hunt.",
        "I’m not affiliated with these institutions — just sharing to make someone’s search a little easier.",
        "",
        "📋 Current Openings:",
        f"1️⃣ {jobs[0]['title']} — {jobs[0]['company']}",
        f"🔗 {jobs[0]['url']}",
        "",
        f"2️⃣ {jobs[1]['title']} — {jobs[1]['company']}",
        f"🔗 {jobs[1]['url']}",
        "",
        f"3️⃣ {jobs[2]['title']} — {jobs[2]['company']}",
        f"🔗 {jobs[2]['url']}",
        "",
        "If you’re exploring roles that use SQL in the finance sector, there are plenty of opportunities right now — and I’ll be sharing more in upcoming posts.",
        "",
        "👇 Follow me if you’d like to see future posts with similar job finds.",
        "",
        "#DataJobs #SQL #Finance #Hiring #JobSearch #CareerGrowth",
    ]
    return "\n".join(lines)


def _write_post_to_file(content: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"li_post_{datetime.now().strftime('%Y%m%d')}.txt"
    file_path = output_dir / filename
    if file_path.exists():
        raise FileExistsError(f"Output file already exists at {file_path}. Delete it or run on a different day.")

    file_path.write_text(content, encoding="utf-8")
    return file_path


def generate_li_post(db_path: str = JOBS_DB_PATH, output_dir: Path | None = None) -> Tuple[str, Path]:
    output_dir = output_dir or Path("li_posts")
    with _connect(db_path) as conn:
        grouped_jobs = _load_unique_jobs(conn)
        selected_jobs = _choose_random_jobs(grouped_jobs)
    post_content = _format_post(selected_jobs)
    file_path = _write_post_to_file(post_content, output_dir)
    return post_content, file_path


if __name__ == "__main__":
    content, path = generate_li_post()
    print(content)
    print("\nSaved to:", path)
