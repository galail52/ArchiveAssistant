from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class StatusCard(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.title = QLabel(title)
        self.value = QLabel("NO")
        self.build_ui()
        self.set_active(False)

    def build_ui(self):
        self.setFrameShape(QFrame.StyledPanel)

        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size:12pt;
            font-weight:bold;
            border:none;
            background:transparent;
        """)

        self.value.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def set_value(
        self,
        text: str,
        active: bool = False,
        accent: str = "#7fc8ff",
    ):
        self.value.setText(text)
        self.set_active(active, accent)

    def set_active(
        self,
        active: bool,
        accent: str = "#7fc8ff",
    ):
        border = accent if active else "#4a4a4a"
        background = "#3f3f3f" if active else "#363636"
        value_color = accent if active else "#9e9e9e"

        self.setStyleSheet(f"""
            QFrame {{
                background-color:{background};
                border:2px solid {border};
                border-radius:8px;
            }}

            QLabel {{
                border:none;
                background:transparent;
            }}
        """)

        self.value.setStyleSheet(f"""
            font-size:18pt;
            font-weight:bold;
            color:{value_color};
            border:none;
            background:transparent;
        """)


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

        layout.addSpacing(15)

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
            key_label.setStyleSheet("font-weight:bold; color:#7fc8ff;")

            desc_label = QLabel(desc)
            desc_label.setWordWrap(False)

            keyboard.addWidget(key_label, row, 0)
            keyboard.addWidget(desc_label, row, 1)

        layout.addLayout(keyboard)
        layout.addStretch()

        self.setLayout(layout)
        self.setMinimumWidth(300)

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
            active=rotation != 0,
            accent="#7fc8ff",
        )

        self.back.set_value(
            "YES" if back else "NO",
            active=back,
            accent="#55ff55",
        )

        self.favorite.set_value(
            "YES" if favorite else "NO",
            active=favorite,
            accent="#ffd54a",
        )

        self.restore.set_value(
            "YES" if restore else "NO",
            active=restore,
            accent="#ffb347",
        )

        self.delete.set_value(
            "YES" if delete else "NO",
            active=delete,
            accent="#ff6666",
        )

    def rotation_label(self, rotation: int) -> str:
        labels = {
            0: "Normal",
            90: "Right",
            180: "Upside Down",
            270: "Left",
        }

        return labels.get(rotation % 360, f"{rotation}°")