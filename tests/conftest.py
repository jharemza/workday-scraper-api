import sys
import types
import pytest

# Provide a dummy `dotenv` module so imports succeed when the dependency is
# unavailable in the test environment.
sys.modules.setdefault(
    "dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None)
)

try:
    from app.main import create_app
except ModuleNotFoundError:  # Flask (and thus app.main) not installed
    create_app = None


@pytest.fixture(scope="session")
def client():
    """Flask test client for API routes."""
    if create_app is None:
        pytest.skip("Flask not available", allow_module_level=True)

    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client
