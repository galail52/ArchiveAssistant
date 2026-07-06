from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame, QSizePolicy


class ThumbnailCard(QFrame):
    clicked = Signal(int)

    def __init__(self, thumbnail_cache):
        super().__init__()

        self.thumbnail_cache = thumbnail_cache

        self.index: int | None = None
        self.filename: Path | None = None
        self.selected = False
        self.pixmap = None

        self.favorite = False
        self.restore = False
        self.delete = False
        self.back = False

        self.setFixedSize(120, 136)
        self.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed,
        )

    def set_image(self, index: int, filename: Path):
        if self.index == index and self.filename == filename:
            return

        self.index = index
        self.filename = filename
        self.pixmap = self.thumbnail_cache.get(filename)
        self.setToolTip(filename.name)
        self.update()

    def clear(self):
        if (
            self.index is None
            and self.filename is None
            and self.pixmap is None
            and not self.favorite
            and not self.restore
            and not self.delete
            and not self.back
            and not self.selected
        ):
            return

        self.index = None
        self.filename = None
        self.selected = False
        self.pixmap = None
        self.favorite = False
        self.restore = False
        self.delete = False
        self.back = False
        self.setToolTip("")
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
        if self.index is not None:
            self.clicked.emit(self.index)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor("#2d2d2d"))

        border = QColor("#5a9cff") if self.selected else QColor("#555555")
        painter.setPen(border)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        if self.pixmap:
            x = (self.width() - self.pixmap.width()) // 2
            painter.drawPixmap(x, 6, self.pixmap)

        if self.index is None:
            return

        painter.setPen(Qt.white)
        painter.drawText(
            self.rect().adjusted(0, 100, 0, 0),
            Qt.AlignCenter,
            str(self.index + 1),
        )

        painter.drawText(
            self.rect().adjusted(4, 116, -4, 0),
            Qt.AlignCenter,
            self.flag_icons(),
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
