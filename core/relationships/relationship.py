from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone

from core.relationships.relationship_type import RelationshipType


@dataclass(frozen=True)
class Relationship:
    relationship_id: int | None
    source_image_id: str
    target_image_id: str
    relationship_type: RelationshipType
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    notes: str = ""
