from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class CommandPalette(QDialog):
    def __init__(self, current_number: int, total: int, parent=None):
        super().__init__(parent)

        self.total = total
        self.target_number = None

        self.setWindowTitle("Go To Image")
        self.setModal(True)
        self.setFixedWidth(360)

        self.label = QLabel(f"Go to image number 1 - {total}:")
        self.input = QLineEdit(str(current_number))
        self.ok_button = QPushButton("Go")
        self.cancel_button = QPushButton("Cancel")
        self.error = QLabel("")

        self.build_ui()
        self.connect_controls()

    def build_ui(self):
        self.input.selectAll()
        self.input.setAlignment(Qt.AlignCenter)

        self.error.setAlignment(Qt.AlignCenter)
        self.error.setStyleSheet("""
            color:#ff7777;
            font-weight:bold;
        """)

        buttons = QHBoxLayout()
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.error)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def connect_controls(self):
        self.ok_button.clicked.connect(self.accept_command)
        self.cancel_button.clicked.connect(self.reject)
        self.input.returnPressed.connect(self.accept_command)

    def accept_command(self):
        text = self.input.text().strip()

        if not text.isdigit():
            self.error.setText("Enter a number.")
            self.input.selectAll()
            return

        number = int(text)

        if number < 1 or number > self.total:
            self.error.setText(f"Use 1 - {self.total}.")
            self.input.selectAll()
            return

        self.target_number = number
        self.accept()

    @classmethod
    def get_target(cls, current_number: int, total: int, parent=None):
        dialog = cls(current_number, total, parent)

        if dialog.exec() == QDialog.Accepted:
            return dialog.target_number

        return None