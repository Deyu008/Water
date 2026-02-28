from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

from app.core.theme import ThemeManager

class TitleBarButton(QPushButton):
    """Custom button for title bar controls (Minimize, Maximize, Close)."""
    def __init__(self, text, parent=None, is_close=False):
        super().__init__(text, parent)
        self.setFixedSize(46, 40)
        self.is_close = is_close
        self.apply_theme()

    def apply_theme(self):
        text_color = ThemeManager.color("titlebar_btn_text")
        hover_bg = ThemeManager.color("titlebar_close_hover") if self.is_close else ThemeManager.color("titlebar_btn_hover")
        pressed_bg = ThemeManager.color("titlebar_close_pressed") if self.is_close else ThemeManager.color("titlebar_btn_pressed")

        self.setStyleSheet(
            f"""
                QPushButton {{
                    border: none;
                    background: transparent;
                    color: {text_color};
                    font-family: "Segoe UI", sans-serif;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    color: {text_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                    color: {text_color};
                }}
            """
        )

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
        self.title_label = QLabel("Water Reminder")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # 3. Window Controls
        # Minimize (—)
        self.btn_minimize = TitleBarButton("─")
        self.btn_minimize.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.btn_minimize)
        
        # Maximize/Restore (□)
        self.btn_maximize = TitleBarButton("□") 
        self.btn_maximize.clicked.connect(self.maximize_clicked.emit)
        layout.addWidget(self.btn_maximize)
        
        # Close (✕)
        self.btn_close = TitleBarButton("✕", is_close=True)
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
            f"font-family: 'Segoe UI', system-ui, sans-serif; font-size: 13px; "
            f"font-weight: 600; color: {ThemeManager.color('titlebar_text')}; "
            "border: none; background: transparent;"
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
