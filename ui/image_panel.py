from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QWidget


class ImagePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_pixmap: QPixmap | None = None
        self.rotation: int = 0
        self.setMinimumSize(900, 700)

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

        pix = self.current_pixmap.transformed(
            QTransform().rotate(self.rotation),
            Qt.SmoothTransformation,
        )

        pix = pix.scaled(
            self.size() * 0.96,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        x = (self.width() - pix.width()) // 2
        y = (self.height() - pix.height()) // 2

        painter.drawPixmap(x, y, pix)

    def resizeEvent(self, event):
        self.update()
        super().resizeEvent(event)