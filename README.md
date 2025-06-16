# workday-scraper-api

Flask API service for automated job scraping with database backend :contentReference[oaicite:0]{index=0}

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Clone & Install](#clone--install)
  - [Configuration](#configuration)
  - [Initialize the Database](#initialize-the-database)
- [Usage](#usage)
  - [CLI Commands](#cli-commands)
  - [API Endpoints](#api-endpoints)
- [Directory Structure](#directory-structure)
- [Logging](#logging)
- [Testing](#testing)
- [CI/CD](#cicd)
- [License](#license)

## Features

- Headless scraping of Workday‐powered job postings
- Persist scraped data in a SQLite database
- Expose a RESTful Flask API to query and trigger scrapes
- Configurable via environment variables and `.env`
- Structured logging to console and rotating log files
- Automated changelog and daily ingestion via GitHub Actions

## Architecture

- **Core**: Python 3.12, Flask
- **Scraper**: Vendored Workday-scraper logic under `app/scraper_pkg`
- **Storage**: SQLite (`jobs.db`)
- **CLI**: `run.py` powered by Click—supports `scrape` & `serve` commands
- **API**: Blueprint `jobs_bp` exposes `/jobs/...` routes
- **Config**: `python-dotenv` + `app/config.py` environment-driven

## Getting Started

### Prerequisites

- Python 3.12
- Git
- (Optional) Conda or virtualenv

### Clone & Install

```bash
git clone https://github.com/jharemza/workday-scraper-api.git
cd workday-scraper-api

# Using virtualenv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root to override defaults (see `app/config.py`):

```dotenv
# Path to SQLite DB
JOBS_DB_PATH=./jobs.db

# Scrape settings
SCRAPE_LIMIT=20

# API server settings
API_HOST=127.0.0.1
API_PORT=5000

# Logging
LOG_LEVEL=INFO
```

### Initialize the Database

On first run the table is auto-created. To reset or customize:

```bash
sqlite3 jobs.db << 'EOF'
DROP TABLE IF EXISTS job_postings;
# paste the CREATE TABLE DDL from app/db.py here
EOF
```

## Usage

### CLI Commands

- Scrape all companies

```bash
python run.py scrape
```

- Scrape specific companies

```bash
python run.py scrape -c "M&T Bank" -c "Acme Corp"
```

- Start the API server

```bash
python run.py serve
```

### API Endpoints

> All responses are JSON.

| Method | Path                          | Description                                           |
| ------ | ----------------------------- | ----------------------------------------------------- |
| GET    | `/jobs/all`                   | List all current job postings                         |
| GET    | `/jobs/today`                 | Jobs scraped on the current date                      |
| GET    | `/jobs/company/{company}`     | All current jobs for a given company                  |
| GET    | `/jobs/company/{company}/new` | Jobs added today for a given company                  |
| POST   | `/jobs/scrape`                | Trigger a fresh scrape (body: `{"companies": [...]}`) |

## Directory Structure

```bash
.
├── .github/
│   └── workflows/     # CI/CD (release & daily ingest)
├── app/
│   ├── main.py        # Flask app & logging setup
│   ├── routes.py      # API endpoints
│   ├── db.py          # SQLite schema & CRUD
│   ├── config.py      # env-driven settings
│   ├── scraper.py     # orchestrates vendored scraper + DB upserts
│   └── scraper_pkg/   # vendored workday_scraper modules
├── docs/
│   └── openapi.yaml   # (optional) OpenAPI spec
├── logs/
│   └── app.log        # auto-rotated logs
├── tests/             # pytest suite
├── .env               # environment overrides (gitignored)
├── jobs.db            # SQLite DB (auto-generated)
├── README.md
├── requirements.txt
└── run.py             # CLI commands (scrape & serve)
```

## Logging

- Console: Verbose, timestamped output
- File: `logs/app.log` (rotates at 10 MB, keeps 5 backups)
- Level: Controlled by `LOG_LEVEL` (DEBUG, INFO, etc.)

## Testing

```bash
pytest --cov=app tests/
```

## CI/CD

- `.github/workflows/release.yml`: Auto-update `CHANGELOG.md` on tags/schedule
- `.github/workflows/ingest.yml`: Daily or manual scrape & optional DB commit

## License

This project is licensed under the [MIT License](LICENSE).

```makefile
::contentReference[oaicite:1]{index=1}
```
