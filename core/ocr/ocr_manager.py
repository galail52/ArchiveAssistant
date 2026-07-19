from datetime import datetime
from datetime import timezone

from core.ocr.engines import QwenVLOCREngine
from core.ocr.ocr_queue import OCRQueue
from core.ocr.ocr_result import OCRResult
from core.ocr.ocr_status import OCRStatus


class OCRManager:
    DEFAULT_ENGINE_NAME = "Qwen3-VL 8B"

    def __init__(self, queue=None, engine=None):
        self.queue = queue or OCRQueue()
        self.engine = engine or QwenVLOCREngine()
        self._latest_result = None

    def queue_image(self, image_path, source_type="unknown", replace_existing=False):
        return self.queue.queue_image(
            image_path,
            source_type,
            replace_existing=replace_existing,
        )

    def queue_missing(self, records, source_type="unknown"):
        return self.queue.queue_missing(records, source_type)

    def status_counts(self):
        counts = self.queue.counts()
        counts.update(self.engine_status())
        return counts

    def engine_status(self):
        available = self.engine.is_available()
        reason = "" if available else self.engine.unavailable_reason()

        return {
            "engine_name": self.engine.name,
            "engine_available": available,
            "engine_message": reason,
        }

    def execute_job(self, job):
        executed_at = datetime.now(timezone.utc)

        if not self.engine.is_available():
            result = OCRResult(
                image_id=job.image_id,
                raw_text="",
                confidence=None,
                engine_name=self.engine.name,
                status=OCRStatus.FAILED,
                executed_at=executed_at,
                warnings=(),
                errors=(self.engine.unavailable_reason(),),
            )
            self._record_result(result)
            return result

        try:
            output = self.engine.extract_text(job.image_path)
        except Exception as error:
            result = OCRResult(
                image_id=job.image_id,
                raw_text="",
                confidence=None,
                engine_name=self.engine.name,
                status=OCRStatus.FAILED,
                executed_at=executed_at,
                warnings=(),
                errors=(f"OCR failed: {error}",),
            )
            self._record_result(result)
            return result

        warnings = tuple(output.warnings)
        errors = tuple(output.errors)

        if errors:
            status = OCRStatus.FAILED
        else:
            status = OCRStatus.COMPLETED

        if status == OCRStatus.COMPLETED and not output.raw_text.strip():
            warnings = warnings + ("OCR completed but returned no text.",)

        result = OCRResult(
            image_id=job.image_id,
            raw_text=output.raw_text,
            confidence=output.confidence,
            engine_name=self.engine.name,
            status=status,
            executed_at=executed_at,
            warnings=warnings,
            errors=errors,
        )
        self._record_result(result)
        return result

    def run_queue(self):
        jobs = list(self.queue.pending_jobs)
        return [
            self.execute_job(job)
            for job in jobs
        ]

    def latest_result(self):
        return self._latest_result

    def _record_result(self, result):
        self.queue.record_result(result)
        self._latest_result = result
        return result
