from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QVBoxLayout,
)


class CollectionHealthDialog(QDialog):
    def __init__(self, report, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Collection Health")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setMinimumHeight(520)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(self.format_report(report))

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

    def format_report(self, report):
        confidence_lines = [
            f"{rating} stars: {count}"
            for rating, count in sorted(
                report.confidence_distribution.items(),
                reverse=True,
            )
        ]

        sections = [
            "Archive Totals",
            f"Images: {report.total_images}",
            "",
            "Review Status",
            f"Reviewed: {report.reviewed}",
            f"Favorites: {report.favorites}",
            f"Needs Restore: {report.restore}",
            f"Needs Research: {report.needs_research}",
            f"Delete: {report.delete}",
            "",
            "Missing Metadata",
            f"People: {report.missing_people}",
            f"Date: {report.missing_date}",
            f"Location: {report.missing_location}",
            f"Event: {report.missing_event}",
            "",
            "Metadata Completion",
            f"{report.completeness:.1f}%",
            "",
            "Confidence Distribution",
            *confidence_lines,
            "",
            "Archive Quality Score",
            f"{report.archive_quality_score:.1f}%",
        ]

        return "\n".join(sections)

    @staticmethod
    def show_report(report, parent=None):
        dialog = CollectionHealthDialog(report, parent)
        dialog.exec()
