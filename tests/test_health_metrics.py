import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.export import ExportRecord
from core.health import archive_quality_score
from core.health import confidence_distribution
from core.health import metadata_completeness
from core.health import percent
from core.metadata_state import MetadataState
from core.review_state import ReviewState


class HealthMetricsTests(unittest.TestCase):
    def make_record(self, metadata):
        return ExportRecord(
            file_path=Path("001.jpg"),
            filename="001.jpg",
            metadata=metadata,
            review_state=ReviewState(),
        )

    def test_percent_calculation(self):
        self.assertEqual(percent(1, 4), 25.0)
        self.assertEqual(percent(1, 3), 33.3)
        self.assertEqual(percent(0, 0), 0.0)

    def test_metadata_completeness(self):
        complete = self.make_record(
            MetadataState(
                people="Ada Lovelace, Charles Babbage",
                event="Reunion",
                location="Murray, Utah",
                date_taken="1958",
            )
        )
        partial = self.make_record(
            MetadataState(
                people="",
                event="Graduation",
                location="",
                date_taken="1962",
            )
        )

        self.assertEqual(metadata_completeness([]), 0.0)
        self.assertEqual(metadata_completeness([complete]), 100.0)
        self.assertEqual(metadata_completeness([complete, partial]), 75.0)

    def test_confidence_distribution(self):
        records = [
            self.make_record(MetadataState(confidence=0)),
            self.make_record(MetadataState(confidence=4)),
            self.make_record(MetadataState(confidence=4)),
            self.make_record(MetadataState(confidence=8)),
        ]

        distribution = confidence_distribution(records)

        self.assertEqual(distribution[0], 1)
        self.assertEqual(distribution[4], 2)
        self.assertEqual(distribution[5], 1)

    def test_archive_quality_score(self):
        distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1}

        self.assertEqual(
            archive_quality_score(
                completeness=100.0,
                reviewed_percent=50.0,
                distribution=distribution,
            ),
            86.0,
        )
        self.assertEqual(archive_quality_score(0.0, 0.0, {}), 0.0)


if __name__ == "__main__":
    unittest.main()
