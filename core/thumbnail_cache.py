from collections import OrderedDict
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ThumbnailCache:
    def __init__(self, max_items: int = 500):
        self.max_items = max_items
        self.items: OrderedDict[str, QPixmap] = OrderedDict()

    def get(self, filename: Path) -> QPixmap:
        cache_key = str(filename)

        if cache_key in self.items:
            pixmap = self.items.pop(cache_key)
            self.items[cache_key] = pixmap
            return pixmap

        pixmap = QPixmap(cache_key).scaled(
            100,
            92,
            Qt.KeepAspectRatio,
            Qt.FastTransformation,
        )

        self.items[cache_key] = pixmap
        self.trim()

        return pixmap

    def preload(self, files):
        for filename in files:
            self.get(filename)

    def clear(self):
        self.items.clear()

    def trim(self):
        while len(self.items) > self.max_items:
            self.items.popitem(last=False)