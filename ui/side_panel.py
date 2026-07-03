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

    def build_ui(self):
        self.setFrameShape(QFrame.StyledPanel)

        self.setStyleSheet("""
            QFrame {
                background-color:#363636;
                border:1px solid #4a4a4a;
                border-radius:8px;
            }

            QLabel {
                border:none;
                background:transparent;
            }
        """)

        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size:12pt;
            font-weight:bold;
        """)

        self.value.setAlignment(Qt.AlignCenter)
        self.value.setStyleSheet("""
            font-size:18pt;
            font-weight:bold;
            color:#9e9e9e;
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def set_value(self, text: str, color: str = "#9e9e9e"):
        self.value.setText(text)
        self.value.setStyleSheet(f"""
            font-size:18pt;
            font-weight:bold;
            color:{color};
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
        self.rotation.set_value(f"{rotation}°", "#7fc8ff")

        self.back.set_value(
            "YES" if back else "NO",
            "#55ff55" if back else "#9e9e9e",
        )

        self.favorite.set_value(
            "YES" if favorite else "NO",
            "#ffd54a" if favorite else "#9e9e9e",
        )

        self.restore.set_value(
            "YES" if restore else "NO",
            "#ffb347" if restore else "#9e9e9e",
        )

        self.delete.set_value(
            "YES" if delete else "NO",
            "#ff6666" if delete else "#9e9e9e",
        )