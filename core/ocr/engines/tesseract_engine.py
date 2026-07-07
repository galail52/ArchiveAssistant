import shutil
import subprocess
from pathlib import Path

from core.ocr.engines.base_engine import OCREngine
from core.ocr.engines.base_engine import OCREngineOutput


class TesseractEngine(OCREngine):
    name = "Tesseract"

    def __init__(self, executable=None, timeout_seconds=30):
        self.executable = executable
        self.timeout_seconds = timeout_seconds

    def executable_path(self):
        if self.executable:
            found = shutil.which(self.executable)

            if found is not None:
                return found

            configured_path = Path(self.executable)

            if configured_path.exists():
                return str(configured_path)

            return None

        return shutil.which("tesseract")

    def is_available(self):
        return self.executable_path() is not None

    def unavailable_reason(self):
        return "Tesseract executable was not found on PATH."

    def extract_text(self, image_path: Path):
        executable = self.executable_path()

        if executable is None:
            return OCREngineOutput(
                errors=(self.unavailable_reason(),),
            )

        try:
            completed = subprocess.run(
                [executable, str(image_path), "stdout"],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return OCREngineOutput(
                errors=("Tesseract OCR timed out.",),
            )
        except OSError as error:
            return OCREngineOutput(
                errors=(f"Tesseract OCR could not start: {error}",),
            )

        stderr_lines = tuple(
            line.strip()
            for line in completed.stderr.splitlines()
            if line.strip()
        )

        if completed.returncode != 0:
            message = (
                stderr_lines
                or (f"Tesseract exited with code {completed.returncode}.",)
            )
            return OCREngineOutput(
                raw_text=completed.stdout,
                errors=message,
            )

        return OCREngineOutput(
            raw_text=completed.stdout,
            confidence=None,
            warnings=stderr_lines,
        )
