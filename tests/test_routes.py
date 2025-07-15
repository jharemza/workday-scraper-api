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
    monkeypatch.setattr(
        "app.scraper.run_institution_scraper",
        lambda cfg: [{"id": "1", "jobDescription": ""}],
    )
    monkeypatch.setattr(config, "JOBS_DB_PATH", str(tmp_path / "route.db"))
    monkeypatch.setattr(db, "JOBS_DB_PATH", str(tmp_path / "route.db"))

    company = "M&T Bank"
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
