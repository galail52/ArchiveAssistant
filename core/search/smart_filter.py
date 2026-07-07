from dataclasses import dataclass

from core.metadata import parse_people


LOW_CONFIDENCE_THRESHOLD = 2


@dataclass(frozen=True)
class SmartFilter:
    id: str
    name: str
    description: str
    predicate: object

    def matches(self, record):
        return bool(self.predicate(record))


def built_in_smart_filters():
    return [
        SmartFilter(
            id="missing_people",
            name="Missing People",
            description="Images without people metadata.",
            predicate=lambda record: not parse_people(record.metadata.people),
        ),
        SmartFilter(
            id="missing_date",
            name="Missing Date",
            description="Images without date metadata.",
            predicate=lambda record: not record.metadata.date_taken.strip(),
        ),
        SmartFilter(
            id="missing_location",
            name="Missing Location",
            description="Images without location metadata.",
            predicate=lambda record: not record.metadata.location.strip(),
        ),
        SmartFilter(
            id="missing_event",
            name="Missing Event",
            description="Images without event metadata.",
            predicate=lambda record: not record.metadata.event.strip(),
        ),
        SmartFilter(
            id="needs_research",
            name="Needs Research",
            description="Images marked as needing research.",
            predicate=lambda record: record.review_state.needs_research,
        ),
        SmartFilter(
            id="marked_delete",
            name="Marked Delete",
            description="Images marked for deletion.",
            predicate=lambda record: record.review_state.delete,
        ),
        SmartFilter(
            id="favorites",
            name="Favorites",
            description="Images marked as favorites.",
            predicate=lambda record: record.review_state.favorite,
        ),
        SmartFilter(
            id="low_confidence",
            name="Low Confidence",
            description=(
                f"Images with confidence {LOW_CONFIDENCE_THRESHOLD} or lower."
            ),
            predicate=lambda record: (
                int(record.metadata.confidence or 0)
                <= LOW_CONFIDENCE_THRESHOLD
            ),
        ),
    ]
