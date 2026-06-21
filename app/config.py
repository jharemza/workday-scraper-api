# app/config.py

import os
from dotenv import load_dotenv


# Load overrides from the project-root .env file, if present.
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Core storage configuration.
JOBS_DB_PATH = os.getenv("JOBS_DB_PATH", os.path.join(BASE_DIR, "jobs.db"))
SQLITE_TIMEOUT = float(os.getenv("SQLITE_TIMEOUT", "10"))

# Logging configuration.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", os.path.join(BASE_DIR, "logs", "app.log"))
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# Scraper behavior.
SCRAPE_LIMIT = int(os.getenv("SCRAPE_LIMIT", "20"))
FACET_LIMIT = int(os.getenv("FACET_LIMIT", "1"))
INSTITUTIONS_CONFIG_PATH = os.getenv(
    "INSTITUTIONS_CONFIG_PATH",
    os.path.join(BASE_DIR, "app", "scraper_pkg", "config", "institutions.yaml"),
)
SCRAPER_USER_AGENT = os.getenv("SCRAPER_USER_AGENT", "Mozilla/5.0")
SCRAPER_LISTING_DELAY_SECONDS = float(os.getenv("SCRAPER_LISTING_DELAY_SECONDS", "0.1"))
SCRAPER_DETAIL_DELAY_SECONDS = float(os.getenv("SCRAPER_DETAIL_DELAY_SECONDS", "0.5"))

# API server settings.
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "5000"))
APP_DEBUG = _get_bool("APP_DEBUG", True)
