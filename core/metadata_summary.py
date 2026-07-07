from core.metadata import parse_people
from core.metadata_state import MetadataState


SUMMARY_LIMITS = {
    "people": 56,
    "event": 48,
    "location": 48,
    "date_taken": 24,
    "note_by": 32,
}


def clean_summary_value(value: str):
    return " ".join(str(value or "").split())


def truncate_summary_value(value: str, limit: int):
    value = clean_summary_value(value)

    if len(value) <= limit:
        return value

    return value[: max(0, limit - 3)].rstrip() + "..."


def metadata_summary_lines(metadata: MetadataState | None):
    if metadata is None:
        return []

    rows = []
    keywords = split_list_value(metadata.keywords)
    people = parse_people(metadata.people)

    fields = [
        ("Event", metadata.event, SUMMARY_LIMITS["event"]),
        ("Location", metadata.location, SUMMARY_LIMITS["location"]),
        ("Date", metadata.date_taken, SUMMARY_LIMITS["date_taken"]),
        ("Note By", metadata.note_by, SUMMARY_LIMITS["note_by"]),
    ]

    if people:
        people_value = " ".join(f"[{person}]" for person in people)
        rows.append(
            f"People: {truncate_summary_value(people_value, SUMMARY_LIMITS['people'])}"
        )

    for label, value, limit in fields:
        display_value = truncate_summary_value(value, limit)

        if display_value:
            rows.append(f"{label}: {display_value}")

    if keywords:
        rows.append(f"Keywords: {len(keywords)}")

    if clean_summary_value(metadata.notes):
        rows.append("Notes: Yes")

    if metadata.confidence:
        rows.append(f"Confidence: {star_rating(metadata.confidence)}")

    return rows


def split_list_value(value: str):
    return [
        clean_summary_value(part)
        for part in str(value or "").split(",")
        if clean_summary_value(part)
    ]


def star_rating(value: int):
    rating = max(0, min(5, int(value or 0)))
    return "★" * rating + "☆" * (5 - rating)
