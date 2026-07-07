from dataclasses import dataclass
from datetime import datetime
from datetime import timezone


@dataclass(frozen=True)
class ImageFingerprint:
    image_id: str
    fingerprint_algorithm: str
    fingerprint_value: str
    created_at: datetime

    @staticmethod
    def create(image_id, fingerprint_algorithm, fingerprint_value):
        return ImageFingerprint(
            image_id=str(image_id),
            fingerprint_algorithm=fingerprint_algorithm,
            fingerprint_value=fingerprint_value,
            created_at=datetime.now(timezone.utc),
        )
