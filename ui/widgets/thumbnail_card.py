from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame


class ThumbnailCard(QFrame):

    clicked = Signal(int)

    def __init__(self, index: int = 0):

        super().__init__()

        self.index = index

        self.selected = False

        self.pixmap = None

        self.favorite = False
        self.restore = False
        self.delete = False
        self.back = False

        self.setFixedSize(120, 150)

    # ---------------------------------------------------------

    def set_thumbnail(self, filename: Path):

        pix = QPixmap(str(filename))

        self.pixmap = pix.scaled(
            100,
            100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.update()

    # ---------------------------------------------------------

    def set_selected(self, selected: bool):

        self.selected = selected

        self.update()

    # ---------------------------------------------------------

    def set_flags(
        self,
        favorite=False,
        restore=False,
        delete=False,
        back=False,
    ):

        self.favorite = favorite
        self.restore = restore
        self.delete = delete
        self.back = back

        self.update()

    # ---------------------------------------------------------

    def mousePressEvent(self, event):

        self.clicked.emit(self.index)

    # ---------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor("#2d2d2d"))

        border = QColor("#5a9cff") if self.selected else QColor("#555555")

        painter.setPen(border)

        painter.drawRect(0, 0, self.width()-1, self.height()-1)

        if self.pixmap:

            x = (self.width() - self.pixmap.width()) // 2

            painter.drawPixmap(x, 8, self.pixmap)

        painter.setPen(Qt.white)

        painter.drawText(
            self.rect().adjusted(0, 112, 0, 0),
            Qt.AlignCenter,
            str(self.index + 1),
        )

        icons = ""

        if self.favorite:
            icons += "⭐ "

        if self.restore:
            icons += "🛠 "

        if self.back:
            icons += "📄 "

        if self.delete:
            icons += "🗑"

        painter.drawText(
            self.rect().adjusted(4, 128, -4, 0),
            Qt.AlignCenter,
            icons,
        )