from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from core.dual_session import DualReviewSession
from ui.image_panel import ImagePanel


class DualSessionDialog(QDialog):
    def __init__(
        self,
        initial_left_folder=None,
        initial_left_index=None,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Dual Session Review")
        self.resize(1200, 720)

        self.dual_session = DualReviewSession()
        self.left_panel = ImagePanel(self.dual_session.left_session)
        self.right_panel = ImagePanel(self.dual_session.right_session)

        self.left_label = QLabel("Left: no folder loaded")
        self.right_label = QLabel("Right: no folder loaded")
        self.status_label = QLabel(
            "Load two folders, navigate each side, then link the current pair. "
            "No metadata is copied automatically."
        )
        self.status_label.setWordWrap(True)

        self.left_previous_button = QPushButton("Previous")
        self.left_next_button = QPushButton("Next")
        self.left_open_button = QPushButton("Open Left Folder")

        self.right_previous_button = QPushButton("Previous")
        self.right_next_button = QPushButton("Next")
        self.right_open_button = QPushButton("Open Right Folder")

        self.link_button = QPushButton("Link Current Pair")
        self.close_button = QPushButton("Close")

        self.build_ui()
        self.connect_controls()
        self.refresh_all()

        if initial_left_folder is not None:
            self.open_left_project(initial_left_folder, initial_left_index)

    def build_ui(self):
        panes = QHBoxLayout()
        panes.setSpacing(8)
        panes.addWidget(
            self.build_session_pane(
                "Left Session",
                self.left_label,
                self.left_panel,
                self.left_previous_button,
                self.left_next_button,
                self.left_open_button,
            ),
            1,
        )
        panes.addWidget(
            self.build_session_pane(
                "Right Session",
                self.right_label,
                self.right_panel,
                self.right_previous_button,
                self.right_next_button,
                self.right_open_button,
            ),
            1,
        )

        actions = QHBoxLayout()
        actions.addWidget(self.status_label, 1)
        actions.addWidget(self.link_button)
        actions.addWidget(self.close_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.addLayout(panes, 1)
        layout.addLayout(actions)
        self.setLayout(layout)

    def build_session_pane(
        self,
        title,
        label,
        image_panel,
        previous_button,
        next_button,
        open_button,
    ):
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold;")

        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        buttons.addWidget(previous_button)
        buttons.addWidget(next_button)
        buttons.addWidget(open_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(title_label)
        layout.addWidget(label)
        layout.addWidget(image_panel, 1)
        layout.addLayout(buttons)

        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLayout(layout)
        return frame

    def connect_controls(self):
        self.left_open_button.clicked.connect(self.choose_left_folder)
        self.right_open_button.clicked.connect(self.choose_right_folder)

        self.left_previous_button.clicked.connect(
            lambda: self.move_left(-1)
        )
        self.left_next_button.clicked.connect(lambda: self.move_left(1))
        self.right_previous_button.clicked.connect(
            lambda: self.move_right(-1)
        )
        self.right_next_button.clicked.connect(lambda: self.move_right(1))

        self.link_button.clicked.connect(self.link_current_pair)
        self.close_button.clicked.connect(self.accept)

    def choose_left_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Left Image Folder",
        )

        if folder:
            self.open_left_project(folder)

    def choose_right_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Right Image Folder",
        )

        if folder:
            self.open_right_project(folder)

    def open_left_project(self, folder, initial_index=None):
        self.dual_session.open_left_project(folder, initial_index)
        self.refresh_left()
        self.refresh_actions()

    def open_right_project(self, folder, initial_index=None):
        self.dual_session.open_right_project(folder, initial_index)
        self.refresh_right()
        self.refresh_actions()

    def move_left(self, offset):
        self.move_session(
            self.dual_session.left_session,
            offset,
            self.refresh_left,
            "Left session",
        )

    def move_right(self, offset):
        self.move_session(
            self.dual_session.right_session,
            offset,
            self.refresh_right,
            "Right session",
        )

    def move_session(self, session, offset, refresh, label):
        if session.image_count == 0:
            return

        moved = session.move(offset)

        if not moved:
            if offset < 0:
                self.status_label.setText(f"{label} is at the first image.")
            else:
                self.status_label.setText(f"{label} is at the last image.")

        refresh()
        self.refresh_actions()

    def link_current_pair(self):
        relationship = self.dual_session.link_current_pair()

        if relationship is None:
            self.status_label.setText(
                "Select two different current images before linking."
            )
            self.refresh_actions()
            return

        self.status_label.setText(
            "Front / Back relationship saved. "
            "No metadata was copied automatically."
        )
        self.refresh_actions()

    def refresh_all(self):
        self.refresh_left()
        self.refresh_right()
        self.refresh_actions()

    def refresh_left(self):
        self.refresh_session(
            self.dual_session.left_session,
            self.left_panel,
            self.left_label,
            "Left",
        )

    def refresh_right(self):
        self.refresh_session(
            self.dual_session.right_session,
            self.right_panel,
            self.right_label,
            "Right",
        )

    def refresh_session(self, session, image_panel, label, side_name):
        current = session.current_file

        if current is None:
            image_panel.clear_image()
            label.setText(f"{side_name}: no image loaded")
            return

        image_panel.load_image(current)
        current_number, total = session.progress
        label.setText(
            f"{side_name}: {current.name} ({current_number} of {total})"
        )

    def refresh_actions(self):
        self.update_nav_buttons(
            self.dual_session.left_session,
            self.left_previous_button,
            self.left_next_button,
        )
        self.update_nav_buttons(
            self.dual_session.right_session,
            self.right_previous_button,
            self.right_next_button,
        )
        self.link_button.setEnabled(
            self.dual_session.can_link_current_pair()
        )

    def update_nav_buttons(self, session, previous_button, next_button):
        current_number, total = session.progress

        previous_button.setEnabled(total > 0 and current_number > 1)
        next_button.setEnabled(total > 0 and current_number < total)

    def closeEvent(self, event):
        self.dual_session.close()
        super().closeEvent(event)

    @staticmethod
    def show_dialog(
        parent=None,
        initial_left_folder=None,
        initial_left_index=None,
    ):
        dialog = DualSessionDialog(
            initial_left_folder=initial_left_folder,
            initial_left_index=initial_left_index,
            parent=parent,
        )
        try:
            dialog.exec()
        finally:
            dialog.dual_session.close()
