from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRectF, QPointF
from PySide6.QtGui import (QPainter, QColor, QPen, QFont, QConicalGradient, QBrush,
                           QFontMetrics, QRadialGradient, QLinearGradient)

from app.core.theme import ThemeManager

class CircularProgress(QWidget):
    """
    Custom circular progress widget with liquid glass background disc.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(280, 280)
        self.resize(220, 220)

        self._progress = 0.0  # 0.0 to 1.0
        self._current_ml = 0
        self._goal_ml = 2000

        # Colors
        self._track_color = QColor()
        self._progress_start_color = QColor()
        self._progress_end_color = QColor()
        self._text_color = QColor()
        self._subtext_color = QColor()
        self._glass_fill = QColor()
        self._glass_border = QColor()
        self._glass_highlight = QColor()

        self._ring_width = 16

        # Cached paint objects (rebuilt on theme/size change)
        self._cached_side = 0
        self._track_pen = QPen()
        self._font_big = QFont()
        self._font_small = QFont()
        self._fm_big_height = 0
        self._fm_small_height = 0
        self._text_gap = 4

        # Animation
        self._anim = QPropertyAnimation(self, b"progress_value")
        self._anim.setDuration(800)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        ThemeManager.signals.theme_applied.connect(self._on_theme_applied)
        self.apply_theme()

    def _on_theme_applied(self, _theme_name: str):
        self.apply_theme()

    def apply_theme(self):
        self._track_color = ThemeManager.qcolor("progress_track")
        self._progress_start_color = ThemeManager.qcolor("progress_start")
        self._progress_end_color = ThemeManager.qcolor("progress_end")
        self._text_color = ThemeManager.qcolor("progress_text")
        self._subtext_color = ThemeManager.qcolor("progress_subtext")
        self._glass_fill = ThemeManager.qcolor("glass_fill")
        self._glass_border = ThemeManager.qcolor("glass_border")
        self._glass_highlight = ThemeManager.qcolor("glass_highlight")
        self._cached_side = 0  # force rebuild
        self.update()

    def get_progress_value(self):
        return self._progress

    def set_progress_value(self, val):
        self._progress = val
        self.update()

    progress_value = Property(float, get_progress_value, set_progress_value)

    def set_value(self, current_ml: int, goal_ml: int):
        self._current_ml = current_ml
        self._goal_ml = max(1, goal_ml)

        target = min(1.0, current_ml / self._goal_ml)

        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(target)
        self._anim.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._cached_side = 0  # force rebuild on next paint

    def _rebuild_cache(self, side: int):
        """Rebuild cached pens/fonts when size changes."""
        self._cached_side = side

        self._track_pen = QPen(self._track_color)
        self._track_pen.setWidth(self._ring_width)
        self._track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        font_size = max(12, int(side * 0.16))
        self._font_big = QFont(self.font().family(), font_size, QFont.Weight.Bold)
        self._fm_big_height = QFontMetrics(self._font_big).height()

        font_size_small = max(8, int(side * 0.06))
        self._font_small = QFont(self.font().family(), font_size_small)
        self._fm_small_height = QFontMetrics(self._font_small).height()

        self._text_gap = max(4, int(side * 0.02))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)

        # Rebuild cached objects if size changed
        if side != self._cached_side:
            self._rebuild_cache(side)

        center_x = width / 2
        center_y = height / 2
        radius = (side - self._ring_width) / 2 - 10
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # 0. Glass disc background behind progress ring
        glass_radius = radius + self._ring_width / 2 + 6
        glass_rect = QRectF(
            center_x - glass_radius, center_y - glass_radius,
            glass_radius * 2, glass_radius * 2,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._glass_fill))
        painter.drawEllipse(glass_rect)

        # Specular highlight on glass disc (top region)
        highlight_grad = QRadialGradient(
            center_x, center_y - glass_radius * 0.35,
            glass_radius * 1.1,
        )
        highlight_grad.setColorAt(0.0, self._glass_highlight)
        highlight_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight_grad))
        painter.drawEllipse(glass_rect)

        # Glass disc border
        glass_border_pen = QPen(self._glass_border, 1.0)
        painter.setPen(glass_border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(glass_rect)

        # 1. Draw track ring (use cached pen, update color in case theme changed)
        self._track_pen.setColor(self._track_color)
        painter.setPen(self._track_pen)
        painter.drawEllipse(rect)

        # 2. Draw progress arc with manually-drawn round endpoints
        if self._progress > 0:
            import math

            gradient = QConicalGradient(center_x, center_y, 90)
            gradient.setColorAt(0, self._progress_start_color)
            gradient.setColorAt(1, self._progress_end_color)

            # Draw arc with FlatCap to avoid built-in cap misalignment
            progress_pen = QPen(QBrush(gradient), self._ring_width)
            progress_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            painter.setPen(progress_pen)

            start_angle = 90 * 16
            span_angle = -int(self._progress * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)

            # Draw manual round caps at start and end points
            half_w = self._ring_width / 2.0
            # Start point: 12 o'clock (90 degrees)
            start_rad = math.radians(90)
            sx = center_x + radius * math.cos(start_rad)
            sy = center_y - radius * math.sin(start_rad)

            # End point: 90 - progress*360 degrees
            end_deg = 90 - self._progress * 360
            end_rad = math.radians(end_deg)
            ex = center_x + radius * math.cos(end_rad)
            ey = center_y - radius * math.sin(end_rad)

            painter.setPen(Qt.PenStyle.NoPen)
            # Start cap color (gradient at 0 = start color)
            painter.setBrush(QBrush(self._progress_start_color))
            painter.drawEllipse(QPointF(sx, sy), half_w, half_w)
            # End cap: sample the gradient color at progress fraction
            # For conical gradient starting at 90° going clockwise, the end is at progress fraction
            end_frac = self._progress
            # Interpolate between start and end colors
            r = int(self._progress_start_color.red() + (self._progress_end_color.red() - self._progress_start_color.red()) * end_frac)
            g = int(self._progress_start_color.green() + (self._progress_end_color.green() - self._progress_start_color.green()) * end_frac)
            b = int(self._progress_start_color.blue() + (self._progress_end_color.blue() - self._progress_start_color.blue()) * end_frac)
            end_cap_color = QColor(r, g, b)
            painter.setBrush(QBrush(end_cap_color))
            painter.drawEllipse(QPointF(ex, ey), half_w, half_w)

        # 3. Draw Center Text
        text_block_height = self._fm_big_height + self._text_gap + self._fm_small_height
        text_top = center_y - text_block_height / 2

        painter.setPen(self._text_color)
        painter.setFont(self._font_big)
        text_rect_big = QRectF(center_x - radius, text_top, radius * 2, float(self._fm_big_height))
        painter.drawText(text_rect_big, Qt.AlignmentFlag.AlignCenter, str(self._current_ml))

        painter.setPen(self._subtext_color)
        painter.setFont(self._font_small)
        text_rect_small = QRectF(
            center_x - radius,
            text_top + self._fm_big_height + self._text_gap,
            radius * 2,
            float(self._fm_small_height),
        )
        painter.drawText(text_rect_small, Qt.AlignmentFlag.AlignCenter, f"/ {self._goal_ml} ml")
