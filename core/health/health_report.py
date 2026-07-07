from dataclasses import dataclass


@dataclass(frozen=True)
class HealthReport:
    total_images: int
    reviewed: int
    favorites: int
    restore: int
    delete: int
    needs_research: int
    missing_people: int
    missing_date: int
    missing_location: int
    missing_event: int
    confidence_distribution: dict[int, int]
    completeness: float
    archive_quality_score: float
