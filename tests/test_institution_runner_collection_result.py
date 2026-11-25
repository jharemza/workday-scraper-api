import json
from pathlib import Path

import pytest
import requests

import app.scraper as scraper
import app.scraper_pkg.institution_runner as runner
from app.scraper_pkg.institution_runner import CollectionResult, CollectionStatus


FIXTURES = Path(__file__).parent / "fixtures"


class Response:
    def __init__(
        self,
        payload=None,
        *,
        http_error=None,
        json_error=None,
        status_code=None,
        headers=None,
    ):
        self.payload = payload
        self.http_error = http_error
        self.json_error = json_error
        self.status_code = status_code
        self.headers = headers or {}

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
    assert result.complete
    assert result.metadata == {}
    assert result.expected_total == 0
    assert result.pages_fetched == 1


def test_saved_listing_fixtures_document_total_semantics():
    """A zero total needs an empty page; positive totals count page rows."""

    empty_listing = json.loads((FIXTURES / "workday_listing_empty.json").read_text())
    populated_listing = json.loads((FIXTURES / "workday_listing_page.json").read_text())

    assert empty_listing == {"jobPostings": [], "total": 0}
    assert populated_listing["total"] == len(populated_listing["jobPostings"])


def test_non_object_json_root_is_parse_failure(monkeypatch):
    install_posts(monkeypatch, [Response([])])

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert not result.is_authoritative
    assert not result.complete


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
    assert not result.complete


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


def test_429_retry_after_retries_with_capped_server_delay(monkeypatch):
    error_response = Response(status_code=429, headers={"Retry-After": "3"})
    retry_error = requests.HTTPError("429", response=error_response)
    sleeps = []
    install_posts(
        monkeypatch,
        [
            Response(http_error=retry_error),
            Response({"facets": []}),
            Response({"jobPostings": [], "total": 0}),
        ],
    )
    monkeypatch.setattr(runner.time, "sleep", sleeps.append)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.VALID_EMPTY
    assert sleeps == [3]


def test_invalid_retry_after_uses_jittered_backoff(monkeypatch):
    error_response = Response(status_code=429, headers={"Retry-After": "tomorrow"})
    retry_error = requests.HTTPError("429", response=error_response)
    sleeps = []
    install_posts(
        monkeypatch,
        [
            Response(http_error=retry_error),
            Response({"facets": []}),
            Response({"jobPostings": [], "total": 0}),
        ],
    )
    monkeypatch.setattr(runner.time, "sleep", sleeps.append)
    monkeypatch.setattr(runner.random, "uniform", lambda *_args: 0.1)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.VALID_EMPTY
    assert sleeps == [0.6]


def test_5xx_and_timeout_retries_use_bounded_attempts_and_timeout_tuple(monkeypatch):
    error_response = Response(status_code=503)
    server_error = requests.HTTPError("503", response=error_response)
    calls = []
    responses = iter(
        [
            Response(http_error=server_error),
            requests.Timeout("slow"),
            Response({"facets": []}),
            Response({"jobPostings": [], "total": 0}),
        ]
    )

    def post(*_args, **kwargs):
        calls.append(kwargs)
        response = next(responses)
        if isinstance(response, Exception):
            raise response
        return response

    sleeps = []
    monkeypatch.setattr(runner.requests, "post", post)
    monkeypatch.setattr(runner.time, "sleep", sleeps.append)
    monkeypatch.setattr(runner.random, "uniform", lambda *_args: 0)
    monkeypatch.setattr(runner.config, "SCRAPER_MAX_RETRIES", 2)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.VALID_EMPTY
    assert [call["timeout"] for call in calls] == [(5.0, 30.0)] * 4
    assert sleeps == [0.5, 1.0]


def test_429_retry_exhaustion_is_non_authoritative_after_three_attempts(monkeypatch):
    error_response = Response(status_code=429)
    retry_error = requests.HTTPError("429", response=error_response)
    calls = []

    def post(*_args, **_kwargs):
        calls.append(True)
        return Response(http_error=retry_error)

    sleeps = []
    monkeypatch.setattr(runner.requests, "post", post)
    monkeypatch.setattr(runner.time, "sleep", sleeps.append)
    monkeypatch.setattr(runner.random, "uniform", lambda *_args: 0)
    monkeypatch.setattr(runner.config, "SCRAPER_MAX_RETRIES", 2)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.HTTP_FAILURE
    assert result.error_stage == "facets"
    assert not result.complete
    assert len(calls) == 3
    assert sleeps == [0.5, 1.0]


def test_request_budget_exhaustion_is_non_authoritative(monkeypatch):
    monkeypatch.setattr(runner.config, "SCRAPER_REQUEST_BUDGET", 1)
    install_posts(monkeypatch, [Response({"facets": []})])

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.REQUEST_BUDGET_EXHAUSTED
    assert result.error_stage == "initial_listing"
    assert not result.is_authoritative


def test_repeated_page_is_incomplete_with_pagination_metadata(monkeypatch):
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
            Response(
                {
                    "jobPostings": [
                        {"bulletFields": ["REQ1"], "externalPath": "job/REQ1"}
                    ]
                }
            ),
        ],
    )
    monkeypatch.setattr(runner.time, "sleep", lambda *_args: None)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert result.error_stage == "validation"
    assert result.expected_total == 2
    assert result.accumulated_distinct_ids == 1
    assert result.pages_fetched == 1
    assert not result.is_authoritative
    assert not result.complete


def test_pagination_total_change_is_incomplete(monkeypatch):
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
            Response(
                {
                    "jobPostings": [
                        {"bulletFields": ["REQ2"], "externalPath": "job/REQ2"}
                    ],
                    "total": 3,
                }
            ),
        ],
    )
    monkeypatch.setattr(runner.time, "sleep", lambda *_args: None)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert result.error_stage == "pagination"
    assert result.expected_total == 2
    assert result.pages_fetched == 1


def test_short_final_page_fails_reconciliation(monkeypatch):
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
            Response({"jobPostings": []}),
        ],
    )
    monkeypatch.setattr(runner.time, "sleep", lambda *_args: None)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.PARSE_FAILURE
    assert result.error_stage == "reconciliation"
    assert result.expected_total == 2
    assert result.pages_fetched == 2


@pytest.mark.parametrize("offset", [-1, 0])
def test_non_monotonic_pagination_offset_is_rejected(offset):
    with pytest.raises(ValueError, match="not monotonic"):
        runner._record_pagination_offset(offset, [0])


def test_duplicate_requisition_id_keeps_first_url_and_reports_duplicate(monkeypatch):
    monkeypatch.setattr(runner.config, "SCRAPE_LIMIT", 1)
    install_posts(
        monkeypatch,
        [
            Response({"facets": []}),
            Response(
                {
                    "jobPostings": [
                        {"bulletFields": ["REQ1"], "externalPath": "job/REQ1-first"}
                    ],
                    "total": 2,
                }
            ),
            Response(
                {
                    "jobPostings": [
                        {"bulletFields": ["REQ1"], "externalPath": "job/REQ1-second"}
                    ]
                }
            ),
        ],
    )
    monkeypatch.setattr(runner.time, "sleep", lambda *_args: None)

    result = runner.collect_listing_metadata(institution())

    assert result.status is CollectionStatus.SUCCESSFUL_NONEMPTY
    assert result.metadata == {"REQ1": "https://example.test/job/REQ1-first"}
    assert result.accumulated_distinct_ids == 1
    assert result.duplicate_requisition_ids == ("REQ1",)


@pytest.mark.parametrize(
    "status",
    [
        CollectionStatus.HTTP_FAILURE,
        CollectionStatus.NETWORK_FAILURE,
        CollectionStatus.PARSE_FAILURE,
        CollectionStatus.REQUEST_BUDGET_EXHAUSTED,
    ],
)
def test_run_scrape_skips_database_mutations_for_every_incomplete_collection(
    monkeypatch, status
):
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
        lambda _cfg: CollectionResult(status, error="incomplete"),
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
