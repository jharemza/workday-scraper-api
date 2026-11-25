import json

from click.testing import CliRunner

import run


def test_scrape_cli_exits_zero_for_complete_run(monkeypatch):
    expected = {"success": True, "institutions": [{"company": "Test"}]}
    monkeypatch.setattr(run, "run_scrape", lambda _targets: expected)

    result = CliRunner().invoke(run.cli, ["scrape", "--companies", "Test"])

    assert result.exit_code == 0
    assert json.loads(result.output) == expected


def test_scrape_cli_exits_nonzero_for_required_institution_failure(monkeypatch):
    expected = {
        "success": False,
        "institutions": [{"company": "Test", "status": "http_failure"}],
    }
    monkeypatch.setattr(run, "run_scrape", lambda _targets: expected)

    result = CliRunner().invoke(run.cli, ["scrape", "--companies", "Test"])

    assert result.exit_code == 1
    assert json.loads(result.output) == expected
