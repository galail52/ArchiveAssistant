import unittest

from core.ai import OCRCleanupReview


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


if __name__ == "__main__":
    unittest.main()
