from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from ui.widgets.thumbnail_card import ThumbnailCard


class ThumbnailStrip(QWidget):
    image_selected = Signal(int)

    WINDOW_SIZE = 9

    def __init__(self):
        super().__init__()

        self.files = []
        self.current_index = 0
        self.state_provider = None

        self.setFixedHeight(144)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(5)

        self.cards = [
            ThumbnailCard()
            for _ in range(self.WINDOW_SIZE)
        ]

        for card in self.cards:
            card.clicked.connect(self.image_selected)
            self.layout.addWidget(card)

        self.layout.addStretch()
        self.setLayout(self.layout)

        self.clear_cards()

    def load_project(self, files, state_provider=None):
        self.files = files
        self.state_provider = state_provider
        self.current_index = 0
        self.update_cards()

    def set_current(self, index):
        if not self.files:
            self.current_index = 0
            self.clear_cards()
            return

        self.current_index = index
        self.update_cards()

    def update_cards(self):
        if not self.files:
            self.clear_cards()
            return

        start, end = self.visible_range()

        for slot, card in enumerate(self.cards):
            index = start + slot

            if index >= end:
                card.clear()
                card.hide()
                continue

            card.show()
            card.set_image(index, self.files[index])
            card.set_selected(index == self.current_index)
            self.apply_flags(card)

    def clear_cards(self):
        for card in self.cards:
            card.clear()
            card.hide()

    def visible_range(self):
        start = max(
            0,
            self.current_index - self.WINDOW_SIZE // 2,
        )

        end = min(
            len(self.files),
            start + self.WINDOW_SIZE,
        )

        if end - start < self.WINDOW_SIZE:
            start = max(
                0,
                end - self.WINDOW_SIZE,
            )

        return start, end

    def apply_flags(self, card):
        if self.state_provider is None or card.index is None:
            return

        state = self.state_provider(self.files[card.index])

        card.set_flags(
            favorite=state.favorite,
            restore=state.needs_restore,
            delete=state.delete,
            back=state.has_back,
        )