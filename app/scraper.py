# app/scraper.py

"""
Orchestrates the full scraping workflow for all configured institutions.

Flow:
  1. Initialize database schema.
  2. Collect listing metadata (req_id → URL).
  3. Compute diff against existing DB entries.
  4. Fetch details only for new postings.
  5. Delete postings no longer present.

This diff-based design minimizes redundant network requests.
"""

from app.db import (
    init_db,
    get_existing_job_ids,
    apply_company_diff,
)
from app.scraper_pkg.config_loader import load_institutions_config
from app.scraper_pkg.institution_runner import (
    collect_listing_metadata,
    fetch_job_details,
)
import logging


logger = logging.getLogger(__name__)


def _validate_fetched_details(expected_req_ids, jobs):
    """Require exactly one valid detail record for every planned insertion."""

    found_req_ids = set()
    for job in jobs:
        req_id = job.get("job_req_id")
        workday_id = job.get("workday_id")
        if not isinstance(req_id, str) or not req_id or not workday_id:
            raise ValueError("detail fetch returned a job without required identifiers")
        if req_id in found_req_ids:
            raise ValueError(f"detail fetch returned duplicate requisition {req_id}")
        found_req_ids.add(req_id)

    if found_req_ids != expected_req_ids:
        raise ValueError(
            "detail fetch did not return exactly the planned requisitions "
            f"(expected {sorted(expected_req_ids)}, got {sorted(found_req_ids)})"
        )


def run_scrape(companies=None):
    """
    Run the Workday scraper for one or more institutions.

    Args:
        companies (list[str] | None): Optional subset of company names to scrape.
                                      If None, all configured institutions run.

    Returns:
        None. Inserts and deletes records in the local database.

    1. Ensure the DB schema exists.
    2. Load all institutions (or use provided list).
    3. For each company:
       a. Collect listing metadata only.
       b. Diffing.
       c. Fetch details only for inserted.
       d. Delete stale postings.
    """
    # 1. Bootstrap DB
    init_db()

    # 2. Determine target companies
    all_insts = load_institutions_config()
    inst_names = [inst["name"] for inst in all_insts]
    targets = companies or inst_names

    # 3. Loop and scrape
    for company in targets:
        cfg = next((i for i in all_insts if i["name"] == company), {"name": company})
        logger.info(f"Starting scrape for {company}")

        # 3a. Collect listing metadata only.
        collection = collect_listing_metadata(cfg)
        if not collection.is_authoritative:
            logger.error(
                "Skipping %s: non-authoritative listing collection (%s): %s",
                company,
                collection.status.value,
                collection.error or "no additional detail",
            )
            continue
        scraped_map = collection.metadata
        scraped_ids = set(scraped_map.keys())

        # 3b. Diffing
        # Compute set-based diffs to identify inserted/deleted postings
        db_ids = set(get_existing_job_ids(company))
        inserted_ids = scraped_ids - db_ids
        deleted_ids = db_ids - scraped_ids
        skipped_count = len(scraped_ids) - len(inserted_ids)

        # 3c. Fetch and validate every detail before beginning any database work.
        if inserted_ids:
            inserted_urls = [scraped_map[i] for i in inserted_ids]
            new_jobs = fetch_job_details(inserted_urls)
            try:
                _validate_fetched_details(inserted_ids, new_jobs)
            except ValueError as exc:
                logger.error("Skipping %s: incomplete detail fetch: %s", company, exc)
                continue
        else:
            new_jobs = []

        # 3d. Apply the complete, validated mutation plan as one transaction.
        try:
            durable_delta = apply_company_diff(company, new_jobs, deleted_ids)
        except Exception as exc:
            logger.error("Skipping %s: transaction rolled back: %s", company, exc)
            continue

        logger.info(f"Completed scrape for {company}")

        summary = (
            f"📊 {company} Summary:\n"
            f"  ✅ Inserted: {durable_delta['inserted']}\n"
            f"  🟡 Skipped : {skipped_count}\n"
            f"  🔴 Deleted : {durable_delta['deleted']}\n"
            f"  📦 Total   : {len(scraped_ids)}\n"
        )
        logger.info(summary)
