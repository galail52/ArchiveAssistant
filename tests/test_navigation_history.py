import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.review_session import ReviewSession


class NavigationHistoryTests(unittest.TestCase):
    def make_session(self, temp_path):
        project_path = temp_path / "project"
        project_path.mkdir()

        for name in ("001.jpg", "002.jpg", "003.jpg"):
            (project_path / name).touch()

        session = ReviewSession()
        session.open_project(project_path)
        return session

    def test_jump_history_returns_to_previous_jump_location(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)

                self.assertTrue(session.jump_to(2))
                self.assertEqual(session.images.index, 2)
                self.assertTrue(session.can_return_to_previous_jump())

                self.assertTrue(session.return_to_previous_jump())
                self.assertEqual(session.images.index, 0)

                self.assertTrue(session.return_to_previous_jump())
                self.assertEqual(session.images.index, 2)
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)

    def test_normal_previous_next_do_not_replace_jump_history(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)

                self.assertTrue(session.jump_to(2))
                self.assertTrue(session.previous_image())
                self.assertEqual(session.images.index, 1)

                self.assertTrue(session.return_to_previous_jump())
                self.assertEqual(session.images.index, 0)
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
