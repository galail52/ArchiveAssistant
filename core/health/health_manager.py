from core.health.health_metrics import archive_quality_score
from core.health.health_metrics import confidence_distribution
from core.health.health_metrics import metadata_completeness
from core.health.health_metrics import percent
from core.health.health_report import HealthReport
from core.metadata import parse_people


class HealthManager:
    def __init__(self, database):
        self.database = database

    def build_report(self, project_path):
        records = self.database.export_records(project_path)
        total = len(records)
        reviewed = sum(1 for record in records if record.reviewed)
        distribution = confidence_distribution(records)
        completeness = metadata_completeness(records)

        return HealthReport(
            total_images=total,
            reviewed=reviewed,
            favorites=sum(
                1 for record in records if record.review_state.favorite
            ),
            restore=sum(
                1 for record in records if record.review_state.needs_restore
            ),
            delete=sum(
                1 for record in records if record.review_state.delete
            ),
            needs_research=sum(
                1 for record in records if record.review_state.needs_research
            ),
            missing_people=sum(
                1
                for record in records
                if not parse_people(record.metadata.people)
            ),
            missing_date=sum(
                1 for record in records if not record.metadata.date_taken.strip()
            ),
            missing_location=sum(
                1 for record in records if not record.metadata.location.strip()
            ),
            missing_event=sum(
                1 for record in records if not record.metadata.event.strip()
            ),
            confidence_distribution=distribution,
            completeness=completeness,
            archive_quality_score=archive_quality_score(
                completeness,
                percent(reviewed, total),
                distribution,
            ),
        )
