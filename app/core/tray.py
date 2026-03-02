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
        self._tray_icon.setToolTip("小范老师的饮水站")

        self._menu = QMenu()  # no parent: QMenu requires QWidget, TrayManager is QObject
        self._title_action = QAction("小范老师的饮水站", self)
        self._title_action.setEnabled(False)

        self._show_window_action = QAction("显示窗口", self)
        self._pause_resume_action = QAction("暂停提醒", self)
        self._quit_action = QAction("退出", self)

        self._quick_drink_menu = QMenu("快速喝水", self._menu)
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
        self._pause_resume_action.setText("继续提醒" if paused else "暂停提醒")

    def show_notification(self, title: str, message: str):
        self._tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )

    def _create_water_drop_icon(self) -> QIcon:
        """Create a high-quality water drop tray icon at 128px for HiDPI support."""
        size = 128
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Circular background with soft gradient
        from PySide6.QtGui import QRadialGradient
        bg = QRadialGradient(size * 0.42, size * 0.38, size * 0.52)
        bg.setColorAt(0.0, QColor("#82CCE6"))
        bg.setColorAt(0.6, QColor("#6BB8D9"))
        bg.setColorAt(1.0, QColor("#55A0C2"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        m = size * 0.03  # margin
        painter.drawEllipse(int(m), int(m), int(size - m * 2), int(size - m * 2))

        # Classic water drop using bezier curves (scaled to size)
        s = size / 64.0
        cx, cy = size / 2.0, size / 2.0
        tip_y = cy - 22 * s
        center_y = cy + 2 * s
        r = 12.5 * s
        k = 0.5522847498 * r  # bezier circle constant

        drop_path = QPainterPath()
        drop_path.moveTo(cx, tip_y)
        # Left curve: tip -> leftmost point of circle
        drop_path.cubicTo(
            cx - 2 * s, tip_y + 8 * s,
            cx - r - 1.5 * s, center_y - 4 * s,
            cx - r, center_y,
        )
        # Bottom arc: left -> bottom center
        drop_path.cubicTo(cx - r, center_y + k, cx - k, center_y + r, cx, center_y + r)
        # Bottom arc: bottom center -> right
        drop_path.cubicTo(cx + k, center_y + r, cx + r, center_y + k, cx + r, center_y)
        # Right curve: rightmost -> tip (mirror of left)
        drop_path.cubicTo(
            cx + r + 1.5 * s, center_y - 4 * s,
            cx + 2 * s, tip_y + 8 * s,
            cx, tip_y,
        )
        drop_path.closeSubpath()

        painter.setBrush(QColor(255, 255, 255, 245))
        painter.drawPath(drop_path)

        # Subtle specular highlight
        highlight = QPainterPath()
        from PySide6.QtCore import QPointF
        highlight.addEllipse(QPointF(cx - 4 * s, cy - 1 * s), 3 * s, 5 * s)
        painter.setBrush(QColor(255, 255, 255, 60))
        painter.drawPath(highlight)

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
