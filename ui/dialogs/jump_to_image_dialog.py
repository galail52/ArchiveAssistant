from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
)


class JumpToImageDialog(QDialog):
    def __init__(self, current, total, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Go To Image")
        self.setModal(True)

        self.range_label = QLabel(f"Valid range: 1 to {total}")

        self.target = QSpinBox()
        self.target.setMinimum(1)
        self.target.setMaximum(total)
        self.target.setValue(current)
        self.target.selectAll()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout()
        layout.addRow(self.range_label)
        layout.addRow("Image number:", self.target)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.target.setFocus()
        self.target.selectAll()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
            return

        super().keyPressEvent(event)

    @staticmethod
    def get_target(current, total, parent=None):
        dialog = JumpToImageDialog(current, total, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.target.value()
