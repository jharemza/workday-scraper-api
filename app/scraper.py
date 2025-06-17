# app/scraper.py

from app.db import (
    init_db,
    get_existing_job_ids,
    insert_job_posting,
    delete_job_posting,
)
from app.scraper_pkg.config_loader import load_institutions_config
from app.scraper_pkg.institution_runner import run_institution_scraper
from tqdm import tqdm


def run_scrape(companies=None):
    """
    1. Ensure the DB schema exists.
    2. Load all institutions (or use provided list).
    3. For each company:
       a. Run the vendored scraper.
       b. Upsert new jobs.
       c. Delete missing jobs.
    Returns a summary dict.
    """
    # 1. Bootstrap DB
    init_db()

    # 2. Determine target companies
    all_insts = load_institutions_config()
    inst_names = [inst["name"] for inst in all_insts]

    if companies:
        targets = companies
    else:
        targets = inst_names

    # 3. Loop and scrape
    for company in targets:
        # 3a. Find config for this company
        cfg = next((i for i in all_insts if i["name"] == company), None)
        if cfg is None:
            # Fallback minimal config
            cfg = {"name": company}

        # 3b. Run the original scraper logic
        jobs = run_institution_scraper(cfg)
        # jobs: list of dicts with keys id, title, location, url, date_posted

        # 3c. Determine existing vs. scraped IDs (use the 'id' field)
        existing = get_existing_job_ids(company)
        scraped = {j["id"] for j in jobs}

        # 3d. Insert new postings
        inserted = 0
        # inside the for‐job loop in run_scrape:

        for job in jobs:
            wid = job["id"]
            title = job.get("title")
            desc = job.get("jobDescription")
            loc = job.get("jobRequisitionLocation", {}).get("descriptor") or job.get(
                "location", {}
            ).get("descriptor")
            url = job.get("externalUrl") or job.get("url")
            posted_on = job.get("postedOn")
            start_date = job.get("startDate")
            time_type = job.get("timeType")
            req_id = job.get("jobReqId")
            post_id = job.get("jobPostingId")
            site_id = job.get("jobPostingSiteId")
            country = job.get("country", {}).get("descriptor")
            logo = job.get("logoImage", {}).get("src")
            can_apply = bool(job.get("canApply"))
            posted = bool(job.get("posted"))
            include_resume = bool(job.get("includeResumeParsing"))
            job_loc = job.get("jobRequisitionLocation", {}).get("descriptor")
            remote = job.get("remoteType")
            q_id = job.get("questionnaireId")

            # salary parsing
            from app.scraper_pkg.institution_runner import extract_salary_range

            salary_low, salary_high = extract_salary_range(desc)

            if wid not in existing:
                insert_job_posting(
                    company,
                    wid,
                    title,
                    desc,
                    loc,
                    url,
                    posted_on,
                    start_date,
                    time_type,
                    req_id,
                    post_id,
                    site_id,
                    country,
                    logo,
                    can_apply,
                    posted,
                    include_resume,
                    job_loc,
                    remote,
                    q_id,
                    salary_low,
                    salary_high,
                )
                inserted += 1

            # 3e. Delete stale postings
            deleted = 0
            for old_id in existing - scraped:
                delete_job_posting(company, old_id)
                deleted += 1

            skipped = len(jobs) - inserted - deleted

        tqdm.write(f"\n📊 {company} Summary:")
        tqdm.write(f"  ✅ Inserted: {inserted}")
        tqdm.write(f"  🟡 Skipped : {skipped}")
        tqdm.write(f"  🔴 Deleted : {deleted}")
        tqdm.write(f"  📦 Total   : {len(jobs)}")
