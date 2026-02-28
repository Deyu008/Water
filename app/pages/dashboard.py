from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QFrame, QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QColor

from app.widgets.circular_progress import CircularProgress
from app.core.theme import ThemeManager

class DashboardPage(QWidget):
    """
    Main dashboard page layout.
    """
    water_added = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._paused = False
        self._next_reminder_time = "--:--"
        self._last_records: list[dict[str, object]] = []
        self.quick_add_buttons: list[QPushButton] = []
        
        # Main Layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(40, 40, 40, 40)
        self._layout.setSpacing(20)
        
        # 1. Greeting Label
        self.lbl_greeting = QLabel("Welcome back! Stay hydrated 💧")
        self.lbl_greeting.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {ThemeManager.color('text_primary')};"
        )
        self._layout.addWidget(self.lbl_greeting)
        
        self._layout.addSpacing(10)
        
        # 2. Circular Progress (Centered)
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.circular_progress = CircularProgress()
        progress_layout.addWidget(self.circular_progress)
        
        self._layout.addWidget(progress_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self._layout.addSpacing(20)
        
        # 3. Quick Add Buttons
        # Use a grid or horizontal layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.quick_add_amounts = [100, 200, 300, 500]
        for amount in self.quick_add_amounts:
            btn = QPushButton(f"+{amount}ml")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(90, 45)
            btn.setStyleSheet(self._quick_add_button_stylesheet())
            btn.clicked.connect(lambda checked=False, a=amount: self.water_added.emit(a))
            btn_layout.addWidget(btn)
            self.quick_add_buttons.append(btn)
            
        self._layout.addLayout(btn_layout)
        
        self._layout.addSpacing(20)
        
        # 4. Status Bar (Next reminder)
        self.lbl_status = QLabel("Next reminder: --:--")
        self.lbl_status.setStyleSheet(
            f"color: {ThemeManager.color('text_muted')}; font-size: 14px;"
        )
        self._layout.addWidget(self.lbl_status, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self._layout.addSpacing(20)
        
        # 5. Recent Activity Header
        self.lbl_recent = QLabel("Recent Activity")
        self.lbl_recent.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {ThemeManager.color('text_primary')};"
        )
        self._layout.addWidget(self.lbl_recent)
        
        # 6. Recent Activity List (Scroll Area)
        # We'll use a QScrollArea containing a VBox
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.recent_container = QWidget()
        self.recent_container.setStyleSheet("background: transparent;")
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setSpacing(10)
        self.recent_layout.addStretch() # Push items to top
        
        self.scroll_area.setWidget(self.recent_container)
        self._layout.addWidget(self.scroll_area)

        ThemeManager.signals.theme_applied.connect(self.apply_theme)
        self.apply_theme()
        
    def update_progress(self, current_ml: int, goal_ml: int):
        self.circular_progress.set_value(current_ml, goal_ml)
        
    def update_recent(self, records: list[dict[str, object]]):
        self._last_records = list(records)

        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        
        # Add new items
        for record in self._last_records:
            # record: {'id': 1, 'time': '14:00', 'amount_ml': 200, 'source': 'button'}
            item_widget = QWidget()
            item_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {ThemeManager.color('bg_card')};
                    border-radius: 10px;
                    border: 1px solid {ThemeManager.color('border_light')};
                }}
            """)
            item_widget.setFixedHeight(50)
            
            row = QHBoxLayout(item_widget)
            row.setContentsMargins(15, 0, 15, 0)
            
            # Time
            time_text = str(record.get('time', '--:--'))
            lbl_time = QLabel(time_text)
            lbl_time.setStyleSheet(
                f"color: {ThemeManager.color('text_muted')}; font-size: 14px; border: none;"
            )
            row.addWidget(lbl_time)
            
            row.addStretch()
            
            # Source Icon/Text
            source = str(record.get('source', 'button'))
            source_text = "🔘" if source == 'button' else "🔔"
            lbl_source = QLabel(source_text)
            lbl_source.setStyleSheet("font-size: 12px; border: none;")
            # row.addWidget(lbl_source) # Optional
            
            # Amount
            raw_amount = record.get('amount_ml', 0)
            try:
                amount_ml = int(str(raw_amount))
            except (TypeError, ValueError):
                amount_ml = 0
            lbl_amount = QLabel(f"+{amount_ml} ml")
            lbl_amount.setStyleSheet(
                f"color: {ThemeManager.color('accent')}; font-weight: bold; font-size: 14px; border: none;"
            )
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

    def _quick_add_button_stylesheet(self) -> str:
        return f"""
            QPushButton {{
                background-color: {ThemeManager.color('btn_pill_bg')};
                color: {ThemeManager.color('btn_pill_text')};
                border: none;
                border-radius: 22px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.color('btn_pill_hover')};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.color('btn_pill_pressed')};
            }}
        """

    def apply_theme(self, *_args):
        self.lbl_greeting.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {ThemeManager.color('text_primary')};"
        )
        self.lbl_status.setStyleSheet(
            f"color: {ThemeManager.color('text_muted')}; font-size: 14px;"
        )
        self.lbl_recent.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {ThemeManager.color('text_primary')};"
        )

        button_style = self._quick_add_button_stylesheet()
        for btn in self.quick_add_buttons:
            btn.setStyleSheet(button_style)

        self.update_recent(self._last_records)
