from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from core.metadata import parse_people
from core.metadata_state import MetadataState
from core.review_state import ReviewState


class ExportFormat(Enum):
    JSON = "json"
    CSV = "csv"
    XMP_SIDECAR = "xmp_sidecar"
    EXIF = "exif"
    IPTC = "iptc"


@dataclass
class ExportJob:
    format: ExportFormat
    project_path: Path
    output_path: Path
    dry_run: bool = True


@dataclass
class ExportRecord:
    file_path: Path
    filename: str
    metadata: MetadataState
    review_state: ReviewState
    reviewed: bool = False

    def as_dict(self):
        return {
            "file_path": str(self.file_path),
            "filename": self.filename,
            "metadata": self.metadata.as_dict(),
            "people": parse_people(self.metadata.people),
            "review": self.review_state.as_dict(),
            "reviewed": self.reviewed,
        }


@dataclass
class ExportWarning:
    file_path: Path
    code: str
    message: str

    def as_dict(self):
        return {
            "file_path": str(self.file_path),
            "code": self.code,
            "message": self.message,
        }


@dataclass
class ExportResult:
    format: ExportFormat
    dry_run: bool
    records_count: int
    output_path: Path | None
    warnings: list[ExportWarning]
    written_files: list[Path]
    message: str = ""

    def summary_lines(self):
        lines = [
            f"Format: {self.format.value}",
            f"Mode: {'Dry run' if self.dry_run else 'Write'}",
            f"Images: {self.records_count}",
            f"Warnings: {len(self.warnings)}",
        ]

        if self.output_path is not None:
            lines.append(f"Output: {self.output_path}")

        if self.written_files:
            lines.append(f"Files written: {len(self.written_files)}")

        if self.message:
            lines.append(self.message)

        return lines
