from pathlib import Path

from core.database import ArchiveDatabase
from core.image_manager import ImageManager
from core.navigator import Navigator
from core.review_state import ReviewState


class ReviewSession:
    def __init__(self):
        self.images = ImageManager()
        self.navigator = Navigator(self.images)
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

    def move(self, offset: int):
        self.navigate(lambda: self.navigator.move(offset))

    def jump_to(self, index: int):
        self.navigate(lambda: self.navigator.jump_to(index))

    def first(self):
        self.navigate(self.navigator.first)

    def last(self):
        self.navigate(self.navigator.last)

    def navigate(self, action):
        if self.image_count == 0:
            return

        previous_file = self.current_file

        self.save_current_state()
        action()

        if self.current_file != previous_file:
            self.load_current_state()

    def next_image(self):
        self.move(1)

    def previous_image(self):
        self.move(-1)

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

    def state_for_file(self, file_path: Path) -> ReviewState:
        if file_path == self.current_file:
            return self.state

        return self.database.load_state(file_path)

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