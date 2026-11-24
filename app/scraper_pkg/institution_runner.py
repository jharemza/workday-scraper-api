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
from dataclasses import dataclass, field
from enum import Enum
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

    # Allow optional currency prefixes like "USD" before each dollar sign and
    # accept commas, spaces, or decimals between thousand separators.
    currency_prefix = r"(?:(?:[A-Za-z]{2,4})\s*)?"
    pattern = (
        rf"{currency_prefix}\$\s*([\d][\d,\s]*(?:[.,]\d+)?)\s*[-–—]\s*"
        rf"{currency_prefix}\$?\s*([\d][\d,\s]*(?:[.,]\d+)?)"
    )
    match = re.search(pattern, description)
    if not match:
        logging.debug("Salary pattern not found in job description.")
        return None, None

    def _clean_numeric(value: str) -> str:
        """Normalize salary text to digits plus an optional decimal point."""

        normalized = value.replace("\xa0", "").replace(" ", "")

        decimal_match = re.match(r"^(.*),(\d{2})$", normalized)
        if decimal_match:
            whole, cents = decimal_match.groups()
            whole = whole.replace(".", "")
            normalized = f"{whole}.{cents}"
        else:
            normalized = normalized.replace(",", "")

        return re.sub(r"[^\d.]", "", normalized)

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


class CollectionStatus(str, Enum):
    """Whether listing metadata can safely drive a destructive diff."""

    VALID_EMPTY = "valid_empty"
    SUCCESSFUL_NONEMPTY = "successful_nonempty"
    UNMATCHED_LOCATION = "unmatched_location"
    HTTP_FAILURE = "http_failure"
    NETWORK_FAILURE = "network_failure"
    PARSE_FAILURE = "parse_failure"


@dataclass(frozen=True)
class CollectionResult:
    """Authoritative listing metadata or a fail-closed collection outcome."""

    status: CollectionStatus
    metadata: dict[str, str] = field(default_factory=dict)
    error: str | None = None

    @property
    def is_authoritative(self) -> bool:
        return self.status in {
            CollectionStatus.VALID_EMPTY,
            CollectionStatus.SUCCESSFUL_NONEMPTY,
        }


def _post_json(url, payload, company_name, request_name):
    """POST and decode a JSON object, never reusing a failed response."""

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        message = f"{request_name} HTTP failure: {exc}"
        log_with_prefix("error", company_name, message)
        return None, CollectionStatus.HTTP_FAILURE, message
    except requests.RequestException as exc:
        message = f"{request_name} network failure: {exc}"
        log_with_prefix("error", company_name, message)
        return None, CollectionStatus.NETWORK_FAILURE, message

    try:
        body = response.json()
    except ValueError as exc:
        message = f"{request_name} JSON parse failure: {exc}"
        log_with_prefix("error", company_name, message)
        return None, CollectionStatus.PARSE_FAILURE, message

    if not isinstance(body, dict):
        message = (
            f"{request_name} JSON root must be an object, " f"got {type(body).__name__}"
        )
        log_with_prefix("error", company_name, message)
        return None, CollectionStatus.PARSE_FAILURE, message

    return body, None, None


def collect_listing_metadata(cfg):
    """
    Collect listing metadata (req_id → URL) for a single institution.

    Uses Workday's JSON facet and pagination APIs to gather all active
    job postings, applying optional location filters.

    Returns:
        CollectionResult: An authoritative valid-empty/nonempty result, or a
        non-authoritative failure/unmatched-location result.  Callers must not
        compute inserts or deletions from a non-authoritative result.
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

    facet_data, failure_status, error = _post_json(
        url, initial_payload, company_name, "Facet request"
    )
    if failure_status:
        return CollectionResult(failure_status, error=error)
    if "facets" not in facet_data or not isinstance(facet_data["facets"], list):
        message = "Facet response must contain a list-valued 'facets' field"
        log_with_prefix("error", company_name, message)
        return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)

    facets = facet_data["facets"]
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
        return CollectionResult(CollectionStatus.UNMATCHED_LOCATION)

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

    data, failure_status, error = _post_json(
        url, job_payload, company_name, "Initial listing request"
    )
    if failure_status:
        return CollectionResult(failure_status, error=error)
    if "jobPostings" not in data or "total" not in data:
        message = "Initial listing response requires 'jobPostings' and 'total'"
        log_with_prefix("error", company_name, message)
        return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)
    jobs_first_batch = data["jobPostings"]
    total = data["total"]
    if (
        not isinstance(jobs_first_batch, list)
        or isinstance(total, bool)
        or not isinstance(total, int)
        or total < 0
    ):
        message = "Initial listing response has invalid 'jobPostings' or 'total' types"
        log_with_prefix("error", company_name, message)
        return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)
    if total == 0:
        if jobs_first_batch:
            message = "Initial listing response has total=0 with nonempty jobPostings"
            log_with_prefix("error", company_name, message)
            return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)
        return CollectionResult(CollectionStatus.VALID_EMPTY)
    if not jobs_first_batch:
        message = "Initial listing response has positive total with empty jobPostings"
        log_with_prefix("error", company_name, message)
        return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)
    total_pages = math.ceil(total / limit)

    log_with_prefix("info", company_name, f"Total job postings found: {total}")
    log_with_prefix("info", company_name, f"Total pages to scrape: {total_pages}")

    # Initialize your progress bar with known total_pages
    page_pbar = tqdm(
        desc=f"{company_name}: Pages scraped", unit="page", total=total_pages
    )

    def extract_req_id(job_posting):
        if not isinstance(job_posting, dict):
            raise ValueError("jobPostings entries must be objects")
        bullet_fields = job_posting.get("bulletFields") or []
        if not isinstance(bullet_fields, list):
            raise ValueError("jobPosting bulletFields must be a list when present")

        if company_name == "First Rand" and len(bullet_fields) > 2:
            return bullet_fields[2] or (bullet_fields[0] if bullet_fields else None)
        elif company_name == "Raymond James" and len(bullet_fields) > 1:
            return bullet_fields[1] or (bullet_fields[0] if bullet_fields else None)

        return bullet_fields[0] if bullet_fields else None

    def collect_batch(jobs):
        if not isinstance(jobs, list):
            raise ValueError("jobPostings must be a list")
        for job in jobs:
            req_id = extract_req_id(job)
            ext_path = job.get("externalPath", "")
            if ext_path and not isinstance(ext_path, str):
                raise ValueError(
                    "jobPosting externalPath must be a string when present"
                )
            if req_id and ext_path:
                job_url = f"{url.rsplit('/jobs', 1)[0]}/job/{ext_path.split('/')[-1]}"
                scraped_map[req_id] = job_url

    try:
        collect_batch(jobs_first_batch)
        page_pbar.update(1)
        offset += limit

        # Loop through the remaining pages. Any failed page invalidates the
        # full listing result so downstream deletion cannot run on a partial map.
        while page_pbar.n < total_pages:
            job_payload = {
                "limit": limit,
                "offset": offset,
                "appliedFacets": applied_facets,
                "searchText": search_text,
            }
            page_data, failure_status, error = _post_json(
                url, job_payload, company_name, "Pagination request"
            )
            if failure_status:
                return CollectionResult(failure_status, error=error)
            if "jobPostings" not in page_data or not isinstance(
                page_data["jobPostings"], list
            ):
                message = (
                    "Pagination response requires a list-valued " "'jobPostings' field"
                )
                log_with_prefix("error", company_name, message)
                return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)
            collect_batch(page_data["jobPostings"])
            offset += limit
            page_pbar.update(1)
            time.sleep(config.SCRAPER_LISTING_DELAY_SECONDS)
    except ValueError as exc:
        message = f"Listing response field validation failure: {exc}"
        log_with_prefix("error", company_name, message)
        return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)
    finally:
        page_pbar.close()

    if not scraped_map:
        message = "Positive listing total produced no usable requisition metadata"
        log_with_prefix("error", company_name, message)
        return CollectionResult(CollectionStatus.PARSE_FAILURE, error=message)

    sm_count = len(scraped_map)
    msg = f"Total job URLs collected: {sm_count}"

    log_with_prefix("info", company_name, "🏁 Metadata collection complete.")
    log_with_prefix("info", company_name, msg)
    log_with_prefix("info", company_name, f"Total pages scraped: {page_pbar.n}")

    return CollectionResult(CollectionStatus.SUCCESSFUL_NONEMPTY, scraped_map)


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
            response = requests.get(
                url, headers={"User-Agent": config.SCRAPER_USER_AGENT}
            )
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

        time.sleep(config.SCRAPER_DETAIL_DELAY_SECONDS)

    return job_postings
