import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.review_session import ReviewSession


class MetadataClipboardTests(unittest.TestCase):
    def test_copy_and_paste_metadata_between_images(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "project"
            project_path.mkdir()
            (project_path / "001.jpg").touch()
            (project_path / "002.jpg").touch()

            os.chdir(temp_path)

            session = None

            try:
                session = ReviewSession()
                session.open_project(project_path)

                session.update_metadata(
                    people="Ada Lovelace",
                    event="Family Reunion",
                    location="Murray, Utah",
                    date_taken="1958-07",
                    keywords="picnic, summer",
                    notes="Standing near the old house.",
                    note_by="Trent",
                    confidence=4,
                )

                self.assertTrue(session.copy_metadata())

                session.next_image()
                self.assertEqual(session.metadata.people, "")

                self.assertTrue(session.paste_metadata())
                self.assertEqual(session.metadata.people, "Ada Lovelace")
                self.assertEqual(session.metadata.event, "Family Reunion")
                self.assertEqual(session.metadata.location, "Murray, Utah")
                self.assertEqual(session.metadata.date_taken, "1958-07")
                self.assertEqual(session.metadata.keywords, "picnic, summer")
                self.assertEqual(session.metadata.notes, "Standing near the old house.")
                self.assertEqual(session.metadata.note_by, "Trent")
                self.assertEqual(session.metadata.confidence, 4)
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
