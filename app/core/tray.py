from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


class TrayManager(QObject):
    show_window_requested = Signal()
    quit_requested = Signal()
    quick_drink_requested = Signal(int)
    pause_requested = Signal()
    resume_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._is_paused = False

        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(self._create_water_drop_icon())
        self._tray_icon.setToolTip("Water Reminder")

        self._menu = QMenu()  # no parent: QMenu requires QWidget, TrayManager is QObject
        self._title_action = QAction("Water Reminder", self)
        self._title_action.setEnabled(False)

        self._show_window_action = QAction("Show Window", self)
        self._pause_resume_action = QAction("Pause Reminders", self)
        self._quit_action = QAction("Quit", self)

        self._quick_drink_menu = QMenu("Quick Drink", self._menu)
        self._quick_drink_actions: dict[int, QAction] = {}
        for amount in (100, 200, 300, 500):
            action = QAction(f"{amount}ml", self)
            action.triggered.connect(lambda _checked=False, ml=amount: self.quick_drink_requested.emit(ml))
            self._quick_drink_actions[amount] = action
            self._quick_drink_menu.addAction(action)

        self._menu.addAction(self._title_action)
        self._menu.addSeparator()
        self._menu.addAction(self._show_window_action)
        self._menu.addSeparator()
        self._menu.addMenu(self._quick_drink_menu)
        self._menu.addSeparator()
        self._menu.addAction(self._pause_resume_action)
        self._menu.addSeparator()
        self._menu.addAction(self._quit_action)

        self._tray_icon.setContextMenu(self._menu)

        self._show_window_action.triggered.connect(self.show_window_requested.emit)
        self._quit_action.triggered.connect(self.quit_requested.emit)
        self._pause_resume_action.triggered.connect(self._handle_pause_resume)
        self._tray_icon.activated.connect(self._on_tray_activated)

    def set_tooltip(self, text: str):
        self._tray_icon.setToolTip(text)

    def set_reminder_paused(self, paused: bool):
        self._is_paused = paused
        self._pause_resume_action.setText("Resume Reminders" if paused else "Pause Reminders")

    def show_notification(self, title: str, message: str):
        self._tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )

    def _create_water_drop_icon(self) -> QIcon:
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2196F3"))
        painter.drawEllipse(2, 2, 60, 60)

        drop_path = QPainterPath()
        drop_path.moveTo(32, 14)
        drop_path.cubicTo(21, 27, 18, 33, 18, 40)
        drop_path.cubicTo(18, 48, 24, 54, 32, 54)
        drop_path.cubicTo(40, 54, 46, 48, 46, 40)
        drop_path.cubicTo(46, 33, 43, 27, 32, 14)
        drop_path.closeSubpath()

        painter.setBrush(QColor("#FFFFFF"))
        painter.drawPath(drop_path)
        painter.end()

        return QIcon(pixmap)

    def _handle_pause_resume(self):
        if self._is_paused:
            self.resume_requested.emit()
            self.set_reminder_paused(False)
        else:
            self.pause_requested.emit()
            self.set_reminder_paused(True)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_requested.emit()

    def show(self):
        if QApplication.instance() is None:
            return
        self._tray_icon.show()

    def hide(self):
        self._tray_icon.hide()
        if self._menu is not None:
            self._menu.deleteLater()
            self._menu = None  # prevent dangling reference
