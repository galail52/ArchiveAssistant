from PySide6.QtCore import QSettings
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

from core.command_registry import CommandRegistry
from core.review_session import ReviewSession
from ui.dialogs.command_palette import CommandPalette
from ui.header_panel import HeaderPanel
from ui.image_panel import ImagePanel
from ui.keyboard_manager import KeyboardManager
from ui.side_panel import SidePanel
from ui.widgets.thumbnail_strip import ThumbnailStrip


class MainWindow(QMainWindow):
    PAN_STEP = 80

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Archive Assistant")
        self.resize(1400, 900)
        self.setMinimumSize(900, 650)

        self.settings = QSettings(
            "ArchiveAssistant",
            "ArchiveAssistant",
        )

        self.session = ReviewSession()
        self.command_registry = CommandRegistry()
        self.keyboard_manager = KeyboardManager(
            self,
            self.command_registry,
        )

        self.header_panel = HeaderPanel()
        self.image_panel = ImagePanel(self.session)
        self.keyboard_manager.register_shortcuts()
        self.side_panel = SidePanel(
            self.keyboard_manager.help_text()
        )
        self.thumbnail_strip = ThumbnailStrip()

        self.previous_button = QPushButton("◀ Previous")
        self.next_button = QPushButton("Next ▶")

        self.build_ui()
        self.create_menu()
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

    def connect_controls(self):
        self.previous_button.clicked.connect(self.previous_image)
        self.next_button.clicked.connect(self.next_image)
        self.thumbnail_strip.image_selected.connect(self.jump_to_image)

    def has_images(self):
        return self.session.image_count > 0

    def has_previous_image(self):
        current_num, _total = self.session.progress
        return current_num > 1

    def has_next_image(self):
        current_num, total = self.session.progress
        return current_num < total

    def can_jump_back(self):
        current_num, _total = self.session.progress
        return current_num > 1

    def can_jump_forward(self):
        current_num, total = self.session.progress
        return current_num < total

    def last_project_folder(self):
        return self.settings.value(
            "last_project_folder",
            "",
            type=str,
        )

    def remember_project_folder(self, folder):
        self.settings.setValue("last_project_folder", folder)

    def open_project(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Cropped Folder",
            self.last_project_folder(),
        )

        if not folder:
            return

        self.remember_project_folder(folder)
        self.session.open_project(folder)

        if self.session.image_count == 0:
            QMessageBox.information(
                self,
                "No Images",
                "No supported image files found.",
            )
            self.refresh_ui()
            return

        self.thumbnail_strip.load_project(
            self.session.images.files,
            self.session.state_for_file,
        )

        self.refresh_ui()

    def refresh_ui(self):
        current = self.session.current_file

        if current is not None:
            self.image_panel.load_image(current)

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
        self.keyboard_manager.update_enabled_states()

    def refresh_status(self):
        self.side_panel.update_status(
            **self.session.state.as_dict(),
            view_state=self.session.view_state,
        )

    def update_buttons(self):
        self.previous_button.setEnabled(self.has_previous_image())
        self.next_button.setEnabled(self.has_next_image())

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
        self.keyboard_manager.update_enabled_states()
        self.image_panel.update()

    def refresh_after_view_action(self):
        self.image_panel.clamp_pan()
        self.image_panel.update()
        self.refresh_status()
        self.keyboard_manager.update_enabled_states()

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
        self.session.set_zoom_fit()
        self.refresh_after_view_action()

    def zoom_100(self):
        self.session.set_zoom_percent(100)
        self.refresh_after_view_action()

    def zoom_200(self):
        self.session.set_zoom_percent(200)
        self.refresh_after_view_action()

    def zoom_400(self):
        self.session.set_zoom_percent(400)
        self.refresh_after_view_action()

    def zoom_in(self):
        self.session.zoom_in()
        self.refresh_after_view_action()

    def zoom_out(self):
        self.session.zoom_out()
        self.refresh_after_view_action()

    def pan_left(self):
        self.pan_view(-self.PAN_STEP, 0)

    def pan_right(self):
        self.pan_view(self.PAN_STEP, 0)

    def pan_up(self):
        self.pan_view(0, -self.PAN_STEP)

    def pan_down(self):
        self.pan_view(0, self.PAN_STEP)

    def pan_view(self, dx, dy):
        self.session.pan_view(dx, dy)
        self.refresh_after_view_action()

    def rotate_left(self):
        self.session.rotate_left()
        self.refresh_after_action()

    def rotate_right(self):
        self.session.rotate_right()
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