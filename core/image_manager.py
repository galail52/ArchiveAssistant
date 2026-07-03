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

        self.files = []

        self.index = 0

        self.project_path = None

    # ---------------------------------------------------------

    def open_project(self, folder):

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

    def next(self):

        if self.index < len(self.files) - 1:
            self.index += 1

    # ---------------------------------------------------------

    def previous(self):

        if self.index > 0:
            self.index -= 1

    # ---------------------------------------------------------

    def jump_to(self, index: int):

        if not self.files:
            return

        index = max(0, min(index, len(self.files) - 1))

        self.index = index

    # ---------------------------------------------------------

    @property
    def current_file(self):

        if not self.files:
            return None

        return self.files[self.index]

    @property
    def count(self):

        return len(self.files)

    @property
    def progress(self):

        if not self.files:
            return (0, 0)

        return (self.index + 1, len(self.files))