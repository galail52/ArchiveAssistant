import csv
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.export import ExportFormat
from core.export import ExportJob
from core.export import ExportManager
from core.export import ExportRecord
from core.metadata_state import MetadataState
from core.review_state import ReviewState


class ExportFoundationTests(unittest.TestCase):
    def make_records(self, project_path):
        return [
            ExportRecord(
                file_path=project_path / "001.jpg",
                filename="001.jpg",
                metadata=MetadataState(
                    people="Ada Lovelace",
                    event="Family Reunion",
                    location="Murray, Utah",
                    date_taken="1958-07",
                    keywords="family, summer",
                    notes="Standing near the old house.",
                    note_by="Trent",
                    confidence=4,
                ),
                review_state=ReviewState(favorite=True),
            ),
            ExportRecord(
                file_path=project_path / "002.jpg",
                filename="002.jpg",
                metadata=MetadataState(event="Needs review"),
                review_state=ReviewState(
                    needs_research=True,
                    delete=True,
                ),
            ),
        ]

    def test_json_export_writes_metadata_output(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            output_path = Path(temp_dir) / "exports" / "metadata.json"

            result = ExportManager().export(
                ExportJob(
                    ExportFormat.JSON,
                    project_path,
                    output_path,
                    dry_run=False,
                ),
                self.make_records(project_path),
            )

            self.assertEqual(result.records_count, 2)
            self.assertEqual(result.written_files, [output_path])

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["records"][0]["filename"], "001.jpg")
            self.assertEqual(
                payload["records"][0]["metadata"]["people"],
                "Ada Lovelace",
            )
            self.assertEqual(
                payload["records"][1]["review"]["delete"],
                True,
            )

    def test_csv_export_writes_metadata_output(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            output_path = Path(temp_dir) / "exports" / "metadata.csv"

            result = ExportManager().export(
                ExportJob(
                    ExportFormat.CSV,
                    project_path,
                    output_path,
                    dry_run=False,
                ),
                self.make_records(project_path),
            )

            self.assertEqual(result.written_files, [output_path])

            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(rows[0]["filename"], "001.jpg")
            self.assertEqual(rows[0]["people"], "Ada Lovelace")
            self.assertEqual(rows[0]["favorite"], "1")
            self.assertEqual(rows[1]["needs_research"], "1")
            self.assertEqual(rows[1]["delete"], "1")

    def test_dry_run_does_not_write_files(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            output_path = Path(temp_dir) / "exports" / "metadata.json"

            result = ExportManager().export(
                ExportJob(
                    ExportFormat.JSON,
                    project_path,
                    output_path,
                    dry_run=True,
                ),
                self.make_records(project_path),
            )

            self.assertTrue(result.dry_run)
            self.assertEqual(result.written_files, [])
            self.assertFalse(output_path.exists())

    def test_export_warnings_are_generated(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()

            result = ExportManager().export(
                ExportJob(
                    ExportFormat.JSON,
                    project_path,
                    Path(temp_dir) / "preview.json",
                    dry_run=True,
                ),
                self.make_records(project_path),
            )

            warning_codes = [warning.code for warning in result.warnings]

            self.assertIn("missing_people", warning_codes)
            self.assertIn("missing_date", warning_codes)
            self.assertIn("missing_location", warning_codes)
            self.assertIn("marked_delete", warning_codes)
            self.assertIn("needs_research", warning_codes)

    def test_image_metadata_exporters_are_dry_run_only(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            output_path = Path(temp_dir) / "image.xmp"

            result = ExportManager().export(
                ExportJob(
                    ExportFormat.XMP_SIDECAR,
                    project_path,
                    output_path,
                    dry_run=False,
                ),
                self.make_records(project_path),
            )

            self.assertTrue(result.dry_run)
            self.assertEqual(result.written_files, [])
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
