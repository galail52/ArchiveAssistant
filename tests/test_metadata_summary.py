import unittest

from core.metadata_state import MetadataState
from core.metadata_summary import metadata_summary_lines


class MetadataSummaryTests(unittest.TestCase):
    def test_empty_metadata_summary_has_no_rows(self):
        self.assertEqual(metadata_summary_lines(MetadataState()), [])

    def test_summary_collapses_whitespace_and_truncates_long_values(self):
        metadata = MetadataState(
            people="Ada   Lovelace,   Charles Babbage",
            event="A" * 80,
            location="Murray, Utah",
            date_taken="1958-07",
            keywords="family, summer, reunion",
            notes="Line one\n\nLine two " + "B" * 120,
            note_by="Trent",
            confidence=4,
        )

        rows = metadata_summary_lines(metadata)

        self.assertIn("People: Ada Lovelace, Charles Babbage", rows)
        self.assertIn("Location: Murray, Utah", rows)
        self.assertIn("Date: 1958-07", rows)
        self.assertIn("Tags: family, summer, reunion", rows)
        self.assertIn("Note By: Trent", rows)
        self.assertIn("Confidence: 4/5", rows)

        event_row = next(row for row in rows if row.startswith("Event: "))
        notes_row = next(row for row in rows if row.startswith("Notes: "))

        self.assertTrue(event_row.endswith("..."))
        self.assertLessEqual(len(event_row), len("Event: ") + 56)
        self.assertTrue(notes_row.endswith("..."))
        self.assertNotIn("\n", notes_row)


if __name__ == "__main__":
    unittest.main()
