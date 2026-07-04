from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.review_session import ReviewSession
from ui.dialogs.command_palette import CommandPalette
from ui.header_panel import HeaderPanel
from ui.image_panel import ImagePanel
from ui.side_panel import SidePanel
from ui.widgets.thumbnail_strip import ThumbnailStrip


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Archive Assistant")
        self.resize(1400, 900)
        self.setMinimumSize(900, 650)

        self.session = ReviewSession()

        self.header_panel = HeaderPanel()
        self.image_panel = ImagePanel()
        self.side_panel = SidePanel()
        self.thumbnail_strip = ThumbnailStrip()

        self.previous_button = QPushButton("◀ Previous")
        self.next_button = QPushButton("Next ▶")

        self.build_ui()
        self.create_menu()
        self.create_shortcuts()
        self.connect_controls()
        self.refresh_ui()

    def build_ui(self):
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(8)
        content.addWidget(self.image_panel, 1)
        content.addWidget(self.side_panel)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addWidget(self.previous_button)
        buttons.addWidget(self.next_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(self.header_panel)
        layout.addLayout(content, 1)
        layout.addWidget(self.thumbnail_strip)
        layout.addLayout(buttons)

        container = QWidget()
        container.setLayout(layout)
        container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

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
            "Home": self.first_image,
            "End": self.last_image,
            "PageUp": self.jump_back,
            "PageDown": self.jump_forward,
            "Ctrl+Left": self.jump_back_far,
            "Ctrl+Right": self.jump_forward_far,
            "G": self.open_command_palette,
            "1": self.zoom_fit,
            "2": self.zoom_100,
            "3": self.zoom_200,
            "4": self.zoom_400,
            "A": self.rotate_left,
            "D": self.rotate_right,
            "B": self.toggle_back,
            "F": self.toggle_favorite,
            "R": self.toggle_restore,
            "X": self.toggle_delete,
            "Esc": self.close,
        }

        for key, callback in bindings.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(callback)
            self.addAction(action)

    def connect_controls(self):
        self.previous_button.clicked.connect(self.previous_image)
        self.next_button.clicked.connect(self.next_image)
        self.thumbnail_strip.image_selected.connect(self.jump_to_image)

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

        self.thumbnail_strip.load_project(
            self.session.images.files,
            self.session.state_for_file,
        )

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
            self.session.stats,
        )

        self.thumbnail_strip.set_current(self.session.images.index)

        self.refresh_status()
        self.update_buttons()

    def refresh_status(self):
        self.side_panel.update_status(
            **self.session.state.as_dict()
        )

    def update_buttons(self):
        current_num, total = self.session.progress

        self.previous_button.setEnabled(current_num > 1)
        self.next_button.setEnabled(current_num < total)

    def refresh_after_action(self):
        current_num, total = self.session.progress

        self.header_panel.update_progress(
            self.session.project_name,
            current_num,
            total,
            self.session.stats,
        )

        self.thumbnail_strip.set_current(self.session.images.index)
        self.refresh_status()
        self.update_buttons()

    def move_images(self, offset):
        self.session.move(offset)
        self.refresh_ui()

    def next_image(self):
        self.move_images(1)

    def previous_image(self):
        self.move_images(-1)

    def jump_forward(self):
        self.move_images(10)

    def jump_back(self):
        self.move_images(-10)

    def jump_forward_far(self):
        self.move_images(50)

    def jump_back_far(self):
        self.move_images(-50)

    def first_image(self):
        self.session.first()
        self.refresh_ui()

    def last_image(self):
        self.session.last()
        self.refresh_ui()

    def jump_to_image(self, index):
        self.session.jump_to(index)
        self.refresh_ui()

    def open_command_palette(self):
        current_num, total = self.session.progress

        if total == 0:
            return

        target = CommandPalette.get_target(
            current_num,
            total,
            self,
        )

        if target is None:
            return

        self.session.jump_to(target - 1)
        self.refresh_ui()

    def zoom_fit(self):
        self.image_panel.set_zoom_fit()

    def zoom_100(self):
        self.image_panel.set_zoom_scale(1.0)

    def zoom_200(self):
        self.image_panel.set_zoom_scale(2.0)

    def zoom_400(self):
        self.image_panel.set_zoom_scale(4.0)

    def rotate_left(self):
        self.session.rotate_left()
        self.image_panel.set_rotation(self.session.state.rotation)
        self.refresh_after_action()

    def rotate_right(self):
        self.session.rotate_right()
        self.image_panel.set_rotation(self.session.state.rotation)
        self.refresh_after_action()

    def toggle_back(self):
        self.session.toggle_back()
        self.refresh_after_action()

    def toggle_favorite(self):
        self.session.toggle_favorite()
        self.refresh_after_action()

    def toggle_restore(self):
        self.session.toggle_restore()
        self.refresh_after_action()

    def toggle_delete(self):
        self.session.toggle_delete()
        self.refresh_after_action()