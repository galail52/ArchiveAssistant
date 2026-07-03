from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QSizePolicy, QVBoxLayout


class StatusCard(QFrame):
    def __init__(self, title: str):
        super().__init__()

        self.title = QLabel(title)
        self.value = QLabel("NO")

        self.build_ui()
        self.set_active(False)

    def build_ui(self):
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size:10pt;
            font-weight:bold;
            border:none;
            background:transparent;
        """)

        self.value.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 4, 6, 5)
        layout.setSpacing(1)
        layout.addWidget(self.title)
        layout.addWidget(self.value)

        self.setLayout(layout)

    def set_value(self, text: str, active=False, accent="#7fc8ff"):
        self.value.setText(text)
        self.set_active(active, accent)

    def set_active(self, active=False, accent="#7fc8ff"):
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
            font-size:15pt;
            font-weight:bold;
            color:{value_color};
            border:none;
            background:transparent;
        """)