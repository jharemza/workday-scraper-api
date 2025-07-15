import pytest
import app.config as config
import app.db as db
try:
    import flask  # noqa: F401
except Exception:
    pytest.skip("flask not installed", allow_module_level=True)


def test_jobs_all(client):
    res = client.get("/jobs/all")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_scrape_route(client, monkeypatch, tmp_path):
    monkeypatch.setattr(
        "app.scraper.run_institution_scraper",
        lambda cfg: [{"id": "1", "jobDescription": ""}],
    )
    monkeypatch.setattr(config, "JOBS_DB_PATH", str(tmp_path / "route.db"))
    monkeypatch.setattr(db, "JOBS_DB_PATH", str(tmp_path / "route.db"))

    company = "M&T Bank"
    res = client.post("/jobs/scrape", json={"companies": [company]})
    assert res.status_code == 202

    data = res.get_json()
    if "scraped" in data:
        assert data["scraped"] is None
    else:
        assert isinstance(data, list)
