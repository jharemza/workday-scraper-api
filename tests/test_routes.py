import requests

def test_jobs_all(base_url):
    res = requests.get(f"{base_url}/jobs/all")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_scrape_route(base_url):
    # Replace this with one of your configured institutions
    company = "M&T Bank"
    res = requests.post(f"{base_url}/jobs/scrape", json={"companies": [company]})
    assert res.status_code == 202

    data = res.json()
    # If jobs were scraped, we expect a list
    if "scraped" in data:
        assert data["scraped"] is None
    else:
        assert isinstance(data, list)
