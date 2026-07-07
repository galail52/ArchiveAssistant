import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.export import ExportRecord
from core.metadata_state import MetadataState
from core.review_state import ReviewState
from core.search import LOW_CONFIDENCE_THRESHOLD
from core.search import SmartFilterManager


class FakeDatabase:
    def __init__(self, records):
        self.records = records
        self.write_count = 0

    def export_records(self, project_path):
        return self.records

    def save_state(self, *_args):
        self.write_count += 1

    def save_metadata(self, *_args):
        self.write_count += 1


class SmartFilterTests(unittest.TestCase):
    def make_record(
        self,
        filename,
        metadata=None,
        state=None,
    ):
        return ExportRecord(
            file_path=Path(filename),
            filename=filename,
            metadata=metadata or MetadataState(),
            review_state=state or ReviewState(),
        )

    def make_records(self):
        return [
            self.make_record(
                "complete.jpg",
                MetadataState(
                    people="Ada Lovelace",
                    event="Reunion",
                    location="Murray, Utah",
                    date_taken="1958",
                    confidence=5,
                ),
                ReviewState(favorite=True),
            ),
            self.make_record(
                "missing_people.jpg",
                MetadataState(
                    people="",
                    event="Graduation",
                    location="Boston",
                    date_taken="1962",
                    confidence=3,
                ),
            ),
            self.make_record(
                "missing_date.jpg",
                MetadataState(
                    people="Grace Hopper",
                    event="Navy",
                    location="Arlington",
                    date_taken="",
                    confidence=4,
                ),
            ),
            self.make_record(
                "missing_location.jpg",
                MetadataState(
                    people="Katherine Johnson",
                    event="Work",
                    location="",
                    date_taken="1969",
                    confidence=4,
                ),
            ),
            self.make_record(
                "missing_event.jpg",
                MetadataState(
                    people="Dorothy Vaughan",
                    event="",
                    location="Virginia",
                    date_taken="1961",
                    confidence=4,
                ),
            ),
            self.make_record(
                "research.jpg",
                MetadataState(
                    people="Mary Jackson",
                    event="Research",
                    location="Virginia",
                    date_taken="1960",
                    confidence=1,
                ),
                ReviewState(needs_research=True),
            ),
            self.make_record(
                "delete.jpg",
                MetadataState(
                    people="Alan Turing",
                    event="Duplicate",
                    location="Manchester",
                    date_taken="1950",
                    confidence=2,
                ),
                ReviewState(delete=True),
            ),
        ]

    def manager(self, records=None):
        if records is None:
            records = self.make_records()

        return SmartFilterManager(FakeDatabase(records))

    def filenames_for_filter(self, filter_id):
        return [
            record.filename
            for record in self.manager().matching_records(Path("p"), filter_id)
        ]

    def test_filter_registration_and_listing(self):
        filters = self.manager().list_filters()
        ids = [smart_filter.id for smart_filter in filters]

        self.assertEqual(len(filters), 8)
        self.assertIn("missing_people", ids)
        self.assertIn("low_confidence", ids)

    def test_missing_metadata_filters(self):
        self.assertEqual(
            self.filenames_for_filter("missing_people"),
            ["missing_people.jpg"],
        )
        self.assertEqual(
            self.filenames_for_filter("missing_date"),
            ["missing_date.jpg"],
        )
        self.assertEqual(
            self.filenames_for_filter("missing_location"),
            ["missing_location.jpg"],
        )
        self.assertEqual(
            self.filenames_for_filter("missing_event"),
            ["missing_event.jpg"],
        )

    def test_review_state_filters(self):
        self.assertEqual(
            self.filenames_for_filter("needs_research"),
            ["research.jpg"],
        )
        self.assertEqual(
            self.filenames_for_filter("marked_delete"),
            ["delete.jpg"],
        )
        self.assertEqual(
            self.filenames_for_filter("favorites"),
            ["complete.jpg"],
        )

    def test_low_confidence_threshold_behavior(self):
        self.assertEqual(LOW_CONFIDENCE_THRESHOLD, 2)
        self.assertEqual(
            self.filenames_for_filter("low_confidence"),
            ["research.jpg", "delete.jpg"],
        )

    def test_empty_archive_has_no_matches(self):
        manager = self.manager([])

        for smart_filter in manager.list_filters():
            self.assertEqual(
                manager.matching_records(Path("p"), smart_filter.id),
                [],
            )

    def test_manager_is_read_only(self):
        database = FakeDatabase(self.make_records())
        manager = SmartFilterManager(database)

        manager.matching_records(Path("p"), "missing_people")
        manager.matching_file_paths(Path("p"), "missing_people")

        self.assertEqual(database.write_count, 0)


if __name__ == "__main__":
    unittest.main()
