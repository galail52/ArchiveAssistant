from pathlib import Path

from core.ocr.ocr_job import OCRJob
from core.ocr.ocr_status import OCRStatus


class OCRQueue:
    def __init__(self):
        self.pending_jobs = []
        self.results = {}

    def queue_image(self, image_path, source_type="unknown", replace_existing=False):
        image_path = Path(image_path)
        image_id = str(image_path)

        existing = self.pending_job(image_id)

        if existing is not None:
            return existing

        if self.results.get(image_id) is not None and not replace_existing:
            return None

        if replace_existing:
            self.results.pop(image_id, None)

        job = OCRJob(
            image_id=image_id,
            image_path=image_path,
            source_type=source_type,
        )
        self.pending_jobs.append(job)
        return job

    def queue_missing(self, records, source_type="unknown"):
        jobs = []

        for record in records:
            image_id = str(record.file_path)

            if self.pending_job(image_id) is not None:
                continue

            if self.results.get(image_id) is not None:
                continue

            job = self.queue_image(record.file_path, source_type)

            if job is not None:
                jobs.append(job)

        return jobs

    def pending_job(self, image_id):
        for job in self.pending_jobs:
            if job.image_id == image_id:
                return job

        return None

    def record_result(self, result):
        self.results[result.image_id] = result
        self.pending_jobs = [
            job
            for job in self.pending_jobs
            if job.image_id != result.image_id
        ]

    def counts(self):
        completed = sum(
            1
            for result in self.results.values()
            if result.status == OCRStatus.COMPLETED
        )
        failed = sum(
            1
            for result in self.results.values()
            if result.status in (OCRStatus.FAILED, OCRStatus.NOT_IMPLEMENTED)
        )

        return {
            "pending": len(self.pending_jobs),
            "completed": completed,
            "failed": failed,
        }

    def pending_count(self):
        return self.counts()["pending"]
