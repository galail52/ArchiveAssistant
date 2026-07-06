from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)


class MetadataDialog(QDialog):
    def __init__(self, metadata, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Metadata")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setMinimumHeight(480)

        self.people = QLineEdit(metadata.people)
        self.note_by = QLineEdit(metadata.note_by)
        self.event = QLineEdit(metadata.event)
        self.location = QLineEdit(metadata.location)
        self.date_taken = QLineEdit(metadata.date_taken)

        self.notes = QTextEdit()
        self.notes.setPlainText(metadata.notes)

        form = QFormLayout()
        form.addRow("People:", self.people)
        form.addRow("Notes:", self.notes)
        form.addRow("Note By:", self.note_by)
        form.addRow("Event:", self.event)
        form.addRow("Location:", self.location)
        form.addRow("Date Taken:", self.date_taken)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def values(self):
        return {
            "people": self.people.text().strip(),
            "notes": self.notes.toPlainText().strip(),
            "note_by": self.note_by.text().strip(),
            "event": self.event.text().strip(),
            "location": self.location.text().strip(),
            "date_taken": self.date_taken.text().strip(),
        }

    @staticmethod
    def get_metadata(metadata, parent=None):
        dialog = MetadataDialog(metadata, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.values()