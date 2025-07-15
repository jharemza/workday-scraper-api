import os
import shutil
import sys
import types
import pytest


# Provide a dummy `dotenv` module so imports succeed when the dependency is
# unavailable in the test environment.
if "dotenv" not in sys.modules:
    dotenv = types.ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):
        return None

    dotenv.load_dotenv = load_dotenv
    sys.modules["dotenv"] = dotenv

try:
    import flask  # noqa: F401
except Exception:
    pytest.skip("flask not installed", allow_module_level=True)

try:
    from app.main import create_app
except ModuleNotFoundError:  # Flask (and thus app.main) not installed
    create_app = None


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    """Flask test client bound to a temporary database."""
    if create_app is None:
        pytest.skip("Flask not available", allow_module_level=True)

    # Copy the example jobs.db to a temp location so tests remain read-only
    db_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jobs.db")
    db_dir = tmp_path_factory.mktemp("db")
    db_path = db_dir / "jobs.db"
    shutil.copyfile(db_src, db_path)

    # Ensure the application points at the temp DB
    os.environ["JOBS_DB_PATH"] = str(db_path)

    app = create_app()
    app.testing = True
    with app.test_client() as test_client:
        yield test_client
