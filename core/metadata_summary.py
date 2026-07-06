from core.metadata_state import MetadataState


SUMMARY_LIMITS = {
    "people": 72,
    "event": 56,
    "location": 56,
    "date_taken": 24,
    "keywords": 64,
    "note_by": 40,
    "notes": 96,
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

    fields = [
        ("People", metadata.people, SUMMARY_LIMITS["people"]),
        ("Event", metadata.event, SUMMARY_LIMITS["event"]),
        ("Location", metadata.location, SUMMARY_LIMITS["location"]),
        ("Date", metadata.date_taken, SUMMARY_LIMITS["date_taken"]),
        ("Tags", metadata.keywords, SUMMARY_LIMITS["keywords"]),
        ("Note By", metadata.note_by, SUMMARY_LIMITS["note_by"]),
    ]

    for label, value, limit in fields:
        display_value = truncate_summary_value(value, limit)

        if display_value:
            rows.append(f"{label}: {display_value}")

    if metadata.confidence:
        rows.append(f"Confidence: {metadata.confidence}/5")

    notes = truncate_summary_value(metadata.notes, SUMMARY_LIMITS["notes"])

    if notes:
        rows.append(f"Notes: {notes}")

    return rows
