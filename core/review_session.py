from pathlib import Path

from core.database import ArchiveDatabase
from core.image_manager import ImageManager
from core.navigator import Navigator
from core.review_state import ReviewState
from core.view_state import ViewState


class ReviewSession:
    def __init__(self):
        self.images = ImageManager()
        self.navigator = Navigator(self.images)
        self.review_state = ReviewState()
        self.view_state = ViewState()

        self.database = ArchiveDatabase(
            Path("data") / "archive.db"
        )

    @property
    def state(self):
        return self.review_state

    def open_project(self, folder: str | Path):
        self.images.open_project(folder)
        self.view_state.reset()

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
            self.review_state.reset()
            self.view_state.reset()
            return

        self.review_state = self.database.load_state(current)
        self.view_state.set_rotation(self.review_state.rotation)
        self.database.mark_last_viewed(current)

    def save_current_state(self):
        current = self.current_file

        if current is None:
            return

        self.database.save_state(current, self.review_state)
        self.database.mark_last_viewed(current)

    def mark_current_reviewed(self):
        current = self.current_file

        if current is None:
            return

        self.database.mark_reviewed(current)

    def move(self, offset: int):
        self.navigate(lambda: self.navigator.move(offset))

    def jump_to(self, index: int):
        self.navigate(lambda: self.navigator.jump_to(index))

    def jump_to_first_unreviewed(self):
        for index, file_path in enumerate(self.images.files):
            if not self.database.is_reviewed(file_path):
                self.jump_to(index)
                return True

        return False

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
            self.database.mark_reviewed(previous_file)
            self.load_current_state()

    def next_image(self):
        self.move(1)

    def previous_image(self):
        self.move(-1)

    def set_zoom_fit(self):
        self.view_state.set_fit()

    def set_zoom_percent(self, percent: int):
        self.view_state.set_zoom_percent(percent)

    def zoom_in(self):
        self.view_state.zoom_in()

    def zoom_out(self):
        self.view_state.zoom_out()

    def pan_view(self, dx: int, dy: int):
        self.view_state.pan(dx, dy)

    def rotate_left(self):
        self.review_state.rotate_left()
        self.view_state.set_rotation(self.review_state.rotation)
        self.save_current_state()

    def rotate_right(self):
        self.review_state.rotate_right()
        self.view_state.set_rotation(self.review_state.rotation)
        self.save_current_state()

    def toggle_back(self):
        self.review_state.toggle_back()
        self.save_current_state()

    def toggle_favorite(self):
        self.review_state.toggle_favorite()
        self.save_current_state()

    def toggle_restore(self):
        self.review_state.toggle_restore()
        self.save_current_state()

    def toggle_delete(self):
        self.review_state.toggle_delete()
        self.save_current_state()

    def state_for_file(self, file_path: Path) -> ReviewState:
        if file_path == self.current_file:
            return self.review_state

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