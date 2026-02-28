from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QIcon

class TitleBarButton(QPushButton):
    """Custom button for title bar controls (Minimize, Maximize, Close)."""
    def __init__(self, text, parent=None, is_close=False):
        super().__init__(text, parent)
        self.setFixedSize(46, 40)
        self.is_close = is_close
        self.setStyleSheet("border: none; background: transparent; font-weight: bold;")
        
        # We'll use style sheets for hover effects for simplicity and performance
        if is_close:
            self.setStyleSheet("""
                QPushButton { border: none; background: transparent; color: #555; font-family: "Segoe UI", sans-serif; font-size: 14px; }
                QPushButton:hover { background-color: #E81123; color: white; }
                QPushButton:pressed { background-color: #F1707A; color: white; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton { border: none; background: transparent; color: #555; font-family: "Segoe UI", sans-serif; font-size: 14px; }
                QPushButton:hover { background-color: #E5E5E5; }
                QPushButton:pressed { background-color: #CACACB; }
            """)

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
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #FAFAFA; border-bottom: 1px solid #E0E0E0;")
        
        self._drag_pos = None
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. App Icon (drawn simply or unicode)
        self.icon_label = QLabel("💧") # Simple unicode for now
        self.icon_label.setStyleSheet("color: #2196F3; font-size: 16px; border: none; background: transparent;")
        self.icon_label.setFixedSize(24, 40)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # 2. Title
        self.title_label = QLabel("Water Reminder")
        self.title_label.setStyleSheet("font-family: 'Segoe UI', system-ui, sans-serif; font-size: 13px; font-weight: 600; color: #333; border: none; background: transparent;")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            if self.window().isMaximized():
                return
                
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.window().move(self.window().pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
