"""
Archive Assistant
-----------------

Header Panel

Displays:
- Project Name
- Current Image
- Progress

Author:
Trent + ChatGPT
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class HeaderPanel(QWidget):

    def __init__(self):

        super().__init__()

        self.project = QLabel("No Project Loaded")
        self.project.setAlignment(Qt.AlignCenter)
"""
Archive Assistant
-----------------
Header Panel

Displays:
- Project Name
- Current Image Number
- Progress Bar

Author:
Trent + ChatGPT
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class HeaderPanel(QWidget):

    def __init__(self):

        super().__init__()

        self.project_label = QLabel("No Project Loaded")
        self.project_label.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel("Image 0 / 0")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()

        self.build_ui()

    # ---------------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout()

        self.project_label.setStyleSheet("""
            font-size:20px;
            font-weight:bold;
        """)

        self.image_label.setStyleSheet("""
            font-size:14px;
        """)

        layout.addWidget(self.project_label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    # ---------------------------------------------------------

    def update_progress(
        self,
        project_name: str,
        current: int,
        total: int,
    ):

        self.project_label.setText(project_name)

        self.image_label.setText(
            f"Image {current} / {total}"
        )

        self.progress.setMaximum(max(total, 1))
        self.progress.setValue(current)