from core.health.providers.base import HealthProvider


class ReviewProvider(HealthProvider):
    def collect(self, records):
        return {
            "total_images": len(records),
            "reviewed": sum(1 for record in records if record.reviewed),
            "favorites": sum(
                1 for record in records if record.review_state.favorite
            ),
            "restore": sum(
                1 for record in records if record.review_state.needs_restore
            ),
            "delete": sum(
                1 for record in records if record.review_state.delete
            ),
            "needs_research": sum(
                1 for record in records if record.review_state.needs_research
            ),
        }
