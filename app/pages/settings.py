from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel,
                               QListView, QPushButton, QScrollArea, QSlider, QSpinBox,
                               QTimeEdit, QVBoxLayout, QWidget)

from app.core.theme import ThemeManager


class ThemeDropdownCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QListView(self))

    def showPopup(self):
        self._configure_popup_view()
        super().showPopup()

    def apply_popup_theme(self):
        self._configure_popup_view()

    def _configure_popup_view(self):
        view = self.view()
        popup = view.window()
        if popup is None:
            return

        bg_card = ThemeManager.color("bg_card")
        border = ThemeManager.color("border")
        hover = ThemeManager.color("bg_hover")
        selected = ThemeManager.color("bg_selected")
        text_primary = ThemeManager.color("text_primary")

        # Keep popup opaque and draw rounded border on the popup itself;
        # this avoids black artifacts around rounded corners on Windows.
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        popup.setStyleSheet(
            f"background-color: {bg_card}; border: 1px solid {border}; border-radius: 8px;"
        )
        popup.setContentsMargins(0, 0, 0, 0)

        view.setFrameShape(QFrame.Shape.NoFrame)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setContentsMargins(0, 0, 0, 0)
        view.viewport().setAutoFillBackground(False)

        view.setStyleSheet(
            f"""
            QListView {{
                background: transparent;
                border: none;
                outline: none;
                padding: 4px;
                color: {text_primary};
            }}
            QListView::viewport {{
                background: transparent;
                border: none;
            }}
            QListView::item {{
                color: {text_primary};
                padding: 6px 12px;
                margin: 1px 0;
                border-radius: 6px;
            }}
            QListView::item:hover {{
                background-color: {hover};
            }}
            QListView::item:selected {{
                background-color: {selected};
                color: {text_primary};
            }}
            """
        )


class SettingsPage(QWidget):
    """
    Settings page with grouped option sections.
    """

    interval_changed = Signal(int)
    goal_changed = Signal(int)
    reminder_start_time_changed = Signal(str)
    reminder_end_time_changed = Signal(str)
    theme_changed = Signal(str)
    sound_changed = Signal(bool)
    autostart_changed = Signal(bool)
    shake_changed = Signal(bool)
    test_reminder_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")

        self._section_frames: list[QFrame] = []
        self._section_title_labels: list[QLabel] = []
        self._muted_labels: list[QLabel] = []
        self._checkboxes: list[QCheckBox] = []
        self._sliders: list[QSlider] = []
        self._accent_buttons: list[QPushButton] = []

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
        self.title_label = QLabel("设置")
        self.content_layout.addWidget(self.title_label)

        # --- Sections ---
        self._init_reminder_section()
        self._init_time_range_section()
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
        layout = self._create_section("提醒设置")

        row = QHBoxLayout()
        lbl = QLabel("提醒间隔（分钟）")
        self._muted_labels.append(lbl)

        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(15, 120)
        self.interval_slider.setSingleStep(5)
        self.interval_slider.setTickPosition(QSlider.TickPosition.NoTicks)
        self.interval_slider.setTickInterval(15)
        self.interval_slider.setMinimumHeight(32)
        self._sliders.append(self.interval_slider)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(15, 120)
        self.interval_spin.setSingleStep(5)
        self.interval_spin.setSuffix(" 分钟")
        self.interval_spin.setFixedWidth(104)

        # Sync
        self.interval_slider.valueChanged.connect(self.interval_spin.setValue)
        self.interval_spin.valueChanged.connect(self.interval_slider.setValue)
        self.interval_spin.valueChanged.connect(self.interval_changed.emit)

        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.interval_spin)

        layout.addLayout(row)
        layout.addWidget(self.interval_slider)

    def _init_time_range_section(self):
        layout = self._create_section("提醒时间段")

        start_row = QHBoxLayout()
        start_label = QLabel("开始时间")
        self._muted_labels.append(start_label)

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime(8, 0))
        self.start_time_edit.setFixedWidth(104)
        self.start_time_edit.timeChanged.connect(
            lambda t: self.reminder_start_time_changed.emit(t.toString("HH:mm"))
        )

        start_row.addWidget(start_label)
        start_row.addStretch()
        start_row.addWidget(self.start_time_edit)
        layout.addLayout(start_row)

        end_row = QHBoxLayout()
        end_label = QLabel("结束时间")
        self._muted_labels.append(end_label)

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        self.end_time_edit.setTime(QTime(22, 0))
        self.end_time_edit.setFixedWidth(104)
        self.end_time_edit.timeChanged.connect(
            lambda t: self.reminder_end_time_changed.emit(t.toString("HH:mm"))
        )

        end_row.addWidget(end_label)
        end_row.addStretch()
        end_row.addWidget(self.end_time_edit)
        layout.addLayout(end_row)

        desc_label = QLabel("只在该时间段内进行饮水提醒")
        self._muted_labels.append(desc_label)
        layout.addWidget(desc_label)

    def _init_goal_section(self):
        layout = self._create_section("每日目标")

        row = QHBoxLayout()
        lbl = QLabel("目标量（毫升）")
        self._muted_labels.append(lbl)

        self.goal_slider = QSlider(Qt.Orientation.Horizontal)
        self.goal_slider.setRange(500, 5000)
        self.goal_slider.setSingleStep(100)
        self.goal_slider.setTickPosition(QSlider.TickPosition.NoTicks)
        self.goal_slider.setTickInterval(500)
        self.goal_slider.setMinimumHeight(32)
        self._sliders.append(self.goal_slider)

        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(500, 5000)
        self.goal_spin.setSingleStep(100)
        self.goal_spin.setSuffix(" ml")
        self.goal_spin.setFixedWidth(104)

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
        layout = self._create_section("外观")

        row = QHBoxLayout()
        self.theme_label = QLabel("主题")

        self.theme_combo = ThemeDropdownCombo()
        self.theme_combo.addItems(["浅色", "深色", "跟随系统"])
        self.theme_combo.setFixedWidth(140)
        self.theme_combo.currentTextChanged.connect(self._on_theme_combo_changed)

        row.addWidget(self.theme_label)
        row.addStretch()
        row.addWidget(self.theme_combo)
        layout.addLayout(row)

    def _init_notifications_section(self):
        layout = self._create_section("通知")

        self.sound_check = QCheckBox("开启提示音")
        self.sound_check.setStyleSheet(
            f"QCheckBox {{ color: {ThemeManager.color('text_muted')}; border: none; }}"
        )
        self.sound_check.toggled.connect(self.sound_changed.emit)
        self._checkboxes.append(self.sound_check)
        layout.addWidget(self.sound_check)

        self.shake_check = QCheckBox("屏幕震动提醒")
        self.shake_check.setStyleSheet(
            f"QCheckBox {{ color: {ThemeManager.color('text_muted')}; border: none; }}"
        )
        self.shake_check.toggled.connect(self.shake_changed.emit)
        self._checkboxes.append(self.shake_check)
        layout.addWidget(self.shake_check)

        self.test_reminder_btn = QPushButton("测试提醒效果")
        self.test_reminder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_reminder_btn.clicked.connect(self.test_reminder_requested.emit)
        self._accent_buttons.append(self.test_reminder_btn)
        layout.addWidget(self.test_reminder_btn)

    def _init_system_section(self):
        layout = self._create_section("系统")

        self.autostart_check = QCheckBox("开机自启动")
        self.autostart_check.setStyleSheet(
            f"QCheckBox {{ color: {ThemeManager.color('text_muted')}; border: none; }}"
        )
        self.autostart_check.toggled.connect(self.autostart_changed.emit)
        self._checkboxes.append(self.autostart_check)
        layout.addWidget(self.autostart_check)

    def _init_about_section(self):
        layout = self._create_section("关于")

        self.about_title_label = QLabel("小范老师的饮水站 v1.0")
        layout.addWidget(self.about_title_label)

        self.about_desc_label = QLabel("用 💧 和爱心为小范老师打造")
        layout.addWidget(self.about_desc_label)

    def _on_theme_combo_changed(self, text):
        mapping = {"浅色": "light", "深色": "dark", "跟随系统": "auto"}
        self.theme_changed.emit(mapping.get(text, "light"))

    def apply_theme(self, *_args):
        bg_primary = ThemeManager.color("bg_primary")
        bg_card = ThemeManager.color("bg_card")
        border = ThemeManager.color("border")
        text_primary = ThemeManager.color("text_primary")
        text_secondary = ThemeManager.color("text_secondary")
        text_muted = ThemeManager.color("text_muted")
        accent = ThemeManager.color("accent")
        accent_hover = ThemeManager.color("accent_hover")
        accent_light = ThemeManager.color("accent_light")
        text_on_accent = ThemeManager.color("text_on_accent")
        bg_input = ThemeManager.color("bg_input")
        border_light = ThemeManager.color("border_light")

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

        self.theme_label.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {text_secondary}; border: none;"
        )

        for checkbox in self._checkboxes:
            checkbox.setStyleSheet(f"QCheckBox {{ color: {text_muted}; border: none; }}")

        for button in self._accent_buttons:
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {accent};
                    color: {text_on_accent};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {accent_hover};
                }}
                QPushButton:pressed {{
                    background-color: {accent_light};
                }}
                """
            )

        self.about_title_label.setStyleSheet(f"border: none; font-weight: bold; color: {accent};")
        self.about_desc_label.setStyleSheet(f"border: none; color: {text_muted};")

        self.theme_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {bg_input};
                color: {text_primary};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 4px 28px 4px 10px;
                font-weight: 500;
            }}
            QComboBox:on, QComboBox:editable, QComboBox:enabled {{
                color: {text_primary};
                background-color: {bg_input};
            }}
            QComboBox:hover {{
                border-color: {accent};
            }}
            QComboBox:focus {{
                border-color: {accent_hover};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border: none;
                background: transparent;
            }}
            """
        )

        slider_style = f"""
            QSlider {{
                min-height: 32px;
                max-height: 32px;
            }}
            QSlider::groove:horizontal {{
                background-color: {border};
                height: 4px;
                border-radius: 2px;
                margin: 14px 0;
            }}
            QSlider::sub-page:horizontal {{
                background-color: {accent};
                border-radius: 2px;
                margin: 14px 0;
            }}
            QSlider::add-page:horizontal {{
                background-color: {border_light};
                border-radius: 2px;
                margin: 14px 0;
            }}
            QSlider::handle:horizontal {{
                background-color: {bg_card};
                width: 14px;
                height: 14px;
                margin: -5px 0 -5px 0;
                border-radius: 7px;
                border: 2px solid {accent};
            }}
            QSlider::handle:horizontal:hover {{
                background-color: {accent_light};
                border-color: {accent_hover};
            }}
        """
        for slider in self._sliders:
            slider.setStyleSheet(slider_style)

        self.theme_combo.apply_popup_theme()

    def load_settings(self, config: dict[str, object]):
        widgets = [
            self.goal_slider,
            self.goal_spin,
            self.interval_slider,
            self.interval_spin,
            self.start_time_edit,
            self.end_time_edit,
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

            if "reminder_start_time" in config:
                raw_val = config["reminder_start_time"]
                if isinstance(raw_val, str) and ":" in raw_val:
                    parts = raw_val.split(":")
                    self.start_time_edit.setTime(QTime(int(parts[0]), int(parts[1])))

            if "reminder_end_time" in config:
                raw_val = config["reminder_end_time"]
                if isinstance(raw_val, str) and ":" in raw_val:
                    parts = raw_val.split(":")
                    self.end_time_edit.setTime(QTime(int(parts[0]), int(parts[1])))

            if "theme" in config:
                raw_theme = config["theme"]
                if isinstance(raw_theme, str):
                    mapping = {"light": "浅色", "dark": "深色", "auto": "跟随系统"}
                    display = mapping.get(raw_theme, "浅色")
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
