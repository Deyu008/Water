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
    # Backgrounds
    "bg_primary": "#FAFAFA",
    "bg_secondary": "#FFFFFF",
    "bg_sidebar": "#F5F5F5",
    "bg_card": "#FFFFFF",
    "bg_hover": "rgba(0, 0, 0, 0.04)",
    "bg_selected": "rgba(33, 150, 243, 0.08)",
    "bg_input": "#FFFFFF",
    "bg_tooltip": "#333333",
    # Borders
    "border": "#E0E0E0",
    "border_light": "#EEEEEE",
    # Text
    "text_primary": "#212121",
    "text_secondary": "#424242",
    "text_muted": "#757575",
    "text_disabled": "#9E9E9E",
    "text_on_accent": "#FFFFFF",
    # Accent
    "accent": "#6BB8D9",
    "accent_light": "#E8F4FB",
    "accent_hover": "#58A6C8",
    "accent_pressed": "#4895B7",
    # Quick-add buttons (Dashboard)
    "btn_pill_bg": "#E8F4FB",
    "btn_pill_text": "#58A6C8",
    "btn_pill_hover": "#D1EAF5",
    "btn_pill_pressed": "#BAE0EF",
    # Title bar
    "titlebar_bg": "#FAFAFA",
    "titlebar_border": "#E0E0E0",
    "titlebar_text": "#333333",
    "titlebar_btn_hover": "#E5E5E5",
    "titlebar_btn_pressed": "#CACACB",
    "titlebar_btn_text": "#555555",
    "titlebar_close_hover": "#E81123",
    "titlebar_close_pressed": "#F1707A",
    # Sidebar
    "sidebar_bg": "#F5F5F5",
    "sidebar_border": "#E0E0E0",
    "sidebar_hover": "#1A000000",
    "sidebar_selected": "#246BB8D9",
    "sidebar_text": "#212121",
    "sidebar_text_selected": "#6BB8D9",
    "sidebar_icon_default": "#646464",
    "sidebar_version": "#999999",
    # Chart
    "chart_bar_start": "#9DD0E8",
    "chart_bar_end": "#6BB8D9",
    "chart_grid": "#F0F0F0",
    "chart_goal": "#FF9800",
    "chart_axis_text": "#757575",
    # Progress ring
    "progress_track": "#F0F0F0",
    "progress_start": "#6BB8D9",
    "progress_end": "#9DD0E8",
    "progress_text": "#212121",
    "progress_subtext": "#757575",
    # Toggle button (History page)
    "toggle_bg": "#E0E0E0",
    "toggle_checked_bg": "#FFFFFF",
    "toggle_text": "#616161",
    "toggle_checked_text": "#6BB8D9",
    # Toast
    "toast_bg_start": "rgba(28, 47, 85, 225)",
    "toast_bg_end": "rgba(20, 30, 54, 225)",
    "toast_border": "rgba(255, 255, 255, 36)",
    "toast_title": "#F5FAFF",
    "toast_body": "rgba(219, 230, 246, 230)",
    "toast_btn_bg": "rgba(88, 166, 200, 230)",
    "toast_btn_hover": "rgba(100, 178, 212, 245)",
    "toast_btn_pressed": "rgba(72, 149, 183, 255)",
    "toast_later_bg": "rgba(255, 255, 255, 45)",
    "toast_later_text": "rgba(255, 255, 255, 220)",
    "toast_later_border": "rgba(255, 255, 255, 60)",
    "toast_later_hover": "rgba(255, 255, 255, 70)",
    "toast_later_pressed": "rgba(255, 255, 255, 85)",
    # Shake overlay (qcolor tokens use #AARRGGBB for reliable QColor parsing)
    "shake_overlay_bg": "#8C000000",
    "shake_title": "#F0FFFFFF",
    "shake_subtitle": "#B4C8DCFF",
    "shake_drop_start": "#FF7AD6FF",
    "shake_drop_end": "#FF399AF5",
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
    # Backgrounds
    "bg_primary": "#121826",
    "bg_secondary": "#1B2338",
    "bg_sidebar": "#0E1420",
    "bg_card": "#1E283A",
    "bg_hover": "rgba(255, 255, 255, 0.06)",
    "bg_selected": "rgba(100, 181, 246, 0.12)",
    "bg_input": "#1E283A",
    "bg_tooltip": "#E0E0E0",
    # Borders
    "border": "#2A3650",
    "border_light": "#232E42",
    # Text
    "text_primary": "#E4E8EE",
    "text_secondary": "#BDC1C6",
    "text_muted": "#8E9AAF",
    "text_disabled": "#5F6B7A",
    "text_on_accent": "#FFFFFF",
    # Accent
    "accent": "#8ECAE6",
    "accent_light": "rgba(142, 202, 230, 0.15)",
    "accent_hover": "#A6D6EC",
    "accent_pressed": "#76BEE0",
    # Quick-add buttons (Dashboard)
    "btn_pill_bg": "rgba(142, 202, 230, 0.15)",
    "btn_pill_text": "#A6D6EC",
    "btn_pill_hover": "rgba(142, 202, 230, 0.25)",
    "btn_pill_pressed": "rgba(142, 202, 230, 0.35)",
    # Title bar
    "titlebar_bg": "#0E1420",
    "titlebar_border": "#2A3650",
    "titlebar_text": "#E4E8EE",
    "titlebar_btn_hover": "rgba(255, 255, 255, 0.08)",
    "titlebar_btn_pressed": "rgba(255, 255, 255, 0.12)",
    "titlebar_btn_text": "#BDC1C6",
    "titlebar_close_hover": "#E81123",
    "titlebar_close_pressed": "#F1707A",
    # Sidebar
    "sidebar_bg": "#0E1420",
    "sidebar_border": "#2A3650",
    "sidebar_hover": "#0FFFFFFF",
    "sidebar_selected": "#1F8ECAE6",
    "sidebar_text": "#E4E8EE",
    "sidebar_text_selected": "#8ECAE6",
    "sidebar_icon_default": "#8E9AAF",
    "sidebar_version": "#5F6B7A",
    # Chart
    "chart_bar_start": "#8ECAE6",
    "chart_bar_end": "#76BEE0",
    "chart_grid": "#2A3650",
    "chart_goal": "#FFB74D",
    "chart_axis_text": "#8E9AAF",
    # Progress ring
    "progress_track": "#2A3650",
    "progress_start": "#8ECAE6",
    "progress_end": "#A6D6EC",
    "progress_text": "#E4E8EE",
    "progress_subtext": "#8E9AAF",
    # Toggle button (History page)
    "toggle_bg": "#2A3650",
    "toggle_checked_bg": "#1E283A",
    "toggle_text": "#8E9AAF",
    "toggle_checked_text": "#8ECAE6",
    # Toast
    "toast_bg_start": "rgba(18, 24, 38, 240)",
    "toast_bg_end": "rgba(14, 20, 32, 240)",
    "toast_border": "rgba(100, 181, 246, 0.15)",
    "toast_title": "#E4E8EE",
    "toast_body": "rgba(189, 193, 198, 230)",
    "toast_btn_bg": "rgba(142, 202, 230, 0.8)",
    "toast_btn_hover": "rgba(142, 202, 230, 0.9)",
    "toast_btn_pressed": "rgba(118, 190, 224, 1.0)",
    "toast_later_bg": "rgba(255, 255, 255, 0.08)",
    "toast_later_text": "rgba(228, 232, 238, 0.85)",
    "toast_later_border": "rgba(255, 255, 255, 0.12)",
    "toast_later_hover": "rgba(255, 255, 255, 0.14)",
    "toast_later_pressed": "rgba(255, 255, 255, 0.18)",
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
        """Get a QColor for a token."""
        return QColor(ThemeManager.color(token))

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
/* === Water Reminder Theme Overrides === */

/* --- Global window --- */
QMainWindow {{
    background: transparent;
}}

/* --- Container --- */
QWidget#Container {{
    background-color: {t("bg_primary")};
    border: 1px solid {t("border")};
    border-radius: 10px;
}}

QWidget#ContainerMaximized {{
    background-color: {t("bg_primary")};
    border: none;
    border-radius: 0px;
}}

/* --- Sidebar --- */
QWidget[objectName="Sidebar"], QWidget#Sidebar {{
    background-color: {t("sidebar_bg")};
    border-right: 1px solid {t("sidebar_border")};
}}

/* --- Pages --- */
QWidget#historyPage {{
    background-color: {t("bg_primary")};
}}

QWidget#settingsPage {{
    background-color: {t("bg_primary")};
}}

/* --- Charts --- */
QChartView {{
    background: transparent;
    border: none;
}}

/* --- Frames (cards) --- */
QFrame {{
    border-color: {t("border")};
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
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {t("border")};
    border-radius: 4px;
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
    height: 8px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {t("border")};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* --- Reusable tokens --- */
QWidget[role="chart-card"] {{
    background: {t("bg_card")};
    border: 1px solid {t("border")};
    border-radius: 12px;
}}

QLabel[role="muted"] {{
    color: {t("text_muted")};
}}

QWidget[role="chart-grid"] {{
    color: {t("chart_grid")};
}}
"""
