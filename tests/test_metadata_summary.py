import unittest

from core.metadata_state import MetadataState
from core.metadata_summary import metadata_summary_lines
from core.metadata_summary import star_rating


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
        self.assertIn("Keywords: 3", rows)
        self.assertIn("Note By: Trent", rows)
        self.assertIn("Notes: Yes", rows)
        self.assertIn("Confidence: ★★★★☆", rows)

        event_row = next(row for row in rows if row.startswith("Event: "))

        self.assertTrue(event_row.endswith("..."))
        self.assertLessEqual(len(event_row), len("Event: ") + 48)

    def test_summary_truncates_long_people_values(self):
        metadata = MetadataState(
            people="Ada Lovelace, Charles Babbage, Grace Hopper, Katherine Johnson",
            event="Reunion",
            location="Murray, Utah",
            date_taken="1958",
            confidence=5,
        )

        rows = metadata_summary_lines(metadata)
        people_row = next(row for row in rows if row.startswith("People: "))

        self.assertTrue(people_row.endswith("..."))
        self.assertLessEqual(len(people_row), len("People: ") + 56)
        self.assertIn("Event: Reunion", rows)
        self.assertIn("Location: Murray, Utah", rows)
        self.assertIn("Date: 1958", rows)
        self.assertIn(f"Confidence: {star_rating(5)}", rows)


if __name__ == "__main__":
    unittest.main()
