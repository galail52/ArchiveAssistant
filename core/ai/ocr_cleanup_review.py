from dataclasses import dataclass


@dataclass(frozen=True)
class OCRCleanupReview:
    original_text: str
    cleaned_text: str
    uncertain_portions: tuple[str, ...] = ()
    corrections: tuple[str, ...] = ()
    confidence: float | None = None
    warnings: tuple[str, ...] = ()

    @classmethod
    def from_result(cls, result, fallback_original=""):
        if not isinstance(result, dict):
            raise ValueError("OCR cleanup result must be a JSON object.")

        original_text = str(result.get("original_text") or fallback_original)
        cleaned_text = str(result.get("cleaned_text") or "")

        if not cleaned_text.strip():
            raise ValueError("OCR cleanup result did not include cleaned text.")

        return cls(
            original_text=original_text,
            cleaned_text=cleaned_text,
            uncertain_portions=tuple(
                str(item) for item in result.get("uncertain_portions", [])
            ),
            corrections=tuple(
                cls._format_correction(item)
                for item in result.get("corrections", [])
            ),
            confidence=cls._confidence(result.get("confidence")),
            warnings=tuple(str(item) for item in result.get("warnings", [])),
        )

    @staticmethod
    def _format_correction(item):
        if isinstance(item, dict):
            original = str(item.get("original") or item.get("from") or "").strip()
            corrected = str(item.get("corrected") or item.get("to") or "").strip()
            reason = str(item.get("reason") or item.get("explanation") or "").strip()
            change = " → ".join(part for part in (original, corrected) if part)
            if reason and change:
                return f"{change}: {reason}"
            return reason or change or str(item)
        return str(item)

    @staticmethod
    def _confidence(value):
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(number, 1.0))
