from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QSizePolicy, QWidget


class ImagePanel(QWidget):
    PAN_STEP = 80

    def __init__(self):
        super().__init__()

        self.current_pixmap: QPixmap | None = None
        self.rotation: int = 0
        self.zoom_scale: float | None = None
        self.pan_x = 0
        self.pan_y = 0

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

    def sizeHint(self):
        return QSize(900, 600)

    def minimumSizeHint(self):
        return QSize(300, 220)

    def load_image(self, filename: Path, rotation: int = 0):
        self.current_pixmap = QPixmap(str(filename))
        self.rotation = rotation
        self.reset_pan()
        self.update()

    def set_rotation(self, rotation: int):
        self.rotation = rotation
        self.reset_pan()
        self.update()

    def set_zoom_fit(self):
        self.zoom_scale = None
        self.reset_pan()
        self.update()

    def set_zoom_scale(self, scale: float):
        self.zoom_scale = scale
        self.reset_pan()
        self.update()

    def pan_left(self):
        self.pan(-self.PAN_STEP, 0)

    def pan_right(self):
        self.pan(self.PAN_STEP, 0)

    def pan_up(self):
        self.pan(0, -self.PAN_STEP)

    def pan_down(self):
        self.pan(0, self.PAN_STEP)

    def pan(self, dx: int, dy: int):
        if self.zoom_scale is None:
            return

        self.pan_x += dx
        self.pan_y += dy
        self.clamp_pan()
        self.update()

    def reset_pan(self):
        self.pan_x = 0
        self.pan_y = 0

    def transformed_pixmap(self):
        if self.current_pixmap is None:
            return None

        pixmap = self.current_pixmap.transformed(
            QTransform().rotate(self.rotation),
            Qt.SmoothTransformation,
        )

        if self.zoom_scale is None:
            return pixmap.scaled(
                self.size() * 0.96,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

        return pixmap.scaled(
            int(pixmap.width() * self.zoom_scale),
            int(pixmap.height() * self.zoom_scale),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

    def clamp_pan(self):
        pixmap = self.transformed_pixmap()

        if pixmap is None:
            self.reset_pan()
            return

        max_x = max(0, (pixmap.width() - self.width()) // 2)
        max_y = max(0, (pixmap.height() - self.height()) // 2)

        self.pan_x = max(-max_x, min(self.pan_x, max_x))
        self.pan_y = max(-max_y, min(self.pan_y, max_y))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1f1f1f"))

        pixmap = self.transformed_pixmap()

        if pixmap is None:
            return

        self.clamp_pan()

        x = (self.width() - pixmap.width()) // 2 - self.pan_x
        y = (self.height() - pixmap.height()) // 2 - self.pan_y

        painter.drawPixmap(x, y, pixmap)

    def resizeEvent(self, event):
        self.clamp_pan()
        self.update()
        super().resizeEvent(event)