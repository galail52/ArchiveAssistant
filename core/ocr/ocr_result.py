from dataclasses import dataclass
from datetime import datetime

from core.ocr.ocr_status import OCRStatus


@dataclass(frozen=True)
class OCRResult:
    image_id: str
    raw_text: str = ""
    confidence: float | None = None
    engine_name: str = "stub"
    status: OCRStatus = OCRStatus.PENDING
    executed_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
