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


def run_institution_scraper(institution: dict):
    """Run scraping for a single institution."""

    # 1. Set local vars from config
    url = institution["workday_url"]
    locations = institution.get("locations", [])
    search_text = institution["search_text"]
    company_name = institution["name"]

    log_with_prefix("info", company_name, "🏁 Starting scrape.")

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
        return []

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
        return []

    # 3. Job collection

    # Initial variables
    offset = 0
    limit = config.SCRAPE_LIMIT
    job_urls = []

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

    # Initialize your progress bar with known total_pages
    page_pbar = tqdm(
        desc=f"{company_name}: Pages scraped", unit="page", total=total_pages
    )

    # Collect URLs from first batch
    first_jobs_data = [
        f"{url.rsplit('/jobs', 1)[0]}/job/{job.get('externalPath', '').split('/')[-1]}"
        for job in jobs_first_batch
        if "externalPath" in job
    ]

    job_urls.extend(first_jobs_data)

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
        jobs_data = [
            f"{url.rsplit('/jobs', 1)[0]}/job/{job.get('externalPath',
                                                       '').split('/')[-1]}"
            for job in jobs
            if "externalPath" in job
        ]

        if not jobs_data:
            break

        job_urls.extend(jobs_data)

        offset += limit
        page_pbar.update(1)
        time.sleep(0.5)

    tqdm.write(f"\n📄 {company_name} Pagination Summary:")
    tqdm.write(f"  🔍 Total job URLs collected: {len(job_urls)}")
    tqdm.write(f"  📄 Total pages scraped: {page_pbar.n}")

    page_pbar.close()

    # 4. Job detail collection
    job_postings = []
    for idx, url in tqdm(
        enumerate(job_urls),
        total=len(job_urls),
        desc=f"{company_name}: Fetching job data",
    ):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            job_data = response.json().get("jobPostingInfo")
            if job_data:
                job_postings.append(job_data)
        except Exception as e:
            log_with_prefix(
                "error", company_name, f"Fetch job detail failed ({url}): {e}"
            )

        time.sleep(0.5)

    return job_postings
