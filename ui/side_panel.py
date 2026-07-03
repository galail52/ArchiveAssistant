from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QGridLayout,
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

    # ---------------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout()

        title = QLabel("Review")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:20pt;
            font-weight:bold;
        """)

        layout.addWidget(title)

        layout.addSpacing(10)

        layout.addWidget(self.rotation)
        layout.addWidget(self.back)
        layout.addWidget(self.favorite)
        layout.addWidget(self.restore)
        layout.addWidget(self.delete)

        layout.addSpacing(20)

        keyboard_title = QLabel("Keyboard")

        keyboard_title.setAlignment(Qt.AlignCenter)

        keyboard_title.setStyleSheet("""
            font-size:16pt;
            font-weight:bold;
        """)

        layout.addWidget(keyboard_title)

        keyboard = QGridLayout()

        keyboard.setHorizontalSpacing(20)
        keyboard.setVerticalSpacing(8)

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

        self.setMinimumWidth(300)

    # ---------------------------------------------------------

    def rotation_label(self, rotation):

        return {
            0: "Normal",
            90: "Right",
            180: "Upside Down",
            270: "Left",
        }.get(rotation, str(rotation))

    # ---------------------------------------------------------

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
            "YES",
            back,
            "#55ff55",
        )

        if not back:
            self.back.set_value("NO")

        self.favorite.set_value(
            "YES",
            favorite,
            "#ffd54a",
        )

        if not favorite:
            self.favorite.set_value("NO")

        self.restore.set_value(
            "YES",
            restore,
            "#ffb347",
        )

        if not restore:
            self.restore.set_value("NO")

        self.delete.set_value(
            "YES",
            delete,
            "#ff6666",
        )

        if not delete:
            self.delete.set_value("NO")