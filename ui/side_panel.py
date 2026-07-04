from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.status_card import StatusCard


class SidePanel(QWidget):
    def __init__(self):
        super().__init__()

        self.rotation = StatusCard("↻ Orientation")
        self.back = StatusCard("📄 Back")
        self.favorite = StatusCard("⭐ Favorite")
        self.restore = StatusCard("🛠 Restore")
        self.delete = StatusCard("🗑 Delete")

        self.build_ui()
        self.update_status()

    def build_ui(self):
        self.setFixedWidth(330)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(7)

        title = QLabel("Review")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:18pt;
            font-weight:bold;
        """)

        layout.addWidget(title)

        for card in self.status_cards:
            card.setMinimumHeight(56)
            card.setMaximumHeight(62)
            layout.addWidget(card)

        keyboard_title = QLabel("Keyboard")
        keyboard_title.setAlignment(Qt.AlignCenter)
        keyboard_title.setStyleSheet("""
            font-size:14pt;
            font-weight:bold;
            margin-top:8px;
        """)

        layout.addWidget(keyboard_title)

        keyboard = QLabel(
            "← / →       Previous / Next\n"
            "Space       Next Image\n"
            "PgUp/Dn     Jump 10\n"
            "Ctrl+←/→    Jump 50\n"
            "Home/End    First / Last\n"
            "G           Go To Image\n"
            "1           Fit Image\n"
            "2           100% Zoom\n"
            "3           200% Zoom\n"
            "4           400% Zoom\n"
            "A / D       Rotate\n"
            "B           Toggle Back\n"
            "F           Favorite\n"
            "R           Restore\n"
            "X           Delete\n"
            "Esc         Exit"
        )

        keyboard.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        keyboard.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )
        keyboard.setStyleSheet("""
            font-family:Consolas, monospace;
            font-size:10pt;
            line-height:105%;
            color:#bdbdbd;
        """)

        layout.addWidget(keyboard)
        layout.addStretch()

        self.setLayout(layout)

    @property
    def status_cards(self):
        return [
            self.rotation,
            self.back,
            self.favorite,
            self.restore,
            self.delete,
        ]

    def rotation_label(self, rotation):
        return {
            0: "Normal",
            90: "Right",
            180: "Upside Down",
            270: "Left",
        }.get(rotation, str(rotation))

    def update_status(
        self,
        rotation=0,
        back=False,
        favorite=False,
        restore=False,
        delete=False,
    ):
        self.rotation.set_value(
            self.rotation_label(rotation),
            rotation != 0,
            "#7fc8ff",
        )

        self.back.set_value(
            "YES" if back else "NO",
            back,
            "#55ff55",
        )

        self.favorite.set_value(
            "YES" if favorite else "NO",
            favorite,
            "#ffd54a",
        )

        self.restore.set_value(
            "YES" if restore else "NO",
            restore,
            "#ffb347",
        )

        self.delete.set_value(
            "YES" if delete else "NO",
            delete,
            "#ff6666",
        )