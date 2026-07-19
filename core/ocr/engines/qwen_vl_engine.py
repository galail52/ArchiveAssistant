import base64
import json
import os
from pathlib import Path

from core.ai.ai_request import AIRequest
from core.ai.ai_settings import AISettings
from core.ai.providers import OllamaProvider
from core.ocr.engines.base_engine import OCREngine
from core.ocr.engines.base_engine import OCREngineOutput


class QwenVLOCREngine(OCREngine):
    name = "Qwen3-VL 8B"
    DEFAULT_ENDPOINT = "http://192.168.0.68:11434"
    DEFAULT_MODEL = "hf.co/Qwen/Qwen3-VL-8B-Instruct-GGUF:Q4_K_M"
    PROMPT = """Transcribe the handwritten text in this photo-back scan.

Rules:
- Omit text that is intentionally crossed out, scribbled out, or cancelled.
- Preserve the original reading order, line breaks, capitalization, punctuation, ages, and symbols.
- Do not explain the image.
- Do not normalize names or place names.
- Do not add labels, Markdown, or commentary.
- Return JSON only in this exact form:
  {"text":"line 1\\nline 2"}
- If no readable uncancelled text exists, return {"text":""}.
"""

    def __init__(self, endpoint_url=None, model_name=None, provider=None):
        self.endpoint_url = (
            endpoint_url
            or os.environ.get("ARCHIVEASSISTANT_OCR_ENDPOINT")
            or os.environ.get("ARCHIVEASSISTANT_AI_ENDPOINT")
            or self.DEFAULT_ENDPOINT
        )
        self.model_name = (
            model_name
            or os.environ.get("ARCHIVEASSISTANT_OCR_MODEL")
            or os.environ.get("ARCHIVEASSISTANT_AI_MODEL")
            or self.DEFAULT_MODEL
        )
        settings = AISettings.for_provider(
            "ollama",
            endpoint_url=self.endpoint_url,
            default_model=self.model_name,
        )
        self.provider = provider or OllamaProvider(settings)

    def is_available(self):
        models, error = self.provider.list_models_result()
        return not error and self.model_name in models

    def unavailable_reason(self):
        models, error = self.provider.list_models_result()
        if error:
            return f"Qwen OCR could not reach Ollama at {self.endpoint_url}: {error}"
        if self.model_name not in models:
            return f"Qwen OCR model is not installed: {self.model_name}"
        return "Qwen OCR is unavailable."

    def extract_text(self, image_path: Path):
        try:
            image_bytes = Path(image_path).read_bytes()
        except OSError as error:
            return OCREngineOutput(errors=(f"Could not read OCR image: {error}",))

        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        response = self.provider.send_request(
            AIRequest(
                prompt=self.PROMPT,
                model_name=self.model_name,
                images=(encoded_image,),
            )
        )

        if not response.success:
            return OCREngineOutput(errors=(response.error_message or "Qwen OCR failed.",))

        text, warning = self._parse_response(response.text)
        warnings = (warning,) if warning else ()
        return OCREngineOutput(raw_text=text, warnings=warnings)

    @staticmethod
    def _parse_response(response_text):
        cleaned = str(response_text or "").strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError:
            return cleaned, "Qwen OCR returned plain text instead of JSON."

        if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
            return cleaned, "Qwen OCR returned malformed JSON; showing its raw response."
        return payload["text"].strip(), ""
