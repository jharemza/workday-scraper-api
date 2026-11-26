import yaml

from app import config


def load_institutions_config(path: str | None = None):
    config_path = path or config.INSTITUTIONS_CONFIG_PATH
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["institutions"]
