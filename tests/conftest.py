import os
import shutil
import sys
import types
from pathlib import Path

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

    project_root = Path(__file__).resolve().parents[1]
    db_src = project_root / "jobs.db"
    db_dir = tmp_path_factory.mktemp("db")
    db_path = Path(db_dir) / "jobs.db"

    # Ensure the environment advertises the temporary database before importing
    # application modules so defaults derived from JOBS_DB_PATH use the temp file.
    os.environ["JOBS_DB_PATH"] = str(db_path)

    from app import config as app_config
    from app import db as app_db

    if db_src.exists():
        shutil.copyfile(db_src, db_path)
    else:
        # Initialise a new empty database with the required schema.
        app_db.JOBS_DB_PATH = str(db_path)
        app_db.init_db()

    # Keep the imported modules aligned with the temporary database location.
    app_config.JOBS_DB_PATH = str(db_path)
    app_db.JOBS_DB_PATH = str(db_path)

    app = create_app()
    app.testing = True
    with app.test_client() as test_client:
        yield test_client
