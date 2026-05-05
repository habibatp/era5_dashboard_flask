import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

    EE_PROJECT_ID = os.getenv("EE_PROJECT_ID", "potent-airfoil-493212-f0")
    EE_SERVICE_ACCOUNT = os.getenv("EE_SERVICE_ACCOUNT", "")
    EE_PRIVATE_KEY_FILE = os.getenv("EE_PRIVATE_KEY_FILE", "")

    CACHE_DIR = BASE_DIR / "data" / "cache"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))