from core.health.health_metrics import metadata_completeness
from core.health.providers.base import HealthProvider
from core.metadata import parse_people


class MetadataProvider(HealthProvider):
    def collect(self, records):
        return {
            "missing_people": sum(
                1
                for record in records
                if not parse_people(record.metadata.people)
            ),
            "missing_date": sum(
                1 for record in records if not record.metadata.date_taken.strip()
            ),
            "missing_location": sum(
                1 for record in records if not record.metadata.location.strip()
            ),
            "missing_event": sum(
                1 for record in records if not record.metadata.event.strip()
            ),
            "completeness": metadata_completeness(records),
        }
