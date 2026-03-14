from __future__ import annotations

import importlib
from typing import Any

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

apply_stylesheet: Any = None
try:
    qt_material = importlib.import_module("qt_material")
    apply_stylesheet = getattr(qt_material, "apply_stylesheet", None)
except Exception:
    apply_stylesheet = None


# ---------------------------------------------------------------------------
# Color token palettes
# ---------------------------------------------------------------------------

_LIGHT: dict[str, str] = {
    # Backgrounds (glass: translucent layers over light gradient backdrop)
    "bg_primary": "rgba(245, 248, 252, 200)",
    "bg_secondary": "rgba(255, 255, 255, 180)",
    "bg_sidebar": "rgba(240, 246, 252, 160)",
    "bg_card": "rgba(255, 255, 255, 140)",
    "bg_hover": "rgba(255, 255, 255, 100)",
    "bg_selected": "rgba(107, 184, 217, 0.12)",
    "bg_input": "rgba(255, 255, 255, 180)",
    "bg_tooltip": "rgba(40, 40, 50, 220)",
    # Glass-specific tokens
    "glass_fill": "rgba(255, 255, 255, 105)",
    "glass_fill_heavy": "rgba(255, 255, 255, 155)",
    "glass_border": "rgba(255, 255, 255, 140)",
    "glass_border_accent": "rgba(107, 184, 217, 0.30)",
    "glass_highlight": "rgba(255, 255, 255, 70)",
    "glass_shadow": "rgba(0, 0, 0, 0.08)",
    "glass_backdrop_start": "#E8F0FA",
    "glass_backdrop_end": "#D6E8F8",
    # Borders (softer for glass)
    "border": "rgba(200, 215, 230, 0.50)",
    "border_light": "rgba(200, 215, 230, 0.30)",
    # Text
    "text_primary": "#1A2B3C",
    "text_secondary": "#3A4B5C",
    "text_muted": "#6B7B8C",
    "text_disabled": "#9EAAB6",
    "text_on_accent": "#FFFFFF",
    # Accent
    "accent": "#5BADD0",
    "accent_light": "rgba(91, 173, 208, 0.15)",
    "accent_hover": "#4A9CC0",
    "accent_pressed": "#3D8BB0",
    # Quick-add buttons (Dashboard) — glass pill buttons
    "btn_pill_bg": "rgba(91, 173, 208, 0.14)",
    "btn_pill_text": "#4A9CC0",
    "btn_pill_hover": "rgba(91, 173, 208, 0.24)",
    "btn_pill_pressed": "rgba(91, 173, 208, 0.36)",
    # Title bar (glass)
    "titlebar_bg": "rgba(240, 246, 252, 120)",
    "titlebar_border": "rgba(200, 215, 230, 0.35)",
    "titlebar_text": "#2A3B4C",
    "titlebar_btn_hover": "rgba(255, 255, 255, 120)",
    "titlebar_btn_pressed": "rgba(200, 215, 230, 0.45)",
    "titlebar_btn_text": "#4A5B6C",
    "titlebar_close_hover": "rgba(232, 17, 35, 0.85)",
    "titlebar_close_pressed": "#F1707A",
    # Sidebar (glass)
    "sidebar_bg": "rgba(235, 242, 250, 140)",
    "sidebar_border": "rgba(200, 215, 230, 0.35)",
    "sidebar_hover": "rgba(255, 255, 255, 90)",
    "sidebar_selected": "rgba(91, 173, 208, 0.16)",
    "sidebar_text": "#2A3B4C",
    "sidebar_text_selected": "#4A9CC0",
    "sidebar_icon_default": "#6B7B8C",
    "sidebar_version": "#9EAAB6",
    # Chart
    "chart_bar_start": "#8DCAE6",
    "chart_bar_end": "#5BADD0",
    "chart_grid": "rgba(200, 215, 230, 0.40)",
    "chart_goal": "#E89840",
    "chart_axis_text": "#6B7B8C",
    # Progress ring
    "progress_track": "rgba(200, 215, 230, 0.35)",
    "progress_start": "#5BADD0",
    "progress_end": "#8DCAE6",
    "progress_text": "#1A2B3C",
    "progress_subtext": "#6B7B8C",
    # Toggle button (History page)
    "toggle_bg": "rgba(200, 215, 230, 0.35)",
    "toggle_checked_bg": "rgba(255, 255, 255, 160)",
    "toggle_text": "#6B7B8C",
    "toggle_checked_text": "#4A9CC0",
    # Toast (glass)
    "toast_bg_start": "rgba(255, 255, 255, 200)",
    "toast_bg_end": "rgba(230, 244, 252, 200)",
    "toast_border": "rgba(91, 173, 208, 0.25)",
    "toast_title": "#2A4B6C",
    "toast_body": "rgba(60, 120, 165, 0.85)",
    "toast_btn_bg": "rgba(91, 173, 208, 0.85)",
    "toast_btn_hover": "rgba(74, 156, 192, 1.0)",
    "toast_btn_pressed": "rgba(61, 139, 176, 1.0)",
    "toast_later_bg": "rgba(91, 173, 208, 0.10)",
    "toast_later_text": "rgba(60, 120, 165, 0.75)",
    "toast_later_border": "rgba(91, 173, 208, 0.22)",
    "toast_later_hover": "rgba(91, 173, 208, 0.18)",
    "toast_later_pressed": "rgba(91, 173, 208, 0.28)",
    # Shake overlay (qcolor tokens use #AARRGGBB for reliable QColor parsing)
    "shake_overlay_bg": "#8C000000",
    "shake_title": "#F0FFFFFF",
    "shake_subtitle": "#B4C8DCFF",
    "shake_drop_start": "#FF82CCE6",
    "shake_drop_end": "#FF6BB8D9",
    "shake_drop_outline": "#64FFFFFF",
    "shake_drop_highlight": "#5AFFFFFF",
    "shake_btn_bg": "rgba(88, 166, 200, 230)",
    "shake_btn_hover": "rgba(100, 178, 212, 245)",
    "shake_btn_pressed": "rgba(72, 149, 183, 255)",
    "shake_dismiss_bg": "rgba(255, 255, 255, 50)",
    "shake_dismiss_text": "rgba(255, 255, 255, 200)",
    "shake_dismiss_border": "rgba(255, 255, 255, 60)",
    "shake_dismiss_hover": "rgba(255, 255, 255, 80)",
    "shake_dismiss_pressed": "rgba(255, 255, 255, 100)",
}

_DARK: dict[str, str] = {
    # Backgrounds (glass: translucent layers over dark gradient backdrop)
    "bg_primary": "rgba(14, 18, 30, 190)",
    "bg_secondary": "rgba(24, 32, 50, 170)",
    "bg_sidebar": "rgba(10, 14, 24, 160)",
    "bg_card": "rgba(24, 32, 50, 140)",
    "bg_hover": "rgba(255, 255, 255, 20)",
    "bg_selected": "rgba(142, 202, 230, 0.14)",
    "bg_input": "rgba(24, 32, 50, 180)",
    "bg_tooltip": "rgba(220, 220, 220, 230)",
    # Glass-specific tokens
    "glass_fill": "rgba(20, 28, 46, 120)",
    "glass_fill_heavy": "rgba(20, 28, 46, 170)",
    "glass_border": "rgba(80, 110, 150, 0.30)",
    "glass_border_accent": "rgba(142, 202, 230, 0.25)",
    "glass_highlight": "rgba(255, 255, 255, 20)",
    "glass_shadow": "rgba(0, 0, 0, 0.30)",
    "glass_backdrop_start": "#0C1020",
    "glass_backdrop_end": "#141C30",
    # Borders (softer for glass)
    "border": "rgba(60, 80, 110, 0.45)",
    "border_light": "rgba(60, 80, 110, 0.25)",
    # Text
    "text_primary": "#E0E6EE",
    "text_secondary": "#B8C2D0",
    "text_muted": "#7E8EA2",
    "text_disabled": "#505C6E",
    "text_on_accent": "#FFFFFF",
    # Accent
    "accent": "#8ECAE6",
    "accent_light": "rgba(142, 202, 230, 0.15)",
    "accent_hover": "#A6D6EC",
    "accent_pressed": "#76BEE0",
    # Quick-add buttons (Dashboard) — glass pill buttons
    "btn_pill_bg": "rgba(142, 202, 230, 0.14)",
    "btn_pill_text": "#A6D6EC",
    "btn_pill_hover": "rgba(142, 202, 230, 0.26)",
    "btn_pill_pressed": "rgba(142, 202, 230, 0.38)",
    # Title bar (glass)
    "titlebar_bg": "rgba(10, 14, 24, 130)",
    "titlebar_border": "rgba(60, 80, 110, 0.30)",
    "titlebar_text": "#E0E6EE",
    "titlebar_btn_hover": "rgba(255, 255, 255, 25)",
    "titlebar_btn_pressed": "rgba(255, 255, 255, 40)",
    "titlebar_btn_text": "#B8C2D0",
    "titlebar_close_hover": "rgba(232, 17, 35, 0.85)",
    "titlebar_close_pressed": "#F1707A",
    # Sidebar (glass)
    "sidebar_bg": "rgba(10, 14, 24, 140)",
    "sidebar_border": "rgba(60, 80, 110, 0.30)",
    "sidebar_hover": "rgba(255, 255, 255, 18)",
    "sidebar_selected": "rgba(142, 202, 230, 0.14)",
    "sidebar_text": "#E0E6EE",
    "sidebar_text_selected": "#8ECAE6",
    "sidebar_icon_default": "#7E8EA2",
    "sidebar_version": "#505C6E",
    # Chart
    "chart_bar_start": "#8ECAE6",
    "chart_bar_end": "#76BEE0",
    "chart_grid": "rgba(60, 80, 110, 0.35)",
    "chart_goal": "#FFB74D",
    "chart_axis_text": "#7E8EA2",
    # Progress ring
    "progress_track": "rgba(60, 80, 110, 0.30)",
    "progress_start": "#8ECAE6",
    "progress_end": "#A6D6EC",
    "progress_text": "#E0E6EE",
    "progress_subtext": "#7E8EA2",
    # Toggle button (History page)
    "toggle_bg": "rgba(60, 80, 110, 0.30)",
    "toggle_checked_bg": "rgba(24, 32, 50, 180)",
    "toggle_text": "#7E8EA2",
    "toggle_checked_text": "#8ECAE6",
    # Toast (glass)
    "toast_bg_start": "rgba(14, 18, 30, 220)",
    "toast_bg_end": "rgba(10, 14, 24, 220)",
    "toast_border": "rgba(100, 140, 180, 0.20)",
    "toast_title": "#E0E6EE",
    "toast_body": "rgba(184, 194, 208, 230)",
    "toast_btn_bg": "rgba(142, 202, 230, 0.80)",
    "toast_btn_hover": "rgba(142, 202, 230, 0.92)",
    "toast_btn_pressed": "rgba(118, 190, 224, 1.0)",
    "toast_later_bg": "rgba(255, 255, 255, 0.08)",
    "toast_later_text": "rgba(224, 230, 238, 0.85)",
    "toast_later_border": "rgba(255, 255, 255, 0.12)",
    "toast_later_hover": "rgba(255, 255, 255, 0.16)",
    "toast_later_pressed": "rgba(255, 255, 255, 0.22)",
    # Shake overlay (qcolor tokens use #AARRGGBB for reliable QColor parsing)
    "shake_overlay_bg": "#B4000000",
    "shake_title": "#F5E4E8EE",
    "shake_subtitle": "#C88E9AAF",
    "shake_drop_start": "#FF64B5F6",
    "shake_drop_end": "#FF42A5F5",
    "shake_drop_outline": "#3CFFFFFF",
    "shake_drop_highlight": "#3CFFFFFF",
    "shake_btn_bg": "rgba(142, 202, 230, 0.8)",
    "shake_btn_hover": "rgba(142, 202, 230, 0.9)",
    "shake_btn_pressed": "rgba(118, 190, 224, 1.0)",
    "shake_dismiss_bg": "rgba(255, 255, 255, 0.08)",
    "shake_dismiss_text": "rgba(228, 232, 238, 0.85)",
    "shake_dismiss_border": "rgba(255, 255, 255, 0.12)",
    "shake_dismiss_hover": "rgba(255, 255, 255, 0.14)",
    "shake_dismiss_pressed": "rgba(255, 255, 255, 0.18)",
}


# ---------------------------------------------------------------------------
# ThemeManager — singleton-style static class
# ---------------------------------------------------------------------------

class _ThemeSignals(QObject):
    """Internal QObject to hold the theme_applied signal."""
    theme_applied = Signal(str)  # emits "light" or "dark"


class ThemeManager:
    """
    Centralized theme manager.

    Usage:
        ThemeManager.apply(app, "dark")    # apply theme
        ThemeManager.is_dark()             # check
        ThemeManager.color("accent")       # get color token
        ThemeManager.qcolor("accent")      # get QColor

    Signal:
        ThemeManager.signals.theme_applied.connect(my_handler)
    """

    _current: str = "light"
    _mode: str = "light"  # "light", "dark", or "auto"
    signals = _ThemeSignals()

    _OVERRIDES_START = "/*__WATER_THEME_OVERRIDES_START__*/"
    _OVERRIDES_END = "/*__WATER_THEME_OVERRIDES_END__*/"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def apply(app: QApplication, mode: str = "light") -> None:
        """Apply theme. *mode* is "light", "dark", or "auto"."""
        ThemeManager._mode = mode

        if mode == "auto":
            resolved = ThemeManager._detect_system_theme()
        else:
            resolved = "dark" if mode == "dark" else "light"

        ThemeManager._current = resolved

        extra = {
            "danger": "#dc3545",
            "warning": "#ffc107",
            "success": "#17a2b8",
            "font_family": "Microsoft YaHei UI, Microsoft YaHei, PingFang SC, Noto Sans CJK SC, Segoe UI, system-ui, sans-serif",
            "density_scale": "-1",
        }

        if apply_stylesheet is not None:
            if resolved == "dark":
                apply_stylesheet(app, theme="dark_blue.xml", extra=extra)
            else:
                apply_stylesheet(
                    app,
                    theme="light_blue.xml",
                    invert_secondary=True,
                    extra=extra,
                )

        ThemeManager._apply_overrides(app)
        ThemeManager.signals.theme_applied.emit(resolved)

    @staticmethod
    def get_current() -> str:
        """Return resolved theme name: 'light' or 'dark'."""
        return ThemeManager._current

    @staticmethod
    def get_mode() -> str:
        """Return user-chosen mode: 'light', 'dark', or 'auto'."""
        return ThemeManager._mode

    @staticmethod
    def is_dark() -> bool:
        return ThemeManager._current == "dark"

    @staticmethod
    def colors() -> dict[str, str]:
        """Return full color dict for current theme."""
        return dict(_DARK if ThemeManager.is_dark() else _LIGHT)

    @staticmethod
    def color(token: str) -> str:
        """Get a single color token value."""
        palette = _DARK if ThemeManager.is_dark() else _LIGHT
        return palette.get(token, "#FF00FF")  # magenta = missing token

    @staticmethod
    def qcolor(token: str) -> QColor:
        """Get a QColor for a token. Handles #hex and CSS rgba() formats."""
        raw = ThemeManager.color(token)
        c = QColor(raw)
        if c.isValid():
            return c
        # QColor can't parse CSS rgba() — do it manually
        import re
        m = re.match(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)', raw)
        if m:
            r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            a_raw = float(m.group(4))
            # Alpha: if >1.0, treat as 0-255 integer; else treat as 0.0-1.0 fraction
            a = int(a_raw) if a_raw > 1.0 else int(a_raw * 255)
            return QColor(r, g, b, min(255, max(0, a)))
        return QColor()  # fallback invalid

    @staticmethod
    def font_family() -> str:
        """Return primary UI font family for current platform."""
        import sys
        if sys.platform == "win32":
            return "Microsoft YaHei UI"
        elif sys.platform == "darwin":
            return "PingFang SC"
        return "Noto Sans CJK SC"

    @staticmethod
    def font_families() -> list[str]:
        """Return prioritized font family list for current platform."""
        import sys
        if sys.platform == "win32":
            return ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "Segoe UI"]
        elif sys.platform == "darwin":
            return ["PingFang SC", "Hiragino Sans GB", "Helvetica Neue"]
        return ["Noto Sans CJK SC", "Source Han Sans CN", "WenQuanYi Micro Hei", "DejaVu Sans"]

    # ------------------------------------------------------------------
    # System theme detection
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_system_theme() -> str:
        """Detect OS color scheme via QStyleHints (Qt 6.5+)."""
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return "light"

        try:
            hints = app.styleHints()
            scheme = hints.colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                return "dark"
        except (AttributeError, RuntimeError):
            pass  # Qt < 6.5 or no style hints

        return "light"

    @staticmethod
    def connect_system_theme_watcher(callback) -> bool:
        """
        Connect a callback to OS theme changes.
        Returns True if successful, False if not supported.

        callback signature: callback(theme_name: str) where theme_name is 'light'/'dark'.
        """
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return False

        try:
            hints = app.styleHints()

            def _on_system_change(scheme):
                if ThemeManager._mode != "auto":
                    return
                new_theme = "dark" if scheme == Qt.ColorScheme.Dark else "light"
                if new_theme != ThemeManager._current:
                    callback(new_theme)

            hints.colorSchemeChanged.connect(_on_system_change)
            return True
        except (AttributeError, RuntimeError):
            return False

    # ------------------------------------------------------------------
    # CSS overrides
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_overrides(app: QApplication) -> None:
        current_ss = app.styleSheet() or ""
        clean_ss = ThemeManager._strip_previous_overrides(current_ss)
        overrides = ThemeManager._build_overrides()
        app.setStyleSheet(
            f"{clean_ss}\n{ThemeManager._OVERRIDES_START}\n{overrides}\n{ThemeManager._OVERRIDES_END}\n"
        )

    @staticmethod
    def _strip_previous_overrides(stylesheet: str) -> str:
        start = stylesheet.find(ThemeManager._OVERRIDES_START)
        end = stylesheet.find(ThemeManager._OVERRIDES_END)
        if start == -1 or end == -1 or end < start:
            return stylesheet
        end += len(ThemeManager._OVERRIDES_END)
        return (stylesheet[:start] + stylesheet[end:]).strip()

    @staticmethod
    def _build_overrides() -> str:
        c = ThemeManager.colors()

        def t(token: str) -> str:
            return c.get(token, "#FF00FF")

        return f"""
/* === Water Reminder Theme Overrides — Liquid Glass === */

/* --- Global window --- */
QMainWindow {{
    background: transparent;
}}

/* --- Container (glass backdrop) --- */
QWidget#Container {{
    background-color: {t("bg_primary")};
    border: 1px solid {t("glass_border")};
    border-radius: 14px;
}}

QWidget#ContainerMaximized {{
    background-color: {t("bg_primary")};
    border: none;
    border-radius: 0px;
}}

/* --- Sidebar (glass) --- */
QWidget[objectName="Sidebar"], QWidget#Sidebar {{
    background-color: {t("sidebar_bg")};
    border-right: 1px solid {t("sidebar_border")};
}}

/* --- Pages --- */
QWidget#historyPage {{
    background-color: transparent;
}}

QWidget#settingsPage {{
    background-color: transparent;
}}

/* --- Charts --- */
QChartView {{
    background: transparent;
    border: none;
}}

/* --- Frames (glass cards) --- */
QFrame {{
    border-color: {t("glass_border")};
}}

/* --- Labels --- */
QLabel {{
    selection-background-color: {t("accent")};
}}

/* --- ScrollArea --- */
QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {t("glass_border")};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {t("text_muted")};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {t("glass_border")};
    border-radius: 3px;
    min-width: 30px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* --- Reusable tokens --- */
QWidget[role="chart-card"] {{
    background: {t("glass_fill")};
    border: 1px solid {t("glass_border")};
    border-radius: 16px;
}}

QLabel[role="muted"] {{
    color: {t("text_muted")};
}}

QWidget[role="chart-grid"] {{
    color: {t("chart_grid")};
}}
"""
