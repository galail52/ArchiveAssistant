import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.database import ArchiveDatabase
from core.relationships import RelationshipManager
from core.relationships import RelationshipType
from core.review_session import ReviewSession


class RelationshipTests(unittest.TestCase):
    def make_database(self, temp_path):
        return ArchiveDatabase(temp_path / "archive.db")

    def make_session(self, temp_path, image_count=3):
        project_path = temp_path / "project"
        project_path.mkdir()

        for index in range(1, image_count + 1):
            (project_path / f"{index:03}.jpg").touch()

        session = ReviewSession()
        session.open_project(project_path)
        return session

    def test_relationship_creation_and_lookup(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database = self.make_database(temp_path)

            try:
                manager = RelationshipManager(database)
                relationship = manager.create_relationship(
                    "front.jpg",
                    "back.jpg",
                    RelationshipType.FRONT_BACK,
                )

                self.assertIsNotNone(relationship.relationship_id)
                self.assertEqual(
                    relationship.relationship_type,
                    RelationshipType.FRONT_BACK,
                )
                self.assertEqual(
                    manager.related_images("front.jpg"),
                    ["back.jpg"],
                )
                self.assertTrue(
                    manager.has_relationship(
                        "front.jpg",
                        "back.jpg",
                        RelationshipType.FRONT_BACK,
                    )
                )
            finally:
                database.connection.close()

    def test_relationship_removal(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database = self.make_database(temp_path)

            try:
                manager = RelationshipManager(database)
                relationship = manager.create_relationship(
                    "front.jpg",
                    "back.jpg",
                )

                self.assertTrue(
                    manager.remove_relationship(
                        relationship.relationship_id,
                    )
                )
                self.assertEqual(manager.related_images("front.jpg"), [])
            finally:
                database.connection.close()

    def test_duplicate_relationship_is_prevented(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database = self.make_database(temp_path)

            try:
                manager = RelationshipManager(database)
                first = manager.create_relationship(
                    "front.jpg",
                    "back.jpg",
                )
                second = manager.create_relationship(
                    "back.jpg",
                    "front.jpg",
                )

                self.assertEqual(
                    first.relationship_id,
                    second.relationship_id,
                )
                self.assertEqual(len(database.all_relationships()), 1)
            finally:
                database.connection.close()

    def test_self_pairing_is_prevented(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database = self.make_database(temp_path)

            try:
                manager = RelationshipManager(database)

                self.assertIsNone(
                    manager.create_relationship(
                        "same.jpg",
                        "same.jpg",
                    )
                )
                self.assertEqual(database.all_relationships(), [])
            finally:
                database.connection.close()

    def test_multiple_unrelated_relationships(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database = self.make_database(temp_path)

            try:
                manager = RelationshipManager(database)
                manager.create_relationship("front-1.jpg", "back-1.jpg")
                manager.create_relationship("front-2.jpg", "back-2.jpg")

                self.assertEqual(
                    manager.related_images("front-1.jpg"),
                    ["back-1.jpg"],
                )
                self.assertEqual(
                    manager.related_images("front-2.jpg"),
                    ["back-2.jpg"],
                )
            finally:
                database.connection.close()

    def test_relationship_persistence(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database = self.make_database(temp_path)

            try:
                manager = RelationshipManager(database)
                relationship = manager.create_relationship(
                    "front.jpg",
                    "back.jpg",
                    notes="caption on reverse",
                )
            finally:
                database.connection.close()

            reopened = self.make_database(temp_path)

            try:
                relationships = reopened.all_relationships()

                self.assertEqual(len(relationships), 1)
                self.assertEqual(
                    relationships[0].relationship_id,
                    relationship.relationship_id,
                )
                self.assertEqual(relationships[0].notes, "caption on reverse")
            finally:
                reopened.connection.close()

    def test_review_session_relationship_integration(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)
                target = session.images.files[1]

                relationship = session.create_current_relationship(target)

                self.assertIsNotNone(relationship)
                self.assertTrue(session.has_relationship())
                self.assertEqual(session.related_images(), [str(target)])
                self.assertTrue(session.jump_to_related_image(target))
                self.assertEqual(session.current_file, target)
                self.assertTrue(
                    session.remove_relationship(
                        relationship.relationship_id,
                    )
                )
                self.assertFalse(session.has_relationship())
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
