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
        self.cards = []
        self.state_provider = None
        self.current_range = (None, None)

        self.setFixedHeight(148)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(5)

        self.setLayout(self.layout)

    def load_project(self, files, state_provider=None):
        self.files = files
        self.state_provider = state_provider
        self.current_index = 0
        self.current_range = (None, None)
        self.rebuild_cards()

    def set_current(self, index):
        if not self.files:
            return

        self.current_index = index
        visible_range = self.visible_range()

        if visible_range != self.current_range:
            self.rebuild_cards()
            return

        self.update_cards()

    def rebuild_cards(self):
        self.clear_cards()

        if not self.files:
            return

        start, end = self.visible_range()
        self.current_range = (start, end)

        for index in range(start, end):
            card = ThumbnailCard(index)
            card.set_thumbnail(self.files[index])
            card.clicked.connect(self.image_selected)

            self.cards.append(card)
            self.layout.addWidget(card)

        self.layout.addStretch()
        self.update_cards()

    def update_cards(self):
        for card in self.cards:
            card.set_selected(card.index == self.current_index)
            self.apply_flags(card)

    def clear_cards(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.cards.clear()

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
        if self.state_provider is None:
            return

        state = self.state_provider(self.files[card.index])

        card.set_flags(
            favorite=state.favorite,
            restore=state.needs_restore,
            delete=state.delete,
            back=state.has_back,
        )