from pathlib import Path

from core.database import ArchiveDatabase
from core.image_manager import ImageManager
from core.metadata_state import MetadataState
from core.navigator import Navigator
from core.review_snapshot import ReviewSnapshot
from core.review_state import ReviewState
from core.view_state import ViewState


class ReviewSession:
    def __init__(self):
        self.images = ImageManager()
        self.navigator = Navigator(self.images)
        self.review_state = ReviewState()
        self.view_state = ViewState()
        self.metadata_state = MetadataState()
        self.metadata_clipboard = None
        self.last_snapshot = None

        self.database = ArchiveDatabase(
            Path("data") / "archive.db"
        )

    @property
    def state(self):
        return self.review_state

    @property
    def metadata(self):
        return self.metadata_state

    def open_project(self, folder: str | Path):
        self.images.open_project(folder)
        self.view_state.reset()
        self.metadata_state.reset()
        self.last_snapshot = None

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

    def check_project_health(self):
        if self.images.project_path is None:
            return None

        return self.database.check_project_health(
            self.images.project_path,
            self.images.files,
        )

    def load_current_state(self):
        current = self.current_file

        if current is None:
            self.review_state.reset()
            self.view_state.reset()
            self.metadata_state.reset()
            self.last_snapshot = None
            return

        self.review_state = self.database.load_state(current)
        self.metadata_state = self.database.load_metadata(current)
        self.view_state.set_rotation(self.review_state.rotation)
        self.database.mark_last_viewed(current)

    def take_snapshot(self):
        current = self.current_file

        if current is None:
            return

        self.last_snapshot = ReviewSnapshot.capture(
            current,
            self.review_state,
        )

    def can_undo(self):
        return (
            self.last_snapshot is not None
            and self.current_file is not None
            and str(self.current_file) == self.last_snapshot.file_path
        )

    def undo_last_review_change(self):
        if not self.can_undo():
            return False

        self.review_state = self.last_snapshot.state
        self.view_state.set_rotation(self.review_state.rotation)
        self.last_snapshot = None
        self.save_current_state()
        return True

    def save_current_state(self):
        current = self.current_file

        if current is None:
            return

        self.database.save_state(current, self.review_state)
        self.database.mark_last_viewed(current)

    def save_current_metadata(self):
        current = self.current_file

        if current is None:
            return

        self.database.save_metadata(current, self.metadata_state)

    def update_metadata(
        self,
        people: str,
        event: str,
        location: str,
        date_taken: str,
        keywords: str,
        notes: str,
        note_by: str,
        confidence: int,
    ):
        self.metadata_state = MetadataState(
            people=people,
            event=event,
            location=location,
            date_taken=date_taken,
            keywords=keywords,
            notes=notes,
            note_by=note_by,
            confidence=confidence,
        )
        self.save_current_metadata()

    def can_copy_metadata_from_previous(self):
        return self.image_count > 0 and self.images.index > 0

    def copy_metadata_from_previous(self):
        if not self.can_copy_metadata_from_previous():
            return False

        previous_file = self.images.files[self.images.index - 1]
        self.metadata_state = self.database.load_metadata(previous_file)
        self.save_current_metadata()
        return True

    def can_copy_metadata(self):
        return self.current_file is not None

    def copy_metadata(self):
        if not self.can_copy_metadata():
            return False

        self.metadata_clipboard = self.metadata_state.copy()
        return True

    def can_paste_metadata(self):
        return (
            self.current_file is not None
            and self.metadata_clipboard is not None
        )

    def paste_metadata(self):
        if not self.can_paste_metadata():
            return False

        self.metadata_state = self.metadata_clipboard.copy()
        self.save_current_metadata()
        return True

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

    def jump_to_next_research(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.needs_research
        )

    def jump_to_next_unreviewed(self):
        return self.jump_to_next_matching(
            lambda file_path, _state: not self.database.is_reviewed(file_path)
        )

    def jump_to_next_favorite(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.favorite
        )

    def jump_to_next_restore(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.needs_restore
        )

    def jump_to_next_back(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.has_back
        )

    def jump_to_next_delete(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.delete
        )

    def jump_to_next_matching(self, predicate):
        if self.image_count == 0:
            return False

        start = self.images.index
        count = self.image_count

        for step in range(1, count + 1):
            index = (start + step) % count
            file_path = self.images.files[index]
            state = self.database.load_state(file_path)

            if predicate(file_path, state):
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
            self.last_snapshot = None
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
        self.take_snapshot()
        self.review_state.rotate_left()
        self.view_state.set_rotation(self.review_state.rotation)
        self.save_current_state()

    def rotate_right(self):
        self.take_snapshot()
        self.review_state.rotate_right()
        self.view_state.set_rotation(self.review_state.rotation)
        self.save_current_state()

    def toggle_back(self):
        self.take_snapshot()
        self.review_state.toggle_back()
        self.save_current_state()

    def toggle_favorite(self):
        self.take_snapshot()
        self.review_state.toggle_favorite()
        self.save_current_state()

    def toggle_restore(self):
        self.take_snapshot()
        self.review_state.toggle_restore()
        self.save_current_state()

    def toggle_research(self):
        self.take_snapshot()
        self.review_state.toggle_research()
        self.save_current_state()

    def toggle_delete(self):
        self.take_snapshot()
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
                "research": 0,
                "deletes": 0,
            }

        return self.database.get_stats(self.images.project_path)
