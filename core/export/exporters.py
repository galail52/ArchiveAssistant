import csv
import json

from core.export.base import BaseExporter
from core.export.models import ExportFormat
from core.export.models import ExportResult


class JsonExporter(BaseExporter):
    format = ExportFormat.JSON

    def write(self, job, records, warnings):
        job.output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "project_path": str(job.project_path),
            "records": [record.as_dict() for record in records],
            "warnings": [warning.as_dict() for warning in warnings],
        }

        job.output_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

        return ExportResult(
            format=job.format,
            dry_run=False,
            records_count=len(records),
            output_path=job.output_path,
            warnings=warnings,
            written_files=[job.output_path],
        )


class CsvExporter(BaseExporter):
    format = ExportFormat.CSV

    FIELDNAMES = [
        "file_path",
        "filename",
        "people",
        "people_values",
        "event",
        "location",
        "date_taken",
        "keywords",
        "notes",
        "note_by",
        "confidence",
        "favorite",
        "has_back",
        "needs_restore",
        "needs_research",
        "delete",
    ]

    def write(self, job, records, warnings):
        job.output_path.parent.mkdir(parents=True, exist_ok=True)

        with job.output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.FIELDNAMES)
            writer.writeheader()

            for record in records:
                metadata = record.metadata
                state = record.review_state
                writer.writerow(
                    {
                        "file_path": str(record.file_path),
                        "filename": record.filename,
                        "people": metadata.people,
                        "people_values": "; ".join(record.as_dict()["people"]),
                        "event": metadata.event,
                        "location": metadata.location,
                        "date_taken": metadata.date_taken,
                        "keywords": metadata.keywords,
                        "notes": metadata.notes,
                        "note_by": metadata.note_by,
                        "confidence": metadata.confidence,
                        "favorite": int(state.favorite),
                        "has_back": int(state.has_back),
                        "needs_restore": int(state.needs_restore),
                        "needs_research": int(state.needs_research),
                        "delete": int(state.delete),
                    }
                )

        return ExportResult(
            format=job.format,
            dry_run=False,
            records_count=len(records),
            output_path=job.output_path,
            warnings=warnings,
            written_files=[job.output_path],
        )


class DryRunOnlyExporter(BaseExporter):
    writes_files = False

    def write(self, job, records, warnings):
        return ExportResult(
            format=job.format,
            dry_run=True,
            records_count=len(records),
            output_path=job.output_path,
            warnings=warnings,
            written_files=[],
            message=(
                f"{job.format.value} export is a dry-run stub; "
                "no image files were modified."
            ),
        )


class XmpSidecarExporter(DryRunOnlyExporter):
    format = ExportFormat.XMP_SIDECAR


class ExifExporter(DryRunOnlyExporter):
    format = ExportFormat.EXIF


class IptcExporter(DryRunOnlyExporter):
    format = ExportFormat.IPTC
