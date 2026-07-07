import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.review_session import ReviewSession
from core.similarity import FingerprintEngine
from core.similarity import ImageFingerprint
from core.similarity import SimilarityManager


class FakeFingerprintEngine:
    def __init__(self, values):
        self.values = values

    def fingerprint(self, image_path):
        image_path = str(image_path)
        value = self.values.get(Path(image_path).name)

        if value is None:
            return None

        return ImageFingerprint.create(
            image_id=image_path,
            fingerprint_algorithm="fake",
            fingerprint_value=value,
        )

    def compare(self, source, target):
        if source.fingerprint_value == target.fingerprint_value:
            return 1.0

        if {
            source.fingerprint_value,
            target.fingerprint_value,
        } == {"near-a", "near-b"}:
            return 0.95

        return 0.1


class SimilarityFoundationTests(unittest.TestCase):
    def write_image(self, path, color=(128, 128, 128), gradient=False):
        if gradient:
            image = Image.new("RGB", (32, 32))

            for x in range(32):
                for y in range(32):
                    value = min(255, x * 8 + y)
                    image.putpixel((x, y), (value, value, value))
        else:
            image = Image.new("RGB", (32, 32), color)

        image.save(path)

    def test_fingerprints_are_deterministic(self):
        with TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "image.jpg"
            self.write_image(image_path, gradient=True)
            engine = FingerprintEngine()

            first = engine.fingerprint(image_path)
            second = engine.fingerprint(image_path)

            self.assertEqual(
                first.fingerprint_value,
                second.fingerprint_value,
            )
            self.assertEqual(first.fingerprint_algorithm, "dhash8_mean")

    def test_identical_images_match_exactly(self):
        with TemporaryDirectory() as temp_dir:
            first_path = Path(temp_dir) / "first.jpg"
            second_path = Path(temp_dir) / "second.jpg"
            self.write_image(first_path, gradient=True)
            self.write_image(second_path, gradient=True)

            manager = SimilarityManager()
            groups = manager.scan([first_path, second_path])

            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0].matches[0].match_type, "exact_duplicate")
            self.assertEqual(groups[0].matches[0].similarity_score, 1.0)

    def test_different_images_do_not_match(self):
        with TemporaryDirectory() as temp_dir:
            first_path = Path(temp_dir) / "black.jpg"
            second_path = Path(temp_dir) / "white.jpg"
            self.write_image(first_path, color=(0, 0, 0))
            self.write_image(second_path, color=(255, 255, 255))

            manager = SimilarityManager()
            groups = manager.scan([first_path, second_path])

            self.assertEqual(groups, [])

    def test_high_confidence_similar_images_group(self):
        manager = SimilarityManager(
            fingerprint_engine=FakeFingerprintEngine(
                {
                    "one.jpg": "near-a",
                    "two.jpg": "near-b",
                    "three.jpg": "far",
                }
            )
        )

        groups = manager.scan([
            Path("one.jpg"),
            Path("two.jpg"),
            Path("three.jpg"),
        ])

        self.assertEqual(len(groups), 1)
        self.assertEqual(
            groups[0].matches[0].match_type,
            "high_confidence_similar",
        )
        self.assertEqual(groups[0].matches[0].similarity_score, 0.95)

    def test_empty_archive_has_no_groups(self):
        manager = SimilarityManager()

        self.assertEqual(manager.scan([]), [])
        self.assertEqual(manager.candidate_groups(), [])

    def test_corrupt_image_is_skipped_without_crashing(self):
        with TemporaryDirectory() as temp_dir:
            corrupt_path = Path(temp_dir) / "corrupt.jpg"
            corrupt_path.write_text("not an image")

            manager = SimilarityManager()
            groups = manager.scan([corrupt_path])

            self.assertEqual(groups, [])
            self.assertEqual(manager.skipped_images, [str(corrupt_path)])

    def test_review_session_similarity_integration(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "project"
            project_path.mkdir()
            self.write_image(project_path / "001.jpg", gradient=True)
            self.write_image(project_path / "002.jpg", gradient=True)
            os.chdir(temp_path)
            session = None

            try:
                session = ReviewSession()
                session.open_project(project_path)

                groups = session.scan_image_similarity()

                self.assertEqual(len(groups), 1)
                self.assertEqual(session.similarity_groups(), groups)
                self.assertEqual(
                    len(
                        session.similarity_matches_for_image(
                            project_path / "001.jpg"
                        )
                    ),
                    1,
                )

                session.clear_similarity_results()

                self.assertEqual(session.similarity_groups(), [])
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)

    def test_similarity_scan_does_not_write_metadata_or_files(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "project"
            project_path.mkdir()
            first = project_path / "001.jpg"
            second = project_path / "002.jpg"
            self.write_image(first, gradient=True)
            self.write_image(second, gradient=True)
            mtimes = {
                first: first.stat().st_mtime_ns,
                second: second.stat().st_mtime_ns,
            }
            os.chdir(temp_path)
            session = None

            try:
                session = ReviewSession()
                session.open_project(project_path)

                def fail_save_metadata(*_args):
                    raise AssertionError(
                        "Similarity scan should not write metadata"
                    )

                session.database.save_metadata = fail_save_metadata
                session.scan_image_similarity()

                self.assertEqual(first.stat().st_mtime_ns, mtimes[first])
                self.assertEqual(second.stat().st_mtime_ns, mtimes[second])
                self.assertEqual(session.metadata.people, "")
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
