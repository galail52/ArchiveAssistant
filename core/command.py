from collections.abc import Callable
from dataclasses import dataclass


@dataclass(slots=True)
class Command:
    id: str
    name: str
    callback: Callable
    shortcut: str | None = None
    category: str = "General"
    show_in_help: bool = True
    show_in_palette: bool = True
    enabled: Callable[[], bool] | None = None
    help_key: str | None = None
    help_name: str | None = None

    def is_enabled(self):
        if self.enabled is None:
            return True

        return self.enabled()

    @property
    def help_display_key(self):
        return self.help_key or self.shortcut or ""

    @property
    def help_display_name(self):
        return self.help_name or self.name