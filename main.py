from __future__ import annotations

import argparse
import ctypes
import os
import sys
import types
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from app.config import AppConfig
from app.core.autostart import AutoStartManager
from app.core.reminder import ReminderEngine
from app.core.sound import SoundManager
from app.core.theme import ThemeManager
from app.core.tray import TrayManager
from app.database import Database
from app.main_window import MainWindow
from app.widgets.toast_reminder import ToastReminder

try:
    from app.pages.dashboard import DashboardPage
except Exception:
    class DashboardPage(QWidget):
        water_added = Signal(int)

        def __init__(self, parent=None):
            super().__init__(parent)
            self._label = QLabel("Dashboard page is not available yet.", self)

        def update_progress(self, current_ml: int, goal_ml: int) -> None:
            del current_ml, goal_ml

        def update_recent(self, records: list[dict]) -> None:
            del records

        def update_next_reminder(self, time_str: str) -> None:
            del time_str

        def set_reminder_paused(self, paused: bool) -> None:
            del paused


try:
    from app.pages.history import HistoryPage
except Exception:
    class HistoryPage(QWidget):
        period_changed = Signal(int)

        def __init__(self, parent=None):
            super().__init__(parent)
            self._label = QLabel("History page is not available yet.", self)

        def update_chart(self, daily_totals: list[dict], goal_ml: int) -> None:
            del daily_totals, goal_ml

        def update_stats(self, avg_ml: int, best_ml: int, total_ml: int) -> None:
            del avg_ml, best_ml, total_ml


try:
    from app.pages.settings import SettingsPage
except Exception:
    class SettingsPage(QWidget):
        interval_changed = Signal(int)
        goal_changed = Signal(int)
        theme_changed = Signal(str)
        sound_changed = Signal(bool)
        autostart_changed = Signal(bool)

        def __init__(self, parent=None):
            super().__init__(parent)
            self._label = QLabel("Settings page is not available yet.", self)

        def load_settings(self, settings: dict) -> None:
            del settings


class WaterApp:
    def __init__(self, smoke_test: bool = False):
        self.smoke_test = bool(smoke_test)
        self.project_root = Path(__file__).resolve().parent
        self._is_quitting = False

        self.app: QApplication | None = None
        self.config: AppConfig | None = None
        self.db: Database | None = None
        self.main_window: MainWindow | None = None
        self.dashboard_page: DashboardPage | None = None
        self.history_page: HistoryPage | None = None
        self.settings_page: SettingsPage | None = None
        self.engine: ReminderEngine | None = None
        self.sound: SoundManager | None = None
        self.tray: TrayManager | None = None
        self.toast: ToastReminder | None = None

    def run(self) -> int:
        self._prepare_runtime()
        self._create_core_objects()
        self._wire_signals()
        self._initial_load()

        if self.smoke_test:
            self.shutdown()
            print("SMOKE TEST PASSED")
            return 0

        self._start_runtime_services()
        assert self.app is not None
        return self.app.exec()

    def _prepare_runtime(self) -> None:
        os.chdir(self.project_root)
        self._set_windows_app_user_model_id()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.config = AppConfig.load()
        ThemeManager.apply(self.app, self.config.theme)

    def _create_core_objects(self) -> None:
        assert self.config is not None

        self.db = Database()
        self.main_window = MainWindow()
        self.dashboard_page = DashboardPage(self.main_window)
        self.history_page = HistoryPage(self.main_window)
        self.settings_page = SettingsPage(self.main_window)
        self._set_real_pages()

        self.engine = ReminderEngine(interval_minutes=self.config.reminder_interval_min)
        self.sound = SoundManager(enabled=self.config.sound_enabled)
        self.tray = TrayManager()

        self._restore_window_geometry()
        self._install_close_to_tray_behavior()

    def _set_real_pages(self) -> None:
        assert self.main_window is not None
        assert self.dashboard_page is not None
        assert self.history_page is not None
        assert self.settings_page is not None

        stack = self.main_window.stack
        while stack.count() > 0:
            w = stack.widget(0)
            stack.removeWidget(w)
            w.deleteLater()

        stack.addWidget(self.dashboard_page)
        stack.addWidget(self.history_page)
        stack.addWidget(self.settings_page)
        stack.setCurrentIndex(0)

    def _wire_signals(self) -> None:
        assert self.main_window is not None
        assert self.dashboard_page is not None
        assert self.history_page is not None
        assert self.settings_page is not None
        assert self.engine is not None
        assert self.sound is not None
        assert self.tray is not None

        self.dashboard_page.water_added.connect(lambda amount: self._add_intake_and_refresh(amount, "button"))

        self.engine.remind_triggered.connect(self._on_reminder_triggered)
        self.engine.next_due_changed.connect(self.dashboard_page.update_next_reminder)
        self.engine.state_changed.connect(self._on_engine_state_changed)

        self.tray.quick_drink_requested.connect(self._on_tray_quick_drink)
        self.tray.show_window_requested.connect(self.show_main_window)
        self.tray.quit_requested.connect(self.shutdown)
        self.tray.pause_requested.connect(self.engine.pause)
        self.tray.resume_requested.connect(self.engine.resume)

        self.settings_page.interval_changed.connect(self._on_interval_changed)
        self.settings_page.goal_changed.connect(self._on_goal_changed)
        self.settings_page.theme_changed.connect(self._on_theme_changed)
        self.settings_page.sound_changed.connect(self._on_sound_changed)
        self.settings_page.autostart_changed.connect(self._on_autostart_changed)

        self.history_page.period_changed.connect(self.refresh_history)

        self.main_window.sidebar.page_changed.connect(self._on_sidebar_page_changed)

    def _start_runtime_services(self) -> None:
        assert self.main_window is not None
        assert self.tray is not None
        assert self.engine is not None

        self.main_window.show()
        self.tray.show()
        self.engine.start()

    def _initial_load(self) -> None:
        assert self.config is not None
        assert self.settings_page is not None

        self.refresh_dashboard()
        self.refresh_history(self._current_history_period())
        self.settings_page.load_settings(
            {
                "daily_goal_ml": self.config.daily_goal_ml,
                "reminder_interval_min": self.config.reminder_interval_min,
                "theme": self.config.theme,
                "sound_enabled": self.config.sound_enabled,
                "autostart_enabled": self.config.autostart_enabled,
            }
        )

    def _set_windows_app_user_model_id(self) -> None:
        if not sys.platform.startswith("win"):
            return

        try:
            app_id = "WaterReminder.Desktop.App"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            return

    def _on_reminder_triggered(self) -> None:
        assert self.sound is not None
        self._show_toast_reminder()
        self.sound.play_reminder()

    def _show_toast_reminder(self) -> None:
        if self.toast is not None:
            self.toast.close()
            self.toast.deleteLater()
            self.toast = None

        total = self.db.get_today_total() if self.db is not None else 0
        self.toast = ToastReminder(today_total_ml=total, drink_amount=200)
        self.toast.drink_clicked.connect(self._on_toast_drink_clicked)
        self.toast.dismissed.connect(self._on_toast_dismissed)
        self.toast.show_reminder()

    def _on_toast_drink_clicked(self, amount: int) -> None:
        self._add_intake_and_refresh(amount, "reminder")

    def _on_toast_dismissed(self) -> None:
        if self.toast is None:
            return
        self.toast.deleteLater()
        self.toast = None

    def _on_tray_quick_drink(self, amount: int) -> None:
        self._add_intake_and_refresh(amount, "tray")
        assert self.tray is not None
        self.tray.show_notification("Water Logged", f"Quick drink +{int(amount)}ml")

    def _add_intake_and_refresh(self, amount: int, source: str) -> None:
        if self.db is None:
            return

        amount_value = int(amount)
        if amount_value <= 0:
            return

        self.db.add_intake(amount_value, source=source)
        self.refresh_dashboard()
        if self._current_page_index() == 1:
            self.refresh_history(self._current_history_period())

    def refresh_dashboard(self) -> None:
        if self.db is None or self.config is None or self.dashboard_page is None:
            return

        today_total = self.db.get_today_total()
        recent = self.db.get_recent(20)
        self.dashboard_page.update_progress(today_total, self.config.daily_goal_ml)
        self.dashboard_page.update_recent(recent)

    def refresh_history(self, days: int) -> None:
        if self.db is None or self.config is None or self.history_page is None:
            return

        days_value = max(1, int(days))
        daily_totals = self.db.get_daily_totals(days=days_value)
        self.history_page.update_chart(daily_totals, self.config.daily_goal_ml)

        totals = [int(entry.get("total_ml", 0)) for entry in daily_totals]
        total_ml = sum(totals)
        best_ml = max(totals) if totals else 0
        avg_ml = int(total_ml / len(totals)) if totals else 0
        self.history_page.update_stats(avg_ml, best_ml, total_ml)

    def _on_interval_changed(self, interval_min: int) -> None:
        if self.engine is not None:
            self.engine.set_interval(int(interval_min))
        if self.config is not None:
            self.config.reminder_interval_min = int(interval_min)
            self.config.save()

    def _on_goal_changed(self, goal_ml: int) -> None:
        if self.config is not None:
            self.config.daily_goal_ml = int(goal_ml)
            self.config.save()
        self.refresh_dashboard()
        if self._current_page_index() == 1:
            self.refresh_history(self._current_history_period())

    def _on_theme_changed(self, theme_name: str) -> None:
        if self.app is not None:
            ThemeManager.apply(self.app, theme_name)
        if self.config is not None:
            self.config.theme = "dark" if theme_name == "dark" else "light"
            self.config.save()

    def _on_sound_changed(self, enabled: bool) -> None:
        if self.sound is not None:
            self.sound.set_enabled(bool(enabled))
        if self.config is not None:
            self.config.sound_enabled = bool(enabled)
            self.config.save()

    def _on_autostart_changed(self, enabled: bool) -> None:
        enabled_value = bool(enabled)
        if enabled_value:
            _ = AutoStartManager.enable()
        else:
            _ = AutoStartManager.disable()

        if self.config is not None:
            self.config.autostart_enabled = enabled_value
            self.config.save()

    def _on_engine_state_changed(self, state: str) -> None:
        paused = state == "paused"
        if self.dashboard_page is not None:
            self.dashboard_page.set_reminder_paused(paused)
        if self.tray is not None:
            self.tray.set_reminder_paused(paused)

    def _on_sidebar_page_changed(self, index: int) -> None:
        idx = int(index)
        if idx == 0:
            self.refresh_dashboard()
        elif idx == 1:
            self.refresh_history(self._current_history_period())
        elif idx == 2:
            self._reload_settings_page()

    def _reload_settings_page(self) -> None:
        if self.settings_page is None or self.config is None:
            return
        self.settings_page.load_settings(
            {
                "daily_goal_ml": self.config.daily_goal_ml,
                "reminder_interval_min": self.config.reminder_interval_min,
                "theme": self.config.theme,
                "sound_enabled": self.config.sound_enabled,
                "autostart_enabled": self.config.autostart_enabled,
            }
        )

    def _current_page_index(self) -> int:
        if self.main_window is None:
            return 0
        return int(self.main_window.stack.currentIndex())

    def _current_history_period(self) -> int:
        if self.history_page is None:
            return 7

        if hasattr(self.history_page, "toggle_group"):
            toggle_group = getattr(self.history_page, "toggle_group")
            checked = toggle_group.checkedButton() if toggle_group is not None else None
            if checked is not None:
                try:
                    days = int(toggle_group.id(checked))
                    return days if days > 0 else 7
                except Exception:
                    return 7
        return 7

    def _install_close_to_tray_behavior(self) -> None:
        assert self.main_window is not None
        original_close_event = self.main_window.closeEvent

        def close_event(window: MainWindow, event: QCloseEvent) -> None:
            if self._is_quitting:
                original_close_event(event)
                return

            window.hide()
            if self.tray is not None:
                self.tray.show_notification("Water Reminder", "App is still running in system tray.")
            event.ignore()

        self.main_window.closeEvent = types.MethodType(close_event, self.main_window)

    def _restore_window_geometry(self) -> None:
        if self.main_window is None or self.config is None or not self.config.window_geometry:
            return

        geo = self.config.window_geometry
        self.main_window.setGeometry(
            int(geo.get("x", 100)),
            int(geo.get("y", 100)),
            max(750, int(geo.get("w", 900))),
            max(500, int(geo.get("h", 650))),
        )

    def _save_window_geometry(self) -> None:
        if self.main_window is None or self.config is None:
            return

        geom = self.main_window.geometry()
        self.config.window_geometry = {
            "x": int(geom.x()),
            "y": int(geom.y()),
            "w": int(geom.width()),
            "h": int(geom.height()),
        }
        self.config.save()

    def show_main_window(self) -> None:
        if self.main_window is None:
            return

        if self.main_window.isMinimized():
            self.main_window.showNormal()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def shutdown(self) -> None:
        if self._is_quitting:
            return
        self._is_quitting = True

        try:
            self._save_window_geometry()
        except Exception:
            pass

        if self.toast is not None:
            self.toast.close()
            self.toast.deleteLater()
            self.toast = None

        if self.engine is not None:
            self.engine.stop()

        if self.tray is not None:
            self.tray.hide()

        if self.db is not None:
            self.db.close()

        if self.app is not None:
            self.app.quit()


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Water Reminder desktop app")
    parser.add_argument("--smoke-test", action="store_true", help="Build app and exit without event loop")
    return parser.parse_args(argv)


def main() -> int:
    args = _parse_args(sys.argv[1:])
    app = WaterApp(smoke_test=args.smoke_test)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
