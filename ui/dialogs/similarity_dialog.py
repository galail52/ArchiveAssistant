from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QVBoxLayout,
)


class SimilarityDialog(QDialog):
    def __init__(self, groups, skipped_images=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Similar Images")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setMinimumHeight(380)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(
            self.format_groups(groups, skipped_images or [])
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

    def format_groups(self, groups, skipped_images):
        lines = [
            "Image Similarity Results",
            "",
            "No changes have been made.",
            "",
            f"Potential similar image groups: {len(groups)}",
        ]

        if skipped_images:
            lines.append(f"Skipped unsupported/corrupt images: {len(skipped_images)}")

        if not groups:
            lines.extend([
                "",
                "No similar image groups found.",
            ])
            return "\n".join(lines)

        for group in groups:
            lines.extend([
                "",
                group.group_id,
                "Images:",
            ])

            for image_id in group.image_ids:
                lines.append(f"- {Path(image_id).name}")

            lines.append("Matches:")

            for match in group.matches:
                source = Path(match.source_image_id).name
                target = Path(match.target_image_id).name
                score = f"{match.similarity_score:.2%}"
                match_type = match.match_type.replace("_", " ").title()
                lines.append(
                    f"- {source} <-> {target}: {score} ({match_type})"
                )

                if match.explanation:
                    lines.append(f"  {match.explanation}")

        return "\n".join(lines)

    @staticmethod
    def show_groups(groups, skipped_images=None, parent=None):
        dialog = SimilarityDialog(groups, skipped_images, parent)
        dialog.exec()
