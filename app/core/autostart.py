from __future__ import annotations

import logging
import platform
import shlex
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class AutoStartManager:
    APP_NAME = "WaterReminder"

    @staticmethod
    def is_enabled() -> bool:
        system = platform.system()
        if system == "Windows":
            return AutoStartManager._win_is_enabled()
        if system == "Linux":
            return AutoStartManager._linux_is_enabled()
        return False

    @staticmethod
    def enable() -> bool:
        system = platform.system()
        if system == "Windows":
            return AutoStartManager._win_enable()
        if system == "Linux":
            return AutoStartManager._linux_enable()
        return False

    @staticmethod
    def disable() -> bool:
        system = platform.system()
        if system == "Windows":
            return AutoStartManager._win_disable()
        if system == "Linux":
            return AutoStartManager._linux_disable()
        return False

    @staticmethod
    def _launch_command() -> str:
        """Return launch command for Windows registry (quoted)."""
        if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"):
            executable = Path(sys.executable).resolve()
            return f'"{executable}"'

        python_executable = Path(sys.executable).resolve()
        script_path = Path(sys.argv[0]).resolve()
        return f'"{python_executable}" "{script_path}"'

    @staticmethod
    def _launch_command_desktop() -> str:
        """Return Exec value for .desktop file (freedesktop spec, space-safe)."""
        if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"):
            return shlex.join([str(Path(sys.executable).resolve())])

        python_executable = str(Path(sys.executable).resolve())
        script_path = str(Path(sys.argv[0]).resolve())
        return shlex.join([python_executable, script_path])

    @staticmethod
    def _win_is_enabled() -> bool:
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ,
            ) as key:
                value, _ = winreg.QueryValueEx(key, AutoStartManager.APP_NAME)
            return bool(value)
        except Exception:
            logger.debug("Failed to check Windows autostart", exc_info=True)
            return False

    @staticmethod
    def _win_enable() -> bool:
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                winreg.SetValueEx(
                    key,
                    AutoStartManager.APP_NAME,
                    0,
                    winreg.REG_SZ,
                    AutoStartManager._launch_command(),
                )
            return True
        except Exception:
            logger.warning("Failed to enable Windows autostart", exc_info=True)
            return False

    @staticmethod
    def _win_disable() -> bool:
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                try:
                    winreg.DeleteValue(key, AutoStartManager.APP_NAME)
                except FileNotFoundError:
                    pass
            return True
        except Exception:
            logger.warning("Failed to disable Windows autostart", exc_info=True)
            return False

    @staticmethod
    def _linux_autostart_file() -> Path:
        return Path.home() / ".config" / "autostart" / f"{AutoStartManager.APP_NAME}.desktop"

    @staticmethod
    def _linux_is_enabled() -> bool:
        try:
            return AutoStartManager._linux_autostart_file().exists()
        except Exception:
            logger.debug("Failed to check Linux autostart", exc_info=True)
            return False

    @staticmethod
    def _linux_enable() -> bool:
        try:
            desktop_file = AutoStartManager._linux_autostart_file()
            desktop_file.parent.mkdir(parents=True, exist_ok=True)

            content = "\n".join(
                [
                    "[Desktop Entry]",
                    "Type=Application",
                    f"Name={AutoStartManager.APP_NAME}",
                    f"Exec={AutoStartManager._launch_command_desktop()}",
                    "Terminal=false",
                    "X-GNOME-Autostart-enabled=true",
                    "",
                ]
            )
            desktop_file.write_text(content, encoding="utf-8")
            return True
        except Exception:
            logger.warning("Failed to enable Linux autostart", exc_info=True)
            return False

    @staticmethod
    def _linux_disable() -> bool:
        try:
            desktop_file = AutoStartManager._linux_autostart_file()
            if desktop_file.exists():
                desktop_file.unlink()
            return True
        except Exception:
            logger.warning("Failed to disable Linux autostart", exc_info=True)
            return False
