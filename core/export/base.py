from abc import ABC
from abc import abstractmethod

from core.export.models import ExportResult


class BaseExporter(ABC):
    format = None
    writes_files = True

    def export(self, job, records, warnings):
        if job.dry_run:
            return ExportResult(
                format=job.format,
                dry_run=True,
                records_count=len(records),
                output_path=job.output_path,
                warnings=warnings,
                written_files=[],
                message="No files were written.",
            )

        return self.write(job, records, warnings)

    @abstractmethod
    def write(self, job, records, warnings):
        raise NotImplementedError
