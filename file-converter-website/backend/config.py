import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------
# PROJECT DIRECTORY
# ---------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------
# LOAD .ENV
# ---------------------------------------

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ---------------------------------------
# FILE SETTINGS
# ---------------------------------------

MAX_FILE_SIZE_MB = int(
    os.getenv(
        "MAX_FILE_SIZE_MB",
        "50"
    )
)

MAX_FILE_SIZE = (
    MAX_FILE_SIZE_MB
    * 1024
    * 1024
)


MAX_FILES_PER_REQUEST = int(
    os.getenv(
        "MAX_FILES_PER_REQUEST",
        "100"
    )
)


# ---------------------------------------
# FRONTEND URL
# ---------------------------------------

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)


# ---------------------------------------
# APPLICATION
# ---------------------------------------

APP_NAME = "File Converter API"

APP_VERSION = "1.0.0"