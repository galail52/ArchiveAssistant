from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QVBoxLayout,
)


class OCRStatusDialog(QDialog):
    def __init__(self, counts, parent=None):
        super().__init__(parent)

        self.setWindowTitle("OCR Status")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setMinimumHeight(320)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(self.format_counts(counts))

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.text.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            return

        super().keyPressEvent(event)

    def format_counts(self, counts):
        lines = [
            "OCR Foundation",
            "",
            "OCR engine integration is not implemented yet.",
            "Queued OCR jobs are planning records only.",
            "No metadata or image files are modified.",
            "",
            "Queue Status",
            f"Pending: {counts.get('pending', 0)}",
            f"Completed: {counts.get('completed', 0)}",
            f"Failed / Not Implemented: {counts.get('failed', 0)}",
        ]

        return "\n".join(lines)

    @staticmethod
    def show_status(counts, parent=None):
        dialog = OCRStatusDialog(counts, parent)
        dialog.exec()
