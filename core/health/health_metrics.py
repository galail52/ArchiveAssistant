from core.metadata import parse_people


def percent(value: int, total: int):
    if total <= 0:
        return 0.0

    return round((value / total) * 100, 1)


def metadata_completeness(records):
    if not records:
        return 0.0

    fields_per_record = 4
    complete_fields = 0

    for record in records:
        metadata = record.metadata

        if parse_people(metadata.people):
            complete_fields += 1

        if metadata.event.strip():
            complete_fields += 1

        if metadata.date_taken.strip():
            complete_fields += 1

        if metadata.location.strip():
            complete_fields += 1

    return percent(complete_fields, len(records) * fields_per_record)


def confidence_distribution(records):
    distribution = {rating: 0 for rating in range(0, 6)}

    for record in records:
        rating = max(0, min(5, int(record.metadata.confidence or 0)))
        distribution[rating] += 1

    return distribution


def confidence_quality_score(distribution):
    total = sum(distribution.values())

    if total <= 0:
        return 0.0

    weighted = sum(rating * count for rating, count in distribution.items())
    return percent(weighted, total * 5)


def archive_quality_score(
    completeness: float,
    reviewed_percent: float,
    distribution,
):
    if not distribution or sum(distribution.values()) <= 0:
        return 0.0

    confidence_score = confidence_quality_score(distribution)
    score = (
        completeness * 0.6
        + reviewed_percent * 0.25
        + confidence_score * 0.15
    )

    return round(score, 1)
