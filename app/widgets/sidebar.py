from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QButtonGroup, QFrame
from PySide6.QtCore import Qt, Signal, QSize, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QIcon, QBrush, QPen, QPalette

class SidebarButton(QPushButton):
    """
    Single navigation button in the sidebar.
    """
    
    def __init__(self, text, icon_str="•", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.icon_str = icon_str
        
        # Colors
        self.default_bg = QColor(240, 240, 240, 0) # Transparent
        self.hover_bg = QColor(230, 230, 230, 100) # Subtle grey
        self.selected_bg = QColor(220, 220, 220, 150) # Highlighted grey
        self.accent_color = QColor(33, 150, 243) # Blue accent
        self.text_color_normal = QColor(33, 33, 33)
        self.text_color_selected = QColor(33, 150, 243)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Determine state
        bg_color = self.default_bg
        is_selected = self.isChecked()
        is_hovered = self.underMouse()
        
        if is_selected:
            bg_color = self.selected_bg
        elif is_hovered:
            bg_color = self.hover_bg
            
        # Draw background (rounded rect)
        rect = self.rect().adjusted(4, 2, -4, -2)
        
        if is_selected or is_hovered:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(rect, 8, 8)
        # Draw Left Accent Border if selected
        if is_selected:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self.accent_color))
            # 3px wide, full height of the inner rect
            accent_rect = QRect(rect.left(), rect.top() + 6, 4, rect.height() - 12)
            painter.drawRoundedRect(accent_rect, 2, 2)
            
        # Draw Icon (Text-based for now)
        painter.setFont(QFont("Segoe UI Emoji", 14)) # Use emoji font for icon
        painter.setPen(self.accent_color if is_selected else QColor(100, 100, 100))
        icon_rect = QRect(rect.left() + 16, rect.top(), 24, rect.height())
        painter.drawText(icon_rect, Qt.AlignCenter, self.icon_str)
        
        # Draw Text
        font = QFont("Segoe UI", 10)
        if is_selected:
            font.setBold(True)
        painter.setFont(font)
        painter.setPen(self.text_color_selected if is_selected else self.text_color_normal)
        text_rect = QRect(rect.left() + 50, rect.top(), rect.width() - 60, rect.height())
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())


class Sidebar(QWidget):
    """
    Left sidebar navigation.
    """
    page_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #F0F0F0; border-right: 1px solid #E0E0E0;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 16)
        layout.setSpacing(8)
        
        # Branding
        branding_label = QLabel("   HydroTrack") # Simple spacing hack for alignment
        branding_label.setStyleSheet("font-family: 'Segoe UI', sans-serif; font-size: 18px; font-weight: 800; color: #2196F3; margin-left: 16px;")
        layout.addWidget(branding_label)
        
        layout.addSpacing(24)
        
        # Navigation Group
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.idClicked.connect(self.page_changed.emit)
        
        # Buttons
        self.btn_dashboard = SidebarButton("Dashboard", "💧")
        self.btn_history = SidebarButton("History", "📊")
        self.btn_settings = SidebarButton("Settings", "⚙")
        
        self._add_nav_button(self.btn_dashboard, 0)
        self._add_nav_button(self.btn_history, 1)
        self._add_nav_button(self.btn_settings, 2)
        
        # Default selection
        self.btn_dashboard.setChecked(True)
        
        layout.addStretch()
        
        # Version info
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #999; font-size: 10px;")
        layout.addWidget(version_label)
        
    def _add_nav_button(self, btn, id):
        self.layout().addWidget(btn)
        self.btn_group.addButton(btn, id)
