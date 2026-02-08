import app.scraper_pkg.institution_runner as runner


def test_salary_with_currency_prefix():
    low, high = runner.extract_salary_range(
        "Salary: USD$132,500.00 - USD$162,000.00"
    )

    assert low == 132500.0
    assert high == 162000.0


def test_salary_with_space_comma_decimal():
    low, high = runner.extract_salary_range("$96 400,00 - $144 600,00")

    assert low == 96400.0
    assert high == 144600.0


def test_salary_with_thousand_commas_only():
    low, high = runner.extract_salary_range("$96,400 - $144,600")

    assert low == 96400.0
    assert high == 144600.0
