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
    insert_job_posting,
    delete_job_posting,
)
from app.scraper_pkg.config_loader import load_institutions_config
from app.scraper_pkg.institution_runner import (
    collect_listing_metadata,
    fetch_job_details,
)
from tqdm import tqdm
import logging


logger = logging.getLogger(__name__)


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
        scraped_map = collect_listing_metadata(cfg)
        scraped_ids = set(scraped_map.keys())

        # 3b. Diffing
        # Compute set-based diffs to identify inserted/deleted postings
        db_ids = set(get_existing_job_ids(company))
        inserted_ids = scraped_ids - db_ids
        deleted_ids = db_ids - scraped_ids
        skipped_count = len(scraped_ids) - len(inserted_ids)
        logger.info(
            f"📊 {company} Summary:\n"
            f"  ✅ Inserted: {len(inserted_ids)}\n"
            f"  🟡 Skipped : {skipped_count}\n"
            f"  🔴 Deleted : {len(deleted_ids)}\n"
            f"  📦 Total   : {len(scraped_ids)}\n"
        )

        # 3c. Fetch details only for jobs to be inserted.
        # Fetch and insert details for new postings only
        if inserted_ids:
            inserted_urls = [scraped_map[i] for i in inserted_ids]
            new_jobs = fetch_job_details(inserted_urls)
            for job in new_jobs:
                insert_job_posting(company, **job)

        # 3d. Delete stale postings
        # Remove postings no longer listed in the source
        for req_id in deleted_ids:
            delete_job_posting(company, job_req_id=req_id)

        logger.info(f"Completed scrape for {company}")

        tqdm.write(f"\n📊 {company} Summary:")
        tqdm.write(f"  ✅ Inserted: {len(inserted_ids)}")
        tqdm.write(f"  🟡 Skipped : {skipped_count}")
        tqdm.write(f"  🔴 Deleted : {len(deleted_ids)}")
        tqdm.write(f"  📦 Total   : {len(scraped_ids)}\n")
