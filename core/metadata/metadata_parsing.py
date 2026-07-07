def parse_people(text: str):
    return [
        name
        for name in (
            " ".join(part.strip().split())
            for part in str(text or "").split(",")
        )
        if name
    ]


def join_people(values):
    return ", ".join(
        name
        for name in (
            " ".join(str(value or "").strip().split())
            for value in values
        )
        if name
    )
