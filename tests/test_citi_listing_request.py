import json
from pathlib import Path

import requests

from app.scraper_pkg.institution_runner import (
    CollectionStatus,
    collect_listing_metadata,
)


FIXTURES = Path(__file__).parent / "fixtures"
CITI_URL = "https://citi.wd5.myworkdayjobs.com/wday/cxs/citi/2/jobs"


class Http400Response:
    status_code = 400
    headers = {}

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        raise requests.HTTPError("400 Client Error", response=self)

    def json(self):
        return self.payload


def test_citi_listing_http_400_is_fail_closed_and_records_request_contract(monkeypatch):
    """A Citi HTTP 400 is never interpreted as an authoritative empty listing."""

    calls = []
    error_payload = json.loads((FIXTURES / "citi_listing_http_400.json").read_text())

    def post(url, *, json=None, headers=None, timeout=None):
        calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return Http400Response(error_payload)

    monkeypatch.setattr(requests, "post", post)
    result = collect_listing_metadata(
        {
            "name": "Citi",
            "workday_url": CITI_URL,
            "search_text": "sql",
        }
    )

    assert calls == [
        {
            "url": CITI_URL,
            "json": {
                "limit": 20,
                "offset": 0,
                "appliedFacets": {},
                "searchText": "sql",
            },
            "headers": {"Content-Type": "application/json"},
            "timeout": (5.0, 30.0),
        }
    ]
    assert result.status is CollectionStatus.HTTP_FAILURE
    assert not result.is_authoritative
    assert not result.complete
    assert result.metadata == {}
    assert "400" in result.error


def test_citi_without_location_filters_skips_facet_preflight(monkeypatch):
    calls = []

    class ListingResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "jobPostings": [
                    {"bulletFields": ["REQ-1"], "externalPath": "job/REQ-1"}
                ],
                "total": 1,
            }

    def post(url, *, json=None, headers=None, timeout=None):
        calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return ListingResponse()

    monkeypatch.setattr(requests, "post", post)
    result = collect_listing_metadata(
        {
            "name": "Citi",
            "workday_url": CITI_URL,
            "search_text": "sql",
        }
    )

    assert result.status is CollectionStatus.SUCCESSFUL_NONEMPTY
    assert calls == [
        {
            "url": CITI_URL,
            "json": {
                "limit": 20,
                "offset": 0,
                "appliedFacets": {},
                "searchText": "sql",
            },
            "headers": {"Content-Type": "application/json"},
            "timeout": (5.0, 30.0),
        }
    ]
