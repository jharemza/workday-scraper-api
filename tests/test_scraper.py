import app.db as db
import app.config as config
from app.scraper import run_scrape
from app.scraper_pkg.institution_runner import run_institution_scraper
import app.scraper_pkg.config_loader as config_loader
import app.scraper_pkg.institution_runner as runner


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

    def raise_for_status(self):
        pass


def test_run_institution_scraper(monkeypatch):
    posts = [
        DummyResponse({"facets": []}),
        DummyResponse({"jobPostings": [{"externalPath": "path/1"}], "total": 2}),
        DummyResponse({"jobPostings": [{"externalPath": "path/2"}], "total": 2}),
    ]

    def mock_post(url, json=None, headers=None):
        return posts.pop(0)

    gets = {
        "http://example.com/job/1": DummyResponse({"jobPostingInfo": {"id": "1"}}),
        "http://example.com/job/2": DummyResponse({"jobPostingInfo": {"id": "2"}}),
    }

    def mock_get(url, headers=None):
        return gets[url]

    monkeypatch.setattr(runner.requests, "post", mock_post)
    monkeypatch.setattr(runner.requests, "get", mock_get)
    monkeypatch.setattr(runner.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(config, "SCRAPE_LIMIT", 1)
    inst = {
        "name": "Test",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": [],
    }

    jobs = run_institution_scraper(inst)
    assert len(jobs) == 2
    assert {j["id"] for j in jobs} == {"1", "2"}


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

    def first(_cfg):
        return [
            {"id": "1", "jobDescription": "desc $50 - $60"},
            {"id": "2", "jobDescription": "desc"},
        ]

    monkeypatch.setattr(runner, "run_institution_scraper", first)
    monkeypatch.setattr("app.scraper.run_institution_scraper", first)
    run_scrape(["Test"])
    rows = db.get_jobs_by_company("Test")
    assert {r["workday_id"] for r in rows} == {"1", "2"}

    def second(_cfg):
        return [
            {"id": "2", "jobDescription": "desc"},
            {"id": "3", "jobDescription": "desc"},
        ]

    monkeypatch.setattr(runner, "run_institution_scraper", second)
    monkeypatch.setattr("app.scraper.run_institution_scraper", second)
    run_scrape(["Test"])
    rows = db.get_jobs_by_company("Test")
    assert {r["workday_id"] for r in rows} == {"2", "3"}


def test_run_scrape_skipped_matches_jobs_minus_inserted(monkeypatch):
    inserted_ids = []
    captured_logs = []

    monkeypatch.setattr("app.scraper.init_db", lambda: None)
    monkeypatch.setattr(
        "app.scraper.load_institutions_config", lambda: [{"name": "Test"}]
    )
    jobs = [
        {"id": "1", "jobDescription": "existing role"},
        {"id": "2", "jobDescription": "new role"},
    ]
    monkeypatch.setattr("app.scraper.run_institution_scraper", lambda _cfg: jobs)
    monkeypatch.setattr("app.scraper.get_existing_job_ids", lambda _company: {"1"})

    def fake_insert(company, workday_id, *args, **kwargs):
        inserted_ids.append((company, workday_id))

    monkeypatch.setattr("app.scraper.insert_job_posting", fake_insert)
    monkeypatch.setattr("app.scraper.delete_job_posting", lambda *a, **k: None)
    monkeypatch.setattr(
        "app.scraper.tqdm.write",
        lambda message: captured_logs.append(message)
    )

    run_scrape(["Test"])

    inserted_count = len(inserted_ids)
    skipped_line = next(line for line in captured_logs if "Skipped" in line)
    skipped_value = int(skipped_line.split(":")[-1].strip())

    assert skipped_value == len(jobs) - inserted_count


def test_run_institution_scraper_facets_error(monkeypatch):
    """If the initial POST request fails, an empty list should be returned."""

    def fail_post(*_args, **_kwargs):
        raise Exception("boom")

    monkeypatch.setattr(runner.requests, "post", fail_post)

    inst = {
        "name": "Test",
        "workday_url": "http://example.com/jobs",
        "search_text": "",
        "locations": [],
    }

    jobs = run_institution_scraper(inst)
    assert jobs == []
