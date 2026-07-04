from PySide6.QtGui import QAction, QKeySequence


class KeyboardManager:
    def __init__(self, window):
        self.window = window
        self.actions = []

    def register_shortcuts(self):
        bindings = {
            "Left": self.window.previous_image,
            "Right": self.window.next_image,
            "Space": self.window.next_image,
            "Home": self.window.first_image,
            "End": self.window.last_image,
            "PageUp": self.window.jump_back,
            "PageDown": self.window.jump_forward,
            "Ctrl+Left": self.window.jump_back_far,
            "Ctrl+Right": self.window.jump_forward_far,
            "Shift+Left": self.window.pan_left,
            "Shift+Right": self.window.pan_right,
            "Shift+Up": self.window.pan_up,
            "Shift+Down": self.window.pan_down,
            "G": self.window.open_command_palette,
            "1": self.window.zoom_fit,
            "2": self.window.zoom_100,
            "3": self.window.zoom_200,
            "4": self.window.zoom_400,
            "+": self.window.zoom_in,
            "=": self.window.zoom_in,
            "-": self.window.zoom_out,
            "A": self.window.rotate_left,
            "D": self.window.rotate_right,
            "B": self.window.toggle_back,
            "F": self.window.toggle_favorite,
            "R": self.window.toggle_restore,
            "X": self.window.toggle_delete,
            "Esc": self.window.close,
        }

        for key, callback in bindings.items():
            self.add_shortcut(key, callback)

    def add_shortcut(self, key, callback):
        action = QAction(self.window)
        action.setShortcut(QKeySequence(key))
        action.triggered.connect(callback)

        self.window.addAction(action)
        self.actions.append(action)