from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.command_registry import CommandRegistry
from core.metadata_state import METADATA_FIELDS
from core.review_session import ReviewSession
from ui.dialogs.collection_health_dialog import CollectionHealthDialog
from ui.dialogs.command_palette import CommandPalette
from ui.dialogs.find_filename_dialog import FindFilenameDialog
from ui.dialogs.jump_to_image_dialog import JumpToImageDialog
from ui.dialogs.metadata_dialog import MetadataDialog
from ui.dialogs.metadata_field_dialog import MetadataFieldDialog
from ui.dialogs.ocr_status_dialog import OCRStatusDialog
from ui.dialogs.smart_filter_dialog import SmartFilterDialog
from ui.header_panel import HeaderPanel
from ui.image_panel import ImagePanel
from ui.keyboard_manager import KeyboardManager
from ui.project_controller import ProjectController
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

        self.metadata_dialog_open = False

        self.session = ReviewSession()
        self.command_registry = CommandRegistry()
        self.project_controller = ProjectController(self)
        self.keyboard_manager = KeyboardManager(
            self,
            self.command_registry,
        )

        self.header_panel = HeaderPanel()
        self.image_panel = ImagePanel(self.session)

        self.keyboard_manager.register_shortcuts()

        self.side_panel = SidePanel(
            self.keyboard_manager.help_text(),
            review_actions={
                "back": self.toggle_back,
                "favorite": self.toggle_favorite,
                "restore": self.toggle_restore,
                "research": self.toggle_research,
                "delete": self.toggle_delete,
            },
        )

        self.thumbnail_strip = ThumbnailStrip()

        self.previous_button = QPushButton("◀ Previous")
        self.next_button = QPushButton("Next ▶")

        self.build_ui()
        self.create_menu()
        self.connect_controls()
        self.refresh_ui()
        self.restore_window_geometry()
        self.focus_image_viewer()

    def restore_window_geometry(self):
        geometry = self.settings.value("main_window/geometry")

        if geometry is not None:
            self.restoreGeometry(geometry)

    def save_window_geometry(self):
        self.settings.setValue(
            "main_window/geometry",
            self.saveGeometry(),
        )

    def focus_image_viewer(self):
        self.image_panel.setFocus()

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

    def open_project(self):
        self.project_controller.open_project()
        self.focus_image_viewer()

    def show_database_stats(self):
        self.project_controller.show_database_stats()

    def show_project_health(self):
        self.project_controller.show_project_health()

    def show_collection_health(self):
        report = self.session.build_health_report()
        self.focus_image_viewer()

        if report is None:
            return

        try:
            CollectionHealthDialog.show_report(report, self)
        finally:
            self.focus_image_viewer()

    def open_smart_filters(self):
        if not self.has_images():
            return

        try:
            filter_id = SmartFilterDialog.get_filter_id(
                self.session.list_smart_filters(),
                self,
            )
        finally:
            self.focus_image_viewer()

        if filter_id is None:
            return

        matches = self.session.apply_smart_filter(filter_id)

        if not matches:
            self.show_navigation_message("No images match that smart filter")
            self.focus_image_viewer()
            return

        self.show_navigation_message(
            f"Smart filter matched {len(matches)} image(s)"
        )
        self.refresh_ui()

    def show_ocr_status(self):
        try:
            OCRStatusDialog.show_status(
                self.session.ocr_status(),
                self,
            )
        finally:
            self.focus_image_viewer()

    def queue_current_for_ocr(self):
        job = self.session.queue_current_for_ocr()

        if job is None:
            self.show_navigation_message("No image selected for OCR")
        else:
            self.show_navigation_message("Queued current image for OCR")

        self.keyboard_manager.update_enabled_states()
        self.focus_image_viewer()

    def queue_missing_ocr(self):
        jobs = self.session.queue_missing_ocr()
        self.show_navigation_message(
            f"Queued {len(jobs)} image(s) for OCR"
        )
        self.keyboard_manager.update_enabled_states()
        self.focus_image_viewer()

    def show_export_preview(self):
        result = self.session.export_preview()
        self.focus_image_viewer()

        if result is None:
            return

        lines = result.summary_lines()

        if result.warnings:
            lines.append("")
            lines.append("First warnings:")

            for warning in result.warnings[:8]:
                lines.append(f"- {warning.file_path.name}: {warning.message}")

        QMessageBox.information(
            self,
            "Export Preview",
            "\n".join(lines),
        )
        self.focus_image_viewer()

    def has_images(self):
        return self.session.image_count > 0

    def can_undo_review_change(self):
        return self.session.can_undo()

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

    def can_return_to_previous_jump(self):
        return self.session.can_return_to_previous_jump()

    def can_copy_metadata_from_previous(self):
        return self.session.can_copy_metadata_from_previous()

    def can_copy_metadata(self):
        return self.session.can_copy_metadata()

    def can_paste_metadata(self):
        return self.session.can_paste_metadata()

    def can_paste_selected_metadata(self):
        return self.session.can_paste_selected_metadata()

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
        self.focus_image_viewer()

    def refresh_status(self):
        self.side_panel.update_status(
            **self.session.state.as_dict(),
            view_state=self.session.view_state,
            metadata=self.session.metadata,
        )

    def update_buttons(self):
        self.previous_button.setEnabled(self.has_previous_image())
        self.next_button.setEnabled(self.has_next_image())

    def show_navigation_message(self, message):
        self.statusBar().showMessage(message, 1800)

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
        self.focus_image_viewer()

    def refresh_after_metadata_action(self):
        self.refresh_status()
        self.keyboard_manager.update_enabled_states()
        self.focus_image_viewer()

    def refresh_after_view_action(self):
        self.image_panel.clamp_pan()
        self.image_panel.update()
        self.refresh_status()
        self.keyboard_manager.update_enabled_states()
        self.focus_image_viewer()

    def move_images(self, offset):
        moved = self.session.move(offset)

        if not moved:
            if offset < 0:
                self.show_navigation_message("Already at first image")
            elif offset > 0:
                self.show_navigation_message("Already at last image")

        self.refresh_ui()

    def next_image(self):
        self.move_images(1)

    def previous_image(self):
        self.move_images(-1)

    def jump_forward(self):
        self.jump_by(10)

    def jump_back(self):
        self.jump_by(-10)

    def jump_forward_far(self):
        self.jump_by(50)

    def jump_back_far(self):
        self.jump_by(-50)

    def jump_by(self, offset):
        moved = self.session.jump_by(offset)

        if not moved:
            if offset < 0:
                self.show_navigation_message("Already at first image")
            elif offset > 0:
                self.show_navigation_message("Already at last image")

        self.refresh_ui()

    def first_image(self):
        if not self.session.first():
            self.show_navigation_message("Already at first image")
        self.refresh_ui()

    def last_image(self):
        if not self.session.last():
            self.show_navigation_message("Already at last image")
        self.refresh_ui()

    def jump_to_image(self, index):
        if not self.session.jump_to(index):
            self.show_navigation_message("Image already selected")
        self.refresh_ui()

    def return_to_previous_jump(self):
        if self.session.return_to_previous_jump():
            self.refresh_ui()
            return

        self.show_navigation_message("No previous jump location")
        self.focus_image_viewer()

    def open_command_palette(self):
        try:
            command = CommandPalette.get_command(
                self.command_registry,
                self,
            )
        finally:
            self.focus_image_viewer()

        if command is None:
            return

        if not command.is_enabled():
            return

        command.callback()

    def open_go_to_image(self):
        current_num, total = self.session.progress

        if total == 0:
            return

        try:
            target = JumpToImageDialog.get_target(
                current_num,
                total,
                self,
            )
        finally:
            self.focus_image_viewer()

        if target is None:
            return

        self.jump_to_image(target - 1)

    def open_find_filename(self):
        if not self.has_images():
            return

        try:
            index = FindFilenameDialog.get_index(
                self.session.images.files,
                self,
            )
        finally:
            self.focus_image_viewer()

        if index is None:
            return

        self.jump_to_image(index)

    def open_metadata_editor(self):
        if not self.has_images():
            return

        if self.metadata_dialog_open:
            return

        self.metadata_dialog_open = True

        try:
            values = MetadataDialog.get_metadata(
                self.session.metadata,
                self,
                self.session.recent_metadata_values(),
            )
        finally:
            self.metadata_dialog_open = False
            self.focus_image_viewer()

        if values is None:
            return

        self.session.update_metadata(**values)
        self.refresh_ui()

    def copy_metadata_from_previous(self):
        if self.session.copy_metadata_from_previous():
            self.refresh_after_metadata_action()

    def copy_metadata(self):
        if self.session.copy_metadata():
            self.refresh_after_metadata_action()

    def paste_metadata(self):
        if self.session.paste_metadata():
            self.refresh_after_metadata_action()

    def copy_selected_metadata_fields(self):
        fields = MetadataFieldDialog.get_fields(
            "Copy Selected Metadata Fields",
            METADATA_FIELDS,
            self,
        )

        self.focus_image_viewer()

        if not fields:
            return

        if self.session.copy_selected_metadata(fields):
            self.refresh_after_metadata_action()

    def paste_selected_metadata_fields(self):
        available_fields = []

        if self.session.metadata_patch_clipboard is not None:
            available_fields = self.session.metadata_patch_clipboard.fields

        fields = MetadataFieldDialog.get_fields(
            "Paste Selected Metadata Fields",
            available_fields,
            self,
        )

        self.focus_image_viewer()

        if not fields:
            return

        if self.session.paste_selected_metadata(fields):
            self.refresh_after_metadata_action()

    def save_metadata_template(self):
        name, accepted = QInputDialog.getText(
            self,
            "Save Metadata Template",
            "Template name:",
        )
        self.focus_image_viewer()

        if not accepted:
            return

        template_id = self.session.save_current_metadata_template(name)

        if template_id is not None:
            self.show_navigation_message("Metadata template saved")

    def select_metadata_template(self, title):
        templates = self.session.metadata_templates()

        if not templates:
            QMessageBox.information(
                self,
                title,
                "No metadata templates have been saved yet.",
            )
            self.focus_image_viewer()
            return None

        template_names = [template.name for template in templates]
        selected_name, accepted = QInputDialog.getItem(
            self,
            title,
            "Template:",
            template_names,
            0,
            False,
        )
        self.focus_image_viewer()

        if not accepted:
            return None

        for template in templates:
            if template.name == selected_name:
                return template

        return None

    def apply_metadata_template(self):
        template = self.select_metadata_template("Apply Metadata Template")

        if template is None:
            return

        if self.session.apply_metadata_template(template.id):
            self.refresh_after_metadata_action()

    def rename_metadata_template(self):
        template = self.select_metadata_template("Rename Metadata Template")

        if template is None:
            return

        name, accepted = QInputDialog.getText(
            self,
            "Rename Metadata Template",
            "Template name:",
            text=template.name,
        )
        self.focus_image_viewer()

        if not accepted:
            return

        if self.session.rename_metadata_template(template.id, name):
            self.show_navigation_message("Metadata template renamed")

    def delete_metadata_template(self):
        template = self.select_metadata_template("Delete Metadata Template")

        if template is None:
            return

        result = QMessageBox.question(
            self,
            "Delete Metadata Template",
            f"Delete metadata template '{template.name}'?",
            QMessageBox.Delete | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        self.focus_image_viewer()

        if result != QMessageBox.Delete:
            return

        if self.session.delete_metadata_template(template.id):
            self.show_navigation_message("Metadata template deleted")

    def jump_to_first_unreviewed(self):
        if self.session.jump_to_first_unreviewed():
            self.refresh_ui()

    def jump_to_next_unreviewed(self):
        if self.session.jump_to_next_unreviewed():
            self.refresh_ui()

    def jump_to_next_favorite(self):
        if self.session.jump_to_next_favorite():
            self.refresh_ui()

    def jump_to_next_restore(self):
        if self.session.jump_to_next_restore():
            self.refresh_ui()

    def jump_to_next_research(self):
        if self.session.jump_to_next_research():
            self.refresh_ui()

    def jump_to_next_back(self):
        if self.session.jump_to_next_back():
            self.refresh_ui()

    def jump_to_next_delete(self):
        if self.session.jump_to_next_delete():
            self.refresh_ui()

    def undo_review_change(self):
        if self.session.undo_last_review_change():
            self.refresh_after_action()

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

    def toggle_research(self):
        self.session.toggle_research()
        self.refresh_after_action()

    def toggle_delete(self):
        self.session.toggle_delete()
        self.refresh_after_action()

    def closeEvent(self, event):
        self.save_window_geometry()
        super().closeEvent(event)
