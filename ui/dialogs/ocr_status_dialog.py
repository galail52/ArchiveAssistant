from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QVBoxLayout,
)


class OCRStatusDialog(QDialog):
    def __init__(self, counts, latest_result=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("OCR Status")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setMinimumHeight(320)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(
            self.format_counts(counts, latest_result)
        )

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

    def format_counts(self, counts, latest_result=None):
        available = "Yes" if counts.get("engine_available") else "No"
        engine_message = counts.get("engine_message", "")

        lines = [
            "OCR Status",
            "",
            f"Engine: {counts.get('engine_name', 'Unknown')}",
            f"Engine Available: {available}",
        ]

        if engine_message:
            lines.append(f"Engine Message: {engine_message}")

        lines.extend([
            "No metadata or image files are modified.",
            "",
            "Queue Status",
            f"Pending: {counts.get('pending', 0)}",
            f"Completed: {counts.get('completed', 0)}",
            f"Failed: {counts.get('failed', 0)}",
        ])

        if latest_result is not None:
            lines.extend([
                "",
                "Latest OCR Result",
                f"Image: {latest_result.image_id}",
                f"Status: {latest_result.status.value}",
                f"Engine: {latest_result.engine_name}",
            ])

            if latest_result.executed_at is not None:
                lines.append(
                    f"Executed: {latest_result.executed_at.isoformat()}"
                )

            if latest_result.warnings:
                lines.append("")
                lines.append("Warnings")
                lines.extend(latest_result.warnings)

            if latest_result.errors:
                lines.append("")
                lines.append("Errors")
                lines.extend(latest_result.errors)

            lines.extend([
                "",
                "Extracted Text",
                latest_result.raw_text,
            ])

        return "\n".join(lines)

    @staticmethod
    def show_status(counts, latest_result=None, parent=None):
        dialog = OCRStatusDialog(counts, latest_result, parent)
        dialog.exec()
