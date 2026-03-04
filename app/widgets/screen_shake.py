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
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QApplication, QGraphicsOpacityEffect, QPushButton, QWidget

from app.core.theme import ThemeManager


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
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # ── shake offset (animated property) ──
        self._shake_offset = 0

        # ── cached colors ──
        self._overlay_bg = QColor()
        self._title_color = QColor()
        self._subtitle_color = QColor()
        self._drop_start = QColor()
        self._drop_end = QColor()
        self._drop_outline = QColor()
        self._drop_highlight = QColor()

        # ── cached drop pixmap ──
        self._drop_pixmap: QPixmap | None = None
        self._last_drop_size: tuple[int, int] = (0, 0)

        # ── cached fonts for paintEvent ──
        self._title_font = QFont(self.font().family(), 28, QFont.Weight.Bold)
        self._sub_font = QFont(self.font().family(), 14)
        # ── opacity effect for fade-out ──
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        # ── buttons ──
        self._drink_btn = QPushButton(f"  喝水 {self._drink_amount}ml  ", self)
        self._dismiss_btn = QPushButton("  稍后再说  ", self)

        self._drink_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)

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
            anim.setEasingCurve(QEasingCurve.Type.InOutSine)
            self._shake_group.addAnimation(anim)

        # settle back to 0
        settle = QPropertyAnimation(self, b"shake_offset_prop", self)
        settle.setDuration(120)
        settle.setStartValue(amplitude if cycles % 2 == 0 else -amplitude)
        settle.setEndValue(0)
        settle.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._shake_group.addAnimation(settle)

        # ── auto-dismiss timer ──
        self._auto_timer = QTimer(self)
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._on_dismiss)

        # ── fade out animation ──
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(300)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_anim.finished.connect(self._on_fade_finished)

        # ── apply theme ──
        ThemeManager.signals.theme_applied.connect(self._on_theme_applied)
        self.apply_theme()

    # ── animated property ──
    def _get_shake_offset(self):
        return self._shake_offset

    def _set_shake_offset(self, val):
        self._shake_offset = val
        self.update()

    shake_offset_prop = Property(int, _get_shake_offset, _set_shake_offset)

    # ── theme ──
    def _on_theme_applied(self, _theme_name: str):
        self.apply_theme()

    def apply_theme(self):
        self._overlay_bg = ThemeManager.qcolor("shake_overlay_bg")
        self._title_color = ThemeManager.qcolor("shake_title")
        self._subtitle_color = ThemeManager.qcolor("shake_subtitle")
        self._drop_start = ThemeManager.qcolor("shake_drop_start")
        self._drop_end = ThemeManager.qcolor("shake_drop_end")
        self._drop_outline = ThemeManager.qcolor("shake_drop_outline")
        self._drop_highlight = ThemeManager.qcolor("shake_drop_highlight")

        # Invalidate cached pixmap
        self._drop_pixmap = None

        self._drink_btn.setStyleSheet(
            "QPushButton {"
            f"  background-color: {ThemeManager.color('shake_btn_bg')};"
            "  color: white; border: none; border-radius: 14px;"
            "  font-weight: 600; font-size: 16px; padding: 12px 28px;"
            "}"
            f"QPushButton:hover {{ background-color: {ThemeManager.color('shake_btn_hover')}; }}"
            f"QPushButton:pressed {{ background-color: {ThemeManager.color('shake_btn_pressed')}; }}"
        )
        self._dismiss_btn.setStyleSheet(
            "QPushButton {"
            f"  background-color: {ThemeManager.color('shake_dismiss_bg')};"
            f"  color: {ThemeManager.color('shake_dismiss_text')};"
            f"  border: 1px solid {ThemeManager.color('shake_dismiss_border')};"
            "  border-radius: 14px; font-size: 14px; padding: 10px 22px;"
            "}"
            f"QPushButton:hover {{ background-color: {ThemeManager.color('shake_dismiss_hover')}; }}"
            f"QPushButton:pressed {{ background-color: {ThemeManager.color('shake_dismiss_pressed')}; }}"
        )
        self.update()

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()

        # Semi-transparent backdrop
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._overlay_bg)
        painter.drawRect(self.rect())

        # Center content area with shake offset
        cx = w // 2 + self._shake_offset
        cy = h // 2 - 40

        # Draw water drop icon (cached pixmap, DPR-aware)
        drop_pixmap = self._get_drop_pixmap(scale=2.5)
        dp_dpr = drop_pixmap.devicePixelRatio()
        lw = int(drop_pixmap.width() / dp_dpr)
        lh = int(drop_pixmap.height() / dp_dpr)
        painter.drawPixmap(
            cx - lw // 2,
            cy - 60 - lh // 2,
            drop_pixmap,
        )

        # Title
        painter.setFont(self._title_font)
        painter.setPen(self._title_color)
        title_rect = QRect(cx - 200, cy + 10, 400, 50)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "小范老师，该喝水啦~")

        # Subtitle
        painter.setFont(self._sub_font)
        painter.setPen(self._subtitle_color)
        sub_rect = QRect(cx - 200, cy + 60, 400, 30)
        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, "喝口水休息一下，照顾好自己哦")

    def _get_drop_pixmap(self, scale: float = 2.5) -> QPixmap:
        """Return cached QPixmap of the water drop icon."""
        s = scale
        # Account for device pixel ratio for crisp rendering on high-DPI
        dpr = self.devicePixelRatio() if self.devicePixelRatio() > 0 else 1.0
        pw_dev = int(40 * s * dpr)
        ph_dev = int(44 * s * dpr)
        size = (pw_dev, ph_dev)
        if self._drop_pixmap is not None and self._last_drop_size == size:
            return self._drop_pixmap

        pixmap = QPixmap(pw_dev, ph_dev)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # Paint in logical coordinates (pixmap handles DPR scaling)
        pw = int(40 * s)
        ph = int(44 * s)
        cx = pw // 2
        cy = ph // 2

        # Classic teardrop bezier shape
        tip_y = cy - 22 * s
        center_y = cy + 2 * s
        r = 12.5 * s
        k = 0.5522847498 * r

        path = QPainterPath()
        path.moveTo(cx, tip_y)
        path.cubicTo(cx - 2 * s, tip_y + 8 * s, cx - r - 1.5 * s, center_y - 4 * s, cx - r, center_y)
        path.cubicTo(cx - r, center_y + k, cx - k, center_y + r, cx, center_y + r)
        path.cubicTo(cx + k, center_y + r, cx + r, center_y + k, cx + r, center_y)
        path.cubicTo(cx + r + 1.5 * s, center_y - 4 * s, cx + 2 * s, tip_y + 8 * s, cx, tip_y)
        path.closeSubpath()

        gradient = QLinearGradient(cx, tip_y, cx, center_y + r)
        gradient.setColorAt(0.0, self._drop_start)
        gradient.setColorAt(1.0, self._drop_end)

        painter.setPen(self._drop_outline)
        painter.setBrush(gradient)
        painter.drawPath(path)

        # highlight
        highlight = QPainterPath()
        highlight.addEllipse(QPoint(int(cx - 5 * s), int(cy - 4 * s)), int(5 * s), int(7 * s))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._drop_highlight)
        painter.drawPath(highlight)

        painter.end()

        self._drop_pixmap = pixmap
        self._last_drop_size = size
        return pixmap

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
