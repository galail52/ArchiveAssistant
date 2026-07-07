from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class ImageSelectionDialog(QDialog):
    def __init__(self, title, image_paths, current_path=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(480)
        self.image_paths = [
            Path(path)
            for path in image_paths
            if current_path is None or Path(path) != Path(current_path)
        ]

        self.list_widget = QListWidget()

        for image_path in self.image_paths:
            item = QListWidgetItem(image_path.name)
            item.setData(Qt.UserRole, str(image_path))
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
        layout.addWidget(QLabel("Choose an image:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.list_widget.setFocus()

    def selected_image_id(self):
        item = self.list_widget.currentItem()

        if item is None:
            return None

        return item.data(Qt.UserRole)

    @staticmethod
    def get_image_id(title, image_paths, current_path=None, parent=None):
        dialog = ImageSelectionDialog(
            title,
            image_paths,
            current_path,
            parent,
        )

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.selected_image_id()


class RelationshipSelectionDialog(QDialog):
    def __init__(self, title, relationships, current_image_id=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(520)
        self.relationships = list(relationships)
        self.current_image_id = str(current_image_id or "")

        self.list_widget = QListWidget()

        for relationship in self.relationships:
            item = QListWidgetItem(self.relationship_label(relationship))
            item.setData(Qt.UserRole, relationship.relationship_id)
            item.setData(Qt.UserRole + 1, self.related_image_id(relationship))
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
        layout.addWidget(QLabel("Choose a relationship:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.list_widget.setFocus()

    def related_image_id(self, relationship):
        if relationship.source_image_id == self.current_image_id:
            return relationship.target_image_id

        return relationship.source_image_id

    def relationship_label(self, relationship):
        related = Path(self.related_image_id(relationship)).name
        label = relationship.relationship_type.value.replace("_", " ").title()
        return f"{label}: {related}"

    def selected_relationship_id(self):
        item = self.list_widget.currentItem()

        if item is None:
            return None

        return item.data(Qt.UserRole)

    def selected_related_image_id(self):
        item = self.list_widget.currentItem()

        if item is None:
            return None

        return item.data(Qt.UserRole + 1)

    @staticmethod
    def get_relationship_id(
        title,
        relationships,
        current_image_id=None,
        parent=None,
    ):
        dialog = RelationshipSelectionDialog(
            title,
            relationships,
            current_image_id,
            parent,
        )

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.selected_relationship_id()

    @staticmethod
    def get_related_image_id(
        title,
        relationships,
        current_image_id=None,
        parent=None,
    ):
        dialog = RelationshipSelectionDialog(
            title,
            relationships,
            current_image_id,
            parent,
        )

        if dialog.exec() != QDialog.Accepted:
            return None

        return dialog.selected_related_image_id()
