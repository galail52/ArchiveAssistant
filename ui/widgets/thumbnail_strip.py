from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget,
)

from ui.widgets.thumbnail_card import ThumbnailCard


class ThumbnailStrip(QWidget):

    image_selected = Signal(int)

    WINDOW_SIZE = 9

    def __init__(self):

        super().__init__()

        self.files = []

        self.current_index = 0

        self.cards = []

        self.layout = QHBoxLayout()

        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(6)

        self.setLayout(self.layout)

    # ---------------------------------------------------------

    def load_project(self, files):

        self.files = files

        self.current_index = 0

        self.refresh()

    # ---------------------------------------------------------

    def set_current(self, index):

        self.current_index = index

        self.refresh()

    # ---------------------------------------------------------

    def refresh(self):

        #
        # Clear old cards
        #

        while self.layout.count():

            item = self.layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.deleteLater()

        self.cards.clear()

        if not self.files:
            return

        start = max(
            0,
            self.current_index - self.WINDOW_SIZE // 2
        )

        end = min(
            len(self.files),
            start + self.WINDOW_SIZE
        )

        if end - start < self.WINDOW_SIZE:

            start = max(
                0,
                end - self.WINDOW_SIZE
            )

        for index in range(start, end):

            card = ThumbnailCard(index)

            card.set_thumbnail(
                self.files[index]
            )

            card.set_selected(
                index == self.current_index
            )

            card.clicked.connect(
                self.image_selected
            )

            self.cards.append(card)

            self.layout.addWidget(card)

        self.layout.addStretch()