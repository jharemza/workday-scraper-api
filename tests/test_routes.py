import pytest

pytest.importorskip("flask")


def test_jobs_all(client):
    res = client.get("/jobs/all")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_scrape_route(client):
    # Replace this with one of your configured institutions
    company = "M&T Bank"
    res = client.post("/jobs/scrape", json={"companies": [company]})
    assert res.status_code == 202

    data = res.get_json()
    # If jobs were scraped, we expect a list
    if "scraped" in data:
        assert data["scraped"] is None
    else:
        assert isinstance(data, list)
