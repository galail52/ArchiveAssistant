from dataclasses import dataclass

from core.metadata_state import METADATA_FIELDS
from core.metadata_state import MetadataState


@dataclass
class MetadataPatch:
    values: dict

    @classmethod
    def from_metadata(cls, metadata: MetadataState, fields):
        return cls(metadata.selected(fields))

    @property
    def fields(self):
        return [
            field
            for field in METADATA_FIELDS
            if field in self.values
        ]

    def apply_to(self, metadata: MetadataState):
        return metadata.with_fields(self.values)
