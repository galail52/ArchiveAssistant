from PySide6.QtGui import QAction, QKeySequence

from core.command import Command


class KeyboardManager:
    def __init__(self, window, registry):
        self.window = window
        self.registry = registry
        self.actions = []

    def register_shortcuts(self):
        self.register(
            "project.open",
            "Open Project",
            self.window.open_project,
            "Ctrl+O",
            "Project",
        )

        self.register(
            "app.command_palette",
            "Command Palette",
            self.window.open_command_palette,
            "G",
            "Application",
            show_in_palette=False,
            help_key="G",
            help_name="Command Palette",
        )

        self.register(
            "nav.goto_image",
            "Go To Image",
            self.window.open_go_to_image,
            None,
            "Navigation",
            enabled=self.window.has_images,
            show_in_help=False,
        )

        self.register(
            "nav.find_filename",
            "Find Filename",
            self.window.open_find_filename,
            None,
            "Navigation",
            enabled=self.window.has_images,
            show_in_help=False,
        )

        self.register(
            "nav.first_unreviewed",
            "First Unreviewed",
            self.window.jump_to_first_unreviewed,
            None,
            "Navigation",
            enabled=self.window.has_images,
            show_in_help=False,
        )

        self.register(
            "nav.previous",
            "Previous Image",
            self.window.previous_image,
            "Left",
            "Navigation",
            enabled=self.window.has_previous_image,
            show_in_palette=False,
            help_key="← / →",
            help_name="Prev / Next",
        )
        self.register(
            "nav.next",
            "Next Image",
            self.window.next_image,
            "Right",
            "Navigation",
            enabled=self.window.has_next_image,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "nav.next.space",
            "Next Image",
            self.window.next_image,
            "Space",
            "Navigation",
            enabled=self.window.has_next_image,
            show_in_palette=False,
            help_name="Next",
        )
        self.register(
            "nav.back10",
            "Jump Back 10",
            self.window.jump_back,
            "PageUp",
            "Navigation",
            enabled=self.window.can_jump_back,
            show_in_palette=False,
            help_key="PgUp/Dn",
            help_name="Jump 10",
        )
        self.register(
            "nav.forward10",
            "Jump Forward 10",
            self.window.jump_forward,
            "PageDown",
            "Navigation",
            enabled=self.window.can_jump_forward,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "nav.back50",
            "Jump Back 50",
            self.window.jump_back_far,
            "Ctrl+Left",
            "Navigation",
            enabled=self.window.can_jump_back,
            show_in_palette=False,
            help_key="Ctrl+←/→",
            help_name="Jump 50",
        )
        self.register(
            "nav.forward50",
            "Jump Forward 50",
            self.window.jump_forward_far,
            "Ctrl+Right",
            "Navigation",
            enabled=self.window.can_jump_forward,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "nav.first",
            "First Image",
            self.window.first_image,
            "Home",
            "Navigation",
            enabled=self.window.has_previous_image,
            show_in_palette=False,
            help_key="Home/End",
            help_name="First / Last",
        )
        self.register(
            "nav.last",
            "Last Image",
            self.window.last_image,
            "End",
            "Navigation",
            enabled=self.window.has_next_image,
            show_in_help=False,
            show_in_palette=False,
        )

        self.register(
            "view.fit",
            "Fit",
            self.window.zoom_fit,
            "1",
            "View",
            enabled=self.window.has_images,
            show_in_palette=False,
        )
        self.register(
            "view.zoom100",
            "100%",
            self.window.zoom_100,
            "2",
            "View",
            enabled=self.window.has_images,
            show_in_palette=False,
            help_key="2 / 3 / 4",
            help_name="100 / 200 / 400",
        )
        self.register(
            "view.zoom200",
            "200%",
            self.window.zoom_200,
            "3",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "view.zoom400",
            "400%",
            self.window.zoom_400,
            "4",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "view.zoom_in",
            "Zoom In",
            self.window.zoom_in,
            "+",
            "View",
            enabled=self.window.has_images,
            show_in_palette=False,
            help_key="+ / -",
            help_name="Zoom In / Out",
        )
        self.register(
            "view.zoom_in_equals",
            "Zoom In",
            self.window.zoom_in,
            "=",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "view.zoom_out",
            "Zoom Out",
            self.window.zoom_out,
            "-",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "view.pan_left",
            "Pan Left",
            self.window.pan_left,
            "Shift+Left",
            "View",
            enabled=self.window.has_images,
            show_in_palette=False,
            help_key="Shift+Arr",
            help_name="Pan",
        )
        self.register(
            "view.pan_right",
            "Pan Right",
            self.window.pan_right,
            "Shift+Right",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "view.pan_up",
            "Pan Up",
            self.window.pan_up,
            "Shift+Up",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "view.pan_down",
            "Pan Down",
            self.window.pan_down,
            "Shift+Down",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )
        self.register(
            "view.rotate_left",
            "Rotate Left",
            self.window.rotate_left,
            "A",
            "View",
            enabled=self.window.has_images,
            show_in_palette=False,
            help_key="A / D",
            help_name="Rotate",
        )
        self.register(
            "view.rotate_right",
            "Rotate Right",
            self.window.rotate_right,
            "D",
            "View",
            enabled=self.window.has_images,
            show_in_help=False,
            show_in_palette=False,
        )

        self.register(
            "review.back",
            "Back",
            self.window.toggle_back,
            "B",
            "Review",
            enabled=self.window.has_images,
            show_in_palette=False,
        )
        self.register(
            "review.favorite",
            "Favorite",
            self.window.toggle_favorite,
            "F",
            "Review",
            enabled=self.window.has_images,
            show_in_palette=False,
        )
        self.register(
            "review.restore",
            "Restore",
            self.window.toggle_restore,
            "R",
            "Review",
            enabled=self.window.has_images,
            show_in_palette=False,
        )
        self.register(
            "review.delete",
            "Delete",
            self.window.toggle_delete,
            "X",
            "Review",
            enabled=self.window.has_images,
            show_in_palette=False,
        )

        self.register(
            "app.exit",
            "Exit",
            self.window.close,
            "Esc",
            "Application",
            show_in_palette=False,
        )

        self.update_enabled_states()

    def register(
        self,
        command_id,
        name,
        callback,
        shortcut,
        category,
        show_in_help=True,
        show_in_palette=True,
        help_key=None,
        help_name=None,
        enabled=None,
    ):
        command = self.registry.register(
            Command(
                id=command_id,
                name=name,
                callback=callback,
                shortcut=shortcut,
                category=category,
                show_in_help=show_in_help,
                show_in_palette=show_in_palette,
                help_key=help_key,
                help_name=help_name,
                enabled=enabled,
            )
        )

        self.add_qt_action(command)

    def add_qt_action(self, command):
        if command.shortcut is None:
            return

        action = QAction(self.window)
        action.setShortcut(QKeySequence(command.shortcut))
        action.triggered.connect(command.callback)
        action.setEnabled(command.is_enabled())

        self.window.addAction(action)
        self.actions.append((action, command))

    def update_enabled_states(self):
        for action, command in self.actions:
            action.setEnabled(command.is_enabled())

    def help_text(self):
        return "\n".join(
            f"{command.help_display_key:<11} {command.help_display_name}"
            for command in self.registry.help_commands()
        )