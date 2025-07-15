import pytest

pytest.importorskip("flask")


def test_jobs_all(client):
    res = client.get("/jobs/all")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_jobs_today(client):
    res = client.get("/jobs/today")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)


def test_jobs_company(client):
    company = "M&T Bank"
    res = client.get(f"/jobs/company/{company}")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    if data:
        assert all(job["company"] == company for job in data)


def test_jobs_company_new(client):
    company = "M&T Bank"
    res = client.get(f"/jobs/company/{company}/new")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    if data:
        assert all(job["company"] == company for job in data)
