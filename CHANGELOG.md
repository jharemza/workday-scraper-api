# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.1.5](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.5) - 2025-06-30

<small>[Compare with v0.1.4](https://github.com/jharemza/workday-scraper-api/compare/v0.1.4...v0.1.5)</small>

## [v0.1.4](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.4) - 2025-06-30

<small>[Compare with v0.1.3](https://github.com/jharemza/workday-scraper-api/compare/v0.1.3...v0.1.4)</small>

### Chore

- remove test file used for changelog trigger ([4f3e4a1](https://github.com/jharemza/workday-scraper-api/commit/4f3e4a16ab44cb4d0919dbdef0b2b073e688251b) by Jeremiah Haremza).

## [v0.1.3](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.3) - 2025-06-30

<small>[Compare with v0.1.2](https://github.com/jharemza/workday-scraper-api/compare/v0.1.2...v0.1.3)</small>

## [v0.1.2](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.2) - 2025-06-30

<small>[Compare with v0.1.1](https://github.com/jharemza/workday-scraper-api/compare/v0.1.1...v0.1.2)</small>

### Docs

- add test file to trigger changelog ([787915b](https://github.com/jharemza/workday-scraper-api/commit/787915b7722bee3ba10702f2bf64351679fce883) by Jeremiah Haremza).

## [v0.1.1](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.1) - 2025-06-22

<small>[Compare with v0.1.0](https://github.com/jharemza/workday-scraper-api/compare/v0.1.0...v0.1.1)</small>

### Docs

- bump changelog for refs/tags/v0.1.0 ([01a9087](https://github.com/jharemza/workday-scraper-api/commit/01a9087b26a5bca5d408163ea9799ba280b25d2b) by github-actions[bot]).

## [v0.1.0](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.0) - 2025-06-20

<small>[Compare with first commit](https://github.com/jharemza/workday-scraper-api/compare/dc1a0d54acba91d0bcdda172da9b34ab9b21f9a2...v0.1.0)</small>

### Features

- add global and per-route JSON error handlers ([4b3abfd](https://github.com/jharemza/workday-scraper-api/commit/4b3abfd4b1842c37fed7c9206b5d381fff61b20d) by Jeremiah Haremza).
- add structured logging with console & rotating file handlers ([d6a0934](https://github.com/jharemza/workday-scraper-api/commit/d6a09340c94ffc7925706c3691d439424c400264) by Jeremiah Haremza).
- added count by category to terminal output. ([a1c1425](https://github.com/jharemza/workday-scraper-api/commit/a1c14253e02f4f28f5039a14541167480da370ac) by Jeremiah Haremza).
- perform initial full scrape and populate job_postings table ([273348d](https://github.com/jharemza/workday-scraper-api/commit/273348d2e6a12e314b7dd5d0dab82b4143982097) by Jeremiah Haremza).

### Bug Fixes

- push CHANGELOG.md to main from detached HEAD ([b3bc89e](https://github.com/jharemza/workday-scraper-api/commit/b3bc89e00f43ba97f637a3b9b32d0edba3856d9f) by Jeremiah Haremza).
- set correct changelog output path for release ([a3733b9](https://github.com/jharemza/workday-scraper-api/commit/a3733b9bad9e69a7fb4b44d437c6d1eb8daa5d87) by Jeremiah Haremza).

### Chore

- finalize README and pyproject.toml in prep for v0.1.0 release ([af68af1](https://github.com/jharemza/workday-scraper-api/commit/af68af13baeb0e20b7052223da421558ecec787a) by Jeremiah Haremza).
- remove unused PostgreSQL config (sticking with SQLite for now) ([e457889](https://github.com/jharemza/workday-scraper-api/commit/e457889a7be7248a85f0a21596966fd0b71b0bf2) by Jeremiah Haremza).
- stop tracking logs/app.log and ignore log files ([75ac9f6](https://github.com/jharemza/workday-scraper-api/commit/75ac9f6d8db56a8bd07250a6b996f8e97bbe85a8) by Jeremiah Haremza).
- load DB path, pagination limits, and server settings from .env ([1c3d25a](https://github.com/jharemza/workday-scraper-api/commit/1c3d25ac5b07d90cf32bf78e837357df349c1202) by Jeremiah Haremza).
- removed print debugging statements. ([c8b5548](https://github.com/jharemza/workday-scraper-api/commit/c8b5548e1178974e4cd770f3ba3ae11c3c9ddc0d) by Jeremiah Haremza).
- vendor in scraper files and created functions for db.py ([ba7d663](https://github.com/jharemza/workday-scraper-api/commit/ba7d663f9443e55c0f1fb3e59070c64a99915520) by Jeremiah Haremza).
- add release workflow for automated CHANGELOG updates ([83579c5](https://github.com/jharemza/workday-scraper-api/commit/83579c59e9468f93d3e20d9e32c29a66c41fc0eb) by Jeremiah Haremza).
- configure git-changelog via pyproject.toml ([042ed18](https://github.com/jharemza/workday-scraper-api/commit/042ed186fe04d8f4c19bc301d00c5c0e88f6e02b) by Jeremiah Haremza).
- scaffold basic folder structure ([90a3015](https://github.com/jharemza/workday-scraper-api/commit/90a3015ebda234376d2d792a8142310ef2170bc6) by Jeremiah Haremza).

### Docs

- bump changelog for refs/tags/v0.1.0 ([061dede](https://github.com/jharemza/workday-scraper-api/commit/061dedea7afa5a9b2fd5961d7e7d1db33ec42a52) by github-actions[bot]).
- added Swagg UI documentation llink to README.md ([2d0f89e](https://github.com/jharemza/workday-scraper-api/commit/2d0f89e4b89054dbcdc92d2426190449355850cc) by Jeremiah Haremza).
- add Swagger UI deployment for OpenAPI docs via GitHub Pages ([3c77b17](https://github.com/jharemza/workday-scraper-api/commit/3c77b17e34535ba98b0e50e84ba6a8c5c253b662) by Jeremiah Haremza).
- add curl usage examples for all API endpoints in README ([760f3f6](https://github.com/jharemza/workday-scraper-api/commit/760f3f63fd0d203a4e033b640a863bcf08fef984) by Jeremiah Haremza).
- complete documentation of all endpoints in OpenAPI and Postman ([97dc8d9](https://github.com/jharemza/workday-scraper-api/commit/97dc8d958dfa222345b845ace54f9ba78e1e749c) by Jeremiah Haremza).
- add CI and Codecov badges for build status and test coverage ([d115a45](https://github.com/jharemza/workday-scraper-api/commit/d115a451995df969fe47fae8bc4fef7fa6075cb1) by Jeremiah Haremza).
- add example curl and Postman requests for API usage ([2d29253](https://github.com/jharemza/workday-scraper-api/commit/2d29253e9a9ff05e4162d83b71d1e647928fe6bf) by Jeremiah Haremza).
- add comprehensive README with project overview, setup, and usage instructions ([a576ae2](https://github.com/jharemza/workday-scraper-api/commit/a576ae223415e3bdf3dbadedcc77ce04a637caf0) by Jeremiah Haremza).

### Style

- configure flake8 and apply black formatting ([3e67594](https://github.com/jharemza/workday-scraper-api/commit/3e6759462630de62ebb57ecf7262a85cd7aa6c76) by Jeremiah Haremza).

### Tests

- add pytest config and initial test for /jobs/scrape route ([9da3637](https://github.com/jharemza/workday-scraper-api/commit/9da3637711b6fd35970fd81ae62a52c312acca0c) by Jeremiah Haremza).
