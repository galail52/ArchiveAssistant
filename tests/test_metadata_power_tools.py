import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.review_session import ReviewSession


class MetadataPowerToolsTests(unittest.TestCase):
    def make_session(self, temp_path):
        project_path = temp_path / "project"
        project_path.mkdir(exist_ok=True)
        (project_path / "001.jpg").touch()
        (project_path / "002.jpg").touch()

        session = ReviewSession()
        session.open_project(project_path)
        return session

    def test_save_apply_rename_and_delete_template(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)

            session = None

            try:
                session = self.make_session(temp_path)
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

                template_id = session.save_current_metadata_template(
                    "Reunion"
                )

                self.assertIsNotNone(template_id)
                self.assertEqual(
                    [template.name for template in session.metadata_templates()],
                    ["Reunion"],
                )

                session.next_image()
                self.assertTrue(session.apply_metadata_template(template_id))
                self.assertEqual(session.metadata.people, "Ada Lovelace")
                self.assertEqual(session.metadata.notes, "Standing near the old house.")

                self.assertTrue(
                    session.rename_metadata_template(
                        template_id,
                        "Summer Reunion",
                    )
                )
                self.assertEqual(
                    [template.name for template in session.metadata_templates()],
                    ["Summer Reunion"],
                )

                self.assertTrue(session.delete_metadata_template(template_id))
                self.assertEqual(session.metadata_templates(), [])
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)

    def test_recent_metadata_history_is_deduplicated_limited_and_persisted(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)

            session = None
            reopened = None

            try:
                session = self.make_session(temp_path)

                for index in range(25):
                    session.update_metadata(
                        people=f"Person {index}",
                        event=f"Event {index}",
                        location=f"Location {index}",
                        date_taken="",
                        keywords=f"keyword {index}",
                        notes="",
                        note_by="",
                        confidence=0,
                    )

                session.update_metadata(
                    people="person 24",
                    event="Event 24",
                    location="Location 24",
                    date_taken="",
                    keywords="keyword 24",
                    notes="",
                    note_by="",
                    confidence=0,
                )

                recent = session.recent_metadata_values()

                self.assertEqual(len(recent["people"]), 20)
                self.assertEqual(recent["people"][0], "person 24")
                self.assertEqual(
                    [value.lower() for value in recent["people"]].count(
                        "person 24"
                    ),
                    1,
                )
                self.assertNotIn("Person 0", recent["people"])

                session.database.connection.close()
                session = None

                reopened = self.make_session(temp_path)
                self.assertEqual(
                    reopened.recent_metadata_values()["event"][0],
                    "Event 24",
                )
            finally:
                if session is not None:
                    session.database.connection.close()

                if reopened is not None:
                    reopened.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
