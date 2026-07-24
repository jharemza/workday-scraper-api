# workday-scraper-api

![CI](https://github.com/jharemza/workday-scraper-api/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/jharemza/workday-scraper-api/graph/badge.svg?token=2LVILJXLMF)](https://codecov.io/gh/jharemza/workday-scraper-api)

Flask API service for automated job scraping with database backend

## 📖 API Documentation

The OpenAPI Swagger UI for this API is available at:

👉 [View the API Docs](https://jharemza.github.io/workday-scraper-api/)

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
- [Example Requests](#example-requests)
  - [Using Curl](#using-curl)
  - [Using Postman](#using-postman)

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
- **Storage**: SQLite via `JOBS_DB_PATH`
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

Configuration defaults live in `app/config.py`. For local development or deployment-specific overrides, copy `.env.example` to a project-root `.env` file and adjust the values there. The application loads `.env` via `python-dotenv`, while `.env` itself remains gitignored.

`JOBS_DB_PATH` is the environment variable that controls which SQLite database file the scraper/API uses at runtime.

```bash
cp .env.example .env
```

Example override:

```dotenv
# Path to the SQLite database file used at runtime
JOBS_DB_PATH=./jobs.db

# Scrape settings
SCRAPE_LIMIT=20
FACET_LIMIT=1

# API server settings
API_HOST=127.0.0.1
API_PORT=5000

# Logging
LOG_LEVEL=INFO
```

See `.env.example` for the full list of supported environment variables and public-safe sample values.

### Initialize the Database

On first run the table is auto-created at the path configured by `JOBS_DB_PATH`. To reset or customize the schema against your configured database path:

```bash
sqlite3 "$JOBS_DB_PATH" << 'EOF'
DROP TABLE IF EXISTS job_postings;
# paste the CREATE TABLE DDL from app/db.py here
EOF
```
`JOBS_DB_PATH` should be exported in your shell or loaded from your project-root `.env` before running the command.

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
├── .env.example       # public-safe environment template
├── .env               # local environment overrides (gitignored)
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
pytest --cov=app --cov-report=xml tests/
```

## CI/CD

- `.github/workflows/release.yml`: Build releases from pushed `vMAJOR.MINOR.PATCH` tags.
- `.github/workflows/ingest.yml`: Daily or manual scrape & optional DB commit

## Release Versioning

Git tags are the authoritative version source for releases. Project metadata exposes the
application version dynamically from `app.__version__` for packaging compatibility, but
it does not drive release numbering.

To cut a release:

1. Create and push a semantic version tag, for example `v0.6.0`.
2. The release workflow generates or reuses the matching `CHANGELOG.md` section.
3. The workflow publishes a GitHub Release with the same tag.

If `CHANGELOG.md` gets ahead of tags or a release job needs to be retried, first ensure
the intended tag exists on GitHub, then run the release workflow manually with that tag
(e.g., `v0.6.0`). The workflow reuses an existing changelog section for that tag instead
of inventing a new version, which keeps changelog entries, Git tags, and GitHub releases
aligned.

## License

This project is licensed under the [MIT License](LICENSE).

## Example Requests

You can interact with the API directly via `curl` or import these into Postman.

---

### Using `curl`

> Replace `{{API_HOST}}` and `{{API_PORT}}` with your configured values (defaults: `127.0.0.1:5000`).

1. **List all jobs**

```bash
curl -X GET http://{{API_HOST}}:{{API_PORT}}/jobs/all
```

2. **Jobs scraped today**

```bash
curl -X GET http://{{API_HOST}}:{{API_PORT}}/jobs/today
```

3. **All current jobs for a company**

```bash
curl -X GET http://{{API_HOST}}:{{API_PORT}}/jobs/company/"M&T%20Bank"
```

4. **New jobs for a company (added today)**

```bash
curl -X GET http://{{API_HOST}}:{{API_PORT}}/jobs/company/"M&T%20Bank"/new
```

5. **Trigger a scrape for one or more companies**

```bash
curl -X POST http://{{API_HOST}}:{{API_PORT}}/jobs/scrape \
  -H "Content-Type: application/json" \
  -d '{"companies": ["M&T Bank", "Acme Corp"]}'
```

---

### Using Postman

1. Create a new Collection called “Workday Scraper API”.
2. Add a Request for each endpoint:

   - Method: GET or POST
   - URL: `http://127.0.0.1:5000/jobs/all` (or other endpoints)
   - Headers: for POST, set `Content-Type: application/json`
   - Body (raw JSON) for `/jobs/scrape`:

     ```json
     {
       "companies": ["M&T Bank", "Acme Corp"]
     }
     ```

3. Save and Send—you’ll see the JSON response in Postman’s response pane.
