import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.ocr import OCRManager
from core.ocr import OCRStatus
from core.ocr.engines import OCREngineOutput
from core.ocr.engines import TesseractEngine


class MissingEngine:
    name = "Missing OCR"

    def is_available(self):
        return False

    def unavailable_reason(self):
        return "OCR engine missing."

    def extract_text(self, _image_path):
        raise AssertionError("Unavailable engines should not be executed")


class EmptyEngine:
    name = "Empty OCR"

    def is_available(self):
        return True

    def unavailable_reason(self):
        return ""

    def extract_text(self, _image_path):
        return OCREngineOutput(raw_text="")


class FailingEngine:
    name = "Failing OCR"

    def is_available(self):
        return True

    def unavailable_reason(self):
        return ""

    def extract_text(self, _image_path):
        raise RuntimeError("unsupported image")


class EchoEngine:
    name = "Echo OCR"

    def __init__(self, text="extracted text"):
        self.text = text

    def is_available(self):
        return True

    def unavailable_reason(self):
        return ""

    def extract_text(self, _image_path):
        return OCREngineOutput(raw_text=self.text)


class OCREngineIntegrationTests(unittest.TestCase):
    def test_tesseract_missing_engine_detection(self):
        engine = TesseractEngine(
            executable="archiveassistant-definitely-missing-tesseract"
        )

        self.assertFalse(engine.is_available())
        self.assertIn("Tesseract", engine.unavailable_reason())

    def test_missing_engine_returns_failed_result(self):
        manager = OCRManager(engine=MissingEngine())
        job = manager.queue_image(Path("001.jpg"))

        result = manager.execute_job(job)

        self.assertEqual(result.status, OCRStatus.FAILED)
        self.assertEqual(result.engine_name, "Missing OCR")
        self.assertEqual(result.errors, ("OCR engine missing.",))
        self.assertIsNone(manager.queue.pending_job(job.image_id))

    def test_manager_handles_empty_ocr_output(self):
        manager = OCRManager(engine=EmptyEngine())
        job = manager.queue_image(Path("001.jpg"))

        result = manager.execute_job(job)

        self.assertEqual(result.status, OCRStatus.COMPLETED)
        self.assertEqual(result.raw_text, "")
        self.assertIn(
            "OCR completed but returned no text.",
            result.warnings,
        )

    def test_manager_handles_engine_failure(self):
        manager = OCRManager(engine=FailingEngine())
        job = manager.queue_image(Path("001.jpg"))

        result = manager.execute_job(job)

        self.assertEqual(result.status, OCRStatus.FAILED)
        self.assertTrue(result.errors)
        self.assertIn("unsupported image", result.errors[0])

    def test_run_queue_processes_pending_jobs(self):
        manager = OCRManager(engine=EchoEngine())
        manager.queue_image(Path("001.jpg"))
        manager.queue_image(Path("002.jpg"))

        results = manager.run_queue()

        self.assertEqual(len(results), 2)
        self.assertEqual(manager.status_counts()["pending"], 0)
        self.assertEqual(manager.status_counts()["completed"], 2)
        self.assertEqual(manager.latest_result(), results[-1])


if __name__ == "__main__":
    unittest.main()
