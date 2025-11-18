import app.db as db
import app.config as config
from app.scraper import run_scrape
from app.scraper_pkg.institution_runner import (
    collect_listing_metadata,
    fetch_job_details,
)
import app.scraper_pkg.config_loader as config_loader
import app.scraper_pkg.institution_runner as runner


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

    def raise_for_status(self):
        pass


def make_job(req_id, workday_id=None):
    return {
        "workday_id": workday_id or req_id.replace("REQ", "WD-"),
        "title": f"Role {req_id}",
        "job_description": "desc $50 - $60",
        "location": "NY",
        "url": f"http://example.com/job/{req_id}",
        "posted_on": "2024-01-01",
        "start_date": "2024-01-15",
        "time_type": "Full time",
        "job_req_id": req_id,
        "job_posting_id": f"JP-{req_id}",
        "job_posting_site_id": f"SITE-{req_id}",
        "country": "US",
        "logo_image": "logo.png",
        "can_apply": True,
        "posted": True,
        "include_resume_parsing": False,
        "job_requisition_location": "NY",
        "remote_type": "Remote",
        "questionnaire_id": f"Q-{req_id}",
        "salary_low": 50.0,
        "salary_high": 60.0,
    }


def test_collect_listing_metadata(monkeypatch):
    posts = [
        DummyResponse({"facets": []}),
        DummyResponse(
            {
                "jobPostings": [{"externalPath": "job/REQ1", "bulletFields": ["REQ1"]}],
                "total": 2,
            }
        ),
        DummyResponse(
            {
                "jobPostings": [{"externalPath": "job/REQ2", "bulletFields": ["REQ2"]}],
                "total": 2,
            }
        ),
    ]

    def mock_post(url, json=None, headers=None):
        return posts.pop(0)

    monkeypatch.setattr(runner.requests, "post", mock_post)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(config, "SCRAPE_LIMIT", 1)

    inst = {
        "name": "Test",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": [],
    }

    metadata = collect_listing_metadata(inst)

    assert metadata == {
        "REQ1": "http://example.com/job/REQ1",
        "REQ2": "http://example.com/job/REQ2",
    }


def test_collect_listing_metadata_first_rand_fallback(monkeypatch):
    posts = [
        DummyResponse({"facets": []}),
        DummyResponse(
            {
                "jobPostings": [
                    {
                        "externalPath": "job/REQ3",
                        "bulletFields": ["BF1", "BF2", "REQ3"],
                    },
                    {
                        "externalPath": "job/REQ4",
                        "bulletFields": ["REQ4_ONLY"],
                    },
                    {"externalPath": "job/NOBULLET", "bulletFields": []},
                    {"externalPath": "job/NOKEY"},
                ],
                "total": 4,
            }
        ),
    ]

    def mock_post(url, json=None, headers=None):
        return posts.pop(0)

    monkeypatch.setattr(runner.requests, "post", mock_post)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(config, "SCRAPE_LIMIT", 10)

    inst = {
        "name": "First Rand",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": [],
    }

    metadata = collect_listing_metadata(inst)

    assert metadata == {
        "REQ3": "http://example.com/job/REQ3",
        "REQ4_ONLY": "http://example.com/job/REQ4",
    }


def test_collect_listing_metadata_raymond_james(monkeypatch):
    posts = [
        DummyResponse({"facets": []}),
        DummyResponse(
            {
                "jobPostings": [
                    {
                        "externalPath": "job/REQRJ",
                        "bulletFields": ["IGNORE", "REQRJ"],
                    }
                ],
                "total": 1,
            }
        ),
    ]

    def mock_post(url, json=None, headers=None):
        return posts.pop(0)

    monkeypatch.setattr(runner.requests, "post", mock_post)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(config, "SCRAPE_LIMIT", 10)

    inst = {
        "name": "Raymond James",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": [],
    }

    metadata = collect_listing_metadata(inst)

    assert metadata == {"REQRJ": "http://example.com/job/REQRJ"}


def test_fetch_job_details(monkeypatch):
    responses = {
        "http://example.com/job/REQ1": DummyResponse(
            {
                "jobPostingInfo": {
                    "id": "WD-REQ1",
                    "title": "Engineer",
                    "jobDescription": "desc $50 - $60",
                    "jobRequisitionLocation": {"descriptor": "NY"},
                    "externalUrl": "http://example.com/job/REQ1",
                    "postedOn": "2024-01-01",
                    "startDate": "2024-02-01",
                    "timeType": "Full",
                    "jobReqId": "REQ1",
                    "jobPostingId": "JP1",
                    "jobPostingSiteId": "SITE1",
                    "country": {"descriptor": "US"},
                    "logoImage": {"src": "logo.png"},
                    "canApply": True,
                    "posted": True,
                    "includeResumeParsing": False,
                    "remoteType": "Remote",
                    "questionnaireId": "Q1",
                }
            }
        ),
        "http://example.com/job/REQ2": DummyResponse(
            {
                "jobPostingInfo": {
                    "id": "WD-REQ2",
                    "title": "Engineer",
                    "jobDescription": "desc $70 - $80",
                    "jobRequisitionLocation": {"descriptor": "NY"},
                    "externalUrl": "http://example.com/job/REQ2",
                    "postedOn": "2024-01-01",
                    "startDate": "2024-02-01",
                    "timeType": "Full",
                    "jobReqId": "REQ2",
                    "jobPostingId": "JP2",
                    "jobPostingSiteId": "SITE2",
                    "country": {"descriptor": "US"},
                    "logoImage": {"src": "logo.png"},
                    "canApply": True,
                    "posted": True,
                    "includeResumeParsing": False,
                    "remoteType": "Remote",
                    "questionnaireId": "Q2",
                }
            }
        ),
    }

    def mock_get(url, headers=None):
        return responses[url]

    monkeypatch.setattr(runner.requests, "get", mock_get)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)

    urls = list(responses.keys())
    jobs = fetch_job_details(urls)

    assert {job["job_req_id"] for job in jobs} == {"REQ1", "REQ2"}
    assert jobs[0]["salary_low"] == 50.0
    assert jobs[0]["salary_high"] == 60.0


def test_run_scrape_db_ops(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "JOBS_DB_PATH", str(db_path))
    monkeypatch.setattr(db, "JOBS_DB_PATH", str(db_path))

    inst_cfg = {
        "name": "Test",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
    }
    monkeypatch.setattr(config_loader, "load_institutions_config", lambda: [inst_cfg])

    metadata_runs = [
        {
            "REQ1": "http://example.com/job/REQ1",
            "REQ2": "http://example.com/job/REQ2",
        },
        {
            "REQ2": "http://example.com/job/REQ2",
            "REQ3": "http://example.com/job/REQ3",
        },
    ]

    def fake_collect(_cfg):
        return metadata_runs.pop(0)

    def fake_fetch(urls):
        jobs = []
        for url in urls:
            req_id = url.split("/")[-1]
            jobs.append(make_job(req_id, workday_id=f"WD-{req_id}"))
        return jobs

    monkeypatch.setattr("app.scraper.collect_listing_metadata", fake_collect)
    monkeypatch.setattr("app.scraper.fetch_job_details", fake_fetch)

    run_scrape([inst_cfg["name"]])
    rows = db.get_jobs_by_company("Test")
    assert {r["job_req_id"] for r in rows} == {"REQ1", "REQ2"}

    run_scrape([inst_cfg["name"]])
    rows = db.get_jobs_by_company("Test")
    assert {r["job_req_id"] for r in rows} == {"REQ2", "REQ3"}


def test_run_scrape_skipped_matches_jobs_minus_inserted(monkeypatch):
    inserted_ids = []

    class DummyLogger:
        def __init__(self):
            self.messages = []

        def info(self, message):
            self.messages.append(message)

    dummy_logger = DummyLogger()

    monkeypatch.setattr("app.scraper.init_db", lambda: None)
    monkeypatch.setattr(
        "app.scraper.load_institutions_config",
        lambda: [
            {
                "name": "Test",
                "workday_url": "http://example.com/jobs",
                "search_text": "",
            }
        ],
    )

    scraped_map = {
        "REQ1": "http://example.com/job/REQ1",
        "REQ2": "http://example.com/job/REQ2",
    }

    monkeypatch.setattr(
        "app.scraper.collect_listing_metadata", lambda _cfg: scraped_map
    )
    monkeypatch.setattr("app.scraper.get_existing_job_ids", lambda _company: {"REQ1"})

    def fake_fetch(urls):
        jobs = []
        for url in urls:
            req_id = url.split("/")[-1]
            jobs.append(make_job(req_id, workday_id=f"WD-{req_id}"))
        return jobs

    def fake_insert(company, workday_id, **kwargs):
        inserted_ids.append((company, workday_id))

    monkeypatch.setattr("app.scraper.fetch_job_details", fake_fetch)
    monkeypatch.setattr("app.scraper.insert_job_posting", fake_insert)
    monkeypatch.setattr("app.scraper.delete_job_posting", lambda *a, **k: None)
    monkeypatch.setattr("app.scraper.logger", dummy_logger)

    run_scrape(["Test"])

    inserted_count = len(inserted_ids)
    summary_entry = next(msg for msg in dummy_logger.messages if "Skipped" in msg)
    skipped_line = next(
        line for line in summary_entry.splitlines() if "Skipped" in line
    )
    skipped_value = int(skipped_line.split(":")[-1].strip())

    assert skipped_value == len(scraped_map) - inserted_count


def test_collect_listing_metadata_facets_error(monkeypatch):
    """If the initial POST request fails, an empty dict should be returned."""

    def fail_post(*_args, **_kwargs):
        raise Exception("boom")

    monkeypatch.setattr(runner.requests, "post", fail_post)

    inst = {
        "name": "Test",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": [],
    }

    metadata = collect_listing_metadata(inst)
    assert metadata == {}
