from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "WaterReminder"


def get_app_dir() -> Path:
    if sys.platform.startswith("win"):
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base_dir = Path.home() / ".local" / "share"

    app_dir = base_dir / APP_NAME
    _ = app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_dir() -> Path:
    return get_app_dir()


def get_db_path() -> Path:
    return get_app_dir() / "water.db"


def get_log_path() -> Path:
    return get_app_dir() / "water.log"


def get_resource_path(relative: str) -> Path:
    base_path: Path
    if hasattr(sys, "_MEIPASS"):
        meipass = getattr(sys, "_MEIPASS", None)
        if isinstance(meipass, str):
            base_path = Path(meipass)
        else:
            base_path = Path(__file__).resolve().parents[2]
    else:
        base_path = Path(__file__).resolve().parents[2]

    return base_path / relative
