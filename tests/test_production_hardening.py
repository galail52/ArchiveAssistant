import hashlib
import os
import sqlite3
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.database import ArchiveDatabase
from core.dual_session import DualReviewSession
from core.export import ExportFormat
from core.ocr import OCRManager
from core.ocr.engines import OCREngineOutput
from core.relationships import RelationshipType
from core.review_session import ReviewSession


class SuccessfulEngine:
    name = "Test OCR"

    def is_available(self):
        return True

    def unavailable_reason(self):
        return ""

    def extract_text(self, _image_path):
        return OCREngineOutput(raw_text="caption text")


class ProductionHardeningTests(unittest.TestCase):

    def test_review_session_close_releases_database_connection(self):
        session = ReviewSession()
        database = session.database

        session.close()
        session.close()

        self.assertIsNone(database.connection)
    def write_image(self, path, color=(128, 128, 128)):
        image = Image.new("RGB", (32, 32), color)
        image.save(path)

    def file_digest(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_old_database_schema_is_migrated_safely(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            db_path = temp_path / "archive.db"

            connection = sqlite3.connect(db_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE photos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_path TEXT NOT NULL,
                        file_path TEXT NOT NULL UNIQUE,
                        filename TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO photos (
                        project_path,
                        file_path,
                        filename
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        str(temp_path / "project"),
                        str(temp_path / "project" / "001.jpg"),
                        "001.jpg",
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            database = ArchiveDatabase(db_path)

            try:
                columns = {
                    row["name"]
                    for row in database.connection.execute(
                        "PRAGMA table_info(photos)"
                    ).fetchall()
                }

                expected_columns = {
                    "rotation",
                    "has_back",
                    "favorite",
                    "needs_restore",
                    "needs_research",
                    "delete_flag",
                    "people",
                    "event",
                    "location",
                    "date_taken",
                    "keywords",
                    "notes",
                    "note_by",
                    "confidence",
                    "reviewed",
                    "last_viewed",
                    "created_at",
                    "updated_at",
                }

                self.assertTrue(expected_columns.issubset(columns))
                self.assertEqual(
                    len(database.export_records(temp_path / "project")),
                    1,
                )
                self.assertEqual(database.all_relationships(), [])
                self.assertTrue((temp_path / "archive.db.backup1").exists())
            finally:
                database.connection.close()

    def test_missing_tables_are_created_on_startup(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            database = ArchiveDatabase(temp_path / "archive.db")

            try:
                tables = {
                    row["name"]
                    for row in database.connection.execute(
                        """
                        SELECT name
                        FROM sqlite_master
                        WHERE type = 'table'
                        """
                    ).fetchall()
                }

                self.assertIn("photos", tables)
                self.assertIn("metadata_templates", tables)
                self.assertIn("metadata_recent_values", tables)
                self.assertIn("relationships", tables)
            finally:
                database.connection.close()

    def test_missing_image_records_are_reported_without_crashing(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "project"
            project_path.mkdir()
            present = project_path / "present.jpg"
            missing = project_path / "missing.jpg"
            self.write_image(present)

            database = ArchiveDatabase(temp_path / "archive.db")

            try:
                database.ensure_photo(project_path, present)
                database.ensure_photo(project_path, missing)

                health = database.check_project_health(
                    project_path,
                    [present],
                )

                self.assertFalse(health["healthy"])
                self.assertEqual(health["missing_files"], [missing])
                self.assertEqual(health["missing_count"], 1)
            finally:
                database.connection.close()

    def test_corrupt_supported_extension_is_skipped_gracefully(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "project"
            project_path.mkdir()
            corrupt = project_path / "corrupt.jpg"
            corrupt.write_text("not an image", encoding="utf-8")
            os.chdir(temp_path)
            session = None

            try:
                session = ReviewSession()
                session.open_project(project_path)

                groups = session.scan_image_similarity()

                self.assertEqual(groups, [])
                self.assertEqual(
                    session.similarity_manager.skipped_images,
                    [str(corrupt)],
                )
                self.assertIsNotNone(session.queue_current_for_ocr())
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)

    def test_read_only_workflows_do_not_mutate_original_images(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "project"
            project_path.mkdir()
            front = project_path / "front.jpg"
            back = project_path / "back.jpg"
            self.write_image(front, color=(120, 120, 120))
            self.write_image(back, color=(130, 130, 130))
            before = {
                front: self.file_digest(front),
                back: self.file_digest(back),
            }
            os.chdir(temp_path)
            session = None
            dual_session = None

            try:
                session = ReviewSession()
                session.open_project(project_path)
                session.toggle_favorite()
                session.update_metadata(
                    people="Example Person",
                    event="Trial",
                    location="Archive",
                    date_taken="",
                    keywords="alpha",
                    notes="",
                    note_by="",
                    confidence=3,
                )
                session.build_health_report()
                session.apply_smart_filter("favorites")
                session.scan_image_similarity()
                session.ocr_manager = OCRManager(engine=SuccessfulEngine())
                session.run_current_ocr()
                session.export_metadata(
                    ExportFormat.XMP_SIDECAR,
                    project_path / "front.xmp",
                    dry_run=False,
                )
                session.create_relationship(
                    front,
                    back,
                    RelationshipType.FRONT_BACK,
                )

                dual_session = DualReviewSession()
                dual_session.open_left_project(project_path, 0)
                dual_session.open_right_project(project_path, 1)
                dual_session.link_current_pair()

                self.assertEqual(before[front], self.file_digest(front))
                self.assertEqual(before[back], self.file_digest(back))
                self.assertFalse((project_path / "front.xmp").exists())
            finally:
                if dual_session is not None:
                    dual_session.close()

                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
