# app/db.py

import sqlite3
from datetime import date
from app.config import JOBS_DB_PATH


def _connect():
    conn = sqlite3.connect(JOBS_DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_jobs():
    conn = _connect()
    rows = conn.execute("SELECT * FROM job_postings").fetchall()
    conn.close()
    return rows


def get_jobs_today():
    today = date.today().isoformat()
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM job_postings WHERE date_scraped LIKE ?", (today + "%",)
    ).fetchall()
    conn.close()
    return rows


def get_jobs_by_company(company):
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM job_postings WHERE company = ?", (company,)
    ).fetchall()
    conn.close()
    return rows


def get_new_jobs_by_company(company):
    today = date.today().isoformat()
    conn = _connect()
    rows = conn.execute(
        """
        SELECT *
        FROM job_postings
        WHERE company = ?
          AND date_scraped LIKE ?
        """,
        (company, today + "%"),
    ).fetchall()
    conn.close()
    return rows


def init_db():
    """Create the job_postings table with the full set of fields, including salary."""
    conn = _connect()
    conn.executescript(
        """
    CREATE TABLE IF NOT EXISTS job_postings (
        id                          INTEGER PRIMARY KEY AUTOINCREMENT,
        company                     TEXT    NOT NULL,
        workday_id                  TEXT    NOT NULL,
        title                       TEXT,
        job_description             TEXT,
        location                    TEXT,
        url                         TEXT,
        posted_on                   TEXT,
        start_date                  TEXT,
        time_type                   TEXT,
        job_req_id                  TEXT,
        job_posting_id              TEXT,
        job_posting_site_id         TEXT,
        country                     TEXT,
        logo_image                  TEXT,
        can_apply                   BOOLEAN,
        posted                      BOOLEAN,
        include_resume_parsing      BOOLEAN,
        job_requisition_location    TEXT,
        remote_type                 TEXT,
        questionnaire_id            TEXT,
        salary_low                  REAL,
        salary_high                 REAL,
        date_scraped                TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company, workday_id)
    );
    """
    )
    conn.close()


def get_existing_job_ids(company):
    conn = _connect()
    rows = conn.execute(
        "SELECT job_req_id FROM job_postings WHERE company = ?", (company,)
    ).fetchall()
    conn.close()
    return {r["job_req_id"] for r in rows}


def insert_job_posting(
    company: str,
    workday_id: str,
    title: str,
    job_description: str,
    location: str,
    url: str,
    posted_on: str,
    start_date: str,
    time_type: str,
    job_req_id: str,
    job_posting_id: str,
    job_posting_site_id: str,
    country: str,
    logo_image: str,
    can_apply: bool,
    posted: bool,
    include_resume_parsing: bool,
    job_requisition_location: str,
    remote_type: str,
    questionnaire_id: str,
    salary_low: float,
    salary_high: float,
):
    conn = _connect()
    conn.execute(
        """
        INSERT INTO job_postings (
            company,
            workday_id,
            title,
            job_description,
            location,
            url,
            posted_on,
            start_date,
            time_type,
            job_req_id,
            job_posting_id,
            job_posting_site_id,
            country,
            logo_image,
            can_apply,
            posted,
            include_resume_parsing,
            job_requisition_location,
            remote_type,
            questionnaire_id,
            salary_low,
            salary_high
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company,
            workday_id,
            title,
            job_description,
            location,
            url,
            posted_on,
            start_date,
            time_type,
            job_req_id,
            job_posting_id,
            job_posting_site_id,
            country,
            logo_image,
            can_apply,
            posted,
            include_resume_parsing,
            job_requisition_location,
            remote_type,
            questionnaire_id,
            salary_low,
            salary_high,
        ),
    )
    conn.commit()
    conn.close()


def delete_job_posting(company, workday_id=None, job_req_id=None):
    """Delete a job posting for a company by identifier.

    Args:
        company (str): The company name used to scope the deletion.
        workday_id (str | None): The Workday primary identifier for the posting.
        job_req_id (str | None): The Workday requisition identifier.

    Either ``workday_id`` or ``job_req_id`` must be provided. ``workday_id``
    remains the default to preserve backwards compatibility with existing
    callers, but ``job_req_id`` is now supported for flows that diff on the
    requisition identifier.
    """

    if workday_id is None and job_req_id is None:
        raise ValueError("Either workday_id or job_req_id is required")

    column = "workday_id" if workday_id is not None else "job_req_id"
    value = workday_id if workday_id is not None else job_req_id

    conn = _connect()
    conn.execute(
        f"DELETE FROM job_postings WHERE company = ? AND {column} = ?",
        (company, value),
    )
    conn.commit()
    conn.close()
