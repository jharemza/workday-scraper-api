"""
Institution-level scraping utilities.

Includes:
  • Facet discovery and pagination for listing metadata.
  • Job-detail fetching and normalization.
  • Salary-range extraction helper.
"""

import requests
import logging
import time
import re
from tqdm import tqdm
import math
import app.config as config


def find_id_by_descriptor(facets, target_descriptor):
    """
    Recursively find the ID and facetParameter for a given descriptor
    across Workday facetParameters.

    Args:
        facets (list): The facets list loaded from JSON.
        target_descriptor (str): The descriptor text to search for.

    Returns:
        tuple: (facetParameter, id) if found, or (None, None) if not found.
    """
    target_descriptor = target_descriptor.strip().lower()

    for facet in facets:
        facet_parameter = facet.get("facetParameter", "")
        values = facet.get("values", [])

        for value in values:
            descriptor = value.get("descriptor", "").strip().lower()
            if descriptor == target_descriptor and "id" in value:
                return facet_parameter, value["id"]

            if "facetParameter" in value and "values" in value:
                nested_facet_parameter = value["facetParameter"]
                nested_values = value["values"]

                found_facet_parameter, found_id = find_id_by_descriptor(
                    [
                        {
                            "facetParameter": nested_facet_parameter,
                            "values": nested_values,
                        }
                    ],
                    target_descriptor,
                )

                if found_id:
                    return found_facet_parameter, found_id

    return None, None


def extract_salary_range(description):
    """Extract salary range (low, high) as floats from jobDescription HTML text."""

    # Match values that may contain spaces, commas, or decimals and account for
    # optional whitespace around the currency symbol and hyphen variations.
    match = re.search(
        r"\$\s*([\d][\d,\s]*(?:\.\d+)?)\s*[-–—]\s*\$?\s*([\d][\d,\s]*(?:\.\d+)?)",
        description,
    )
    if not match:
        logging.debug("Salary pattern not found in job description.")
        return None, None

    def _clean_numeric(value: str) -> str:
        """Strip non-numeric characters (except decimal point) from salary text."""

        return re.sub(r"[^\d.]", "", value)

    low_str = _clean_numeric(match.group(1))
    high_str = _clean_numeric(match.group(2))

    try:
        low = float(low_str)
        high = float(high_str)
        return low, high
    except ValueError:
        logging.debug(f"Float conversion failed: low='{low_str}', high='{high_str}'")
        return None, None


def log_with_prefix(level, company_name, message):
    getattr(logging, level)(f"[{company_name}] {message}")


def collect_listing_metadata(cfg):
    """
    Collect listing metadata (req_id → URL) for a single institution.

    Uses Workday's JSON facet and pagination APIs to gather all active
    job postings, applying optional location filters.

    Returns:
        dict[str, str]: Map of req_id → job URL.
    """

    # 1. Set local vars from config
    company_name = cfg["name"]
    url = cfg["workday_url"]
    locations = cfg.get("locations", [])
    search_text = cfg["search_text"]

    log_with_prefix("info", company_name, "🏁 Starting metadata collection.")

    # 2. Initial fetch for facets
    initial_payload = {
        "limit": config.FACET_LIMIT,
        "offset": 0,
        "appliedFacets": {},
        "searchText": "",
    }

    try:
        response = requests.post(
            url, json=initial_payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    except Exception as e:
        log_with_prefix("error", company_name, f"Failed to fetch facets: {e}")
        return {}

    facets = response.json().get("facets", [])
    location_ids = []

    if locations:
        for loc in tqdm(locations, desc=f"{company_name}: Location facets", unit="loc"):
            facet_param, loc_id = find_id_by_descriptor(facets, loc)
            if loc_id:
                location_ids.append(loc_id)
            else:
                log_with_prefix(
                    "error", company_name, f"Location '{loc}' not found in facets."
                )

    if locations and not location_ids:
        log_with_prefix(
            "warning",
            company_name,
            "No valid location IDs matched descriptors. Skipping.",
        )
        return {}

    # 3. Job collection

    # Initial variables
    offset = 0
    limit = config.SCRAPE_LIMIT
    scraped_map = {}

    applied_facets = {}
    if location_ids:
        applied_facets["locations"] = location_ids

    # First request to discover total jobs
    job_payload = {
        "limit": limit,
        "offset": offset,
        "appliedFacets": applied_facets,
        "searchText": search_text,
    }

    try:
        response = requests.post(
            url, json=job_payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    except Exception as e:
        log_with_prefix("error", company_name, f"Pagination request failed: {e}")

    # Compute how many pages to expect
    data = response.json()
    jobs_first_batch = data.get("jobPostings", [])
    total = data.get("total", 0)
    total_pages = math.ceil(total / limit)

    log_with_prefix("info", company_name, f"Total job postings found: {total}")
    log_with_prefix("info", company_name, f"Total pages to scrape: {total_pages}")

    # Initialize your progress bar with known total_pages
    page_pbar = tqdm(
        desc=f"{company_name}: Pages scraped", unit="page", total=total_pages
    )

    def extract_req_id(job_posting):
        bullet_fields = job_posting.get("bulletFields") or []

        if company_name == "First Rand" and len(bullet_fields) > 2:
            return bullet_fields[2] or (bullet_fields[0] if bullet_fields else None)
        elif company_name == "Raymond James" and len(bullet_fields) > 1:
            return bullet_fields[1] or (bullet_fields[0] if bullet_fields else None)

        return bullet_fields[0] if bullet_fields else None

    # Collect URLs from first batch
    for job in jobs_first_batch:
        req_id = extract_req_id(job)

        ext_path = job.get("externalPath", "")
        if req_id and ext_path:
            job_url = f"{url.rsplit('/jobs', 1)[0]}/job/{ext_path.split('/')[-1]}"
            scraped_map[req_id] = job_url

    page_pbar.update(1)
    offset += limit

    # Loop through the *remaining* pages
    while page_pbar.n < total_pages:

        job_payload = {
            "limit": limit,
            "offset": offset,
            "appliedFacets": applied_facets,
            "searchText": search_text,
        }

        try:
            response = requests.post(
                url, json=job_payload, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        except Exception as e:
            log_with_prefix("error", company_name, f"Pagination request failed: {e}")
            break

        jobs = response.json().get("jobPostings", [])

        for job in jobs:
            req_id = extract_req_id(job)

            ext_path = job.get("externalPath", "")
            if req_id and ext_path:
                job_url = f"{url.rsplit('/jobs', 1)[0]}/job/{ext_path.split('/')[-1]}"
                scraped_map[req_id] = job_url

        offset += limit
        page_pbar.update(1)
        time.sleep(0.1)

    sm_count = len(scraped_map)
    msg = f"Total job URLs collected: {sm_count}"

    log_with_prefix("info", company_name, "🏁 Metadata collection complete.")
    log_with_prefix("info", company_name, msg)
    log_with_prefix("info", company_name, f"Total pages scraped: {page_pbar.n}")

    page_pbar.close()

    return scraped_map


def fetch_job_details(urls):
    """
    Fetch and normalize detailed job data for each URL.

    Performs individual GET requests, extracts key fields expected by
    insert_job_posting(), and parses salary ranges.

    Args:
        urls (Iterable[str]): Job posting URLs.

    Returns:
        list[dict]: Normalized job objects.
    """

    job_postings = []
    for idx, url in tqdm(
        enumerate(urls),
        total=len(urls),
        desc="Fetching job data",
    ):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            job_data = response.json().get("jobPostingInfo")
            if not job_data:
                continue

            desc = job_data.get("jobDescription")
            loc_info = job_data.get("jobRequisitionLocation", {})
            salary_low, salary_high = extract_salary_range(desc)

            job = {
                "workday_id": job_data.get("id"),
                "title": job_data.get("title"),
                "job_description": desc,
                "location": loc_info.get("descriptor"),
                "url": job_data.get("externalUrl") or job_data.get("url"),
                "posted_on": job_data.get("postedOn"),
                "start_date": job_data.get("startDate"),
                "time_type": job_data.get("timeType"),
                "job_req_id": job_data.get("jobReqId"),
                "job_posting_id": job_data.get("jobPostingId"),
                "job_posting_site_id": job_data.get("jobPostingSiteId"),
                "country": job_data.get("country", {}).get("descriptor"),
                "logo_image": job_data.get("logoImage", {}).get("src"),
                "can_apply": bool(job_data.get("canApply")),
                "posted": bool(job_data.get("posted")),
                "include_resume_parsing": bool(job_data.get("includeResumeParsing")),
                "job_requisition_location": loc_info.get("descriptor"),
                "remote_type": job_data.get("remoteType"),
                "questionnaire_id": job_data.get("questionnaireId"),
                "salary_low": salary_low,
                "salary_high": salary_high,
            }

            job_postings.append(job)

        except Exception as e:
            log_with_prefix("error", "GLOBAL", f"Fetch job detail failed ({url}): {e}")
            continue

        time.sleep(0.5)

    return job_postings
