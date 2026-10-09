from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "agentforge.db"


def get_setting(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


class Settings:
    APP_NAME = "AgentForge AI"
    APP_VERSION = "0.1.0"
    DATABASE_URL = get_setting("DATABASE_URL", f"sqlite:///{DB_PATH}")
    API_PREFIX = "/api/v1"
    REQUEST_TIMEOUT_SECONDS = 15
    DEFAULT_TOOL_LIMIT = 10
    DEFAULT_TASK_LIMIT = 5
    ALLOWED_UPLOAD_TYPES = {"text/plain", "text/markdown", "application/octet-stream"}
    MAX_UPLOAD_BYTES = 2 * 1024 * 1024
    BASE_STORAGE_DIR = BASE_DIR / "data"
    BASE_STORAGE_DIR.mkdir(exist_ok=True, parents=True)


settings = Settings()
