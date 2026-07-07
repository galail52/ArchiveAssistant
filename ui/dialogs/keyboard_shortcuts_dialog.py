from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class KeyboardShortcutsDialog(QDialog):
    def __init__(self, help_text, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setMinimumHeight(520)

        shortcuts = QLabel(help_text)
        shortcuts.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        shortcuts.setTextInteractionFlags(Qt.TextSelectableByKeyboard)
        shortcuts.setStyleSheet("""
            font-family:Consolas, monospace;
            font-size:10pt;
            color:#d0d0d0;
        """)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        layout.addWidget(shortcuts, 1)
        layout.addWidget(buttons)
        self.setLayout(layout)

        shortcuts.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            return

        super().keyPressEvent(event)

    @staticmethod
    def show_help(help_text, parent=None):
        dialog = KeyboardShortcutsDialog(help_text, parent)
        dialog.exec()
