from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from core.command_model import CommandModel


class CommandPalette(QDialog):
    def __init__(self, registry, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.setMinimumWidth(420)

        self.model = CommandModel(registry)
        self.selected_command = None

        self.prompt = QLabel("Command")
        self.edit = QLineEdit()
        self.edit.textChanged.connect(self.update_matches)

        self.preview = QLabel("")
        self.preview.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.prompt)
        layout.addWidget(self.edit)
        layout.addWidget(self.preview)
        layout.addWidget(buttons)

        self.setLayout(layout)

        self.update_matches()

    def update_matches(self):
        self.model.set_query(self.edit.text())

        command = self.model.first_match()
        self.selected_command = command

        if command is None:
            self.preview.setText("No matching commands.")
            return

        shortcut = command.shortcut or ""

        self.preview.setText(
            f"{command.category}\n\n"
            f"{command.name}\n"
            f"{shortcut}"
        )

    @staticmethod
    def get_command(registry, parent=None):
        dialog = CommandPalette(registry, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.selected_command