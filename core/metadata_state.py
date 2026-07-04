from dataclasses import dataclass


@dataclass
class MetadataState:
    notes: str = ""
    people: str = ""
    location: str = ""
    date_taken: str = ""

    def reset(self):
        self.notes = ""
        self.people = ""
        self.location = ""
        self.date_taken = ""

    def as_dict(self):
        return {
            "notes": self.notes,
            "people": self.people,
            "location": self.location,
            "date_taken": self.date_taken,
        }