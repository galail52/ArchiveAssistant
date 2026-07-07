from pathlib import Path

from core.relationships import RelationshipType
from core.review_session import ReviewSession


class DualReviewSession:
    STATUS_MISSING_IMAGE = "missing_image"
    STATUS_SELF_PAIR = "self_pair"
    STATUS_ALREADY_LINKED = "already_linked"
    STATUS_NOT_LINKED = "not_linked"

    def __init__(self, left_session=None, right_session=None):
        self.left_session = left_session or ReviewSession()
        self.right_session = right_session or ReviewSession()
        self._closed = False

    def open_left_project(self, folder: str | Path, initial_index=None):
        self._open_project(self.left_session, folder, initial_index)

    def open_right_project(self, folder: str | Path, initial_index=None):
        self._open_project(self.right_session, folder, initial_index)

    def current_pair(self):
        return (
            self.left_session.current_file,
            self.right_session.current_file,
        )

    def can_link_current_pair(self):
        return self.current_pair_status() in (
            self.STATUS_NOT_LINKED,
            self.STATUS_ALREADY_LINKED,
        )

    def link_current_pair(self, notes=""):
        if not self.can_link_current_pair():
            return None

        existing = self.current_pair_relationship()

        if existing is not None:
            return existing

        left_image, right_image = self.current_pair()

        return self.left_session.create_relationship(
            left_image,
            right_image,
            RelationshipType.FRONT_BACK,
            notes,
        )

    def current_pair_status(self):
        left_image, right_image = self.current_pair()

        if left_image is None or right_image is None:
            return self.STATUS_MISSING_IMAGE

        if left_image == right_image:
            return self.STATUS_SELF_PAIR

        if self.current_pair_relationship() is not None:
            return self.STATUS_ALREADY_LINKED

        return self.STATUS_NOT_LINKED

    def current_pair_relationship(self):
        left_image, right_image = self.current_pair()

        if left_image is None or right_image is None or left_image == right_image:
            return None

        return self.left_session.relationship_manager.find_relationship(
            left_image,
            right_image,
            RelationshipType.FRONT_BACK,
        )

    def close(self):
        if self._closed:
            return

        self.left_session.database.connection.close()
        self.right_session.database.connection.close()
        self._closed = True

    def _open_project(self, session, folder: str | Path, initial_index):
        session.open_project(folder)

        if initial_index is None or session.image_count == 0:
            return

        target = max(0, min(initial_index, session.image_count - 1))
        session.images.jump_to(target)
        session.load_current_state()
