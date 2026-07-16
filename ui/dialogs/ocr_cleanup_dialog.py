from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class OCRCleanupDialog(QDialog):
    ACTION_CLOSED = "closed"
    ACTION_ADD_TO_METADATA = "add_to_metadata"

    def __init__(self, review, parent=None):
        super().__init__(parent)
        self.review = review
        self.action = self.ACTION_CLOSED

        self.setWindowTitle("AI OCR Cleanup Review")
        self.setModal(True)
        self.resize(1000, 650)

        original, _original_editor = self._text_panel(
            "Original OCR",
            review.original_text,
            read_only=True,
        )
        cleaned, self.cleaned_editor = self._text_panel(
            "Suggested Cleanup (editable)",
            review.cleaned_text,
            read_only=False,
        )

        comparison = QHBoxLayout()
        comparison.addWidget(original, 1)
        comparison.addWidget(cleaned, 1)

        details = QTextEdit()
        details.setReadOnly(True)
        details.setMaximumHeight(190)
        details.setPlainText(self._details_text(review))

        copy_button = QPushButton("Copy Cleaned Text")
        copy_button.clicked.connect(self.copy_cleaned_text)

        metadata_button = QPushButton("Add to Metadata")
        metadata_button.clicked.connect(self.add_to_metadata)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        footer = QHBoxLayout()
        footer.addWidget(copy_button)
        footer.addWidget(metadata_button)
        footer.addStretch(1)
        footer.addWidget(buttons)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "Edit the suggestion as needed. Add to Metadata saves the approved text to Notes."
        ))
        layout.addLayout(comparison, 1)
        layout.addWidget(QLabel("Uncertainty and Corrections"))
        layout.addWidget(details)
        layout.addLayout(footer)
        self.setLayout(layout)

        self.cleaned_editor.setFocus()

    def copy_cleaned_text(self):
        QGuiApplication.clipboard().setText(self.cleaned_text())

    def add_to_metadata(self):
        if not self.cleaned_text().strip():
            return
        self.action = self.ACTION_ADD_TO_METADATA
        self.accept()

    def cleaned_text(self):
        return self.cleaned_editor.toPlainText()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    @staticmethod
    def _text_panel(title, text, read_only):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        editor = QTextEdit()
        editor.setReadOnly(read_only)
        editor.setPlainText(text)
        layout.addWidget(QLabel(title))
        layout.addWidget(editor)
        widget.setLayout(layout)
        return widget, editor

    @staticmethod
    def _details_text(review):
        lines = []
        if review.confidence is not None:
            lines.append(f"Confidence: {review.confidence:.0%}")

        lines.extend(["", "Uncertain portions:"])
        lines.extend(f"- {item}" for item in review.uncertain_portions)
        if not review.uncertain_portions:
            lines.append("- None reported")

        lines.extend(["", "Corrections:"])
        lines.extend(f"- {item}" for item in review.corrections)
        if not review.corrections:
            lines.append("- None reported")

        if review.warnings:
            lines.extend(["", "Warnings:"])
            lines.extend(f"- {item}" for item in review.warnings)

        return "\n".join(lines)

    @staticmethod
    def show_review(review, parent=None):
        dialog = OCRCleanupDialog(review, parent)
        dialog.exec()
        return dialog.action, dialog.cleaned_text()
