from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSequentialAnimationGroup,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QGraphicsOpacityEffect, QPushButton, QWidget


class ScreenShakeReminder(QWidget):
    """
    Fullscreen translucent overlay that shakes to grab attention.

    When shown, a semi-transparent dark overlay covers the entire screen,
    a centered water-drop icon + message pulses, and the overlay content
    shakes left/right for several cycles before settling.

    Signals:
        drink_clicked(int): user pressed the drink button
        dismissed(): overlay was dismissed (button or timeout)
    """

    drink_clicked = Signal(int)
    dismissed = Signal()

    def __init__(self, drink_amount: int = 200, parent=None):
        super().__init__(parent)
        self._drink_amount = max(1, int(drink_amount))
        self._is_dismissing = False

        # ── window setup ──
        self.setWindowFlags(
            Qt.Window
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        # ── shake offset (animated property) ──
        self._shake_offset = 0

        # ── opacity effect for fade-out ──
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        # ── buttons ──
        self._drink_btn = QPushButton(f"  Drink {self._drink_amount}ml  ", self)
        self._dismiss_btn = QPushButton("  Dismiss  ", self)

        self._drink_btn.setCursor(Qt.PointingHandCursor)
        self._dismiss_btn.setCursor(Qt.PointingHandCursor)

        self._drink_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: rgba(58, 134, 255, 230);"
            "  color: white; border: none; border-radius: 14px;"
            "  font-weight: 600; font-size: 16px; padding: 12px 28px;"
            "}"
            "QPushButton:hover { background-color: rgba(70, 145, 255, 245); }"
            "QPushButton:pressed { background-color: rgba(42, 116, 230, 255); }"
        )
        self._dismiss_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: rgba(255, 255, 255, 50);"
            "  color: rgba(255, 255, 255, 200); border: 1px solid rgba(255,255,255,60);"
            "  border-radius: 14px; font-size: 14px; padding: 10px 22px;"
            "}"
            "QPushButton:hover { background-color: rgba(255, 255, 255, 80); }"
            "QPushButton:pressed { background-color: rgba(255, 255, 255, 100); }"
        )

        self._drink_btn.clicked.connect(self._on_drink)
        self._dismiss_btn.clicked.connect(self._on_dismiss)

        # ── shake animation ──
        self._shake_group = QSequentialAnimationGroup(self)
        amplitude = 18
        single_duration = 60  # ms per half-shake
        cycles = 8

        for i in range(cycles):
            direction = amplitude if i % 2 == 0 else -amplitude
            anim = QPropertyAnimation(self, b"shake_offset_prop", self)
            anim.setDuration(single_duration)
            anim.setStartValue(0 if i == 0 else (-direction))
            anim.setEndValue(direction)
            anim.setEasingCurve(QEasingCurve.InOutSine)
            self._shake_group.addAnimation(anim)

        # settle back to 0
        settle = QPropertyAnimation(self, b"shake_offset_prop", self)
        settle.setDuration(120)
        settle.setStartValue(amplitude if cycles % 2 == 0 else -amplitude)
        settle.setEndValue(0)
        settle.setEasingCurve(QEasingCurve.OutCubic)
        self._shake_group.addAnimation(settle)

        # ── auto-dismiss timer ──
        self._auto_timer = QTimer(self)
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._on_dismiss)

        # ── fade out animation ──
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(300)
        self._fade_anim.setEasingCurve(QEasingCurve.InCubic)
        self._fade_anim.finished.connect(self._on_fade_finished)

    # ── animated property ──
    def _get_shake_offset(self):
        return self._shake_offset

    def _set_shake_offset(self, val):
        self._shake_offset = val
        self.update()

    shake_offset_prop = Property(int, _get_shake_offset, _set_shake_offset)

    # ── public API ──
    def show_shake(self):
        """Show fullscreen overlay with shake animation."""
        self._is_dismissing = False
        self._opacity_effect.setOpacity(1.0)
        self._shake_offset = 0

        # Cover entire primary screen
        screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.geometry()
        else:
            geo = QRect(0, 0, 1920, 1080)

        self.setGeometry(geo)
        self._layout_buttons()
        self.show()
        self.raise_()

        self._shake_group.stop()
        self._shake_group.start()

        self._auto_timer.start(10000)  # auto dismiss after 10s

    # ── painting ──
    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()

        # Semi-transparent backdrop
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 140))
        painter.drawRect(self.rect())

        # Center content area with shake offset
        cx = w // 2 + self._shake_offset
        cy = h // 2 - 40

        # Draw water drop icon
        self._paint_drop(painter, cx, cy - 60, scale=2.5)

        # Title
        title_font = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(255, 255, 255, 240))
        title_rect = QRect(cx - 200, cy + 10, 400, 50)
        painter.drawText(title_rect, Qt.AlignCenter, "Time to Drink Water!")

        # Subtitle
        sub_font = QFont("Segoe UI", 14)
        painter.setFont(sub_font)
        painter.setPen(QColor(200, 220, 255, 180))
        sub_rect = QRect(cx - 200, cy + 60, 400, 30)
        painter.drawText(sub_rect, Qt.AlignCenter, "Stay hydrated for better health")

    def _paint_drop(self, painter: QPainter, cx: int, cy: int, scale: float = 1.0):
        """Draw a water drop icon centered at (cx, cy)."""
        s = scale
        path = QPainterPath()
        path.moveTo(cx, cy - 20 * s)
        path.cubicTo(
            cx - 18 * s, cy - 2 * s,
            cx - 16 * s, cy + 12 * s,
            cx, cy + 22 * s,
        )
        path.cubicTo(
            cx + 16 * s, cy + 12 * s,
            cx + 18 * s, cy - 2 * s,
            cx, cy - 20 * s,
        )

        from PySide6.QtGui import QLinearGradient

        gradient = QLinearGradient(cx, cy - 20 * s, cx, cy + 22 * s)
        gradient.setColorAt(0.0, QColor(122, 214, 255, 255))
        gradient.setColorAt(1.0, QColor(57, 154, 245, 255))

        painter.setPen(QColor(255, 255, 255, 100))
        painter.setBrush(gradient)
        painter.drawPath(path)

        # highlight
        highlight = QPainterPath()
        highlight.addEllipse(QPoint(int(cx - 5 * s), int(cy - 4 * s)), int(5 * s), int(7 * s))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 90))
        painter.drawPath(highlight)

    # ── button layout ──
    def _layout_buttons(self):
        cx = self.width() // 2
        cy = self.height() // 2 + 80

        drink_w, drink_h = 180, 48
        dismiss_w, dismiss_h = 120, 42
        gap = 16

        total_w = drink_w + gap + dismiss_w
        start_x = cx - total_w // 2

        self._drink_btn.setGeometry(start_x, cy, drink_w, drink_h)
        self._dismiss_btn.setGeometry(start_x + drink_w + gap, cy + 3, dismiss_w, dismiss_h)

    # ── handlers ──
    def _on_drink(self):
        self.drink_clicked.emit(self._drink_amount)
        self._dismiss_fade()

    def _on_dismiss(self):
        self._dismiss_fade()

    def _dismiss_fade(self):
        if self._is_dismissing:
            return
        self._is_dismissing = True
        self._auto_timer.stop()
        self._shake_group.stop()

        self._fade_anim.stop()
        self._fade_anim.setStartValue(self._opacity_effect.opacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.start()

    def _on_fade_finished(self):
        if not self._is_dismissing:
            return
        self.hide()
        self.dismissed.emit()
        self._is_dismissing = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_buttons()
