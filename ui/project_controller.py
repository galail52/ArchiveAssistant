from PySide6.QtWidgets import QFileDialog, QMessageBox


class ProjectController:
    def __init__(self, window):
        self.window = window
        self.session = window.session

    def last_project_folder(self):
        return self.window.settings.value(
            "last_project_folder",
            "",
            type=str,
        )

    def remember_project_folder(self, folder):
        self.window.settings.setValue(
            "last_project_folder",
            folder,
        )

    def open_project(self):
        folder = QFileDialog.getExistingDirectory(
            self.window,
            "Select Cropped Folder",
            self.last_project_folder(),
        )

        if not folder:
            return

        self.remember_project_folder(folder)
        self.session.open_project(folder)

        if self.session.image_count == 0:
            QMessageBox.information(
                self.window,
                "No Images",
                "No supported image files found.",
            )
            self.window.refresh_ui()
            return

        self.window.thumbnail_strip.load_project(
            self.session.images.files,
            self.session.state_for_file,
        )

        self.window.refresh_ui()