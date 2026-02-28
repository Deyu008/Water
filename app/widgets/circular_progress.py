from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QConicalGradient, QBrush, QFontMetrics

from app.core.theme import ThemeManager

class CircularProgress(QWidget):
    """
    Custom circular progress widget with smooth animation.
    
    Visual Design:
    - Outer ring: thin track (background, gray/light)
    - Inner ring: progress arc (gradient from #2196F3 to #64B5F6, blue spectrum)
    - Center: large text showing current/goal
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
        
        self._ring_width = 16
        
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
        
        # Calculate target progress (capped at 1.0 for the ring, but text shows real value)
        target = min(1.0, current_ml / self._goal_ml)
        
        # Animate
        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(target)
        self._anim.start()
        
        # If no animation is desired for text update (immediate), we could trigger update here
        # but the animation loop calls update() so text will refresh with the ring
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Setup geometry
        width = self.width()
        height = self.height()
        side = min(width, height)
        
        # Center point
        center_x = width / 2
        center_y = height / 2
        
        # Radius for the ring
        # Subtract ring width / 2 to keep stroke inside
        radius = (side - self._ring_width) / 2 - 10 
        
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 1. Draw track ring
        track_pen = QPen(self._track_color)
        track_pen.setWidth(self._ring_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)
        
        # 2. Draw progress arc
        # We want to start from top (90 degrees). Qt angles: 0 is 3 o'clock, increases counter-clockwise.
        # So top is 90. But drawArc takes startAngle in 1/16th of a degree.
        # However, for gradients it's easier to use QConicalGradient or just rotate the painter.
        
        # Let's use a simpler approach for the arc: drawArc with a gradient pen if possible, 
        # but standard QPen doesn't support gradient along the path easily in Qt5/6 without QBrush.
        # A solid color or simple gradient is fine. Let's try QConicalGradient for a nice effect.
        
        if self._progress > 0:
            # Create a conical gradient
            gradient = QConicalGradient(center_x, center_y, 90)
            gradient.setColorAt(0, self._progress_start_color)
            gradient.setColorAt(1, self._progress_end_color)
            
            # To make the gradient follow the arc, we can just use a solid color 
            # or a brush. But stroking a path with a gradient is tricky.
            # Simplified: Use the start color, maybe slight variation. 
            # Or actually, QPen can take a QBrush.
            
            pen_brush = QBrush(gradient)
            progress_pen = QPen(pen_brush, self._ring_width)
            progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(progress_pen)
            
            # Span angle is negative for clockwise
            # 360 * progress
            # Start at 90 deg (12 o'clock) -> 90 * 16
            start_angle = 90 * 16
            span_angle = -int(self._progress * 360 * 16)
            
            painter.drawArc(rect, start_angle, span_angle)

        # 3. Draw Center Text
        painter.setPen(self._text_color)

        # Current Value (Big)
        font_size = max(12, int(side * 0.16))
        font_big = QFont("Segoe UI", font_size, QFont.Weight.Bold)
        painter.setFont(font_big)

        fm_big = QFontMetrics(font_big)
        big_height = fm_big.height()

        # Goal Value (Small)
        font_size_small = max(8, int(side * 0.06))
        font_small = QFont("Segoe UI", font_size_small)
        fm_small = QFontMetrics(font_small)
        small_height = fm_small.height()

        text_gap = max(4, int(side * 0.02))
        text_block_height = big_height + text_gap + small_height
        text_top = center_y - text_block_height / 2

        text_rect_big = QRectF(center_x - radius, text_top, radius * 2, float(big_height))
        painter.drawText(text_rect_big, Qt.AlignmentFlag.AlignCenter, str(self._current_ml))

        painter.setPen(self._subtext_color)
        painter.setFont(font_small)

        text_rect_small = QRectF(
            center_x - radius,
            text_top + big_height + text_gap,
            radius * 2,
            float(small_height),
        )
        painter.drawText(text_rect_small, Qt.AlignmentFlag.AlignCenter, f"/ {self._goal_ml} ml")
