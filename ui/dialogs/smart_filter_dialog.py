from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class SmartFilterDialog(QDialog):
    def __init__(self, filters, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Smart Filters")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.filters = list(filters)

        self.list_widget = QListWidget()

        for smart_filter in self.filters:
            item = QListWidgetItem(smart_filter.name)
            item.setData(Qt.UserRole, smart_filter.id)
            item.setToolTip(smart_filter.description)
            self.list_widget.addItem(item)

        if self.list_widget.count():
            self.list_widget.setCurrentRow(0)

        self.list_widget.itemDoubleClicked.connect(self.accept)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Choose a smart filter:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self.list_widget.setFocus()

    def selected_filter_id(self):
        item = self.list_widget.currentItem()

        if item is None:
            return None

        return item.data(Qt.UserRole)

    @staticmethod
    def get_filter_id(filters, parent=None):
        dialog = SmartFilterDialog(filters, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.selected_filter_id()
