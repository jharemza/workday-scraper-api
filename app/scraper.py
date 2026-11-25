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


def _institution_result(company, **overrides):
    """Build a machine-readable outcome for one required institution."""

    result = {
        "company": company,
        "metadata_ids_found": 0,
        "detail_fetch_succeeded": 0,
        "failed_detail": 0,
        "actual_inserted": 0,
        "actual_deleted": 0,
        "actual_updated": 0,
        "institution_complete": False,
        "status": "not_started",
        "error": None,
    }
    result.update(overrides)
    return result


def _validate_fetched_details(expected_req_ids, jobs):
    """Require exactly one valid detail record for every planned insertion."""

    found_req_ids = set()
    for job in jobs:
        if not isinstance(job, dict):
            raise ValueError("detail fetch returned a non-object record")
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


def _count_valid_detail_ids(jobs):
    """Count uniquely identified detail rows for observable failure metrics."""

    return len(
        {
            job.get("job_req_id")
            for job in jobs
            if isinstance(job, dict)
            and isinstance(job.get("job_req_id"), str)
            and job.get("job_req_id")
            and job.get("workday_id")
        }
    )


def run_scrape(companies=None):
    """
    Run the Workday scraper for one or more institutions.

    Args:
        companies (list[str] | None): Optional subset of company names to scrape.
                                      If None, all configured institutions run.

    Returns:
        dict: A machine-readable aggregate and per-institution outcomes. Every
        selected institution is required until an explicit optional-institution
        policy is introduced.

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

    institution_results = []

    # 3. Loop and scrape
    for company in targets:
        cfg = next((i for i in all_insts if i["name"] == company), {"name": company})
        logger.info(f"Starting scrape for {company}")
        result = _institution_result(company)

        # 3a. Collect listing metadata only.
        try:
            collection = collect_listing_metadata(cfg)
        except Exception as exc:
            logger.error("Skipping %s: listing collection crashed: %s", company, exc)
            institution_results.append(
                _institution_result(
                    company,
                    status="collection_exception",
                    error=str(exc),
                )
            )
            continue
        if not collection.is_authoritative:
            logger.error(
                "Skipping %s: non-authoritative listing collection (%s): %s",
                company,
                collection.status.value,
                collection.error or "no additional detail",
            )
            result.update(
                status=collection.status.value,
                error=collection.error,
            )
            institution_results.append(result)
            continue
        scraped_map = collection.metadata
        scraped_ids = set(scraped_map.keys())
        result["metadata_ids_found"] = len(scraped_ids)

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
            result["detail_fetch_succeeded"] = _count_valid_detail_ids(new_jobs)
            result["failed_detail"] = max(
                0, len(inserted_ids) - result["detail_fetch_succeeded"]
            )
            try:
                _validate_fetched_details(inserted_ids, new_jobs)
            except ValueError as exc:
                logger.error("Skipping %s: incomplete detail fetch: %s", company, exc)
                result.update(status="detail_validation_failure", error=str(exc))
                institution_results.append(result)
                continue
        else:
            new_jobs = []

        # 3d. Apply the complete, validated mutation plan as one transaction.
        try:
            durable_delta = apply_company_diff(company, new_jobs, deleted_ids)
        except Exception as exc:
            logger.error("Skipping %s: transaction rolled back: %s", company, exc)
            result.update(status="transaction_failure", error=str(exc))
            institution_results.append(result)
            continue

        result.update(
            actual_inserted=durable_delta["inserted"],
            actual_deleted=durable_delta["deleted"],
            institution_complete=True,
            status="complete",
        )
        institution_results.append(result)
        logger.info(f"Completed scrape for {company}")

        summary = (
            f"📊 {company} Summary:\n"
            f"  🧭 Metadata IDs found: {result['metadata_ids_found']}\n"
            f"  🔎 Detail fetch succeeded: {result['detail_fetch_succeeded']}\n"
            f"  ⚠️ Failed detail: {result['failed_detail']}\n"
            f"  ✅ Actual inserted: {result['actual_inserted']}\n"
            f"  🔴 Actual deleted: {result['actual_deleted']}\n"
            f"  🔁 Actual updated: {result['actual_updated']}\n"
            f"  🟡 Skipped existing: {skipped_count}\n"
            f"  🛡️ Institution complete: {result['institution_complete']}\n"
        )
        logger.info(summary)

    success = all(result["institution_complete"] for result in institution_results)
    return {"success": success, "institutions": institution_results}
