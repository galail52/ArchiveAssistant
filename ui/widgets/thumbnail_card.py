from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QSizePolicy


class ThumbnailCard(QFrame):
    clicked = Signal(int)

    _cache: dict[str, QPixmap] = {}

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
        self.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed,
        )

    def set_thumbnail(self, filename: Path):
        cache_key = str(filename)

        if cache_key not in self._cache:
            pixmap = QPixmap(cache_key).scaled(
                100,
                100,
                Qt.KeepAspectRatio,
                Qt.FastTransformation,
            )

            self._cache[cache_key] = pixmap

        self.pixmap = self._cache[cache_key]
        self.update()

    def set_selected(self, selected: bool):
        if self.selected == selected:
            return

        self.selected = selected
        self.update()

    def set_flags(
        self,
        favorite=False,
        restore=False,
        delete=False,
        back=False,
    ):
        changed = (
            self.favorite != favorite
            or self.restore != restore
            or self.delete != delete
            or self.back != back
        )

        self.favorite = favorite
        self.restore = restore
        self.delete = delete
        self.back = back

        if changed:
            self.update()

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor("#2d2d2d"))

        border = QColor("#5a9cff") if self.selected else QColor("#555555")
        painter.setPen(border)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        if self.pixmap:
            x = (self.width() - self.pixmap.width()) // 2
            painter.drawPixmap(x, 8, self.pixmap)

        painter.setPen(Qt.white)
        painter.drawText(
            self.rect().adjusted(0, 112, 0, 0),
            Qt.AlignCenter,
            str(self.index + 1),
        )

        icons = self.flag_icons()

        painter.drawText(
            self.rect().adjusted(4, 128, -4, 0),
            Qt.AlignCenter,
            icons,
        )

    def flag_icons(self):
        icons = []

        if self.favorite:
            icons.append("⭐")

        if self.restore:
            icons.append("🛠")

        if self.back:
            icons.append("📄")

        if self.delete:
            icons.append("🗑")

        return " ".join(icons)