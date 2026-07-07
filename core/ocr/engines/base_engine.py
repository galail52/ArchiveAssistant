from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OCREngineOutput:
    raw_text: str = ""
    confidence: float | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


class OCREngine:
    name = "OCR Engine"

    def is_available(self):
        return False

    def unavailable_reason(self):
        return "OCR engine is not available."

    def extract_text(self, image_path: Path):
        raise NotImplementedError
