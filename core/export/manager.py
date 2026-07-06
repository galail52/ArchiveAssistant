from core.export.exporters import CsvExporter
from core.export.exporters import ExifExporter
from core.export.exporters import IptcExporter
from core.export.exporters import JsonExporter
from core.export.exporters import XmpSidecarExporter
from core.export.models import ExportFormat
from core.export.validators import export_warnings


class ExportManager:
    def __init__(self):
        exporters = [
            JsonExporter(),
            CsvExporter(),
            XmpSidecarExporter(),
            ExifExporter(),
            IptcExporter(),
        ]
        self.exporters = {
            exporter.format: exporter
            for exporter in exporters
        }

    def export(self, job, records):
        exporter = self.exporters[job.format]
        warnings = export_warnings(records)

        if not exporter.writes_files:
            job.dry_run = True

        return exporter.export(job, records, warnings)

    def formats(self):
        return list(ExportFormat)
