import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.review_session import ReviewSession


class PerformancePolishTests(unittest.TestCase):
    def make_session(self, temp_path):
        project_path = temp_path / "project"
        project_path.mkdir()
        (project_path / "001.jpg").touch()

        session = ReviewSession()
        session.open_project(project_path)
        return session

    def test_review_session_stats_are_cached_and_invalidated(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)
                original_get_stats = session.database.get_stats
                calls = []

                def tracked_get_stats(project_path):
                    calls.append(project_path)
                    return original_get_stats(project_path)

                session.database.get_stats = tracked_get_stats

                first = session.stats
                second = session.stats

                self.assertEqual(first, second)
                self.assertEqual(len(calls), 1)

                session.toggle_favorite()
                updated = session.stats

                self.assertTrue(updated["favorites"])
                self.assertEqual(len(calls), 2)
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
