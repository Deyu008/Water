import math

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QButtonGroup
from PySide6.QtCore import Qt, Signal, QRect, QRectF, QPointF, QEvent
from PySide6.QtGui import (QPainter, QColor, QFont, QBrush, QPen, QPainterPath,
                           QLinearGradient)

from app.core.theme import ThemeManager


class SidebarButton(QPushButton):
    """
    Single navigation button in the sidebar — liquid glass style.
    """
    
    def __init__(self, text, icon_str="water", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_str = icon_str

        # Neutralize qt-material global QPushButton styling (ALL pseudo-states)
        self.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; padding: 0; margin: 0; }
            QPushButton:hover { background-color: transparent; border: none; }
            QPushButton:pressed { background-color: transparent; border: none; }
            QPushButton:checked { background-color: transparent; border: none; }
            QPushButton:checked:hover { background-color: transparent; border: none; }
            QPushButton:flat { background-color: transparent; border: none; }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # Colors
        self.default_bg = QColor(0, 0, 0, 0)  # Transparent
        self.hover_bg = QColor()
        self.selected_bg = QColor()
        self.accent_color = QColor()
        self.text_color_normal = QColor()
        self.text_color_selected = QColor()
        self.icon_color_default = QColor()
        self._glass_border = QColor()
        self._glass_highlight = QColor()
        self.apply_theme()

    def apply_theme(self):
        self.hover_bg = ThemeManager.qcolor("sidebar_hover")
        self.selected_bg = ThemeManager.qcolor("sidebar_selected")
        self.accent_color = ThemeManager.qcolor("accent")
        self.text_color_normal = ThemeManager.qcolor("sidebar_text")
        self.text_color_selected = ThemeManager.qcolor("sidebar_text_selected")
        self.icon_color_default = ThemeManager.qcolor("sidebar_icon_default")
        self._glass_border = ThemeManager.qcolor("glass_border")
        self._glass_highlight = ThemeManager.qcolor("glass_highlight")
        self.update()

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def _draw_water_icon(self, painter: QPainter, icon_rect: QRect, color: QColor):
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))

        cx = icon_rect.center().x()
        top = float(icon_rect.top() + 3)
        bottom = float(icon_rect.bottom() - 2)
        left = float(cx - icon_rect.width() * 0.24)
        right = float(cx + icon_rect.width() * 0.24)
        shoulder_y = float(icon_rect.top() + icon_rect.height() * 0.58)

        drop_path = QPainterPath()
        drop_path.moveTo(QPointF(cx, top))
        drop_path.cubicTo(QPointF(left - 2, shoulder_y - 5), QPointF(left - 1, shoulder_y + 3), QPointF(cx, bottom))
        drop_path.cubicTo(QPointF(right + 1, shoulder_y + 3), QPointF(right + 2, shoulder_y - 5), QPointF(cx, top))
        drop_path.closeSubpath()
        painter.drawPath(drop_path)
        painter.restore()

    def _draw_chart_icon(self, painter: QPainter, icon_rect: QRect, color: QColor):
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))

        bar_width = max(3, int(icon_rect.width() * 0.18))
        gap = max(2, int(icon_rect.width() * 0.1))
        total_width = bar_width * 3 + gap * 2
        start_x = icon_rect.center().x() - total_width // 2
        baseline = icon_rect.bottom() - 3
        heights = [int(icon_rect.height() * 0.38), int(icon_rect.height() * 0.62), int(icon_rect.height() * 0.82)]

        for idx, height in enumerate(heights):
            x = start_x + idx * (bar_width + gap)
            y = baseline - height
            painter.drawRoundedRect(QRect(x, y, bar_width, height), 1.6, 1.6)

        painter.restore()

    def _draw_gear_icon(self, painter: QPainter, icon_rect: QRect, color: QColor):
        painter.save()
        center = icon_rect.center()
        outer_r = max(4.5, icon_rect.width() * 0.27)
        inner_r = max(2.0, icon_rect.width() * 0.11)
        tooth_start = outer_r + 0.8
        tooth_end = outer_r + 2.6

        pen = QPen(color)
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        for idx in range(8):
            angle = (math.pi / 4.0) * idx
            sx = center.x() + math.cos(angle) * tooth_start
            sy = center.y() - math.sin(angle) * tooth_start
            ex = center.x() + math.cos(angle) * tooth_end
            ey = center.y() - math.sin(angle) * tooth_end
            painter.drawLine(QPointF(sx, sy), QPointF(ex, ey))

        painter.drawEllipse(QPointF(center.x(), center.y()), outer_r, outer_r)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(center.x(), center.y()), inner_r, inner_r)
        painter.restore()

    def _draw_icon(self, painter: QPainter, icon_rect: QRect, is_selected: bool):
        icon_color = self.accent_color if is_selected else self.icon_color_default

        if self.icon_str == "water":
            self._draw_water_icon(painter, icon_rect, icon_color)
            return

        if self.icon_str == "chart":
            self._draw_chart_icon(painter, icon_rect, icon_color)
            return

        self._draw_gear_icon(painter, icon_rect, icon_color)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine state
        is_selected = self.isChecked()
        is_hovered = self.underMouse()
        
        # Draw glass background (rounded rect)
        rect = self.rect().adjusted(4, 2, -4, -2)
        rectf = QRectF(rect)
        glass_radius = 12.0
        
        if is_selected or is_hovered:
            bg_color = self.selected_bg if is_selected else self.hover_bg

            # Glass fill
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bg_color))
            path = QPainterPath()
            path.addRoundedRect(rectf, glass_radius, glass_radius)
            painter.drawPath(path)

            # Glass specular highlight (top edge)
            highlight_grad = QLinearGradient(rectf.topLeft(), QPointF(rectf.left(), rectf.top() + rectf.height() * 0.5))
            highlight_grad.setColorAt(0.0, self._glass_highlight)
            highlight_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(highlight_grad))
            highlight_rect = QRectF(rectf.left(), rectf.top(), rectf.width(), rectf.height() * 0.5)
            highlight_path = QPainterPath()
            highlight_path.addRoundedRect(highlight_rect, glass_radius, glass_radius)
            painter.drawPath(path & highlight_path)

            # Glass border
            pen = QPen(self._glass_border, 0.8)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rectf, glass_radius, glass_radius)

        # Draw Left Accent Border if selected (liquid accent pill)
        if is_selected:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.accent_color))
            accent_rect = QRect(rect.left(), rect.top() + 6, 4, rect.height() - 12)
            painter.drawRoundedRect(accent_rect, 2, 2)
            
        # Draw Icon
        icon_rect = QRect(rect.left() + 16, rect.top() + (rect.height() - 24) // 2, 24, 24)
        self._draw_icon(painter, icon_rect, is_selected)
        
        # Draw Text
        font = QFont(self.font().family(), 10)
        if is_selected:
            font.setBold(True)
        painter.setFont(font)
        painter.setPen(self.text_color_selected if is_selected else self.text_color_normal)
        text_rect = QRect(rect.left() + 50, rect.top(), rect.width() - 60, rect.height())
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


class Sidebar(QWidget):
    """
    Left sidebar navigation.
    """
    page_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("Sidebar")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 20, 0, 16)
        self._layout.setSpacing(8)

        # Branding
        self.branding_label = QLabel("小范老师的饮水站")
        self.branding_label.setContentsMargins(20, 0, 0, 0)
        self._layout.addWidget(self.branding_label)

        self._layout.addSpacing(24)
        
        # Navigation Group
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.idClicked.connect(self.page_changed.emit)

        # Buttons
        self.btn_dashboard = SidebarButton("饮水台", "water")
        self.btn_history = SidebarButton("小账本", "chart")
        self.btn_settings = SidebarButton("设置", "gear")
        
        self._add_nav_button(self.btn_dashboard, 0)
        self._add_nav_button(self.btn_history, 1)
        self._add_nav_button(self.btn_settings, 2)
        
        # Default selection
        self.btn_dashboard.setChecked(True)
        
        self._layout.addStretch()

        # Version info
        self.version_label = QLabel("v1.0.0")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.version_label)

        ThemeManager.signals.theme_applied.connect(self._on_theme_applied)
        self.apply_theme()
        
    def _add_nav_button(self, btn, id):
        self._layout.addWidget(btn)
        self.btn_group.addButton(btn, id)

    def _on_theme_applied(self, _theme_name: str):
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(
            f"background-color: {ThemeManager.color('sidebar_bg')};"
            f"border-right: 1px solid {ThemeManager.color('sidebar_border')};"
        )
        self.branding_label.setStyleSheet(
            f"font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC', 'Segoe UI', sans-serif;"
            f"font-size: 18px; font-weight: 800; color: {ThemeManager.color('accent')};"
            f"background: transparent;"
        )
        self.version_label.setStyleSheet(
            f"color: {ThemeManager.color('sidebar_version')}; font-size: 10px; background: transparent;"
        )

        for btn in (self.btn_dashboard, self.btn_history, self.btn_settings):
            btn.apply_theme()
