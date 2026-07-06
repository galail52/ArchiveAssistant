from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class StarRating(QWidget):
    def __init__(self, value=0, parent=None):
        super().__init__(parent)

        self._value = max(0, min(5, int(value)))
        self.buttons = []

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        clear = QPushButton("Clear")
        clear.clicked.connect(lambda: self.set_value(0))
        layout.addWidget(clear)

        for index in range(1, 6):
            button = QPushButton()
            button.setFixedWidth(34)
            button.clicked.connect(
                lambda _checked=False, rating=index: self.set_value(rating)
            )
            self.buttons.append(button)
            layout.addWidget(button)

        layout.addStretch(1)
        self.setLayout(layout)
        self.refresh()

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = max(0, min(5, int(value)))
        self.refresh()

    def refresh(self):
        for index, button in enumerate(self.buttons, start=1):
            button.setText("★" if index <= self._value else "☆")
            button.setStyleSheet("""
                QPushButton {
                    font-size: 16pt;
                    padding: 2px;
                }
            """)


class MetadataDialog(QDialog):
    def __init__(self, metadata, parent=None):
        super().__init__(parent)

        self.settings = QSettings(
            "ArchiveAssistant",
            "ArchiveAssistant",
        )

        self.setWindowTitle("Edit Metadata")
        self.setModal(True)
        self.setMinimumWidth(580)
        self.setMinimumHeight(520)

        self.people = QLineEdit(metadata.people)
        self.event = QLineEdit(metadata.event)
        self.location = QLineEdit(metadata.location)
        self.date_taken = QLineEdit(metadata.date_taken)
        self.date_taken.setPlaceholderText(
            "YYYY, YYYY-MM, YYYY-MM-DD, or Unknown"
        )
        self.keywords = QLineEdit(metadata.keywords)
        self.note_by = QLineEdit(metadata.note_by)

        self.confidence = StarRating(metadata.confidence)

        self.notes = QTextEdit()
        self.notes.setPlainText(metadata.notes)

        form = QFormLayout()
        form.addRow("People:", self.people)
        form.addRow("Event:", self.event)
        form.addRow("Location:", self.location)
        form.addRow("Date Taken:", self.date_taken)
        form.addRow("Keywords / Tags:", self.keywords)
        form.addRow("Notes:", self.notes)
        form.addRow("Note By:", self.note_by)
        form.addRow("Confidence:", self.confidence)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.save)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

        self.restore_dialog_geometry()
        self.original_values = self.values()

        self.people.setFocus()
        self.people.selectAll()

    def restore_dialog_geometry(self):
        geometry = self.settings.value("metadata_dialog/geometry")

        if geometry is not None:
            self.restoreGeometry(geometry)

    def save_dialog_geometry(self):
        self.settings.setValue(
            "metadata_dialog/geometry",
            self.saveGeometry(),
        )

    def save(self):
        if not self.valid_date_taken():
            QMessageBox.warning(
                self,
                "Invalid Date Taken",
                "Date Taken should be one of:\n\n"
                "1958\n"
                "1958-07\n"
                "1958-07-05\n"
                "Unknown\n\n"
                "Or leave it blank.",
            )
            self.date_taken.setFocus()
            self.date_taken.selectAll()
            return

        self.save_dialog_geometry()
        self.accept()

    def reject(self):
        if self.is_dirty():
            result = QMessageBox.question(
                self,
                "Discard Metadata Changes?",
                "Discard metadata changes?",
                QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )

            if result != QMessageBox.Discard:
                return

        self.save_dialog_geometry()
        super().reject()

    def is_dirty(self):
        return self.values() != self.original_values

    def valid_date_taken(self):
        value = self.date_taken.text().strip()

        if not value:
            return True

        if value.lower() == "unknown":
            return True

        formats = [
            "%Y",
            "%Y-%m",
            "%Y-%m-%d",
        ]

        for date_format in formats:
            try:
                parsed = datetime.strptime(value, date_format)

                if date_format == "%Y" and parsed.year < 1800:
                    return False

                return True
            except ValueError:
                continue

        return False

    def values(self):
        return {
            "people": self.clean_list(self.people.text()),
            "event": self.clean_text(self.event.text()),
            "location": self.clean_text(self.location.text()),
            "date_taken": self.clean_text(self.date_taken.text()),
            "keywords": self.clean_list(self.keywords.text()),
            "notes": self.clean_multiline(self.notes.toPlainText()),
            "note_by": self.clean_text(self.note_by.text()),
            "confidence": self.confidence.value(),
        }

    def clean_text(self, value):
        return " ".join(value.strip().split())

    def clean_list(self, value):
        parts = [
            self.clean_text(part)
            for part in value.split(",")
        ]

        return ", ".join(part for part in parts if part)

    def clean_multiline(self, value):
        lines = [
            self.clean_text(line)
            for line in value.strip().splitlines()
        ]

        return "\n".join(line for line in lines if line)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            return

        if event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.save()
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ControlModifier:
                self.save()
                return

            if self.focusWidget() is not self.notes:
                self.save()
                return

        super().keyPressEvent(event)

    @staticmethod
    def get_metadata(metadata, parent=None):
        dialog = MetadataDialog(metadata, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.values()