import math
import random

from PySide6.QtCore import Qt, QRectF, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QWidget


class _Particle:
    __slots__ = ("x", "y", "vx", "vy", "size", "color", "rotation", "rot_speed", "shape")

    def __init__(self, screen_w: int, screen_h: int):
        self.x = random.uniform(0, screen_w)
        self.y = random.uniform(-screen_h * 0.6, -10)
        self.vx = random.uniform(-1.8, 1.8)
        self.vy = random.uniform(2.0, 5.5)
        self.size = random.uniform(6, 14)
        self.color = random.choice([
            QColor("#FF6B6B"), QColor("#4ECDC4"), QColor("#45B7D1"),
            QColor("#96CEB4"), QColor("#FFEAA7"), QColor("#DDA0DD"),
            QColor("#FF9FF3"), QColor("#F9CA24"), QColor("#74B9FF"),
        ])
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4, 4)
        self.shape = random.choice(["rect", "circle", "star"])


class CelebrationOverlay(QWidget):
    dismissed = Signal()

    _PARTICLE_COUNT = 90
    _FPS_INTERVAL = 33
    _AUTO_CLOSE_MS = 8000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        screen = QApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())

        self._particles: list[_Particle] = []
        self._fade_alpha = 0
        self._fade_in = True

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(self._FPS_INTERVAL)
        self._anim_timer.timeout.connect(self._tick)

        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.setInterval(self._AUTO_CLOSE_MS)
        self._close_timer.timeout.connect(self._dismiss)

    def show_celebration(self):
        w = max(self.width(), 800)
        h = max(self.height(), 600)
        self._particles = [_Particle(w, h) for _ in range(self._PARTICLE_COUNT)]
        self._fade_alpha = 0
        self._fade_in = True
        self.show()
        self._anim_timer.start()
        self._close_timer.start()

    def _tick(self):
        if self._fade_in and self._fade_alpha < 180:
            self._fade_alpha = min(180, self._fade_alpha + 12)

        h = self.height()
        w = self.width()
        for p in self._particles:
            p.y += p.vy
            p.x += p.vx
            p.rotation += p.rot_speed
            p.vx += random.uniform(-0.25, 0.25)
            if p.y > h + 20:
                p.y = random.uniform(-40, -10)
                p.x = random.uniform(0, w)
                p.vy = random.uniform(2.0, 5.5)
                p.vx = random.uniform(-1.8, 1.8)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(0, 0, 0, self._fade_alpha))

        for p in self._particles:
            painter.save()
            painter.translate(p.x, p.y)
            painter.rotate(p.rotation)
            c = QColor(p.color)
            c.setAlpha(min(255, self._fade_alpha + 75))
            painter.setBrush(c)
            painter.setPen(Qt.PenStyle.NoPen)
            half = p.size / 2
            if p.shape == "rect":
                painter.drawRect(QRectF(-half, -half, p.size, p.size * 0.6))
            elif p.shape == "circle":
                painter.drawEllipse(QRectF(-half, -half, p.size, p.size))
            else:
                self._draw_star(painter, half * 0.8, half * 0.35)
            painter.restore()

        if self._fade_alpha > 80:
            text_alpha = min(255, (self._fade_alpha - 80) * 3)
            center_y = self.height() // 2 - 80

            emoji_font = QFont(painter.font())
            emoji_font.setPointSize(60)
            painter.setFont(emoji_font)
            painter.setPen(QColor(255, 255, 255, text_alpha))
            painter.drawText(
                QRectF(0, center_y - 50, self.width(), 80),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "\U0001f389",
            )

            title_font = QFont(painter.font())
            title_font.setPointSize(28)
            title_font.setBold(True)
            painter.setFont(title_font)
            painter.setPen(QColor(255, 255, 255, text_alpha))
            painter.drawText(
                QRectF(0, center_y + 30, self.width(), 50),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "\u76ee\u6807\u8fbe\u6210\uff01",
            )

            sub_font = QFont(painter.font())
            sub_font.setPointSize(14)
            sub_font.setBold(False)
            painter.setFont(sub_font)
            painter.setPen(QColor(200, 220, 255, text_alpha))
            painter.drawText(
                QRectF(0, center_y + 80, self.width(), 35),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "\u606d\u559c\u5c0f\u8303\u8001\u5e08\uff0c\u4eca\u65e5\u996e\u6c34\u76ee\u6807\u5df2\u5b8c\u6210\uff01",
            )

            hint_font = QFont(painter.font())
            hint_font.setPointSize(11)
            painter.setFont(hint_font)
            painter.setPen(QColor(180, 200, 230, max(0, text_alpha - 60)))
            painter.drawText(
                QRectF(0, center_y + 130, self.width(), 30),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "\u70b9\u51fb\u4efb\u610f\u4f4d\u7f6e\u5173\u95ed",
            )

        painter.end()

    @staticmethod
    def _draw_star(painter: QPainter, outer_r: float, inner_r: float):
        path = QPainterPath()
        points = 5
        angle_step = math.pi / points
        for i in range(points * 2):
            r = outer_r if i % 2 == 0 else inner_r
            angle = i * angle_step - math.pi / 2
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        painter.drawPath(path)

    def mousePressEvent(self, event):
        self._dismiss()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._dismiss()

    def _dismiss(self):
        self._anim_timer.stop()
        self._close_timer.stop()
        self.dismissed.emit()
        self.close()
