"""
Liquid Glass Effect utilities for iOS 26-style frosted glass UI.

Provides painting helpers for:
- Frosted glass backgrounds with translucent fills
- Specular highlight gradients (top-edge light refraction)
- Soft inner glow borders
- Glass reflection overlays
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)


def paint_glass_background(
    painter: QPainter,
    rect: QRectF,
    *,
    fill_color: QColor,
    border_color: QColor,
    highlight_color: QColor | None = None,
    radius: float = 18.0,
    border_width: float = 1.0,
) -> None:
    """
    Paint a frosted-glass panel with:
    1. Semi-transparent fill
    2. Top-edge specular highlight gradient
    3. Subtle glass border with inner glow
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)

    # 1. Base fill (semi-transparent)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(fill_color))
    painter.drawPath(path)

    # 2. Specular highlight — a subtle top-to-middle gradient
    if highlight_color is None:
        highlight_color = QColor(255, 255, 255, 45)

    highlight_grad = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.top() + rect.height() * 0.45))
    highlight_grad.setColorAt(0.0, highlight_color)
    highlight_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

    painter.setBrush(QBrush(highlight_grad))
    # Clip to top half for highlight
    highlight_rect = QRectF(rect.left(), rect.top(), rect.width(), rect.height() * 0.5)
    highlight_path = QPainterPath()
    highlight_path.addRoundedRect(highlight_rect, radius, radius)
    painter.drawPath(path & highlight_path)

    # 3. Border with soft glow
    pen = QPen(border_color, border_width)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)

    painter.restore()


def paint_glass_circle(
    painter: QPainter,
    center: QPointF,
    radius: float,
    *,
    fill_color: QColor,
    border_color: QColor,
    highlight_color: QColor | None = None,
    border_width: float = 1.0,
) -> None:
    """Paint a circular glass element (for progress ring background)."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)

    # Base fill
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(fill_color))
    painter.drawEllipse(rect)

    # Specular highlight (top portion)
    if highlight_color is None:
        highlight_color = QColor(255, 255, 255, 40)

    highlight_grad = QRadialGradient(
        center.x(), center.y() - radius * 0.3,
        radius * 1.2,
    )
    highlight_grad.setColorAt(0.0, highlight_color)
    highlight_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

    painter.setBrush(QBrush(highlight_grad))
    painter.drawEllipse(rect)

    # Border
    pen = QPen(border_color, border_width)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(rect)

    painter.restore()


def glass_stylesheet(
    fill: str,
    border: str,
    radius: int = 18,
    border_width: int = 1,
) -> str:
    """Generate a CSS stylesheet string for glass-style QWidget/QFrame."""
    return (
        f"background-color: {fill};"
        f"border: {border_width}px solid {border};"
        f"border-radius: {radius}px;"
    )
