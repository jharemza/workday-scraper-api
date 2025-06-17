# app/config.py

import os
from dotenv import load_dotenv

# 1. Load from .env in project root (if present)
load_dotenv()

# 2. Base directory for defaults
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 3. Configuration values with sensible defaults
JOBS_DB_PATH = os.getenv("JOBS_DB_PATH", os.path.join(BASE_DIR, "jobs.db"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

SCRAPE_LIMIT = int(os.getenv("SCRAPE_LIMIT", "20"))

FACET_LIMIT = int(os.getenv("FACET_LIMIT", "1"))

# 4. API server settings (used by your CLI serve command)
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "5000"))
