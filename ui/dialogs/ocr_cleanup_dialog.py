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
    def __init__(self, review, parent=None):
        super().__init__(parent)
        self.review = review

        self.setWindowTitle("AI OCR Cleanup Review")
        self.setModal(True)
        self.resize(1000, 650)

        original = self._text_panel("Original OCR", review.original_text)
        cleaned = self._text_panel("Suggested Cleanup", review.cleaned_text)

        comparison = QHBoxLayout()
        comparison.addWidget(original, 1)
        comparison.addWidget(cleaned, 1)

        details = QTextEdit()
        details.setReadOnly(True)
        details.setMaximumHeight(190)
        details.setPlainText(self._details_text(review))

        copy_button = QPushButton("Copy Cleaned Text")
        copy_button.clicked.connect(self.copy_cleaned_text)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        footer = QHBoxLayout()
        footer.addWidget(copy_button)
        footer.addStretch(1)
        footer.addWidget(buttons)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "AI suggestion only. Original OCR is preserved and no archive data is changed."
        ))
        layout.addLayout(comparison, 1)
        layout.addWidget(QLabel("Uncertainty and Corrections"))
        layout.addWidget(details)
        layout.addLayout(footer)
        self.setLayout(layout)

        copy_button.setFocus()

    def copy_cleaned_text(self):
        QGuiApplication.clipboard().setText(self.review.cleaned_text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    @staticmethod
    def _text_panel(title, text):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(text)
        layout.addWidget(QLabel(title))
        layout.addWidget(editor)
        widget.setLayout(layout)
        return widget

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
