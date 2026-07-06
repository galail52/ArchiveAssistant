from core.export.models import ExportWarning


def export_warnings(records):
    warnings = []

    for record in records:
        metadata = record.metadata
        state = record.review_state

        if not metadata.people.strip():
            warnings.append(
                ExportWarning(
                    record.file_path,
                    "missing_people",
                    "People metadata is missing.",
                )
            )

        if not metadata.date_taken.strip():
            warnings.append(
                ExportWarning(
                    record.file_path,
                    "missing_date",
                    "Date metadata is missing.",
                )
            )

        if not metadata.location.strip():
            warnings.append(
                ExportWarning(
                    record.file_path,
                    "missing_location",
                    "Location metadata is missing.",
                )
            )

        if state.delete:
            warnings.append(
                ExportWarning(
                    record.file_path,
                    "marked_delete",
                    "Image is marked for delete.",
                )
            )

        if state.needs_research:
            warnings.append(
                ExportWarning(
                    record.file_path,
                    "needs_research",
                    "Image is marked as needing research.",
                )
            )

    return warnings
