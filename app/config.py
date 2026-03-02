from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

from .core.paths import get_config_dir


@dataclass
class AppConfig:
    daily_goal_ml: int = 2000
    reminder_interval_min: int = 60
    theme: str = "light"  # "light", "dark", or "auto"
    sound_enabled: bool = True
    autostart_enabled: bool = False
    reminder_sound: str = "default.wav"
    shake_reminder_enabled: bool = False
    window_geometry: dict[str, int] | None = None

    @classmethod
    def get_config_path(cls) -> Path:
        return get_config_dir() / "config.json"

    @classmethod
    def load(cls) -> "AppConfig":
        path = cls.get_config_path()
        if not path.exists():
            return cls()

        try:
            raw_obj = cast(object, json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            return cls()

        if not isinstance(raw_obj, dict):
            return cls()

        raw_dict = cast(dict[object, object], raw_obj)
        raw: dict[str, object] = {}
        for key, value in raw_dict.items():
            if isinstance(key, str):
                raw[key] = value

        theme_raw = raw.get("theme")
        theme_value = theme_raw if isinstance(theme_raw, str) and theme_raw in {"light", "dark", "auto"} else "light"

        reminder_sound_raw = raw.get("reminder_sound")
        reminder_sound_value = reminder_sound_raw if isinstance(reminder_sound_raw, str) else "default.wav"

        return cls(
            daily_goal_ml=_to_int(raw.get("daily_goal_ml"), 2000),
            reminder_interval_min=_to_int(raw.get("reminder_interval_min"), 60),
            theme=theme_value,
            sound_enabled=_to_bool(raw.get("sound_enabled"), True),
            autostart_enabled=_to_bool(raw.get("autostart_enabled"), False),
            reminder_sound=reminder_sound_value,
            shake_reminder_enabled=_to_bool(raw.get("shake_reminder_enabled"), False),
            window_geometry=_to_window_geometry(raw.get("window_geometry")),
        )

    def save(self) -> None:
        path = self.get_config_path()
        _ = path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(asdict(self), ensure_ascii=False, indent=2).encode("utf-8")
        # Atomic write: write to temp file then os.replace()
        fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, str(path))
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


def _to_int(value: object, default: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            try:
                return int(stripped)
            except ValueError:
                return default
        return default
    if value is None:
        return default
    return default


def _to_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    if isinstance(value, int):
        return value != 0
    return default


def _to_window_geometry(value: object) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None

    value_dict = cast(dict[str, object], value)
    required_keys = ("x", "y", "w", "h")
    geometry: dict[str, int] = {}
    for key in required_keys:
        if key not in value_dict:
            return None
        geometry[key] = _to_int(value_dict[key], 0)
    return geometry
