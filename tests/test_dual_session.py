import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.dual_session import DualReviewSession
from core.metadata_state import MetadataState
from core.relationships import RelationshipType


class DualSessionTests(unittest.TestCase):
    def make_project(self, root, name, filenames):
        project_path = root / name
        project_path.mkdir()

        for filename in filenames:
            (project_path / filename).touch()

        return project_path

    def close_dual_session(self, dual_session):
        dual_session.close()

    def test_sessions_navigate_independently(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            dual_session = None

            try:
                left_project = self.make_project(
                    temp_path,
                    "fronts",
                    ["front-1.jpg", "front-2.jpg"],
                )
                right_project = self.make_project(
                    temp_path,
                    "backs",
                    ["back-1.jpg", "back-2.jpg"],
                )

                dual_session = DualReviewSession()
                dual_session.open_left_project(left_project)
                dual_session.open_right_project(right_project)

                left_current = dual_session.left_session.current_file
                self.assertTrue(dual_session.right_session.next_image())

                self.assertEqual(
                    dual_session.left_session.current_file,
                    left_current,
                )
                self.assertEqual(
                    dual_session.right_session.current_file.name,
                    "back-2.jpg",
                )
            finally:
                if dual_session is not None:
                    self.close_dual_session(dual_session)

                os.chdir(original_cwd)

    def test_current_pair_can_be_linked_as_front_back(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            dual_session = None

            try:
                left_project = self.make_project(
                    temp_path,
                    "fronts",
                    ["front.jpg"],
                )
                right_project = self.make_project(
                    temp_path,
                    "backs",
                    ["back.jpg"],
                )

                dual_session = DualReviewSession()
                dual_session.open_left_project(left_project)
                dual_session.open_right_project(right_project)

                relationship = dual_session.link_current_pair()

                self.assertIsNotNone(relationship)
                self.assertEqual(
                    relationship.relationship_type,
                    RelationshipType.FRONT_BACK,
                )
                self.assertEqual(
                    relationship.source_image_id,
                    str(dual_session.left_session.current_file),
                )
                self.assertEqual(
                    relationship.target_image_id,
                    str(dual_session.right_session.current_file),
                )
                self.assertTrue(
                    dual_session.left_session.relationship_manager.has_relationship(
                        dual_session.left_session.current_file,
                        dual_session.right_session.current_file,
                        RelationshipType.FRONT_BACK,
                    )
                )
            finally:
                if dual_session is not None:
                    self.close_dual_session(dual_session)

                os.chdir(original_cwd)

    def test_self_pairing_is_prevented(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            dual_session = None

            try:
                project = self.make_project(
                    temp_path,
                    "same-project",
                    ["image.jpg"],
                )

                dual_session = DualReviewSession()
                dual_session.open_left_project(project)
                dual_session.open_right_project(project)

                self.assertFalse(dual_session.can_link_current_pair())
                self.assertIsNone(dual_session.link_current_pair())
                self.assertFalse(
                    dual_session.left_session.has_relationship(
                        dual_session.left_session.current_file,
                    )
                )
            finally:
                if dual_session is not None:
                    self.close_dual_session(dual_session)

                os.chdir(original_cwd)

    def test_linking_does_not_copy_metadata(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            dual_session = None

            try:
                left_project = self.make_project(
                    temp_path,
                    "fronts",
                    ["front.jpg"],
                )
                right_project = self.make_project(
                    temp_path,
                    "backs",
                    ["back.jpg"],
                )

                dual_session = DualReviewSession()
                dual_session.open_left_project(left_project)
                dual_session.open_right_project(right_project)

                dual_session.left_session.update_metadata(
                    people="Front Person",
                    event="",
                    location="",
                    date_taken="",
                    keywords="",
                    notes="",
                    note_by="",
                    confidence=0,
                )

                dual_session.right_session.database.save_metadata = Mock(
                    side_effect=AssertionError(
                        "relationship linking must not save metadata"
                    )
                )

                relationship = dual_session.link_current_pair()

                self.assertIsNotNone(relationship)
                self.assertEqual(
                    dual_session.right_session.metadata_state,
                    MetadataState(),
                )
            finally:
                if dual_session is not None:
                    self.close_dual_session(dual_session)

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
