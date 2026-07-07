from core.ocr.ocr_queue import OCRQueue
from core.ocr.ocr_result import OCRResult
from core.ocr.ocr_status import OCRStatus


class OCRManager:
    STUB_ENGINE_NAME = "ArchiveAssistant OCR Stub"

    def __init__(self, queue=None):
        self.queue = queue or OCRQueue()

    def queue_image(self, image_path, source_type="unknown"):
        return self.queue.queue_image(image_path, source_type)

    def queue_missing(self, records, source_type="unknown"):
        return self.queue.queue_missing(records, source_type)

    def status_counts(self):
        return self.queue.counts()

    def stub_result_for_job(self, job):
        return OCRResult(
            image_id=job.image_id,
            raw_text="",
            confidence=None,
            engine_name=self.STUB_ENGINE_NAME,
            status=OCRStatus.NOT_IMPLEMENTED,
            warnings=("OCR engine integration is not implemented yet.",),
            errors=(),
        )

    def mark_job_not_implemented(self, job):
        result = self.stub_result_for_job(job)
        self.queue.record_result(result)
        return result
