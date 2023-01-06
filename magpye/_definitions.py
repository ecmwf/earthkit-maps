from pathlib import Path

ROOT_DIR = Path(__file__).parents[1]
SCHEMA_DIR = ROOT_DIR / "schemas"
STATIC_DIR = ROOT_DIR / "static"

DATA_DIR = Path(__file__).parents[0] / "data"
DOMAINS_DIR = DATA_DIR / "domains"
