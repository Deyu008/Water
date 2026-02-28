from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QButtonGroup, QGraphicsProxyWidget)
from PySide6.QtCore import Qt, Signal, QSize, QDateTime
from PySide6.QtCharts import (QChart, QChartView, QBarSet, QBarSeries, 
                              QBarCategoryAxis, QValueAxis, QLineSeries)
from PySide6.QtGui import QColor, QPainter, QFont, QPen, QGradient, QLinearGradient, QBrush

from app.core.theme import ThemeManager

class StatsCard(QFrame):
    def __init__(self, title, value, icon="📊", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedWidth(120)
        self.setFixedHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        
        self.title_lbl = QLabel(title)
        layout.addWidget(self.title_lbl)
        
        self.value_lbl = QLabel(value)
        layout.addWidget(self.value_lbl)

        self.apply_theme()

    def set_value(self, value):
        self.value_lbl.setText(str(value))

    def apply_theme(self):
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {ThemeManager.color('bg_card')};
                border: 1px solid {ThemeManager.color('border')};
                border-radius: 12px;
            }}
            """
        )
        self.title_lbl.setStyleSheet(
            f"color: {ThemeManager.color('text_muted')}; font-size: 12px; font-weight: 600; border: none;"
        )
        self.value_lbl.setStyleSheet(
            f"color: {ThemeManager.color('accent')}; font-size: 18px; font-weight: bold; border: none;"
        )


class HistoryPage(QWidget):
    """
    History and statistics page.
    """
    period_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyPage")
        self.setStyleSheet(f"background-color: {ThemeManager.color('bg_primary')};")
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        # 1. Header & Toggle
        header_layout = QHBoxLayout()
        
        self.title_lbl = QLabel("Drinking History")
        self.title_lbl.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {ThemeManager.color('text_primary')};"
        )
        header_layout.addWidget(self.title_lbl)
        
        header_layout.addStretch()
        
        # Toggle Buttons (7 Days / 30 Days)
        self.toggle_group = QButtonGroup(self)
        self.toggle_bg = QFrame()
        self.toggle_bg.setStyleSheet(self._toggle_background_stylesheet())
        toggle_layout = QHBoxLayout(self.toggle_bg)
        toggle_layout.setContentsMargins(2, 2, 2, 2)
        toggle_layout.setSpacing(0)
        
        self.btn_7_days = self._create_toggle_btn("7 Days", 7)
        self.btn_30_days = self._create_toggle_btn("30 Days", 30)
        
        toggle_layout.addWidget(self.btn_7_days)
        toggle_layout.addWidget(self.btn_30_days)
        
        self.btn_7_days.setChecked(True)
        self.toggle_group.buttonClicked.connect(self._on_toggle_clicked)
        
        header_layout.addWidget(self.toggle_bg)
        self.main_layout.addLayout(header_layout)
        
        # 2. Chart Section
        self.chart_container = QFrame()
        self.chart_container.setStyleSheet(self._chart_container_stylesheet())
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(4, 4, 4, 4)
        
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setBackgroundVisible(False)
        self.chart.legend().setVisible(False)
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("background: transparent;")
        
        chart_layout.addWidget(self.chart_view)
        self.main_layout.addWidget(self.chart_container, stretch=1)
        
        # 3. Stats Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.card_avg = StatsCard("Average", "0 ml")
        self.card_best = StatsCard("Best Day", "0 ml")
        self.card_total = StatsCard("Total", "0 ml")
        
        stats_layout.addStretch()
        stats_layout.addWidget(self.card_avg)
        stats_layout.addWidget(self.card_best)
        stats_layout.addWidget(self.card_total)
        stats_layout.addStretch()
        
        self.main_layout.addLayout(stats_layout)
        
        # Initialize empty chart
        self._init_chart()
        ThemeManager.signals.theme_applied.connect(self.apply_theme)
        self.apply_theme()

    def _create_toggle_btn(self, text, id):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedSize(80, 28)
        btn.setStyleSheet(self._toggle_button_stylesheet())
        self.toggle_group.addButton(btn, id)
        return btn

    def _on_toggle_clicked(self, btn):
        days = self.toggle_group.id(btn)
        self.period_changed.emit(days)

    def _toggle_background_stylesheet(self) -> str:
        return f"""
            QFrame {{
                background-color: {ThemeManager.color('toggle_bg')};
                border-radius: 16px;
                padding: 2px;
            }}
        """

    def _toggle_button_stylesheet(self) -> str:
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 14px;
                color: {ThemeManager.color('toggle_text')};
                font-weight: 500;
            }}
            QPushButton:checked {{
                background-color: {ThemeManager.color('toggle_checked_bg')};
                color: {ThemeManager.color('toggle_checked_text')};
                font-weight: bold;
            }}
            QPushButton:hover:!checked {{
                background-color: {ThemeManager.color('toggle_checked_bg')};
            }}
        """

    def _chart_container_stylesheet(self) -> str:
        return f"""
            QFrame {{
                background-color: {ThemeManager.color('bg_card')};
                border-radius: 16px;
                border: 1px solid {ThemeManager.color('border')};
            }}
        """

    def _init_chart(self):
        # 1. Create Axes
        self.axis_x = QBarCategoryAxis()
        self.axis_x.setLabelsFont(QFont("Segoe UI", 8))
        self.axis_x.setLabelsColor(ThemeManager.qcolor("chart_axis_text"))
        self.axis_x.setGridLineVisible(False)
        self.axis_x.setLinePen(QPen(Qt.PenStyle.NoPen))
        
        self.axis_y = QValueAxis()
        self.axis_y.setLabelsFont(QFont("Segoe UI", 8))
        self.axis_y.setLabelsColor(ThemeManager.qcolor("chart_axis_text"))
        self.axis_y.setGridLineColor(ThemeManager.qcolor("chart_grid"))
        self.axis_y.setLinePen(QPen(Qt.PenStyle.NoPen))
        self.axis_y.setLabelFormat("%d")
        
        # Hidden axis for the line series
        self.axis_x_line = QValueAxis()
        self.axis_x_line.setVisible(False)
        
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_x_line, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        
        # 2. Bar Series
        self.bar_set = QBarSet("Water")
        self.bar_set.setBorderColor(Qt.GlobalColor.transparent)
        
        # Gradient for bars
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QGradient.CoordinateMode.ObjectBoundingMode)
        gradient.setColorAt(0.0, ThemeManager.qcolor("chart_bar_start"))
        gradient.setColorAt(1.0, ThemeManager.qcolor("chart_bar_end"))
        self.bar_set.setBrush(gradient)
        
        self.bar_series = QBarSeries()
        self.bar_series.append(self.bar_set)
        self.bar_series.setBarWidth(0.5)
        
        self.chart.addSeries(self.bar_series)
        self.bar_series.attachAxis(self.axis_x)
        self.bar_series.attachAxis(self.axis_y)
        
        # 3. Goal Line Series
        self.goal_series = QLineSeries()
        pen = QPen(ThemeManager.qcolor("chart_goal"))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        self.goal_series.setPen(pen)
        
        self.chart.addSeries(self.goal_series)
        self.goal_series.attachAxis(self.axis_x_line)
        self.goal_series.attachAxis(self.axis_y)

        self._apply_chart_theme()

    def update_chart(self, daily_totals: list[dict[str, int | str]], goal_ml: int):
        """
        Update chart with data like [{"date": "2026-02-28", "total_ml": 1500}, ...]
        """
        self.bar_set.remove(0, self.bar_set.count())
        self.goal_series.clear()
        categories = []
        
        max_val = float(goal_ml)
        
        if not daily_totals:
            self.axis_x.clear()
            self.axis_y.setRange(0, goal_ml * 1.2)
            self.axis_x_line.setRange(-0.5, 0.5) # Default range
            return

        for entry in daily_totals:
            raw_val = entry.get("total_ml", 0)
            try:
                val = float(raw_val)
            except (TypeError, ValueError):
                val = 0.0
            self.bar_set.append(val)
            
            date_str = str(entry.get("date", ""))
            if len(date_str) >= 10:
                short_date = date_str[5:] # 2026-02-28 -> 02-28
            else:
                short_date = date_str
            categories.append(short_date)
            max_val = max(max_val, val)
            
        self.axis_x.setCategories(categories)
        self.axis_y.setRange(0, max_val * 1.1)
        
        # Update goal line
        count = len(categories)
        self.axis_x_line.setRange(-0.5, count - 0.5)
        
        self.goal_series.append(-0.5, goal_ml)
        self.goal_series.append(count - 0.5, goal_ml)

    def update_stats(self, avg_ml: int, best_ml: int, total_ml: int):
        self.card_avg.set_value(f"{int(avg_ml)} ml")
        self.card_best.set_value(f"{int(best_ml)} ml")
        self.card_total.set_value(f"{int(total_ml)} ml")

    def _apply_chart_theme(self):
        self.axis_x.setLabelsColor(ThemeManager.qcolor("chart_axis_text"))
        self.axis_y.setLabelsColor(ThemeManager.qcolor("chart_axis_text"))
        self.axis_y.setGridLineColor(ThemeManager.qcolor("chart_grid"))

        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QGradient.CoordinateMode.ObjectBoundingMode)
        gradient.setColorAt(0.0, ThemeManager.qcolor("chart_bar_start"))
        gradient.setColorAt(1.0, ThemeManager.qcolor("chart_bar_end"))
        self.bar_set.setBrush(gradient)

        goal_pen = self.goal_series.pen()
        goal_pen.setColor(ThemeManager.qcolor("chart_goal"))
        self.goal_series.setPen(goal_pen)

    def apply_theme(self, *_args):
        self.setStyleSheet(f"background-color: {ThemeManager.color('bg_primary')};")
        self.title_lbl.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {ThemeManager.color('text_primary')};"
        )

        self.toggle_bg.setStyleSheet(self._toggle_background_stylesheet())
        toggle_btn_style = self._toggle_button_stylesheet()
        self.btn_7_days.setStyleSheet(toggle_btn_style)
        self.btn_30_days.setStyleSheet(toggle_btn_style)

        self.chart_container.setStyleSheet(self._chart_container_stylesheet())

        self.card_avg.apply_theme()
        self.card_best.apply_theme()
        self.card_total.apply_theme()

        self._apply_chart_theme()
