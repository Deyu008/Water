from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QLinearGradient, QColor, QBrush, QPainterPath

from app.core.theme import ThemeManager

class TitleBarButton(QPushButton):
    """Custom button for title bar controls — liquid glass hover effect."""
    def __init__(self, icon_kind, parent=None, is_close=False):
        super().__init__("", parent)
        self.setFixedSize(46, 40)
        self.is_close = is_close
        self.icon_kind = icon_kind
        self._icon_color = ThemeManager.qcolor("titlebar_btn_text")
        self.apply_theme()

    def apply_theme(self):
        text_color = ThemeManager.color("titlebar_btn_text")
        hover_bg = ThemeManager.color("titlebar_close_hover") if self.is_close else ThemeManager.color("titlebar_btn_hover")
        pressed_bg = ThemeManager.color("titlebar_close_pressed") if self.is_close else ThemeManager.color("titlebar_btn_pressed")
        glass_border = ThemeManager.color("glass_border")
        self._icon_color = ThemeManager.qcolor("titlebar_btn_text")

        self.setStyleSheet(
            f"""
                QPushButton {{
                    border: none;
                    background: transparent;
                    color: {text_color};
                    font-family: "Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Segoe UI", sans-serif;
                    font-size: 14px;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    border: 0.5px solid {glass_border};
                    color: {text_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                    color: {text_color};
                }}
            """
        )
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        icon_color = self._icon_color
        if not icon_color.isValid():
            return

        pen = QPen(icon_color)
        pen.setWidthF(1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0

        if self.icon_kind == "minimize":
            half = 6.0
            y = cy + 4.0
            painter.drawLine(int(cx - half), int(y), int(cx + half), int(y))
            return

        if self.icon_kind == "maximize":
            size = 12.0
            half = size / 2.0
            if self.window() is not None and self.window().isMaximized():
                back = QRectF(cx - half - 2.0, cy - half + 1.0, size, size)
                front = QRectF(cx - half + 1.5, cy - half - 2.0, size, size)
                painter.drawRect(back)
                painter.drawRect(front)
            else:
                rect = QRectF(cx - half, cy - half, size, size)
                painter.drawRect(rect)
            return

        if self.icon_kind == "close":
            half = 5.8
            painter.drawLine(int(cx - half), int(cy - half), int(cx + half), int(cy + half))
            painter.drawLine(int(cx + half), int(cy - half), int(cx - half), int(cy + half))

class TitleBar(QWidget):
    """
    Custom title bar for frameless window.
    """
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self._drag_pos = None
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. App Icon (drawn simply or unicode)
        self.icon_label = QLabel("💧") # Simple unicode for now
        self.icon_label.setFixedSize(24, 40)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # 2. Title
        self.title_label = QLabel("小范老师的饮水站")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # 3. Window Controls
        # Minimize (—)
        self.btn_minimize = TitleBarButton("minimize")
        self.btn_minimize.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.btn_minimize)

        # Maximize/Restore (□)
        self.btn_maximize = TitleBarButton("maximize")
        self.btn_maximize.clicked.connect(self.maximize_clicked.emit)
        layout.addWidget(self.btn_maximize)

        # Close (✕)
        self.btn_close = TitleBarButton("close", is_close=True)
        self.btn_close.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.btn_close)

        ThemeManager.signals.theme_applied.connect(lambda _: self.apply_theme())
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(
            f"background-color: {ThemeManager.color('titlebar_bg')}; "
            f"border-bottom: 1px solid {ThemeManager.color('titlebar_border')};"
        )
        self.icon_label.setStyleSheet(
            f"color: {ThemeManager.color('accent')}; "
            "font-size: 16px; border: none; background: transparent;"
        )
        self.title_label.setStyleSheet(
            f"font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC', 'Segoe UI', system-ui, sans-serif; font-size: 13px; "
            f"font-weight: 600; color: {ThemeManager.color('titlebar_text')}; "
            "border: none; background: transparent; letter-spacing: 0.5px;"
        )
        self.btn_minimize.apply_theme()
        self.btn_maximize.apply_theme()
        self.btn_close.apply_theme()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            if self.window().isMaximized():
                return
                
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.window().move(self.window().pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.maximize_clicked.emit()
