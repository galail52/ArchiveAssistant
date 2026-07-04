from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class FindFilenameDialog(QDialog):
    def __init__(self, files, parent=None):
        super().__init__(parent)

        self.files = list(files)
        self.selected_index = None

        self.setWindowTitle("Find Filename")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setMinimumHeight(420)

        self.label = QLabel("Search filename:")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Example: IMG_3487 or Christmas")

        self.results = QListWidget()

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.search.textChanged.connect(self.refresh_results)
        self.search.returnPressed.connect(self.accept_current)
        self.results.itemDoubleClicked.connect(self.accept_item)
        self.buttons.accepted.connect(self.accept_current)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.search)
        layout.addWidget(self.results)
        layout.addWidget(self.buttons)

        self.setLayout(layout)
        self.refresh_results()

    def refresh_results(self):
        query = self.search.text().strip().lower()
        self.results.clear()

        if not query:
            return

        for index, file_path in enumerate(self.files):
            name = Path(file_path).name

            if query in name.lower():
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, index)
                self.results.addItem(item)

        if self.results.count() > 0:
            self.results.setCurrentRow(0)

    def accept_current(self):
        item = self.results.currentItem()

        if item is None:
            return

        self.selected_index = item.data(Qt.UserRole)
        self.accept()

    def accept_item(self, item):
        self.selected_index = item.data(Qt.UserRole)
        self.accept()

    @staticmethod
    def get_index(files, parent=None):
        dialog = FindFilenameDialog(files, parent)

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.selected_index