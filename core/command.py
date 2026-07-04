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

    def is_enabled(self):
        if self.enabled is None:
            return True

        return self.enabled()