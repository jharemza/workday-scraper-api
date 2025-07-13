import pytest
from app import db

@pytest.fixture()
def temp_db(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(db, "JOBS_DB_PATH", str(db_file))
    db.init_db()
    return db_file

def test_insert_retrieve_delete(temp_db):
    sample = {
        "company": "TestCo",
        "workday_id": "WD123",
        "title": "Engineer",
        "job_description": "desc",
        "location": "NY",
        "url": "http://example.com",
        "posted_on": "2024-01-01",
        "start_date": "2024-02-01",
        "time_type": "Full",
        "job_req_id": "REQ1",
        "job_posting_id": "JP1",
        "job_posting_site_id": "SITE1",
        "country": "US",
        "logo_image": "logo.png",
        "can_apply": True,
        "posted": True,
        "include_resume_parsing": True,
        "job_requisition_location": "NYC",
        "remote_type": "Remote",
        "questionnaire_id": "Q1",
        "salary_low": 100.0,
        "salary_high": 200.0,
    }

    db.insert_job_posting(**sample)

    all_jobs = db.get_all_jobs()
    assert len(all_jobs) == 1

    by_company = db.get_jobs_by_company("TestCo")
    assert len(by_company) == 1

    today_jobs = db.get_jobs_today()
    assert len(today_jobs) == 1

    db.delete_job_posting("TestCo", "WD123")
    assert db.get_all_jobs() == []
