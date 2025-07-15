import pytest
try:
    import flask  # noqa: F401
except Exception:
    pytest.skip("flask not installed", allow_module_level=True)
from app.main import create_app


@pytest.fixture(scope="session")
def client():
    """Flask test client for API routes."""
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client
