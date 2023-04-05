from pathlib import Path

ROOT_DIR = Path(__file__).parents[1]
DATA_DIR = Path(__file__).parents[0] / "data"
DOMAINS_DIR = DATA_DIR / "domains"
SCHEMA_DIR = DATA_DIR / "schemas"
STATIC_DIR = DATA_DIR / "static"
FONTS_DIR = STATIC_DIR / "fonts"
