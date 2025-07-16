# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.1.15](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.15) - 2025-07-16

<small>[Compare with v0.1.14](https://github.com/jharemza/workday-scraper-api/compare/v0.1.14...v0.1.15)</small>

### Tests

- add unit test for job fetch error handling in institution scraper (#17) ([639aefe](https://github.com/jharemza/workday-scraper-api/commit/639aefe3e0099646e5a95cf66a6b8b9ab46f1c4c) by jharemza).
- handle job fetch errors ([c5f7e1f](https://github.com/jharemza/workday-scraper-api/commit/c5f7e1f152172dbc7c2bd5abaf208d35571adf2a) by jharemza).

## [v0.1.14](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.14) - 2025-07-16

<small>[Compare with v0.1.13](https://github.com/jharemza/workday-scraper-api/compare/v0.1.13...v0.1.14)</small>

### Tests

- verify unmatched location handling ([f8ed159](https://github.com/jharemza/workday-scraper-api/commit/f8ed159ccaf86d3a967be76745ac0480f586aca8) by jharemza).

## [v0.1.13](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.13) - 2025-07-16

<small>[Compare with v0.1.12](https://github.com/jharemza/workday-scraper-api/compare/v0.1.12...v0.1.13)</small>

### Tests

- ensure run_institution_scraper returns empty list on facet fetch error (#15) ([dae69d6](https://github.com/jharemza/workday-scraper-api/commit/dae69d6f2050e53fcd6fc64e28a3b1b5560fcdb6) by jharemza).
- cover facets failure path ([076ecd2](https://github.com/jharemza/workday-scraper-api/commit/076ecd2d162cb64d542c5f0cecf0d8bc8ba16fbf) by jharemza).

## [v0.1.12](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.12) - 2025-07-16

<small>[Compare with v0.1.11](https://github.com/jharemza/workday-scraper-api/compare/v0.1.11...v0.1.12)</small>

### Tests

- exercise error cases in routes (#14) ([9cec51a](https://github.com/jharemza/workday-scraper-api/commit/9cec51aad22e2f1d4f74110edf3331519eaedd02) by jharemza).
- cover error paths in routes ([1e87bc3](https://github.com/jharemza/workday-scraper-api/commit/1e87bc3289084f5b605fafb5b608deca53c0c96f) by jharemza).

## [v0.1.11](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.11) - 2025-07-15

<small>[Compare with v0.1.10](https://github.com/jharemza/workday-scraper-api/compare/v0.1.10...v0.1.11)</small>

### Tests

- add trigger_scrape test and reformat CLI script with black (#13) ([c491975](https://github.com/jharemza/workday-scraper-api/commit/c491975e9d3be04a51b4b396db8a1a4117e687c4) by jharemza).
- add trigger_scrape endpoint test ([978f827](https://github.com/jharemza/workday-scraper-api/commit/978f82745a98b09a53589aa48544491400ff7caa) by jharemza).

## [v0.1.10](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.10) - 2025-07-15

<small>[Compare with v0.1.9](https://github.com/jharemza/workday-scraper-api/compare/v0.1.9...v0.1.10)</small>

### Bug Fixes

- scrape when DB table missing (#12) ([7120500](https://github.com/jharemza/workday-scraper-api/commit/7120500f1800f916fd306b00e97e3f23ec964427) by jharemza).
- trigger scrape when jobs table missing ([7a0c22b](https://github.com/jharemza/workday-scraper-api/commit/7a0c22bb18c5fcdef959b1ffef4e4730992dbd9e) by jharemza).

## [v0.1.9](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.9) - 2025-07-15

<small>[Compare with v0.1.8](https://github.com/jharemza/workday-scraper-api/compare/v0.1.8...v0.1.9)</small>

### Bug Fixes

- resolve tests merge conflicts ([12b9088](https://github.com/jharemza/workday-scraper-api/commit/12b90884427691e029f33ebb5ea67ab0c7025841) by jharemza).

### Style

- run isort on route tests ([b9393f7](https://github.com/jharemza/workday-scraper-api/commit/b9393f7a2a29aac470daf7b061ddeaa917080640) by jharemza).

### Tests

- fix test_scrape_route to initialize test database ([4310550](https://github.com/jharemza/workday-scraper-api/commit/43105507d910af6f8e63f1d7cf5093b1e1cb58f5) by Jeremiah Haremza).

## [v0.1.8](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.8) - 2025-07-15

<small>[Compare with v0.1.7](https://github.com/jharemza/workday-scraper-api/compare/v0.1.7...v0.1.8)</small>

### Tests

- add API route tests for job endpoints (#10) ([de09873](https://github.com/jharemza/workday-scraper-api/commit/de09873d2521e642a070f663afb076c461d47c7f) by jharemza).
- drop scrape endpoint to avoid network ([8ee0b69](https://github.com/jharemza/workday-scraper-api/commit/8ee0b69976f29ee7a875f4421b73378274c58a1b) by jharemza).

## [v0.1.7](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.7) - 2025-07-13

<small>[Compare with v0.1.6](https://github.com/jharemza/workday-scraper-api/compare/v0.1.6...v0.1.7)</small>

### Docs

- add AGENTS.md with guidelines for Codex agent contributions ([533bd00](https://github.com/jharemza/workday-scraper-api/commit/533bd00de32ac0ae7b274d6992dc694aaddbae05) by Jeremiah Haremza).

## [v0.1.6](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.6) - 2025-07-13

<small>[Compare with v0.1.5](https://github.com/jharemza/workday-scraper-api/compare/v0.1.5...v0.1.6)</small>

### Chore

- deduplicate and clean up requirements.txt ([4c931eb](https://github.com/jharemza/workday-scraper-api/commit/4c931eb142e601525f2af76af969230fe8560f50) by Jeremiah Haremza).

## [v0.1.5](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.5) - 2025-07-13

<small>[Compare with v0.1.4](https://github.com/jharemza/workday-scraper-api/compare/v0.1.4...v0.1.5)</small>

### Style

- reformat tests/test_utils.py using black ([e71a068](https://github.com/jharemza/workday-scraper-api/commit/e71a068c92f3810ca7aa703163ec3bf3975dbc30) by Jeremiah Haremza).
- add double line spacing to satisfy flake8 ([7cdc35a](https://github.com/jharemza/workday-scraper-api/commit/7cdc35a98f9fca9096e02d05242c8bdb51e59842) by jharemza).

### Tests

- add utils tests and stub Flask dependencies for isolated execution ([dcd9cd7](https://github.com/jharemza/workday-scraper-api/commit/dcd9cd78d1fd54dd8a78f605f38d411dff0966ac) by jharemza).
- add utils unit tests ([f225300](https://github.com/jharemza/workday-scraper-api/commit/f22530047ff34f88eafc7b0819617e96d27ddab7) by jharemza).

## [v0.1.4](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.4) - 2025-07-13

<small>[Compare with v0.1.3](https://github.com/jharemza/workday-scraper-api/compare/v0.1.3...v0.1.4)</small>

### Style

- add double line spacing to satisfy flake8 ([f1f4e14](https://github.com/jharemza/workday-scraper-api/commit/f1f4e14c727e79ba6c7a6c3e0147b9ede9a8c530) by jharemza).

### Tests

- add CRUD tests for job posting database operations (#8) ([30e6488](https://github.com/jharemza/workday-scraper-api/commit/30e6488ec9df77d39c085b6df696eb856ece9702) by jharemza).
- add db crud tests with temp sqlite ([e874a8c](https://github.com/jharemza/workday-scraper-api/commit/e874a8c72fa014aa8a8d6a48eb612dab67371f6f) by jharemza).

## [v0.1.3](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.3) - 2025-07-13

<small>[Compare with v0.1.2](https://github.com/jharemza/workday-scraper-api/compare/v0.1.2...v0.1.3)</small>

### Chore

- remove unused scraper_pkg/scraper.py script (#7) ([39f2adb](https://github.com/jharemza/workday-scraper-api/commit/39f2adb6537633872d4525d7439cc705c738d0bb) by jharemza).
- remove unused scraper script ([6dc5910](https://github.com/jharemza/workday-scraper-api/commit/6dc591093e5341ea8e9c196bc31a829e7a462e06) by jharemza).

## [v0.1.2](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.2) - 2025-07-13

<small>[Compare with v0.1.1](https://github.com/jharemza/workday-scraper-api/compare/v0.1.1...v0.1.2)</small>

### Tests

- fix Codecov 0% coverage issue for app/ folder (#6) ([2874d1f](https://github.com/jharemza/workday-scraper-api/commit/2874d1f3c19ab11a1a9ed7559e5eb7cdccf9480a) by jharemza). Related issues/PRs: [#4](https://github.com/jharemza/workday-scraper-api/issues/4)
- run flask app via test client ([d3cf539](https://github.com/jharemza/workday-scraper-api/commit/d3cf53948a96134bfb5f3fa3bc525d27ca7e7c6f) by jharemza).

## [v0.1.1](https://github.com/jharemza/workday-scraper-api/releases/tag/v0.1.1) - 2025-07-01

<small>[Compare with v0.1.0](https://github.com/jharemza/workday-scraper-api/compare/v0.1.0...v0.1.1)</small>

### Chore

- remove test file used for changelog trigger ([4f3e4a1](https://github.com/jharemza/workday-scraper-api/commit/4f3e4a16ab44cb4d0919dbdef0b2b073e688251b) by Jeremiah Haremza).

### Docs

- bump changelog ([6c059cc](https://github.com/jharemza/workday-scraper-api/commit/6c059cc4b481b27999ecfa652c031288e70bf1b1) by github-actions[bot]).
- add test file to trigger changelog ([787915b](https://github.com/jharemza/workday-scraper-api/commit/787915b7722bee3ba10702f2bf64351679fce883) by Jeremiah Haremza).
- bump changelog for refs/heads/main ([8c281ea](https://github.com/jharemza/workday-scraper-api/commit/8c281ea838cdd3ee3a3e0abce5f4dd0fd5e9cfb4) by github-actions[bot]).
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
