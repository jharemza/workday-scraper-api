import yaml


def load_institutions_config(path: str = "app/scraper_pkg/config/institutions.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["institutions"]
