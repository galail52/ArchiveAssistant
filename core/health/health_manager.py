from core.health.health_metrics import archive_quality_score
from core.health.health_metrics import percent
from core.health.health_report import HealthReport
from core.health.providers import ConfidenceProvider
from core.health.providers import MetadataProvider
from core.health.providers import ReviewProvider


class HealthManager:
    def __init__(self, database, providers=None):
        self.database = database
        self.providers = providers or [
            ReviewProvider(),
            MetadataProvider(),
            ConfidenceProvider(),
        ]

    def build_report(self, project_path):
        records = self.database.export_records(project_path)
        metrics = {}

        for provider in self.providers:
            metrics.update(provider.collect(records))

        total = metrics["total_images"]
        reviewed = metrics["reviewed"]
        distribution = metrics["confidence_distribution"]
        completeness = metrics["completeness"]

        return HealthReport(
            total_images=total,
            reviewed=reviewed,
            favorites=metrics["favorites"],
            restore=metrics["restore"],
            delete=metrics["delete"],
            needs_research=metrics["needs_research"],
            missing_people=metrics["missing_people"],
            missing_date=metrics["missing_date"],
            missing_location=metrics["missing_location"],
            missing_event=metrics["missing_event"],
            confidence_distribution=distribution,
            completeness=completeness,
            archive_quality_score=archive_quality_score(
                completeness,
                percent(reviewed, total),
                distribution,
            ),
        )
