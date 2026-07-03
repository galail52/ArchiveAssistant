from pathlib import Path

from core.database import ArchiveDatabase
from core.image_manager import ImageManager
from core.review_state import ReviewState


class ReviewSession:
    def __init__(self):
        self.images = ImageManager()
        self.state = ReviewState()

        self.database = ArchiveDatabase(
            Path("data") / "archive.db"
        )

    def open_project(self, folder: str | Path):
        self.images.open_project(folder)

        for file_path in self.images.files:
            self.database.ensure_photo(
                self.images.project_path,
                file_path,
            )

        last_viewed = self.database.get_last_viewed_path(
            self.images.project_path
        )

        if last_viewed in self.images.files:
            self.images.index = self.images.files.index(last_viewed)

        self.load_current_state()

    def load_current_state(self):
        current = self.current_file

        if current is None:
            self.state.reset()
            return

        self.state = self.database.load_state(current)

        self.database.mark_last_viewed(current)

    def save_current_state(self):
        current = self.current_file

        if current is None:
            return

        self.database.save_state(current, self.state)
        self.database.mark_last_viewed(current)

    def next_image(self):
        self.save_current_state()
        self.images.next()
        self.load_current_state()

    def previous_image(self):
        self.save_current_state()
        self.images.previous()
        self.load_current_state()

    def rotate_left(self):
        self.state.rotate_left()
        self.save_current_state()

    def rotate_right(self):
        self.state.rotate_right()
        self.save_current_state()

    def toggle_back(self):
        self.state.toggle_back()
        self.save_current_state()

    def toggle_favorite(self):
        self.state.toggle_favorite()
        self.save_current_state()

    def toggle_restore(self):
        self.state.toggle_restore()
        self.save_current_state()

    def toggle_delete(self):
        self.state.toggle_delete()
        self.save_current_state()

    def jump_to(self, index):
        self.save_current_state()
        self.images.jump_to(index)
        self.load_current_state()

    @property
    def current_file(self):
        return self.images.current_file

    @property
    def progress(self):
        return self.images.progress

    @property
    def project_name(self):
        if self.images.project_path is None:
            return ""

        return self.images.project_path.name

    @property
    def image_count(self):
        return self.images.count

    @property
    def stats(self):
        if self.images.project_path is None:
            return {
                "total": 0,
                "reviewed": 0,
                "backs": 0,
                "favorites": 0,
                "restore": 0,
                "deletes": 0,
            }

        return self.database.get_stats(self.images.project_path)