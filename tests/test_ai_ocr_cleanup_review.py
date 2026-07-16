import unittest
from unittest.mock import Mock

from core.ai import OCRCleanupReview
from core.ocr import OCRResult, OCRStatus
from core.review_session import ReviewSession


class OCRCleanupReviewTests(unittest.TestCase):
    def test_builds_review_without_changing_original(self):
        review = OCRCleanupReview.from_result({
            "original_text": "Chnstmas 1958",
            "cleaned_text": "Christmas 1958",
            "uncertain_portions": ["Bil"],
            "corrections": [{
                "original": "Chnstmas",
                "corrected": "Christmas",
                "reason": "Likely OCR substitution.",
            }],
            "confidence": 0.91,
        })

        self.assertEqual(review.original_text, "Chnstmas 1958")
        self.assertEqual(review.cleaned_text, "Christmas 1958")
        self.assertIn("Chnstmas → Christmas", review.corrections[0])
        self.assertEqual(review.confidence, 0.91)

    def test_requires_cleaned_text(self):
        with self.assertRaises(ValueError):
            OCRCleanupReview.from_result({"original_text": "raw"})

    def test_combined_workflow_runs_cleanup_after_successful_ocr(self):
        session = ReviewSession.__new__(ReviewSession)
        result = OCRResult(
            image_id="image.png",
            raw_text="Chnstmas 1958",
            status=OCRStatus.COMPLETED,
        )
        session.run_current_ocr = Mock(return_value=result)
        session.clean_latest_ocr_with_ai = Mock(return_value=("review", ""))

        returned_result, review, error = session.run_current_ocr_with_ai_cleanup()

        self.assertIs(returned_result, result)
        self.assertEqual(review, "review")
        self.assertEqual(error, "")
        session.clean_latest_ocr_with_ai.assert_called_once_with()

    def test_combined_workflow_stops_when_ocr_has_no_text(self):
        session = ReviewSession.__new__(ReviewSession)
        result = OCRResult(
            image_id="image.png",
            raw_text="",
            status=OCRStatus.COMPLETED,
            warnings=("OCR completed but returned no text.",),
        )
        session.run_current_ocr = Mock(return_value=result)
        session.clean_latest_ocr_with_ai = Mock()

        returned_result, review, error = session.run_current_ocr_with_ai_cleanup()

        self.assertIs(returned_result, result)
        self.assertIsNone(review)
        self.assertIn("without extracted text", error)
        session.clean_latest_ocr_with_ai.assert_not_called()

    def test_accepts_cleaned_transcription_alias(self):
        review = OCRCleanupReview.from_result({
            "raw_ocr_text": "Chnstmas 1958",
            "cleaned_transcription": "Christmas 1958",
        })

        self.assertEqual(review.original_text, "Chnstmas 1958")
        self.assertEqual(review.cleaned_text, "Christmas 1958")

    def test_accepts_corrected_text_alias(self):
        review = OCRCleanupReview.from_result(
            {"corrected_text": "Christmas 1958"},
            fallback_original="Chnstmas 1958",
        )

        self.assertEqual(review.original_text, "Chnstmas 1958")
        self.assertEqual(review.cleaned_text, "Christmas 1958")

    def test_accepts_nested_result_and_camel_case(self):
        review = OCRCleanupReview.from_result({
            "result": {
                "cleanedTranscription": "Christmas 1958",
                "uncertainWords": ["Bill"],
                "confidenceScore": 0.88,
            }
        }, fallback_original="Chnstmas 1958")

        self.assertEqual(review.original_text, "Chnstmas 1958")
        self.assertEqual(review.cleaned_text, "Christmas 1958")
        self.assertEqual(review.uncertain_portions, ("Bill",))
        self.assertEqual(review.confidence, 0.88)

    def test_error_reports_returned_fields(self):
        with self.assertRaisesRegex(ValueError, "Returned fields: explanation"):
            OCRCleanupReview.from_result({"explanation": "No transcription"})


if __name__ == "__main__":
    unittest.main()
