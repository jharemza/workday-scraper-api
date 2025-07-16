import app.scraper_pkg.institution_runner as runner
from app.scraper_pkg.institution_runner import run_institution_scraper


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

    def raise_for_status(self):
        pass


def test_unmatched_location_facets(monkeypatch):
    """Return empty list when location descriptors don't match facets."""

    def mock_post(url, json=None, headers=None):
        payload = {
            "facets": [
                {
                    "facetParameter": "locations",
                    "values": [{"descriptor": "Other", "id": "1"}],
                }
            ]
        }
        return DummyResponse(payload)

    monkeypatch.setattr(runner.requests, "post", mock_post)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)

    inst = {
        "name": "Test",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": ["New York"],
    }

    jobs = run_institution_scraper(inst)
    assert jobs == []
