from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QSizePolicy, QWidget


class ImagePanel(QWidget):
    def __init__(self):
        super().__init__()

        self.current_pixmap: QPixmap | None = None
        self.rotation: int = 0

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
        self.update()

    def set_rotation(self, rotation: int):
        self.rotation = rotation
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1f1f1f"))

        if self.current_pixmap is None:
            return

        pixmap = self.current_pixmap.transformed(
            QTransform().rotate(self.rotation),
            Qt.SmoothTransformation,
        )

        pixmap = pixmap.scaled(
            self.size() * 0.96,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        x = (self.width() - pixmap.width()) // 2
        y = (self.height() - pixmap.height()) // 2

        painter.drawPixmap(x, y, pixmap)

    def resizeEvent(self, event):
        self.update()
        super().resizeEvent(event)