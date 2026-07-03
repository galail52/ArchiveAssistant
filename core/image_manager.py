"""
Archive Assistant
-----------------

Image Manager

Responsible for:
- Opening projects
- Finding images
- Navigation

Author:
Trent + ChatGPT
"""

from pathlib import Path


IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
}


class ImageManager:

    def __init__(self):

        self.project_path: Path | None = None
        self.files: list[Path] = []
        self.index: int = 0

    # ---------------------------------------------------------

    def open_project(self, folder: str | Path):

        self.project_path = Path(folder)

        self.files = sorted(
            [
                file
                for file in self.project_path.iterdir()
                if file.suffix.lower() in IMAGE_EXTENSIONS
            ]
        )

        self.index = 0

    # ---------------------------------------------------------

    @property
    def count(self) -> int:
        return len(self.files)

    # ---------------------------------------------------------

    @property
    def current_file(self) -> Path | None:

        if not self.files:
            return None

        return self.files[self.index]

    # ---------------------------------------------------------

    def next(self):

        if self.index < len(self.files) - 1:
            self.index += 1

    # ---------------------------------------------------------

    def previous(self):

        if self.index > 0:
            self.index -= 1

    # ---------------------------------------------------------

    @property
    def progress(self):

        if not self.files:
            return (0, 0)

        return (
            self.index + 1,
            len(self.files),
        )