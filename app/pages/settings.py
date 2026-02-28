from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSlider, QSpinBox, QCheckBox, QPushButton,
                               QComboBox, QFrame, QScrollArea)
from PySide6.QtCore import Qt, Signal

class SettingsPage(QWidget):
    """
    Settings page with grouped option sections.
    """
    interval_changed = Signal(int)
    goal_changed = Signal(int)
    theme_changed = Signal(str)
    sound_changed = Signal(bool)
    autostart_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        # Content Widget inside Scroll Area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #FAFAFA;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(16)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 8px;")
        self.content_layout.addWidget(title)
        
        # --- Sections ---
        
        # 1. Reminder Settings
        self._init_reminder_section()
        
        # 2. Daily Goal
        self._init_goal_section()
        
        # 3. Appearance
        self._init_appearance_section()
        
        # 4. Notifications
        self._init_notifications_section()
        
        # 5. System
        self._init_system_section()
        
        # 6. About
        self._init_about_section()
        
        self.content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_section(self, title):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 600; color: #424242; border: none;")
        layout.addWidget(title_lbl)
        
        self.content_layout.addWidget(frame)
        return layout

    def _init_reminder_section(self):
        layout = self._create_section("Reminder Settings")
        
        row = QHBoxLayout()
        lbl = QLabel("Interval (minutes)")
        lbl.setStyleSheet("border: none; color: #616161;")
        
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setRange(15, 120)
        self.interval_slider.setSingleStep(5)
        self.interval_slider.setTickPosition(QSlider.TicksBelow)
        self.interval_slider.setTickInterval(15)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(15, 120)
        self.interval_spin.setSingleStep(5)
        self.interval_spin.setSuffix(" min")
        self.interval_spin.setFixedWidth(80)
        
        # Sync
        self.interval_slider.valueChanged.connect(self.interval_spin.setValue)
        self.interval_spin.valueChanged.connect(self.interval_slider.setValue)
        self.interval_spin.valueChanged.connect(self.interval_changed.emit)
        
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.interval_spin)
        
        layout.addLayout(row)
        layout.addWidget(self.interval_slider)

    def _init_goal_section(self):
        layout = self._create_section("Daily Goal")
        
        row = QHBoxLayout()
        lbl = QLabel("Target (ml)")
        lbl.setStyleSheet("border: none; color: #616161;")
        
        self.goal_slider = QSlider(Qt.Horizontal)
        self.goal_slider.setRange(500, 5000)
        self.goal_slider.setSingleStep(100)
        self.goal_slider.setTickPosition(QSlider.TicksBelow)
        self.goal_slider.setTickInterval(500)
        
        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(500, 5000)
        self.goal_spin.setSingleStep(100)
        self.goal_spin.setSuffix(" ml")
        self.goal_spin.setFixedWidth(80)
        
        # Sync
        self.goal_slider.valueChanged.connect(self.goal_spin.setValue)
        self.goal_spin.valueChanged.connect(self.goal_slider.setValue)
        self.goal_spin.valueChanged.connect(self.goal_changed.emit)
        
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.goal_spin)
        
        layout.addLayout(row)
        layout.addWidget(self.goal_slider)

    def _init_appearance_section(self):
        layout = self._create_section("Appearance")
        
        row = QHBoxLayout()
        lbl = QLabel("Theme")
        lbl.setStyleSheet("border: none; color: #616161;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setFixedWidth(100)
        self.theme_combo.currentTextChanged.connect(
            lambda t: self.theme_changed.emit(t.lower())
        )
        
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.theme_combo)
        layout.addLayout(row)

    def _init_notifications_section(self):
        layout = self._create_section("Notifications")
        
        self.sound_check = QCheckBox("Enable Sound")
        self.sound_check.setStyleSheet("QCheckBox { color: #616161; border: none; }")
        self.sound_check.toggled.connect(self.sound_changed.emit)
        layout.addWidget(self.sound_check)

    def _init_system_section(self):
        layout = self._create_section("System")
        
        self.autostart_check = QCheckBox("Auto-start on boot")
        self.autostart_check.setStyleSheet("QCheckBox { color: #616161; border: none; }")
        self.autostart_check.toggled.connect(self.autostart_changed.emit)
        layout.addWidget(self.autostart_check)

    def _init_about_section(self):
        layout = self._create_section("About")
        
        lbl = QLabel("Water Reminder v1.0")
        lbl.setStyleSheet("border: none; font-weight: bold; color: #2196F3;")
        layout.addWidget(lbl)
        
        desc = QLabel("Made with 💧 and Python (PySide6)")
        desc.setStyleSheet("border: none; color: #757575;")
        layout.addWidget(desc)

    def load_settings(self, config: dict):
        """
        Populate all fields from config dict.
        keys: daily_goal_ml, reminder_interval_min, theme, sound_enabled, autostart_enabled
        """
        # Block signals to prevent emitting changes during load
        self.blockSignals(True)
        
        if "daily_goal_ml" in config:
            val = config["daily_goal_ml"]
            self.goal_slider.setValue(val)
            self.goal_spin.setValue(val)
            
        if "reminder_interval_min" in config:
            val = config["reminder_interval_min"]
            self.interval_slider.setValue(val)
            self.interval_spin.setValue(val)
            
        if "theme" in config:
            theme = config["theme"].capitalize()
            idx = self.theme_combo.findText(theme)
            if idx >= 0:
                self.theme_combo.setCurrentIndex(idx)
                
        if "sound_enabled" in config:
            self.sound_check.setChecked(bool(config["sound_enabled"]))
            
        if "autostart_enabled" in config:
            self.autostart_check.setChecked(bool(config["autostart_enabled"]))
            
        self.blockSignals(False)
