from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QVBoxLayout,
)


class AIStatusDialog(QDialog):
    def __init__(self, status, response=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("AI Status")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setMinimumHeight(360)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(self.format_status(status, response))

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

    def format_status(self, status, response=None):
        availability = "Yes" if status.get("available") else "No"
        enabled = "Yes" if status.get("enabled") else "No"
        models = status.get("models", [])

        lines = [
            "AI Provider Status",
            "",
            "AI is not connected to metadata workflows yet.",
            "AI responses are informational only and require human approval.",
            "AI status checks and test prompts do not modify archive data.",
            "",
            f"Enabled: {enabled}",
            f"Provider Type: {status.get('provider_type', '')}",
            f"Provider: {status.get('provider_name', 'Unknown')}",
            f"Endpoint: {status.get('endpoint_url', '')}",
            f"Default Model: {status.get('default_model') or 'Not set'}",
            f"Available: {availability}",
        ]

        if status.get("error_message"):
            lines.extend([
                "",
                "Last Error",
                status["error_message"],
            ])

        lines.extend([
            "",
            "Available Models",
        ])

        if models:
            lines.extend(f"- {model}" for model in models)
        else:
            lines.append("No models reported.")

        if response is not None:
            lines.extend([
                "",
                "Last Response",
                f"Success: {'Yes' if response.success else 'No'}",
            ])

            if response.model_name:
                lines.append(f"Model: {response.model_name}")

            if response.error_message:
                lines.append(f"Error: {response.error_message}")

            if response.text:
                lines.extend([
                    "",
                    response.text,
                ])

        return "\n".join(lines)

    @staticmethod
    def show_status(status, response=None, parent=None):
        dialog = AIStatusDialog(status, response, parent)
        dialog.exec()
