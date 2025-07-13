import sys
import types
import pytest
from app.routes import row_to_dict
from app.scraper_pkg.institution_runner import extract_salary_range, find_id_by_descriptor

# Provide a minimal Flask stub so `app.routes` can be imported without the real
# dependency present in the execution environment.
class DummyBlueprint:
    def __init__(self, *args, **kwargs):
        pass

    def route(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator


flask_stub = types.SimpleNamespace(
    Blueprint=DummyBlueprint,
    jsonify=lambda *a, **k: {},
    request=types.SimpleNamespace(get_json=lambda *a, **k: {}),
    current_app=types.SimpleNamespace(logger=types.SimpleNamespace(error=lambda *a, **k: None)),
)
sys.modules.setdefault("flask", flask_stub)
sys.modules.setdefault("yaml", types.SimpleNamespace(safe_load=lambda *a, **k: {}))
sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=lambda *a, **k: None))
sys.modules.setdefault("requests", types.SimpleNamespace())


class DummyRow:
    """Simple row-like object for testing row_to_dict."""

    def __init__(self, data):
        self._data = data

    def keys(self):
        return self._data.keys()

    def __getitem__(self, key):
        return self._data[key]


def test_row_to_dict_simple():
    row = DummyRow({"a": 1, "b": "two"})
    assert row_to_dict(row) == {"a": 1, "b": "two"}


def test_extract_salary_range_valid():
    desc = "Competitive pay of $50,000.00 - $70,000.00 per year"
    low, high = extract_salary_range(desc)
    assert low == pytest.approx(50000.0)
    assert high == pytest.approx(70000.0)


def test_extract_salary_range_invalid_numbers():
    desc = "Salary range is $abc - $123"
    low, high = extract_salary_range(desc)
    assert low is None and high is None


def test_extract_salary_range_missing_pattern():
    desc = "No salary info available"
    low, high = extract_salary_range(desc)
    assert low is None and high is None


def test_find_id_by_descriptor_nested():
    facets = [
        {
            "facetParameter": "locations",
            "values": [
                {"descriptor": "New York", "id": "ny"},
                {
                    "facetParameter": "sub",
                    "values": [
                        {"descriptor": "Remote", "id": "remote"}
                    ],
                },
            ],
        }
    ]

    param, fid = find_id_by_descriptor(facets, "Remote")
    assert param == "sub" and fid == "remote"

    param, fid = find_id_by_descriptor(facets, "New York")
    assert param == "locations" and fid == "ny"

    param, fid = find_id_by_descriptor(facets, "Missing")
    assert param is None and fid is None
