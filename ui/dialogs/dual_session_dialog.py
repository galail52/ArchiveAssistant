from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeySequence, QShortcut
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
        self.active_side = "left"
        self.last_left_folder = initial_left_folder
        self.last_right_folder = None

        self.left_panel = ImagePanel(self.dual_session.left_session)
        self.right_panel = ImagePanel(self.dual_session.right_session)

        self.left_label = QLabel("Left: no folder loaded")
        self.right_label = QLabel("Right: no folder loaded")
        self.relationship_label = QLabel("Pair status: load both sides")
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
        self.register_shortcuts()
        self.refresh_all()

        if initial_left_folder is not None:
            self.open_left_project(initial_left_folder, initial_left_index)

    def build_ui(self):
        panes = QHBoxLayout()
        panes.setSpacing(8)
        self.left_frame = self.build_session_pane(
            "Front / Left Session",
            self.left_label,
            self.left_panel,
            self.left_previous_button,
            self.left_next_button,
            self.left_open_button,
        )
        self.right_frame = self.build_session_pane(
            "Back / Right Session",
            self.right_label,
            self.right_panel,
            self.right_previous_button,
            self.right_next_button,
            self.right_open_button,
        )
        panes.addWidget(self.left_frame, 1)
        panes.addWidget(self.right_frame, 1)

        actions = QHBoxLayout()
        status_layout = QVBoxLayout()
        status_layout.setSpacing(2)
        status_layout.addWidget(self.relationship_label)
        status_layout.addWidget(self.status_label)

        actions.addLayout(status_layout, 1)
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

    def register_shortcuts(self):
        self.add_dialog_shortcut("Left", lambda: self.move_active(-1))
        self.add_dialog_shortcut("A", lambda: self.move_active(-1))
        self.add_dialog_shortcut("Right", lambda: self.move_active(1))
        self.add_dialog_shortcut("D", lambda: self.move_active(1))
        self.add_dialog_shortcut("Return", self.link_current_pair)
        self.add_dialog_shortcut("Enter", self.link_current_pair)
        self.add_dialog_shortcut("Ctrl+L", self.link_current_pair)
        self.add_dialog_shortcut("Esc", self.accept)

    def add_dialog_shortcut(self, key_sequence, callback):
        shortcut = QShortcut(QKeySequence(key_sequence), self)
        shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        shortcut.activated.connect(callback)

    def choose_left_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Left Image Folder",
            self.folder_dialog_start(self.last_left_folder),
        )

        if folder:
            self.open_left_project(folder)

    def choose_right_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Right Image Folder",
            self.folder_dialog_start(self.last_right_folder),
        )

        if folder:
            self.open_right_project(folder)

    def folder_dialog_start(self, folder):
        if folder is None:
            return ""

        return str(folder)

    def open_left_project(self, folder, initial_index=None):
        self.dual_session.open_left_project(folder, initial_index)
        self.last_left_folder = folder
        self.set_active_side("left")
        self.refresh_left()
        self.refresh_actions()

    def open_right_project(self, folder, initial_index=None):
        self.dual_session.open_right_project(folder, initial_index)
        self.last_right_folder = folder
        self.set_active_side("right")
        self.refresh_right()
        self.refresh_actions()

    def switch_active_pane(self):
        if self.active_side == "left":
            self.set_active_side("right")
        else:
            self.set_active_side("left")

    def set_active_side(self, side):
        self.active_side = side
        self.refresh_active_pane()

        if side == "left":
            self.left_panel.setFocus()
        else:
            self.right_panel.setFocus()

    def move_active(self, offset):
        if self.active_side == "left":
            self.move_left(offset)
        else:
            self.move_right(offset)

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
        status = self.dual_session.current_pair_status()

        if status == DualReviewSession.STATUS_ALREADY_LINKED:
            self.status_label.setText(
                "Current pair is already linked as Front / Back."
            )
            self.refresh_actions()
            return

        relationship = self.dual_session.link_current_pair()

        if relationship is None:
            self.status_label.setText(self.status_message(status))
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
            if session.images.project_path is None:
                label.setText(f"{side_name}: no folder loaded")
            else:
                label.setText(f"{side_name}: no images found")
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
        self.relationship_label.setText(
            f"Pair status: {self.relationship_status_text()}"
        )
        self.refresh_active_pane()

    def relationship_status_text(self):
        status = self.dual_session.current_pair_status()

        if status == DualReviewSession.STATUS_ALREADY_LINKED:
            return "Already linked as Front / Back"

        if status == DualReviewSession.STATUS_NOT_LINKED:
            return "Not linked"

        if status == DualReviewSession.STATUS_SELF_PAIR:
            return "Cannot link the same image"

        return "Load both sides"

    def status_message(self, status):
        if status == DualReviewSession.STATUS_SELF_PAIR:
            return "Choose two different images before linking."

        return "Load images on both sides before linking."

    def refresh_active_pane(self):
        active_style = (
            "QFrame { border: 2px solid #4f8cff; border-radius: 4px; }"
        )
        inactive_style = (
            "QFrame { border: 1px solid #666666; border-radius: 4px; }"
        )

        self.left_frame.setStyleSheet(
            active_style if self.active_side == "left" else inactive_style
        )
        self.right_frame.setStyleSheet(
            active_style if self.active_side == "right" else inactive_style
        )

    def update_nav_buttons(self, session, previous_button, next_button):
        current_number, total = session.progress

        previous_button.setEnabled(total > 0 and current_number > 1)
        next_button.setEnabled(total > 0 and current_number < total)

    def event(self, event):
        if (
            event.type() == QEvent.KeyPress
            and event.key() == Qt.Key_Tab
        ):
            self.switch_active_pane()
            return True

        return super().event(event)

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
