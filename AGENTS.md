# Project Agents.md Guide for OpenAI Codex

This Agents.md file provides comprehensive guidance for OpenAI Codex and other AI agents working with this codebase.

## Overview

This repository powers a scalable Workday job scraping and automation pipeline via a Flask-based API and modular scraper logic. Agents contributing to this codebase should prioritize clean modular design, high test coverage, and consistency with existing patterns.

## ✅ Core Directories and Responsibilities

| Path               | Purpose                                            |
| ------------------ | -------------------------------------------------- |
| `app/`             | API application code (Flask, routes, schemas)      |
| `scraper/`         | Workday scraping logic and source-specific modules |
| `tests/`           | Unit and integration tests                         |
| `config.py`        | Application settings and environment configuration |
| `requirements.txt` | Dependency management                              |

## Contribution Guidelines

### Coding Style

- Python 3.10+ required
- Format all code with Black
- Lint with flake8
- Follow PEP 8 where applicable
- Use descriptive function and variable names
- Group related logic into helper modules
- Avoid unnecessary abstraction unless justified by multi-institution logic

### Testing

- Use `pytest` as the test runner
- Maintain test coverage for all public methods
- Use `requests-mock` or `unittest.mock` to isolate external calls
- Run all tests before submitting changes:

```bash
pytest --cov=.
```

## Migration Context

This project is being upgraded to support multi-institution scraping, where each Workday instance is handled via a configuration-driven pattern. Ongoing refactoring efforts focus on:

- Abstracting institution-specific logic from `scraper.py`
- Implementing `InstitutionConfig` and `JobNormalizer` patterns
- Improving error handling and response payload clarity
- Ensuring all scraped job entries integrate cleanly with the Notion API

Agents should not hard-code logic for a specific employer. Instead, all customizations must be expressed via configuration or modular override classes.

## Validation Checklist

Before finalizing a pull request:

- [ ] Run flake8 with no errors
- [ ] Run black . with no changes
- [ ] Run pytest --cov=. and verify no test failures

## How Agents Should Work

- Operate only inside the scoped project directories (app/, scraper/, tests/)
- Use tests/ for validation and regression protection
- If creating new modules, include a test\_\*.py file with appropriate coverage
- Document any new environment variables in README.md or .env.example
- Format PRs with:
  - A concise title
  - A bulleted list of changes
  - Tags for related issues (e.g. Closes #23)

## Example PR Message

```text
feat: add support for scraping Tesla job board

- Introduced TeslaConfig for source-specific search parameters
- Added JobNormalizer subclass to handle Tesla formatting
- Updated test_scraper.py to include Tesla scraping test case

Closes #42
```
