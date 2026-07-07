from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from pathlib import Path


@dataclass(frozen=True)
class OCRJob:
    image_id: str
    image_path: Path
    source_type: str = "unknown"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
