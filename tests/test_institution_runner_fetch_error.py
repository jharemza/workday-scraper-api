import app.scraper_pkg.institution_runner as runner
from app.scraper_pkg.institution_runner import fetch_job_details


def test_fetch_error_returns_empty(monkeypatch):
    def mock_get(url, headers=None):
        raise Exception("boom")

    monkeypatch.setattr(runner.requests, "get", mock_get)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)

    jobs = fetch_job_details(["http://example.com/job/REQ1"])
    assert jobs == []
