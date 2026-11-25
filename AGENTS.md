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
- Add or update regression tests for every changed behavior, including changes
  to return types, control flow, or downstream side effects.
- For HTTP, network, JSON, parsing, validation, and other defensive paths,
  test both the failure outcome and the fail-closed behavior at the caller.
  Do not treat an error response as an authoritative empty result.
- Run all tests before submitting changes:

```bash
pytest --cov=app --cov-report=xml
```

- For changed modules with defensive branches, also run focused coverage with
  missing-line output and add tests for uncovered changed lines:

```bash
pytest -q tests/<relevant_test_file>.py --cov=<changed_module> --cov-report=term-missing
```

- Do not lower Codecov thresholds, exclude changed code from coverage, or
  disable coverage reporting merely to satisfy a check. Treat a failing
  `codecov/patch` result as missing regression coverage unless an actual
  configuration defect has been separately approved for correction.

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
- [ ] Run `black --check app tests` with no formatting changes required
- [ ] Run `pytest --cov=app --cov-report=xml` and verify no test failures
- [ ] Run focused missing-line coverage for changed defensive code and cover
      the changed error-handling branches
- [ ] Run `git diff --check` with no whitespace errors
- [ ] Push the feature branch and verify every required GitHub Actions check
      and `codecov/patch` check passes before declaring Git delivery complete
- [ ] If checks are pending or failing, report that state and keep the PR open;
      do not claim delivery is complete until the required checks are green

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
