from dataclasses import dataclass
from dataclasses import replace


METADATA_FIELDS = [
    "people",
    "event",
    "location",
    "date_taken",
    "keywords",
    "notes",
    "note_by",
    "confidence",
]

RECENT_METADATA_FIELDS = [
    "people",
    "event",
    "location",
    "keywords",
]


@dataclass
class MetadataState:
    people: str = ""
    event: str = ""
    location: str = ""
    date_taken: str = ""
    keywords: str = ""
    notes: str = ""
    note_by: str = ""
    confidence: int = 0

    def reset(self):
        self.people = ""
        self.event = ""
        self.location = ""
        self.date_taken = ""
        self.keywords = ""
        self.notes = ""
        self.note_by = ""
        self.confidence = 0

    def as_dict(self):
        return {
            "people": self.people,
            "event": self.event,
            "location": self.location,
            "date_taken": self.date_taken,
            "keywords": self.keywords,
            "notes": self.notes,
            "note_by": self.note_by,
            "confidence": self.confidence,
        }

    def copy(self):
        return replace(self)

    def selected(self, fields):
        return {
            field: getattr(self, field)
            for field in fields
            if field in METADATA_FIELDS
        }

    def with_fields(self, values):
        metadata = self.copy()

        for field, value in values.items():
            if field in METADATA_FIELDS:
                setattr(metadata, field, value)

        return metadata
