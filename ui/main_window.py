from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from core.review_session import ReviewSession
from ui.header_panel import HeaderPanel
from ui.image_panel import ImagePanel
from ui.side_panel import SidePanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Archive Assistant")
        self.resize(1400, 900)

        self.session = ReviewSession()

        self.header_panel = HeaderPanel()
        self.image_panel = ImagePanel()
        self.side_panel = SidePanel()

        self.build_ui()
        self.create_menu()
        self.create_shortcuts()
        self.refresh_ui()

    def build_ui(self):
        content = QHBoxLayout()
        content.addWidget(self.image_panel, 8)
        content.addWidget(self.side_panel, 2)

        layout = QVBoxLayout()
        layout.addWidget(self.header_panel)
        layout.addLayout(content)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_menu(self):
        menu = self.menuBar().addMenu("&File")

        open_action = menu.addAction("Open Project")
        open_action.triggered.connect(self.open_project)

        menu.addSeparator()

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

    def create_shortcuts(self):
        bindings = {
            "Left": self.previous_image,
            "Right": self.next_image,
            "Space": self.next_image,
            "A": self.rotate_left,
            "D": self.rotate_right,
            "B": self.toggle_back,
            "F": self.toggle_favorite,
            "R": self.toggle_restore,
            "X": self.toggle_delete,
        }

        for key, callback in bindings.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(callback)
            self.addAction(action)

    def open_project(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Cropped Folder",
        )

        if not folder:
            return

        self.session.open_project(folder)

        if self.session.image_count == 0:
            QMessageBox.information(
                self,
                "No Images",
                "No supported image files found.",
            )
            return

        self.refresh_ui()

    def refresh_ui(self):
        current = self.session.current_file

        if current is not None:
            self.image_panel.load_image(
                current,
                self.session.state.rotation,
            )

        current_num, total = self.session.progress

        self.header_panel.update_progress(
            self.session.project_name,
            current_num,
            total,
        )

        self.refresh_status()

    def refresh_status(self):
        self.side_panel.update_status(
            rotation=self.session.state.rotation,
            back=self.session.state.has_back,
            favorite=self.session.state.favorite,
            restore=self.session.state.needs_restore,
            delete=self.session.state.delete,
        )

    def next_image(self):
        self.session.next_image()
        self.refresh_ui()

    def previous_image(self):
        self.session.previous_image()
        self.refresh_ui()

    def rotate_left(self):
        self.session.rotate_left()
        self.image_panel.set_rotation(self.session.state.rotation)
        self.refresh_status()

    def rotate_right(self):
        self.session.rotate_right()
        self.image_panel.set_rotation(self.session.state.rotation)
        self.refresh_status()

    def toggle_back(self):
        self.session.toggle_back()
        self.refresh_status()

    def toggle_favorite(self):
        self.session.toggle_favorite()
        self.refresh_status()

    def toggle_restore(self):
        self.session.toggle_restore()
        self.refresh_status()

    def toggle_delete(self):
        self.session.toggle_delete()
        self.refresh_status()