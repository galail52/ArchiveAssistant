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

        payload = cls._candidate_payload(result)
        original_text = str(cls._first_value(
            payload,
            "original_text",
            "original_ocr_text",
            "raw_text",
            "raw_ocr_text",
        ) or fallback_original)
        cleaned_text = str(cls._first_value(
            payload,
            "cleaned_text",
            "cleaned_transcription",
            "cleaned_ocr_text",
            "cleaned_ocr",
            "corrected_text",
            "corrected_transcription",
            "transcription",
        ) or "")

        if not cleaned_text.strip():
            keys = ", ".join(sorted(str(key) for key in payload)) or "none"
            raise ValueError(
                "OCR cleanup result did not include cleaned text. "
                f"Returned fields: {keys}."
            )

        return cls(
            original_text=original_text,
            cleaned_text=cleaned_text,
            uncertain_portions=tuple(
                str(item) for item in cls._list_value(
                    payload,
                    "uncertain_portions",
                    "uncertainties",
                    "uncertain_words",
                )
            ),
            corrections=tuple(
                cls._format_correction(item)
                for item in cls._list_value(
                    payload,
                    "corrections",
                    "changes",
                    "significant_corrections",
                )
            ),
            confidence=cls._confidence(cls._first_value(
                payload,
                "confidence",
                "confidence_score",
            )),
            warnings=tuple(str(item) for item in cls._list_value(
                payload,
                "warnings",
                "notes",
            )),
        )

    @classmethod
    def _candidate_payload(cls, result):
        current = result
        for _depth in range(3):
            if not isinstance(current, dict):
                break
            if cls._first_value(
                current,
                "cleaned_text",
                "cleaned_transcription",
                "cleaned_ocr_text",
                "cleaned_ocr",
                "corrected_text",
                "corrected_transcription",
                "transcription",
            ):
                return current
            nested = cls._first_value(
                current,
                "result",
                "output",
                "response",
                "data",
                "ocr_cleanup",
            )
            if not isinstance(nested, dict):
                break
            current = nested
        return current if isinstance(current, dict) else result

    @staticmethod
    def _first_value(mapping, *names):
        normalized = {
            OCRCleanupReview._normalize_key(key): value
            for key, value in mapping.items()
        }
        for name in names:
            value = normalized.get(OCRCleanupReview._normalize_key(name))
            if value not in (None, ""):
                return value
        return None

    @classmethod
    def _list_value(cls, mapping, *names):
        value = cls._first_value(mapping, *names)
        if value is None:
            return []
        if isinstance(value, (list, tuple)):
            return value
        return [value]

    @staticmethod
    def _normalize_key(value):
        return "".join(
            character.lower()
            for character in str(value)
            if character.isalnum()
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
