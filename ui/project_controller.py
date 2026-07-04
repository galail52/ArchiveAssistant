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

        self.warn_if_project_unhealthy()

        self.window.refresh_ui()

    def warn_if_project_unhealthy(self):
        health = self.session.check_project_health()

        if health is None or health["healthy"]:
            return

        QMessageBox.warning(
            self.window,
            "Project Health Warning",
            (
                "The project does not match the database.\n\n"
                f"Files on disk: {health['disk_count']}\n"
                f"Database entries: {health['database_count']}\n\n"
                f"Missing files: {health['missing_count']}\n"
                f"New files: {health['new_count']}\n\n"
                "Open Project Health Check for more details."
            ),
        )

    def show_database_stats(self):
        stats = self.session.stats
        total = stats["total"]

        reviewed_percent = (
            round((stats["reviewed"] / total) * 100, 1)
            if total
            else 0
        )

        QMessageBox.information(
            self.window,
            "Database Stats",
            (
                f"Project: {self.session.project_name}\n\n"
                f"Total photos: {stats['total']}\n"
                f"Reviewed: {stats['reviewed']} ({reviewed_percent}%)\n\n"
                f"Backs: {stats['backs']}\n"
                f"Favorites: {stats['favorites']}\n"
                f"Restore: {stats['restore']}\n"
                f"Deletes: {stats['deletes']}"
            ),
        )

    def show_project_health(self):
        health = self.session.check_project_health()

        if health is None:
            return

        status = (
            "✓ Project Healthy"
            if health["healthy"]
            else "⚠ Needs Attention"
        )

        QMessageBox.information(
            self.window,
            "Project Health Check",
            (
                f"{status}\n\n"
                f"Files on disk: {health['disk_count']}\n"
                f"Database entries: {health['database_count']}\n\n"
                f"Missing files: {health['missing_count']}\n"
                f"New files: {health['new_count']}"
            ),
        )