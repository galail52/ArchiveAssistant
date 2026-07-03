from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class HeaderPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.project_label = QLabel("No Project Loaded")
        self.project_label.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel("Image 0 / 0")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.stats_label = QLabel("Reviewed: 0 | Backs: 0 | Favorites: 0 | Restore: 0 | Delete: 0")
        self.stats_label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()

        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()

        self.project_label.setStyleSheet("""
            font-size:20px;
            font-weight:bold;
        """)

        self.image_label.setStyleSheet("""
            font-size:14px;
        """)

        self.stats_label.setStyleSheet("""
            font-size:13px;
            color:#cfcfcf;
        """)

        layout.addWidget(self.project_label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def update_progress(
        self,
        project_name: str,
        current: int,
        total: int,
        stats: dict | None = None,
    ):
        self.project_label.setText(project_name)

        self.image_label.setText(
            f"Image {current} / {total}"
        )

        if stats is None:
            stats = {
                "reviewed": 0,
                "backs": 0,
                "favorites": 0,
                "restore": 0,
                "deletes": 0,
            }

        self.stats_label.setText(
            f"Reviewed: {stats['reviewed']} | "
            f"Backs: {stats['backs']} | "
            f"Favorites: {stats['favorites']} | "
            f"Restore: {stats['restore']} | "
            f"Delete: {stats['deletes']}"
        )

        self.progress.setMaximum(max(total, 1))
        self.progress.setValue(current)