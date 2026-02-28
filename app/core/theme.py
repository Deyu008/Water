from __future__ import annotations

from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet


class ThemeManager:
    _current = "light"
    _OVERRIDES_START = "/*__WATER_THEME_OVERRIDES_START__*/"
    _OVERRIDES_END = "/*__WATER_THEME_OVERRIDES_END__*/"

    @staticmethod
    def apply(app: QApplication, theme_name: str = "light") -> None:
        normalized = "dark" if theme_name == "dark" else "light"

        extra = {
            "danger": "#dc3545",
            "warning": "#ffc107",
            "success": "#17a2b8",
            "font_family": "Segoe UI, system-ui, sans-serif",
            "density_scale": "-1",
        }

        if normalized == "dark":
            apply_stylesheet(app, theme="dark_blue.xml", extra=extra)
        else:
            apply_stylesheet(
                app,
                theme="light_blue.xml",
                invert_secondary=True,
                extra=extra,
            )

        ThemeManager._current = normalized
        ThemeManager._apply_overrides(app)

    @staticmethod
    def get_current() -> str:
        return ThemeManager._current

    @staticmethod
    def _apply_overrides(app: QApplication) -> None:
        current_ss = app.styleSheet() or ""
        clean_ss = ThemeManager._strip_previous_overrides(current_ss)
        overrides = ThemeManager._build_overrides(ThemeManager._current)
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
    def _build_overrides(theme_name: str) -> str:
        dark = theme_name == "dark"

        container_bg = "#1E1E1E" if dark else "#FAFAFA"
        container_border = "#333A45" if dark else "#E0E0E0"
        page_bg = "#161A20" if dark else "#FAFAFA"
        chart_card_bg = "#202733" if dark else "#FFFFFF"
        chart_grid = "#334155" if dark else "#F0F0F0"
        status_text = "#B0BEC5" if dark else "#757575"

        return f"""
/* Frameless window compatibility */
QMainWindow {{
    background: transparent;
}}

QWidget#Container {{
    background-color: {container_bg};
    border: 1px solid {container_border};
    border-radius: 10px;
}}

/* Sidebar specific styling (keep structure, let paintEvent decide selected look) */
QWidget[objectName="Sidebar"], QWidget#Sidebar {{
    border-right: 1px solid {container_border};
}}

/* History page/chart area compatibility */
QWidget#historyPage {{
    background-color: {page_bg};
}}

QChartView {{
    background: transparent;
    border: none;
}}

QFrame {{
    border-color: {container_border};
}}

/* Dashboard status text readability */
QLabel {{
    selection-background-color: #3A86FF;
}}

/* Chart-like card fallback */
QWidget[role="chart-card"] {{
    background: {chart_card_bg};
    border: 1px solid {container_border};
    border-radius: 12px;
}}

/* Reusable muted text token */
QLabel[role="muted"] {{
    color: {status_text};
}}

/* Keep a subtle grid token for custom painters */
QWidget[role="chart-grid"] {{
    color: {chart_grid};
}}
"""
