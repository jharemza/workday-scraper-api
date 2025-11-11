import app.scraper_pkg.institution_runner as runner
from app.scraper_pkg.institution_runner import collect_listing_metadata
from tests.test_scraper import DummyResponse


def test_unmatched_location_facets(monkeypatch):
    """Return empty dict when location descriptors don't match facets."""

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

    metadata = collect_listing_metadata(inst)
    assert metadata == {}
