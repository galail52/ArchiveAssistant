import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.export import ExportRecord
from core.health import HealthManager
from core.metadata_state import MetadataState
from core.review_state import ReviewState


class FakeDatabase:
    def __init__(self, records):
        self.records = records

    def export_records(self, project_path):
        return self.records


class HealthManagerTests(unittest.TestCase):
    def make_record(
        self,
        filename,
        metadata=None,
        state=None,
        reviewed=False,
    ):
        return ExportRecord(
            file_path=Path(filename),
            filename=filename,
            metadata=metadata or MetadataState(),
            review_state=state or ReviewState(),
            reviewed=reviewed,
        )

    def build_report(self, records):
        return HealthManager(FakeDatabase(records)).build_report(
            Path("project")
        )

    def test_empty_archive(self):
        report = self.build_report([])

        self.assertEqual(report.total_images, 0)
        self.assertEqual(report.reviewed, 0)
        self.assertEqual(report.missing_people, 0)
        self.assertEqual(report.completeness, 0.0)
        self.assertEqual(report.archive_quality_score, 0.0)

    def test_complete_archive(self):
        report = self.build_report(
            [
                self.make_record(
                    "001.jpg",
                    MetadataState(
                        people="Ada Lovelace, Charles Babbage",
                        event="Reunion",
                        location="Murray, Utah",
                        date_taken="1958",
                        confidence=5,
                    ),
                    ReviewState(favorite=True),
                    reviewed=True,
                )
            ]
        )

        self.assertEqual(report.total_images, 1)
        self.assertEqual(report.reviewed, 1)
        self.assertEqual(report.favorites, 1)
        self.assertEqual(report.missing_people, 0)
        self.assertEqual(report.missing_date, 0)
        self.assertEqual(report.missing_location, 0)
        self.assertEqual(report.missing_event, 0)
        self.assertEqual(report.confidence_distribution[5], 1)
        self.assertEqual(report.completeness, 100.0)
        self.assertEqual(report.archive_quality_score, 100.0)

    def test_mixed_archive(self):
        report = self.build_report(
            [
                self.make_record(
                    "001.jpg",
                    MetadataState(
                        people="Ada Lovelace",
                        event="Reunion",
                        location="Murray, Utah",
                        date_taken="1958",
                        confidence=4,
                    ),
                    ReviewState(favorite=True),
                    reviewed=True,
                ),
                self.make_record(
                    "002.jpg",
                    MetadataState(
                        people="",
                        event="",
                        location="",
                        date_taken="",
                        confidence=0,
                    ),
                    ReviewState(needs_research=True, delete=True),
                    reviewed=False,
                ),
            ]
        )

        self.assertEqual(report.total_images, 2)
        self.assertEqual(report.reviewed, 1)
        self.assertEqual(report.favorites, 1)
        self.assertEqual(report.delete, 1)
        self.assertEqual(report.needs_research, 1)
        self.assertEqual(report.missing_people, 1)
        self.assertEqual(report.missing_date, 1)
        self.assertEqual(report.missing_location, 1)
        self.assertEqual(report.missing_event, 1)
        self.assertEqual(report.completeness, 50.0)
        self.assertEqual(report.archive_quality_score, 48.5)


if __name__ == "__main__":
    unittest.main()
