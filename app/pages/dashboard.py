from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QFrame, QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QColor

from app.widgets.circular_progress import CircularProgress

class DashboardPage(QWidget):
    """
    Main dashboard page layout.
    """
    water_added = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._paused = False
        self._next_reminder_time = "--:--"
        
        # Main Layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(40, 40, 40, 40)
        self._layout.setSpacing(20)
        
        # 1. Greeting Label
        self.lbl_greeting = QLabel("Welcome back! Stay hydrated 💧")
        self.lbl_greeting.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        self._layout.addWidget(self.lbl_greeting)
        
        self._layout.addSpacing(10)
        
        # 2. Circular Progress (Centered)
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.circular_progress = CircularProgress()
        progress_layout.addWidget(self.circular_progress)
        
        self._layout.addWidget(progress_container, alignment=Qt.AlignCenter)
        
        self._layout.addSpacing(20)
        
        # 3. Quick Add Buttons
        # Use a grid or horizontal layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.quick_add_amounts = [100, 200, 300, 500]
        for amount in self.quick_add_amounts:
            btn = QPushButton(f"+{amount}ml")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(90, 45)
            # Styling: Pill shape, blue accent
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E3F2FD;
                    color: #1976D2;
                    border: none;
                    border-radius: 22px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #BBDEFB;
                }
                QPushButton:pressed {
                    background-color: #90CAF9;
                }
            """)
            btn.clicked.connect(lambda checked=False, a=amount: self.water_added.emit(a))
            btn_layout.addWidget(btn)
            
        self._layout.addLayout(btn_layout)
        
        self._layout.addSpacing(20)
        
        # 4. Status Bar (Next reminder)
        self.lbl_status = QLabel("Next reminder: --:--")
        self.lbl_status.setStyleSheet("color: #757575; font-size: 14px;")
        self._layout.addWidget(self.lbl_status, alignment=Qt.AlignCenter)
        
        self._layout.addSpacing(20)
        
        # 5. Recent Activity Header
        lbl_recent = QLabel("Recent Activity")
        lbl_recent.setStyleSheet("font-size: 18px; font-weight: 600; color: #333;")
        self._layout.addWidget(lbl_recent)
        
        # 6. Recent Activity List (Scroll Area)
        # We'll use a QScrollArea containing a VBox
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.recent_container = QWidget()
        self.recent_container.setStyleSheet("background: transparent;")
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setSpacing(10)
        self.recent_layout.addStretch() # Push items to top
        
        self.scroll_area.setWidget(self.recent_container)
        self._layout.addWidget(self.scroll_area)
        
    def update_progress(self, current_ml: int, goal_ml: int):
        self.circular_progress.set_value(current_ml, goal_ml)
        
    def update_recent(self, records: list[dict]):
        # Clear existing items (except the stretch at the end)
        # The safest way is to remove all widgets
        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                # We want to keep the stretch? No, let's just re-add it.
                # But takeAt removes it from layout.
                pass
        
        # Add new items
        for record in records:
            # record: {'id': 1, 'time': '14:00', 'amount_ml': 200, 'source': 'button'}
            item_widget = QWidget()
            item_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 10px;
                    border: 1px solid #EEEEEE;
                }
            """)
            item_widget.setFixedHeight(50)
            
            row = QHBoxLayout(item_widget)
            row.setContentsMargins(15, 0, 15, 0)
            
            # Time
            lbl_time = QLabel(record.get('time', '--:--'))
            lbl_time.setStyleSheet("color: #757575; font-size: 14px; border: none;")
            row.addWidget(lbl_time)
            
            row.addStretch()
            
            # Source Icon/Text
            source = record.get('source', 'button')
            source_text = "🔘" if source == 'button' else "🔔"
            lbl_source = QLabel(source_text)
            lbl_source.setStyleSheet("font-size: 12px; border: none;")
            # row.addWidget(lbl_source) # Optional
            
            # Amount
            lbl_amount = QLabel(f"+{record.get('amount_ml', 0)} ml")
            lbl_amount.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 14px; border: none;")
            row.addWidget(lbl_amount)
            
            self.recent_layout.addWidget(item_widget)
            
        self.recent_layout.addStretch()
        
    def update_next_reminder(self, time_str: str):
        self._next_reminder_time = time_str
        self._update_status_label()
        
    def set_reminder_paused(self, paused: bool):
        self._paused = paused
        self._update_status_label()
        
    def _update_status_label(self):
        text = f"Next reminder: {self._next_reminder_time}"
        if self._paused:
            text += " [Paused]"
        self.lbl_status.setText(text)
