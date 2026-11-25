import pytest
import requests

import app.scraper as scraper
import app.scraper_pkg.institution_runner as runner
from app.scraper_pkg.institution_runner import CollectionResult, CollectionStatus


class Response:
    def __init__(self, payload=None, *, http_error=None, json_error=None):
        self.payload = payload
        self.http_error = http_error
        self.json_error = json_error

    def raise_for_status(self):
        if self.http_error:
            raise self.http_error

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.payload


def institution():
    return {
        "name": "Test",
        "workday_url": "https://example.test/jobs",
        "search_text": "",
        "locations": [],
    }


def install_posts(monkeypatch, responses):
    responses = iter(responses)
    monkeypatch.setattr(
        runner.requests,
        "post",
        lambda *_args, **_kwargs: next(responses),
    )


@pytest.mark.parametrize("message", ["429 Too Many Requests", "500 Server Error"])
def test_facet_http_errors_are_not_authoritative(monkeypatch, message):
    install_posts(monkeypatch, [Response(http_error=requests.HTTPError(message))])

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.HTTP_FAILURE
    assert not result.is_authoritative
    assert result.metadata == {}


def test_facet_connection_error_is_not_authoritative(monkeypatch):
    monkeypatch.setattr(
        runner.requests,
        "post",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            requests.ConnectionError("offline")
        ),
    )

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.NETWORK_FAILURE
    assert not result.is_authoritative


def test_initial_listing_http_failure_cannot_reuse_facet_response(monkeypatch):
    install_posts(
        monkeypatch,
        [Response({"facets": []}), Response(http_error=requests.HTTPError("429"))],
    )

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.HTTP_FAILURE
    assert not result.is_authoritative
    assert result.metadata == {}


@pytest.mark.parametrize(
    "json_error", [ValueError("HTML response"), ValueError("empty body")]
)
def test_invalid_listing_json_is_parse_failure(monkeypatch, json_error):
    install_posts(
        monkeypatch,
        [Response({"facets": []}), Response(json_error=json_error)],
    )

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert not result.is_authoritative


@pytest.mark.parametrize(
    "responses",
    [
        [Response({}), Response({"jobPostings": [], "total": 0})],
        [Response({"facets": []}), Response({"total": 0})],
    ],
)
def test_missing_required_facet_or_listing_fields_are_parse_failures(
    monkeypatch, responses
):
    install_posts(monkeypatch, responses)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert not result.is_authoritative


def test_valid_empty_listing_is_authoritative(monkeypatch):
    install_posts(
        monkeypatch,
        [Response({"facets": []}), Response({"jobPostings": [], "total": 0})],
    )

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.VALID_EMPTY
    assert result.is_authoritative
    assert result.metadata == {}


def test_non_object_json_root_is_parse_failure(monkeypatch):
    install_posts(monkeypatch, [Response([])])

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert not result.is_authoritative


def test_matched_location_is_collected_with_applied_facet(monkeypatch):
    cfg = institution() | {"locations": ["New York"]}
    install_posts(
        monkeypatch,
        [
            Response(
                {
                    "facets": [
                        {
                            "facetParameter": "locations",
                            "values": [{"descriptor": "New York", "id": "NY"}],
                        }
                    ]
                }
            ),
            Response(
                {
                    "jobPostings": [
                        {"bulletFields": ["REQ1"], "externalPath": "job/REQ1"}
                    ],
                    "total": 1,
                }
            ),
        ],
    )

    result = runner.collect_listing_metadata(cfg)

    assert result.status is CollectionStatus.SUCCESSFUL_NONEMPTY
    assert result.metadata == {"REQ1": "https://example.test/job/REQ1"}


@pytest.mark.parametrize(
    "listing",
    [
        {"jobPostings": "not-a-list", "total": 1},
        {"jobPostings": [], "total": True},
        {"jobPostings": [], "total": -1},
        {"jobPostings": [{"bulletFields": ["REQ1"]}], "total": 0},
        {"jobPostings": [], "total": 1},
    ],
)
def test_inconsistent_or_invalid_listing_metadata_is_parse_failure(
    monkeypatch, listing
):
    install_posts(monkeypatch, [Response({"facets": []}), Response(listing)])

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert not result.is_authoritative


@pytest.mark.parametrize(
    "posting",
    [
        "not-an-object",
        {"bulletFields": "REQ1", "externalPath": "job/REQ1"},
        {"bulletFields": ["REQ1"], "externalPath": 42},
    ],
)
def test_malformed_posting_fields_are_parse_failures(monkeypatch, posting):
    install_posts(
        monkeypatch,
        [
            Response({"facets": []}),
            Response({"jobPostings": [posting], "total": 1}),
        ],
    )

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert not result.is_authoritative


def test_positive_listing_without_requisition_metadata_is_parse_failure(monkeypatch):
    install_posts(
        monkeypatch,
        [
            Response({"facets": []}),
            Response(
                {
                    "jobPostings": [
                        {"bulletFields": [], "externalPath": "job/no-requisition"}
                    ],
                    "total": 1,
                }
            ),
        ],
    )

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert not result.is_authoritative


@pytest.mark.parametrize(
    "second_page",
    [
        Response(http_error=requests.HTTPError("500")),
        Response({"total": 2}),
    ],
)
def test_pagination_failure_is_non_authoritative(monkeypatch, second_page):
    monkeypatch.setattr(runner.config, "SCRAPE_LIMIT", 1)
    install_posts(
        monkeypatch,
        [
            Response({"facets": []}),
            Response(
                {
                    "jobPostings": [
                        {"bulletFields": ["REQ1"], "externalPath": "job/REQ1"}
                    ],
                    "total": 2,
                }
            ),
            second_page,
        ],
    )
    monkeypatch.setattr(runner.time, "sleep", lambda *_args, **_kwargs: None)

    result = runner.collect_listing_metadata(institution())

    assert result.status in {
        CollectionStatus.HTTP_FAILURE,
        CollectionStatus.PARSE_FAILURE,
    }
    assert not result.is_authoritative


def test_run_scrape_skips_database_mutations_for_failed_collection(monkeypatch):
    class Logger:
        def __init__(self):
            self.errors = []

        def info(self, *_args, **_kwargs):
            pass

        def error(self, *args, **_kwargs):
            self.errors.append(args)

    logger = Logger()
    monkeypatch.setattr(scraper, "init_db", lambda: None)
    monkeypatch.setattr(scraper, "load_institutions_config", lambda: [institution()])
    monkeypatch.setattr(
        scraper,
        "collect_listing_metadata",
        lambda _cfg: CollectionResult(CollectionStatus.HTTP_FAILURE, error="429"),
    )
    monkeypatch.setattr(
        scraper,
        "get_existing_job_ids",
        lambda *_args: pytest.fail("diff must not run"),
    )
    monkeypatch.setattr(
        scraper,
        "fetch_job_details",
        lambda *_args: pytest.fail("fetch must not run"),
    )
    monkeypatch.setattr(
        scraper,
        "delete_job_posting",
        lambda *_args: pytest.fail("delete must not run"),
    )
    monkeypatch.setattr(scraper, "logger", logger)

    scraper.run_scrape(["Test"])

    assert logger.errors
