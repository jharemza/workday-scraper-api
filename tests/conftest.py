import pytest

@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:5000"
