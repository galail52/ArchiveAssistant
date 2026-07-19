import tempfile
import unittest
from pathlib import Path

from core.ai.ai_response import AIResponse
from core.ocr.engines import QwenVLOCREngine


class FakeProvider:
    def __init__(self, response_text='{"text":"Rebecca Lynn Southard\\n3 yrs old"}'):
        self.response_text = response_text
        self.last_request = None

    def list_models_result(self):
        return [QwenVLOCREngine.DEFAULT_MODEL], ""

    def send_request(self, request):
        self.last_request = request
        return AIResponse.success_response(
            text=self.response_text,
            provider_name="Fake Ollama",
            model_name=request.model_name,
        )


class QwenVLOCREngineTests(unittest.TestCase):
    def test_engine_sends_base64_image_and_returns_transcription(self):
        provider = FakeProvider()
        engine = QwenVLOCREngine(provider=provider)

        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "scan.png"
            image_path.write_bytes(b"fake-image")
            output = engine.extract_text(image_path)

        self.assertEqual(output.raw_text, "Rebecca Lynn Southard\n3 yrs old")
        self.assertEqual(output.errors, ())
        self.assertEqual(len(provider.last_request.images), 1)
        self.assertEqual(provider.last_request.model_name, engine.model_name)
        self.assertIn("Omit text that is intentionally crossed out", provider.last_request.prompt)

    def test_plain_text_response_is_preserved_with_warning(self):
        engine = QwenVLOCREngine(provider=FakeProvider("LAGGENHILL"))

        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "scan.png"
            image_path.write_bytes(b"fake-image")
            output = engine.extract_text(image_path)

        self.assertEqual(output.raw_text, "LAGGENHILL")
        self.assertEqual(
            output.warnings,
            ("Qwen OCR returned plain text instead of JSON.",),
        )

    def test_markdown_wrapped_json_is_accepted(self):
        response = '```json\n{"text":"CASTLE KENNEDY\\nGALLOWAY"}\n```'
        engine = QwenVLOCREngine(provider=FakeProvider(response))

        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "scan.png"
            image_path.write_bytes(b"fake-image")
            output = engine.extract_text(image_path)

        self.assertEqual(output.raw_text, "CASTLE KENNEDY\nGALLOWAY")
        self.assertEqual(output.warnings, ())


if __name__ == "__main__":
    unittest.main()
