from dataclasses import dataclass

from core.ocr.ocr_status import OCRStatus


@dataclass(frozen=True)
class OCRResult:
    image_id: str
    raw_text: str = ""
    confidence: float | None = None
    engine_name: str = "stub"
    status: OCRStatus = OCRStatus.PENDING
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
