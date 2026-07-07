from core.health.health_metrics import confidence_distribution
from core.health.providers.base import HealthProvider


class ConfidenceProvider(HealthProvider):
    def collect(self, records):
        return {
            "confidence_distribution": confidence_distribution(records),
        }
