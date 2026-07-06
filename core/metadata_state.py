from dataclasses import dataclass


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