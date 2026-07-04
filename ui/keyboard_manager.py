from PySide6.QtGui import QAction, QKeySequence


class KeyboardManager:
    def __init__(self, window):
        self.window = window
        self.actions = []
        self.shortcuts = []

    def register_shortcuts(self):
        self.add_help_only("Ctrl+O", "Open Project")

        self.add_shortcut("Left", self.window.previous_image, "Prev Image")
        self.add_shortcut("Right", self.window.next_image, "Next Image")
        self.add_shortcut("Space", self.window.next_image, "Next Image")

        self.add_shortcut("PageUp", self.window.jump_back, "Jump Back 10")
        self.add_shortcut("PageDown", self.window.jump_forward, "Jump Forward 10")
        self.add_shortcut("Ctrl+Left", self.window.jump_back_far, "Jump Back 50")
        self.add_shortcut("Ctrl+Right", self.window.jump_forward_far, "Jump Forward 50")

        self.add_shortcut("Home", self.window.first_image, "First Image")
        self.add_shortcut("End", self.window.last_image, "Last Image")
        self.add_shortcut("G", self.window.open_command_palette, "Go To Image")

        self.add_shortcut("1", self.window.zoom_fit, "Fit")
        self.add_shortcut("2", self.window.zoom_100, "100%")
        self.add_shortcut("3", self.window.zoom_200, "200%")
        self.add_shortcut("4", self.window.zoom_400, "400%")
        self.add_shortcut("+", self.window.zoom_in, "Zoom In")
        self.add_shortcut("=", self.window.zoom_in, "Zoom In", show=False)
        self.add_shortcut("-", self.window.zoom_out, "Zoom Out")

        self.add_shortcut("Shift+Left", self.window.pan_left, "Pan Left")
        self.add_shortcut("Shift+Right", self.window.pan_right, "Pan Right")
        self.add_shortcut("Shift+Up", self.window.pan_up, "Pan Up")
        self.add_shortcut("Shift+Down", self.window.pan_down, "Pan Down")

        self.add_shortcut("A", self.window.rotate_left, "Rotate Left")
        self.add_shortcut("D", self.window.rotate_right, "Rotate Right")

        self.add_shortcut("B", self.window.toggle_back, "Back")
        self.add_shortcut("F", self.window.toggle_favorite, "Favorite")
        self.add_shortcut("R", self.window.toggle_restore, "Restore")
        self.add_shortcut("X", self.window.toggle_delete, "Delete")

        self.add_shortcut("Esc", self.window.close, "Exit")

    def add_shortcut(self, key, callback, description, show=True):
        action = QAction(self.window)
        action.setShortcut(QKeySequence(key))
        action.triggered.connect(callback)

        self.window.addAction(action)
        self.actions.append(action)

        if show:
            self.shortcuts.append((key, description))

    def add_help_only(self, key, description):
        self.shortcuts.append((key, description))

    def help_text(self):
        grouped = [
            ("Ctrl+O", "Open Project"),
            ("← / →", "Prev / Next"),
            ("Space", "Next"),
            ("PgUp/Dn", "Jump 10"),
            ("Ctrl+←/→", "Jump 50"),
            ("Home/End", "First / Last"),
            ("G", "Go To"),
            ("1", "Fit"),
            ("2 / 3 / 4", "100 / 200 / 400"),
            ("+ / -", "Zoom In / Out"),
            ("Shift+Arr", "Pan"),
            ("A / D", "Rotate"),
            ("B", "Back"),
            ("F", "Favorite"),
            ("R", "Restore"),
            ("X", "Delete"),
            ("Esc", "Exit"),
        ]

        return "\n".join(
            f"{key:<11} {description}"
            for key, description in grouped
        )