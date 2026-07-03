"""
Archive Assistant
-----------------

Review Session

Coordinates the current review session.

Owns:
- ImageManager
- ReviewState

Author:
Trent + ChatGPT
"""

from pathlib import Path

from core.image_manager import ImageManager
from core.review_state import ReviewState


class ReviewSession:

    def __init__(self):

        self.images = ImageManager()
        self.state = ReviewState()

    # ---------------------------------------------------------
    # Project
    # ---------------------------------------------------------

    def open_project(self, folder: str | Path):

        self.images.open_project(folder)

        self.state.reset()

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def next_image(self):

        self.images.next()

        self.state.reset()

    def previous_image(self):

        self.images.previous()

        self.state.reset()

    # ---------------------------------------------------------
    # Review Actions
    # ---------------------------------------------------------

    def rotate_left(self):

        self.state.rotate_left()

    def rotate_right(self):

        self.state.rotate_right()

    def toggle_back(self):

        self.state.toggle_back()

    def toggle_favorite(self):

        self.state.toggle_favorite()

    def toggle_restore(self):

        self.state.toggle_restore()

    def toggle_delete(self):

        self.state.toggle_delete()

    # ---------------------------------------------------------
    # Convenience Properties
    # ---------------------------------------------------------

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