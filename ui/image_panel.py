"""
Archive Assistant
-----------------

Image Panel

Responsible for:
- Displaying the current image
- Preview rotation
- Auto scaling
- Keeping the image centered

Author:
Trent + ChatGPT
"""

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

    # ---------------------------------------------------------

    def load_image(self, filename: Path):

        self.current_pixmap = QPixmap(str(filename))

        self.rotation = 0

        self.update()

    # ---------------------------------------------------------

    def rotate_left(self):

        self.rotation -= 90

        self.update()

    # ---------------------------------------------------------

    def rotate_right(self):

        self.rotation += 90

        self.update()

    # ---------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        #
        # Background
        #

        painter.fillRect(
            self.rect(),
            QColor("#1f1f1f")
        )

        if self.current_pixmap is None:
            return

        #
        # Rotate
        #

        pix = self.current_pixmap.transformed(
            QTransform().rotate(self.rotation),
            Qt.SmoothTransformation,
        )

        #
        # Scale
        #

        pix = pix.scaled(
            self.size() * 0.96,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        #
        # Center
        #

        x = (self.width() - pix.width()) // 2
        y = (self.height() - pix.height()) // 2

        painter.drawPixmap(x, y, pix)

    # ---------------------------------------------------------

    def resizeEvent(self, event):

        self.update()

        super().resizeEvent(event)