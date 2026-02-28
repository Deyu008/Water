from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QPushButton, QGraphicsDropShadowEffect, QWidget

from app.core.theme import ThemeManager


class ToastReminder(QWidget):
    drink_clicked = Signal(int)
    dismissed = Signal()

    def __init__(self, today_total_ml: int = 0, drink_amount: int = 200, parent=None):
        super().__init__(parent)

        self._today_total_ml = max(0, int(today_total_ml))
        self._drink_amount = max(1, int(drink_amount))
        self._title = "Time to Drink Water!"
        self._message = f"Stay hydrated! You've had {self._today_total_ml}ml of water today."
        self._margin = 20
        self._is_dismissing = False

        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        self._drink_btn = QPushButton(f"Drink {self._drink_amount}ml", self)
        self._later_btn = QPushButton("Later", self)
        self._drink_btn.clicked.connect(self._on_drink_clicked)
        self._later_btn.clicked.connect(self._dismiss)

        self._auto_timer = QTimer(self)
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._dismiss)

        self._slide_anim = QPropertyAnimation(self, b"geometry", self)
        self._slide_anim.setDuration(300)
        self._slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_anim.setDuration(220)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_anim.finished.connect(self._on_fade_finished)

        self._update_size_and_layout()
        ThemeManager.signals.theme_applied.connect(self.apply_theme)
        self.apply_theme()

    def apply_theme(self, *_args):
        self._drink_btn.setStyleSheet(
            "QPushButton {"
            f"background-color: {ThemeManager.color('toast_btn_bg')};"
            f"color: {ThemeManager.color('text_on_accent')};"
            "border: none;"
            "border-radius: 10px;"
            "font-weight: 600;"
            "padding: 8px 14px;"
            "}"
            f"QPushButton:hover {{ background-color: {ThemeManager.color('toast_btn_hover')}; }}"
            f"QPushButton:pressed {{ background-color: {ThemeManager.color('toast_btn_pressed')}; }}"
        )
        self._later_btn.setStyleSheet(
            "QPushButton {"
            f"background-color: {ThemeManager.color('toast_later_bg')};"
            f"color: {ThemeManager.color('toast_later_text')};"
            f"border: 1px solid {ThemeManager.color('toast_later_border')};"
            "border-radius: 10px;"
            "padding: 8px 12px;"
            "}"
            f"QPushButton:hover {{ background-color: {ThemeManager.color('toast_later_hover')}; }}"
            f"QPushButton:pressed {{ background-color: {ThemeManager.color('toast_later_pressed')}; }}"
        )
        self.update()

    def show_reminder(self):
        self._is_dismissing = False
        self.setWindowOpacity(1.0)

        final_rect = self._final_geometry()
        start_rect = QRect(final_rect)
        start_rect.moveLeft(final_rect.left() + self.width() + 24)

        self._slide_anim.stop()
        self._fade_anim.stop()

        self.setGeometry(start_rect)
        self.show()
        self.raise_()

        self._slide_anim.setStartValue(start_rect)
        self._slide_anim.setEndValue(final_rect)
        self._slide_anim.start()

        self._auto_timer.start(8000)

    def _dismiss(self):
        if self._is_dismissing:
            return
        self._is_dismissing = True
        self._auto_timer.stop()

        current_rect = self.geometry()
        end_rect = QRect(current_rect)
        end_rect.moveTopRight(current_rect.topRight() + QPoint(24, 0))

        self._slide_anim.stop()
        self._slide_anim.setDuration(220)
        self._slide_anim.setStartValue(current_rect)
        self._slide_anim.setEndValue(end_rect)
        self._slide_anim.start()

        self._fade_anim.stop()
        self._fade_anim.setStartValue(self.windowOpacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.start()

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect().adjusted(8, 8, -8, -8)
        radius = 18

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, ThemeManager.qcolor("toast_bg_start"))
        gradient.setColorAt(1.0, ThemeManager.qcolor("toast_bg_end"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, radius, radius)

        border_pen = QPen(ThemeManager.qcolor("toast_border"), 1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), radius, radius)

        icon_center = QPoint(rect.left() + 38, rect.top() + 38)
        self._paint_drop_icon(painter, icon_center)

        text_left = rect.left() + 72
        text_right = rect.right() - 18
        title_rect = QRect(text_left, rect.top() + 18, text_right - text_left, 28)
        body_rect = QRect(text_left, rect.top() + 46, text_right - text_left, 52)

        title_font = QFont(self.font())
        title_font.setPointSize(14)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(ThemeManager.qcolor("toast_title"))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._title)

        body_font = QFont(self.font())
        body_font.setPointSize(10)
        painter.setFont(body_font)
        painter.setPen(ThemeManager.qcolor("toast_body"))
        painter.drawText(
            body_rect,
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            self._message,
        )

    def _on_drink_clicked(self):
        self.drink_clicked.emit(self._drink_amount)
        self._dismiss()

    def _on_fade_finished(self):
        if not self._is_dismissing:
            return
        self.hide()
        self.dismissed.emit()
        self._is_dismissing = False

    def _update_size_and_layout(self):
        width = 360
        padding = 18
        icon_block = 54
        text_width = width - padding * 2 - icon_block

        title_font = QFont(self.font())
        title_font.setPointSize(14)
        title_font.setBold(True)
        body_font = QFont(self.font())
        body_font.setPointSize(10)

        title_h = QFontMetrics(title_font).height()
        body_rect = QFontMetrics(body_font).boundingRect(
            QRect(0, 0, text_width, 1000), Qt.TextFlag.TextWordWrap, self._message
        )
        text_bottom = padding + title_h + 8 + body_rect.height()

        btn_h = 34
        btn_top = max(82, text_bottom + 10)
        height = max(120, btn_top + btn_h + padding)

        self.setFixedSize(width, height)

        right = width - padding
        later_w = 78
        drink_w = 128
        gap = 10
        self._later_btn.setGeometry(right - later_w, btn_top, later_w, btn_h)
        self._drink_btn.setGeometry(right - later_w - gap - drink_w, btn_top, drink_w, btn_h)

    def _final_geometry(self) -> QRect:
        screen = self.screen() or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else QRect(0, 0, 1280, 720)
        x = available.x() + available.width() - self.width() - self._margin
        y = available.y() + self._margin
        return QRect(x, y, self.width(), self.height())

    def _paint_drop_icon(self, painter: QPainter, center: QPoint):
        path = QPainterPath()
        top = QPoint(center.x(), center.y() - 16)
        left = QPoint(center.x() - 12, center.y() + 6)
        right = QPoint(center.x() + 12, center.y() + 6)
        bottom = QPoint(center.x(), center.y() + 18)

        path.moveTo(top)
        path.cubicTo(center.x() - 16, center.y() - 4, center.x() - 14, center.y() + 10, bottom.x(), bottom.y())
        path.cubicTo(center.x() + 14, center.y() + 10, center.x() + 16, center.y() - 4, right.x(), right.y())
        path.cubicTo(center.x() + 8, center.y() - 6, center.x() + 2, center.y() - 12, top.x(), top.y())

        gradient = QLinearGradient(top, bottom)
        gradient.setColorAt(0.0, QColor(122, 214, 255, 255))
        gradient.setColorAt(1.0, QColor(57, 154, 245, 255))

        painter.setPen(QPen(QColor(255, 255, 255, 140), 1))
        painter.setBrush(gradient)
        painter.drawPath(path)

        highlight = QPainterPath()
        highlight.addEllipse(QPoint(center.x() - 4, center.y() - 1), 4, 6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 110))
        painter.drawPath(highlight)
