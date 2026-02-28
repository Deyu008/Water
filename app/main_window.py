from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QSizeGrip
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

from app.core.theme import ThemeManager
from app.widgets.title_bar import TitleBar
from app.widgets.sidebar import Sidebar

class MainWindow(QMainWindow):
    """
    Main application window with frameless design.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(750, 500)
        self.resize(900, 650)
        
        # Resize logic variables
        self._resize_margin = 5
        self._resizing = False
        self._resize_edge = None
        self._drag_pos = None
        
        self._build_ui()
        self._setup_connections()
        ThemeManager.signals.theme_applied.connect(lambda _: self.apply_theme())
        self.apply_theme()
        
        # Enable mouse tracking for resize cursor updates
        self.setMouseTracking(True)
        self.centralWidget().setMouseTracking(True)

    def _build_ui(self):
        # Main Container (Central Widget)
        # We need a container for the shadow effect and rounded corners
        self.container = QWidget()
        self.container.setObjectName("Container")
        self.setCentralWidget(self.container)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Title Bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # 2. Content Area (Sidebar + Stack)
        self.content_area = QWidget()
        self.content_layout = QHBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.content_layout.addWidget(self.sidebar)
        
        # Stacked Widget (Pages)
        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)
        
        # Placeholder Pages
        self._add_placeholder_page("Dashboard 💧", "")
        self._add_placeholder_page("History 📊", "")
        self._add_placeholder_page("Settings ⚙", "")
        
        self.main_layout.addWidget(self.content_area)
        
        # Size Grip (Bottom Right)
        # We add it to the main layout but strictly it should float or be in a status bar
        # For a clean frameless window, usually we just handle events.
        # But let's add a small invisible one for fallback
        self.size_grip = QSizeGrip(self.container)
        self.size_grip.setStyleSheet("width: 16px; height: 16px; margin: 0px; background: transparent;")
        # Position handled by layout or manual placement. 
        # In a VBox it's hard. Let's just rely on mouse events for resize.
        self.size_grip.hide() # Hide explicit grip, use mouse events

    def _add_placeholder_page(self, text, bg_color):
        page = QLabel(text)
        page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page.setStyleSheet(f"font-size: 24px; color: {ThemeManager.color('text_muted')};")
        self.stack.addWidget(page)

    def _setup_connections(self):
        # Sidebar navigation
        self.sidebar.page_changed.connect(self.stack.setCurrentIndex)
        
        # Title bar actions
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.apply_theme()

    def apply_theme(self):
        _ = ThemeManager.colors()
        if self.isMaximized():
            self.container.setObjectName("ContainerMaximized")
        else:
            self.container.setObjectName("Container")
        # Force style refresh
        self.container.style().unpolish(self.container)
        self.container.style().polish(self.container)
            
    # Resize Logic
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._hit_test(event.pos())
            if edge:
                self._resizing = True
                self._resize_edge = edge
                self._drag_pos = event.globalPosition().toPoint()
                event.accept()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.isMaximized():
            super().mouseMoveEvent(event)
            return

        if self._resizing:
            self._handle_resize(event.globalPosition().toPoint())
            event.accept()
        else:
            # Update cursor shape
            edge = self._hit_test(event.pos())
            if edge:
                self.setCursor(self._get_cursor(edge))
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self._resize_edge = None
            self.setCursor(Qt.CursorShape.ArrowCursor) # Reset cursor
        super().mouseReleaseEvent(event)

    def _hit_test(self, pos: QPoint):
        rect = self.rect()
        m = self._resize_margin
        
        left = pos.x() < m
        right = pos.x() > rect.width() - m
        top = pos.y() < m
        bottom = pos.y() > rect.height() - m
        
        if top and left: return 'top_left'
        if top and right: return 'top_right'
        if bottom and left: return 'bottom_left'
        if bottom and right: return 'bottom_right'
        if top: return 'top'
        if bottom: return 'bottom'
        if left: return 'left'
        if right: return 'right'
        return None

    def _get_cursor(self, edge):
        cursors = {
            'top_left': Qt.CursorShape.SizeFDiagCursor,
            'top_right': Qt.CursorShape.SizeBDiagCursor,
            'bottom_left': Qt.CursorShape.SizeBDiagCursor,
            'bottom_right': Qt.CursorShape.SizeFDiagCursor,
            'top': Qt.CursorShape.SizeVerCursor,
            'bottom': Qt.CursorShape.SizeVerCursor,
            'left': Qt.CursorShape.SizeHorCursor,
            'right': Qt.CursorShape.SizeHorCursor,
        }
        return cursors.get(edge, Qt.CursorShape.ArrowCursor)

    def _handle_resize(self, global_pos):
        if not self._resize_edge:
            return
        diff = global_pos - self._drag_pos
        geo = self.geometry()
        
        if 'right' in self._resize_edge:
            new_width = geo.width() + diff.x()
            if new_width >= self.minimumWidth():
                geo.setWidth(new_width)
        
        if 'bottom' in self._resize_edge:
            new_height = geo.height() + diff.y()
            if new_height >= self.minimumHeight():
                geo.setHeight(new_height)
                
        if 'left' in self._resize_edge:
            new_width = geo.width() - diff.x()
            if new_width >= self.minimumWidth():
                geo.setLeft(geo.left() + diff.x())
                
        if 'top' in self._resize_edge:
            new_height = geo.height() - diff.y()
            if new_height >= self.minimumHeight():
                geo.setTop(geo.top() + diff.y())
                
        self.setGeometry(geo)
        self._drag_pos = global_pos
