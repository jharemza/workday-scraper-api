import hashlib
import logging

import pytest

import app.db as db
import app.scraper as scraper
from app.scraper_pkg.institution_runner import CollectionResult, CollectionStatus


COMPANY = "Transaction Test"
CONFIG = {
    "name": COMPANY,
    "workday_url": "https://example.test/jobs",
    "search_text": "",
}


def job(req_id, workday_id=None):
    return {
        "workday_id": workday_id or f"WD-{req_id}",
        "title": f"Role {req_id}",
        "job_description": "description",
        "location": "NY",
        "url": f"https://example.test/job/{req_id}",
        "posted_on": "2026-11-24",
        "start_date": None,
        "time_type": "Full time",
        "job_req_id": req_id,
        "job_posting_id": f"posting-{req_id}",
        "job_posting_site_id": "external",
        "country": "US",
        "logo_image": None,
        "can_apply": True,
        "posted": True,
        "include_resume_parsing": False,
        "job_requisition_location": "NY",
        "remote_type": None,
        "questionnaire_id": None,
        "salary_low": None,
        "salary_high": None,
    }


def req_ids():
    return {row["job_req_id"] for row in db.get_jobs_by_company(COMPANY)}


def req_hash():
    return hashlib.sha256(",".join(sorted(req_ids())).encode()).hexdigest()


@pytest.fixture()
def seeded_company(monkeypatch, tmp_path):
    db_file = tmp_path / "transactional.db"
    monkeypatch.setattr(db, "JOBS_DB_PATH", str(db_file))
    db.init_db()
    for req_id in ("A", "B", "C"):
        db.insert_job_posting(COMPANY, **job(req_id))
    return db_file


def configure_run(monkeypatch, collection, fetch):
    monkeypatch.setattr(scraper, "init_db", lambda: None)
    monkeypatch.setattr(scraper, "load_institutions_config", lambda: [CONFIG])
    monkeypatch.setattr(scraper, "collect_listing_metadata", lambda _cfg: collection)
    monkeypatch.setattr(scraper, "fetch_job_details", fetch)


@pytest.mark.parametrize(
    "status",
    [CollectionStatus.HTTP_FAILURE, CollectionStatus.PARSE_FAILURE],
)
def test_incomplete_listing_never_mutates_seeded_rows(
    seeded_company, monkeypatch, status
):
    before_hash = req_hash()
    configure_run(
        monkeypatch,
        CollectionResult(status, error="incomplete"),
        lambda _urls: pytest.fail("details must not be fetched"),
    )

    scraper.run_scrape([COMPANY])

    assert req_ids() == {"A", "B", "C"}
    assert req_hash() == before_hash


def test_partial_detail_fetch_keeps_original_rows(seeded_company, monkeypatch):
    before_hash = req_hash()
    configure_run(
        monkeypatch,
        CollectionResult(
            CollectionStatus.SUCCESSFUL_NONEMPTY,
            {"A": "https://example.test/job/A", "D": "https://example.test/job/D"},
        ),
        lambda _urls: [],
    )

    scraper.run_scrape([COMPANY])

    assert req_ids() == {"A", "B", "C"}
    assert req_hash() == before_hash


@pytest.mark.parametrize(
    "details",
    [
        [{**job("D"), "workday_id": None}],
        [job("D"), job("D", workday_id="WD-D-duplicate")],
    ],
)
def test_invalid_detail_identifiers_or_duplicates_keep_original_rows(
    seeded_company, monkeypatch, details
):
    before_hash = req_hash()
    configure_run(
        monkeypatch,
        CollectionResult(
            CollectionStatus.SUCCESSFUL_NONEMPTY,
            {"A": "https://example.test/job/A", "D": "https://example.test/job/D"},
        ),
        lambda _urls: details,
    )

    scraper.run_scrape([COMPANY])

    assert req_ids() == {"A", "B", "C"}
    assert req_hash() == before_hash


def test_existing_only_listing_can_commit_deletions_without_detail_fetch(
    seeded_company, monkeypatch
):
    configure_run(
        monkeypatch,
        CollectionResult(
            CollectionStatus.SUCCESSFUL_NONEMPTY,
            {"A": "https://example.test/job/A"},
        ),
        lambda _urls: pytest.fail("existing postings do not need a detail fetch"),
    )

    scraper.run_scrape([COMPANY])

    assert req_ids() == {"A"}


def test_duplicate_workday_id_rolls_back_all_company_mutations(
    seeded_company, monkeypatch
):
    before_hash = req_hash()
    configure_run(
        monkeypatch,
        CollectionResult(
            CollectionStatus.SUCCESSFUL_NONEMPTY,
            {"A": "https://example.test/job/A", "D": "https://example.test/job/D"},
        ),
        lambda _urls: [job("D", workday_id="WD-A")],
    )

    scraper.run_scrape([COMPANY])

    assert req_ids() == {"A", "B", "C"}
    assert req_hash() == before_hash
    with db._connect() as conn:
        assert not conn.in_transaction


def test_delete_without_an_identifier_is_rejected(seeded_company):
    with pytest.raises(ValueError, match="required"):
        db.delete_job_posting(COMPANY)


def test_mid_transaction_exception_rolls_back_inserts_and_deletes(
    seeded_company, monkeypatch
):
    before_hash = req_hash()
    original_delete = db.delete_job_posting

    def failing_delete(*args, **kwargs):
        if kwargs.get("job_req_id") == "C":
            raise RuntimeError("injected delete failure")
        return original_delete(*args, **kwargs)

    monkeypatch.setattr(db, "delete_job_posting", failing_delete)
    configure_run(
        monkeypatch,
        CollectionResult(
            CollectionStatus.SUCCESSFUL_NONEMPTY,
            {"A": "https://example.test/job/A", "D": "https://example.test/job/D"},
        ),
        lambda _urls: [job("D")],
    )

    scraper.run_scrape([COMPANY])

    assert req_ids() == {"A", "B", "C"}
    assert req_hash() == before_hash
    with db._connect() as conn:
        assert not conn.in_transaction


def test_complete_company_diff_commits_once_with_expected_deltas(
    seeded_company, monkeypatch, caplog
):
    caplog.set_level(logging.INFO, logger=scraper.__name__)
    before_count = len(req_ids())
    before_hash = req_hash()
    configure_run(
        monkeypatch,
        CollectionResult(
            CollectionStatus.SUCCESSFUL_NONEMPTY,
            {"A": "https://example.test/job/A", "D": "https://example.test/job/D"},
        ),
        lambda _urls: [job("D")],
    )

    scraper.run_scrape([COMPANY])

    assert before_count == 3
    assert req_ids() == {"A", "D"}
    assert len(req_ids()) == 2
    assert req_hash() != before_hash
    assert "Inserted: 1" in caplog.text
    assert "Deleted : 2" in caplog.text
    with db._connect() as conn:
        assert not conn.in_transaction
