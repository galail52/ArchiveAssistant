import os
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.ocr import OCRJob
from core.ocr import OCRManager
from core.ocr import OCRQueue
from core.ocr import OCRResult
from core.ocr import OCRStatus
from core.review_session import ReviewSession


class OCRFoundationTests(unittest.TestCase):
    def make_session(self, temp_path, image_count=2):
        project_path = temp_path / "project"
        project_path.mkdir()

        for index in range(1, image_count + 1):
            (project_path / f"{index:03}.jpg").touch()

        session = ReviewSession()
        session.open_project(project_path)
        return session

    def test_ocr_job_creation_is_immutable(self):
        job = OCRJob(
            image_id="image-1",
            image_path=Path("001.jpg"),
            source_type="front",
        )

        self.assertEqual(job.image_id, "image-1")
        self.assertEqual(job.image_path, Path("001.jpg"))
        self.assertEqual(job.source_type, "front")

        with self.assertRaises(FrozenInstanceError):
            job.source_type = "back"

    def test_ocr_result_creation_is_immutable(self):
        result = OCRResult(
            image_id="image-1",
            raw_text="handwritten note",
            confidence=0.75,
            engine_name="test",
            status=OCRStatus.COMPLETED,
            warnings=("low contrast",),
        )

        self.assertEqual(result.raw_text, "handwritten note")
        self.assertEqual(result.status, OCRStatus.COMPLETED)

        with self.assertRaises(FrozenInstanceError):
            result.raw_text = "changed"

    def test_ocr_queue_counts_and_deduplicates_pending_jobs(self):
        queue = OCRQueue()

        first = queue.queue_image(Path("001.jpg"))
        second = queue.queue_image(Path("001.jpg"))

        self.assertEqual(first, second)
        self.assertEqual(queue.counts(), {
            "pending": 1,
            "completed": 0,
            "failed": 0,
        })

        queue.record_result(
            OCRResult(
                image_id=first.image_id,
                status=OCRStatus.COMPLETED,
            )
        )

        self.assertEqual(queue.counts(), {
            "pending": 0,
            "completed": 1,
            "failed": 0,
        })

    def test_stub_manager_returns_not_implemented_result(self):
        manager = OCRManager()
        job = manager.queue_image(Path("001.jpg"))
        result = manager.mark_job_not_implemented(job)

        self.assertEqual(result.status, OCRStatus.NOT_IMPLEMENTED)
        self.assertEqual(result.engine_name, OCRManager.STUB_ENGINE_NAME)
        self.assertEqual(manager.status_counts(), {
            "pending": 0,
            "completed": 0,
            "failed": 1,
        })

    def test_queue_current_image_from_review_session(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)
                job = session.queue_current_for_ocr()

                self.assertIsNotNone(job)
                self.assertEqual(job.image_path, session.current_file)
                self.assertEqual(session.ocr_status()["pending"], 1)
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)

    def test_queue_missing_ocr_empty_archive(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path, image_count=0)

                self.assertEqual(session.queue_missing_ocr(), [])
                self.assertEqual(session.ocr_status()["pending"], 0)
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)

    def test_queue_missing_ocr_queues_each_image_once(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path, image_count=2)

                self.assertEqual(len(session.queue_missing_ocr()), 2)
                self.assertEqual(len(session.queue_missing_ocr()), 0)
                self.assertEqual(session.ocr_status()["pending"], 2)
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)

    def test_queue_current_for_ocr_does_not_write_metadata(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)

                def fail_save_metadata(*_args):
                    raise AssertionError("OCR should not write metadata")

                session.database.save_metadata = fail_save_metadata

                job = session.queue_current_for_ocr()

                self.assertIsNotNone(job)
                self.assertEqual(session.metadata.people, "")
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
