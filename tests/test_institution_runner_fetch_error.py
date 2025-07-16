import app.scraper_pkg.institution_runner as runner
from app.scraper_pkg.institution_runner import run_institution_scraper
from tests.test_scraper import DummyResponse


def test_fetch_error_returns_empty(monkeypatch):
    posts = [
        DummyResponse({"facets": []}),
        DummyResponse({"jobPostings": [{"externalPath": "path/1"}], "total": 1}),
    ]

    def mock_post(url, json=None, headers=None):
        return posts.pop(0)

    def mock_get(url, headers=None):
        raise Exception("boom")

    monkeypatch.setattr(runner.requests, "post", mock_post)
    monkeypatch.setattr(runner.requests, "get", mock_get)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)

    inst = {
        "name": "Test",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": [],
    }

    jobs = run_institution_scraper(inst)
    assert jobs == []
