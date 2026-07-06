from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)


FIELD_LABELS = {
    "people": "People",
    "event": "Event",
    "location": "Location",
    "date_taken": "Date",
    "keywords": "Keywords",
    "notes": "Notes",
    "note_by": "Note Author",
    "confidence": "Confidence",
}


class MetadataFieldDialog(QDialog):
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.checkboxes = []

        layout = QVBoxLayout()

        for field in fields:
            checkbox = QCheckBox(FIELD_LABELS.get(field, field))
            checkbox.setChecked(True)
            checkbox.setProperty("field_name", field)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        if self.checkboxes:
            self.checkboxes[0].setFocus()

    def selected_fields(self):
        return [
            checkbox.property("field_name")
            for checkbox in self.checkboxes
            if checkbox.isChecked()
        ]

    @staticmethod
    def get_fields(title, fields, parent=None):
        dialog = MetadataFieldDialog(title, fields, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.selected_fields()
