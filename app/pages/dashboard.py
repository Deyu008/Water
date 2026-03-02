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
        self._layout.setContentsMargins(24, 20, 24, 16)
        self._layout.setSpacing(12)
        
        # 1. Greeting Label
        self.lbl_greeting = QLabel(self._get_greeting())
        self.lbl_greeting.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {ThemeManager.color('text_primary')}; padding: 4px 0;"
        )
        self._layout.addWidget(self.lbl_greeting)

        self.lbl_sub_greeting = QLabel("今天也要记得多喝水哦~ 💧")
        self.lbl_sub_greeting.setStyleSheet(
            f"font-size: 14px; color: {ThemeManager.color('text_muted')}; padding: 0 0 4px 0;"
        )
        self._layout.addWidget(self.lbl_sub_greeting)
        
        self._layout.addSpacing(4)
        
        # 2. Circular Progress (Centered)
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.circular_progress = CircularProgress()
        progress_layout.addWidget(self.circular_progress)
        
        self._layout.addWidget(progress_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self._layout.addSpacing(8)
        
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
        
        self._layout.addSpacing(8)
        
        # 4. Status Bar (Next reminder)
        self.lbl_status = QLabel("下次提醒：--:--")
        self.lbl_status.setStyleSheet(
            f"color: {ThemeManager.color('text_muted')}; font-size: 14px;"
        )
        self._layout.addWidget(self.lbl_status, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self._layout.addSpacing(8)
        
        # 5. Recent Activity Header
        self.lbl_recent = QLabel("最近记录")
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
        self.recent_layout.setContentsMargins(4, 4, 4, 4)
        self.recent_layout.setSpacing(10)
        self.recent_layout.addStretch() # Push items to top
        
        self.scroll_area.setWidget(self.recent_container)
        self._layout.addWidget(self.scroll_area)

        ThemeManager.signals.theme_applied.connect(self.apply_theme)
        self.apply_theme()
        
    def update_progress(self, current_ml: int, goal_ml: int):
        self.lbl_greeting.setText(self._get_greeting())
        self.circular_progress.set_value(current_ml, goal_ml)

    @staticmethod
    def _get_greeting() -> str:
        import datetime
        hour = datetime.datetime.now().hour
        if 5 <= hour < 9:
            greeting = "小范老师，早上好呀！"
        elif 9 <= hour < 12:
            greeting = "小范老师，上午好呀！"
        elif 12 <= hour < 14:
            greeting = "小范老师，中午好呀！"
        elif 14 <= hour < 18:
            greeting = "小范老师，下午好呀！"
        elif 18 <= hour < 22:
            greeting = "小范老师，晚上好呀！"
        else:
            greeting = "小范老师，夜深了！快去睡觉！"
        return greeting
        
    def update_recent(self, records: list[dict[str, object]]):
        self._last_records = list(records)
        num_records = len(self._last_records)

        # Reuse existing item widgets; create new ones only if needed
        # Count existing widgets (exclude the trailing stretch)
        existing_count = 0
        for i in range(self.recent_layout.count()):
            if self.recent_layout.itemAt(i).widget() is not None:
                existing_count += 1

        # Remove excess widgets
        while existing_count > num_records:
            for i in range(self.recent_layout.count() - 1, -1, -1):
                item = self.recent_layout.itemAt(i)
                if item.widget() is not None:
                    w = item.widget()
                    self.recent_layout.removeWidget(w)
                    w.deleteLater()
                    existing_count -= 1
                    break

        # Remove trailing stretch (we'll re-add it at the end)
        while self.recent_layout.count() > 0:
            item = self.recent_layout.itemAt(self.recent_layout.count() - 1)
            if item.widget() is None and item.layout() is None:
                self.recent_layout.takeAt(self.recent_layout.count() - 1)
            else:
                break

        # Update existing / create new widgets
        for idx, record in enumerate(self._last_records):
            time_text = str(record.get('time', '--:--'))
            raw_amount = record.get('amount_ml', 0)
            try:
                amount_ml = int(str(raw_amount))
            except (TypeError, ValueError):
                amount_ml = 0

            if idx < existing_count:
                # Reuse existing widget
                item_widget = self.recent_layout.itemAt(idx).widget()
                if item_widget is not None:
                    self._update_recent_item(item_widget, time_text, amount_ml)
            else:
                # Create new widget
                item_widget = self._create_recent_item(time_text, amount_ml)
                self.recent_layout.addWidget(item_widget)

        self.recent_layout.addStretch()

    def _create_recent_item(self, time_text: str, amount_ml: int) -> QWidget:
        item_widget = QWidget()
        item_widget.setStyleSheet(self._recent_item_stylesheet())
        item_widget.setFixedHeight(50)

        row = QHBoxLayout(item_widget)
        row.setContentsMargins(15, 0, 15, 0)

        lbl_time = QLabel(time_text)
        lbl_time.setObjectName("recent_time")
        lbl_time.setStyleSheet(
            f"color: {ThemeManager.color('text_muted')}; font-size: 14px; border: none;"
        )
        row.addWidget(lbl_time)
        row.addStretch()

        lbl_amount = QLabel(f"+{amount_ml} ml")
        lbl_amount.setObjectName("recent_amount")
        lbl_amount.setStyleSheet(
            f"color: {ThemeManager.color('accent')}; font-weight: bold; font-size: 14px; border: none;"
        )
        row.addWidget(lbl_amount)
        return item_widget

    def _update_recent_item(self, item_widget: QWidget, time_text: str, amount_ml: int):
        item_widget.setStyleSheet(self._recent_item_stylesheet())
        lbl_time = item_widget.findChild(QLabel, "recent_time")
        if lbl_time is not None:
            lbl_time.setText(time_text)
            lbl_time.setStyleSheet(
                f"color: {ThemeManager.color('text_muted')}; font-size: 14px; border: none;"
            )
        lbl_amount = item_widget.findChild(QLabel, "recent_amount")
        if lbl_amount is not None:
            lbl_amount.setText(f"+{amount_ml} ml")
            lbl_amount.setStyleSheet(
                f"color: {ThemeManager.color('accent')}; font-weight: bold; font-size: 14px; border: none;"
            )
        
    def update_next_reminder(self, time_str: str):
        self._next_reminder_time = time_str
        self._update_status_label()
        
    def set_reminder_paused(self, paused: bool):
        self._paused = paused
        self._update_status_label()
        
    def _update_status_label(self):
        text = f"下次提醒：{self._next_reminder_time}"
        if self._paused:
            text += " [已暂停]"
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

    def _recent_item_stylesheet(self) -> str:
        return f"""
            QWidget {{
                background-color: {ThemeManager.color('bg_card')};
                border-radius: 10px;
                border: 1px solid {ThemeManager.color('border_light')};
            }}
        """

    def apply_theme(self, *_args):
        self.lbl_greeting.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {ThemeManager.color('text_primary')};"
        )
        self.lbl_sub_greeting.setStyleSheet(
            f"font-size: 14px; color: {ThemeManager.color('text_muted')}; padding: 0;"
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
