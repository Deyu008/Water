from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel,
                               QScrollArea, QSlider, QSpinBox, QVBoxLayout, QWidget)

from app.core.theme import ThemeManager


class SettingsPage(QWidget):
    """
    Settings page with grouped option sections.
    """

    interval_changed = Signal(int)
    goal_changed = Signal(int)
    theme_changed = Signal(str)
    sound_changed = Signal(bool)
    autostart_changed = Signal(bool)
    shake_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")

        self._section_frames: list[QFrame] = []
        self._section_title_labels: list[QLabel] = []
        self._muted_labels: list[QLabel] = []
        self._checkboxes: list[QCheckBox] = []

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        # Content Widget inside Scroll Area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(16)

        # Title
        self.title_label = QLabel("Settings")
        self.content_layout.addWidget(self.title_label)

        # --- Sections ---
        self._init_reminder_section()
        self._init_goal_section()
        self._init_appearance_section()
        self._init_notifications_section()
        self._init_system_section()
        self._init_about_section()

        self.content_layout.addStretch()

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)

        ThemeManager.signals.theme_applied.connect(self.apply_theme)
        self.apply_theme()

    def _create_section(self, title):
        frame = QFrame()
        self._section_frames.append(frame)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_lbl = QLabel(title)
        self._section_title_labels.append(title_lbl)
        layout.addWidget(title_lbl)

        self.content_layout.addWidget(frame)
        return layout

    def _init_reminder_section(self):
        layout = self._create_section("Reminder Settings")

        row = QHBoxLayout()
        lbl = QLabel("Interval (minutes)")
        self._muted_labels.append(lbl)

        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(15, 120)
        self.interval_slider.setSingleStep(5)
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
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
        self._muted_labels.append(lbl)

        self.goal_slider = QSlider(Qt.Orientation.Horizontal)
        self.goal_slider.setRange(500, 5000)
        self.goal_slider.setSingleStep(100)
        self.goal_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
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
        self._muted_labels.append(lbl)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto (System)"])
        self.theme_combo.setFixedWidth(140)
        self.theme_combo.currentTextChanged.connect(self._on_theme_combo_changed)

        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.theme_combo)
        layout.addLayout(row)

    def _init_notifications_section(self):
        layout = self._create_section("Notifications")

        self.sound_check = QCheckBox("Enable Sound")
        self.sound_check.setStyleSheet(
            f"QCheckBox {{ color: {ThemeManager.color('text_muted')}; border: none; }}"
        )
        self.sound_check.toggled.connect(self.sound_changed.emit)
        self._checkboxes.append(self.sound_check)
        layout.addWidget(self.sound_check)

        self.shake_check = QCheckBox("Screen shake reminder")
        self.shake_check.setStyleSheet(
            f"QCheckBox {{ color: {ThemeManager.color('text_muted')}; border: none; }}"
        )
        self.shake_check.toggled.connect(self.shake_changed.emit)
        self._checkboxes.append(self.shake_check)
        layout.addWidget(self.shake_check)

    def _init_system_section(self):
        layout = self._create_section("System")

        self.autostart_check = QCheckBox("Auto-start on boot")
        self.autostart_check.setStyleSheet(
            f"QCheckBox {{ color: {ThemeManager.color('text_muted')}; border: none; }}"
        )
        self.autostart_check.toggled.connect(self.autostart_changed.emit)
        self._checkboxes.append(self.autostart_check)
        layout.addWidget(self.autostart_check)

    def _init_about_section(self):
        layout = self._create_section("About")

        self.about_title_label = QLabel("Water Reminder v1.0")
        layout.addWidget(self.about_title_label)

        self.about_desc_label = QLabel("Made with 💧 and Python (PySide6)")
        layout.addWidget(self.about_desc_label)

    def _on_theme_combo_changed(self, text):
        mapping = {"Light": "light", "Dark": "dark", "Auto (System)": "auto"}
        self.theme_changed.emit(mapping.get(text, "light"))

    def apply_theme(self, *_args):
        bg_primary = ThemeManager.color("bg_primary")
        bg_card = ThemeManager.color("bg_card")
        border = ThemeManager.color("border")
        text_primary = ThemeManager.color("text_primary")
        text_secondary = ThemeManager.color("text_secondary")
        text_muted = ThemeManager.color("text_muted")
        accent = ThemeManager.color("accent")

        self.content_widget.setStyleSheet(f"background-color: {bg_primary};")
        self.title_label.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {text_primary}; margin-bottom: 8px;"
        )

        for frame in self._section_frames:
            frame.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {bg_card};
                    border: 1px solid {border};
                    border-radius: 12px;
                }}
                """
            )

        for title_lbl in self._section_title_labels:
            title_lbl.setStyleSheet(
                f"font-size: 16px; font-weight: 600; color: {text_secondary}; border: none;"
            )

        for label in self._muted_labels:
            label.setStyleSheet(f"border: none; color: {text_muted};")

        for checkbox in self._checkboxes:
            checkbox.setStyleSheet(f"QCheckBox {{ color: {text_muted}; border: none; }}")

        self.about_title_label.setStyleSheet(f"border: none; font-weight: bold; color: {accent};")
        self.about_desc_label.setStyleSheet(f"border: none; color: {text_muted};")

    def load_settings(self, config: dict[str, object]):
        widgets = [
            self.goal_slider,
            self.goal_spin,
            self.interval_slider,
            self.interval_spin,
            self.theme_combo,
            self.sound_check,
            self.autostart_check,
            self.shake_check,
        ]
        for widget in widgets:
            widget.blockSignals(True)

        try:
            if "daily_goal_ml" in config:
                raw_goal = config["daily_goal_ml"]
                if isinstance(raw_goal, int | float | str):
                    val = int(raw_goal)
                    self.goal_slider.setValue(val)
                    self.goal_spin.setValue(val)

            if "reminder_interval_min" in config:
                raw_interval = config["reminder_interval_min"]
                if isinstance(raw_interval, int | float | str):
                    val = int(raw_interval)
                    self.interval_slider.setValue(val)
                    self.interval_spin.setValue(val)

            if "theme" in config:
                raw_theme = config["theme"]
                if isinstance(raw_theme, str):
                    mapping = {"light": "Light", "dark": "Dark", "auto": "Auto (System)"}
                    display = mapping.get(raw_theme, "Light")
                    idx = self.theme_combo.findText(display)
                    if idx >= 0:
                        self.theme_combo.setCurrentIndex(idx)

            if "sound_enabled" in config:
                self.sound_check.setChecked(bool(config["sound_enabled"]))

            if "autostart_enabled" in config:
                self.autostart_check.setChecked(bool(config["autostart_enabled"]))

            if "shake_reminder_enabled" in config:
                self.shake_check.setChecked(bool(config["shake_reminder_enabled"]))
        finally:
            for widget in widgets:
                widget.blockSignals(False)
