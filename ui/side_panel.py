from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QGridLayout,
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
        self.setMinimumWidth(260)
        self.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding,
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        title = QLabel("Review")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:18pt;
            font-weight:bold;
        """)

        layout.addWidget(title)

        for card in self.status_cards:
            card.setMinimumHeight(58)
            card.setMaximumHeight(68)
            layout.addWidget(card)

        keyboard_title = QLabel("Keyboard")
        keyboard_title.setAlignment(Qt.AlignCenter)
        keyboard_title.setStyleSheet("""
            font-size:14pt;
            font-weight:bold;
            margin-top:8px;
        """)

        layout.addWidget(keyboard_title)

        keyboard = QGridLayout()
        keyboard.setHorizontalSpacing(14)
        keyboard.setVerticalSpacing(2)

        shortcuts = [
            ("← / →", "Previous / Next"),
            ("Space", "Next Image"),
            ("A", "Rotate Left"),
            ("D", "Rotate Right"),
            ("B", "Toggle Back"),
            ("F", "Favorite"),
            ("R", "Restore"),
            ("X", "Delete"),
            ("Esc", "Exit"),
        ]

        for row, (key, desc) in enumerate(shortcuts):
            key_label = QLabel(key)
            key_label.setStyleSheet(
                "font-weight:bold;color:#7fc8ff;"
            )

            desc_label = QLabel(desc)

            keyboard.addWidget(key_label, row, 0)
            keyboard.addWidget(desc_label, row, 1)

        layout.addLayout(keyboard)
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