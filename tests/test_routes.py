import pytest
import app.config as config
import app.db as db

pytest.importorskip("flask")


def test_jobs_all(client):
    res = client.get("/jobs/all")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_jobs_today(client):
    res = client.get("/jobs/today")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)


def test_jobs_company(client):
    company = "M&T Bank"
    res = client.get(f"/jobs/company/{company}")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    if data:
        assert all(job["company"] == company for job in data)


def test_jobs_company_new(client):
    company = "M&T Bank"
    res = client.get(f"/jobs/company/{company}/new")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    if data:
        assert all(job["company"] == company for job in data)


def test_scrape_route(client, monkeypatch, tmp_path):
    db_path = tmp_path / "route.db"
    monkeypatch.setattr(config, "JOBS_DB_PATH", str(db_path))
    monkeypatch.setattr(db, "JOBS_DB_PATH", str(db_path))

    company = "M&T Bank"

    monkeypatch.setattr(
        "app.scraper.load_institutions_config",
        lambda: [
            {"name": company, "workday_url": "http://example.com/jobs", "search_text": ""}
        ],
    )
    monkeypatch.setattr(
        "app.scraper.collect_listing_metadata",
        lambda cfg: {"REQ1": "http://example.com/job/REQ1"},
    )

    def fake_fetch(urls):
        return [
            {
                "workday_id": "1",
                "title": "Role",
                "job_description": "desc",
                "location": "NY",
                "url": urls[0],
                "posted_on": "2024-01-01",
                "start_date": "2024-01-15",
                "time_type": "Full",
                "job_req_id": "REQ1",
                "job_posting_id": "JP1",
                "job_posting_site_id": "SITE1",
                "country": "US",
                "logo_image": "logo.png",
                "can_apply": True,
                "posted": True,
                "include_resume_parsing": False,
                "job_requisition_location": "NY",
                "remote_type": "Remote",
                "questionnaire_id": "Q1",
                "salary_low": 50.0,
                "salary_high": 60.0,
            }
        ]

    monkeypatch.setattr("app.scraper.fetch_job_details", fake_fetch)

    res = client.get(f"/jobs/company/{company}")
    assert res.status_code == 202

    # After scraping, verify the job can be fetched via the API
    res = client.get(f"/jobs/company/{company}")
    assert res.status_code == 200
    rows = res.get_json()
    assert rows
    assert {row["workday_id"] for row in rows} == {"1"}


def test_trigger_scrape(client, monkeypatch):
    monkeypatch.setattr("app.routes.run_scrape", lambda comps: "ok")
    res = client.post("/jobs/scrape", json={"companies": ["TestCo"]})
    assert res.status_code == 202
    assert res.get_json() == {"scraped": "ok"}


def _raise(*_args, **_kwargs):
    raise Exception("boom")


def test_jobs_all_error(client, monkeypatch):
    monkeypatch.setattr("app.routes.get_all_jobs", _raise)
    res = client.get("/jobs/all")
    assert res.status_code == 500
    assert "error" in res.get_json()


def test_jobs_today_error(client, monkeypatch):
    monkeypatch.setattr("app.routes.get_jobs_today", _raise)
    res = client.get("/jobs/today")
    assert res.status_code == 500
    assert "error" in res.get_json()


def test_jobs_company_error(client, monkeypatch):
    monkeypatch.setattr("app.routes.get_jobs_by_company", _raise)
    res = client.get("/jobs/company/TestCo")
    assert res.status_code == 500
    assert "error" in res.get_json()


def test_jobs_company_new_error(client, monkeypatch):
    monkeypatch.setattr("app.routes.get_new_jobs_by_company", _raise)
    res = client.get("/jobs/company/TestCo/new")
    assert res.status_code == 500
    assert "error" in res.get_json()


def test_trigger_scrape_error(client, monkeypatch):
    monkeypatch.setattr("app.routes.run_scrape", _raise)
    res = client.post("/jobs/scrape", json={"companies": ["TestCo"]})
    assert res.status_code == 500
    assert "error" in res.get_json()
