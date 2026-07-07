import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.export import ExportRecord
from core.health import HealthManager
from core.health.providers import ConfidenceProvider
from core.health.providers import MetadataProvider
from core.health.providers import ReviewProvider
from core.metadata_state import MetadataState
from core.review_state import ReviewState


class FakeDatabase:
    def __init__(self, records):
        self.records = records

    def export_records(self, project_path):
        return self.records


class HealthProviderTests(unittest.TestCase):
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

    def test_review_provider_collects_review_totals(self):
        records = [
            self.make_record(
                "001.jpg",
                state=ReviewState(favorite=True),
                reviewed=True,
            ),
            self.make_record(
                "002.jpg",
                state=ReviewState(
                    needs_restore=True,
                    needs_research=True,
                    delete=True,
                ),
            ),
        ]

        metrics = ReviewProvider().collect(records)

        self.assertEqual(metrics["total_images"], 2)
        self.assertEqual(metrics["reviewed"], 1)
        self.assertEqual(metrics["favorites"], 1)
        self.assertEqual(metrics["restore"], 1)
        self.assertEqual(metrics["needs_research"], 1)
        self.assertEqual(metrics["delete"], 1)

    def test_metadata_provider_collects_missing_metadata(self):
        records = [
            self.make_record(
                "001.jpg",
                MetadataState(
                    people="Ada Lovelace",
                    event="Reunion",
                    location="Murray, Utah",
                    date_taken="1958",
                ),
            ),
            self.make_record("002.jpg", MetadataState()),
        ]

        metrics = MetadataProvider().collect(records)

        self.assertEqual(metrics["missing_people"], 1)
        self.assertEqual(metrics["missing_event"], 1)
        self.assertEqual(metrics["missing_location"], 1)
        self.assertEqual(metrics["missing_date"], 1)
        self.assertEqual(metrics["completeness"], 50.0)

    def test_confidence_provider_collects_distribution(self):
        records = [
            self.make_record("001.jpg", MetadataState(confidence=0)),
            self.make_record("002.jpg", MetadataState(confidence=5)),
        ]

        metrics = ConfidenceProvider().collect(records)

        self.assertEqual(metrics["confidence_distribution"][0], 1)
        self.assertEqual(metrics["confidence_distribution"][5], 1)

    def test_manager_uses_provider_metrics_for_report(self):
        records = [
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
                MetadataState(confidence=0),
                ReviewState(needs_research=True),
            ),
        ]

        report = HealthManager(FakeDatabase(records)).build_report(Path("p"))

        self.assertEqual(report.total_images, 2)
        self.assertEqual(report.reviewed, 1)
        self.assertEqual(report.favorites, 1)
        self.assertEqual(report.needs_research, 1)
        self.assertEqual(report.missing_people, 1)
        self.assertEqual(report.completeness, 50.0)

    def test_provider_based_empty_archive_report(self):
        report = HealthManager(FakeDatabase([])).build_report(Path("p"))

        self.assertEqual(report.total_images, 0)
        self.assertEqual(report.completeness, 0.0)
        self.assertEqual(report.archive_quality_score, 0.0)


if __name__ == "__main__":
    unittest.main()
