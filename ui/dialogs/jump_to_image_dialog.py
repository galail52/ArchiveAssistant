from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
)


class JumpToImageDialog(QDialog):
    def __init__(self, current, total, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Go To Image")
        self.setModal(True)

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
        layout.addRow("Image number:", self.target)
        layout.addWidget(buttons)

        self.setLayout(layout)

    @staticmethod
    def get_target(current, total, parent=None):
        dialog = JumpToImageDialog(current, total, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.target.value()