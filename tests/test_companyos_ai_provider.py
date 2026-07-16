from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.ai.ai_manager import AIManager
from core.ai.ai_request import AIRequest
from core.ai.ai_settings import AISettings
from core.ai.archive_advisory import ArchiveAdvisoryClient
from core.ai.providers.companyos_provider import CompanyOSProvider


class CompanyOSProviderTests(unittest.TestCase):
    def settings(self, token_file):
        return AISettings.for_provider(
            "companyos",
            endpoint_url="http://localhost:8766",
            default_model="archive-model",
            token_file=str(token_file),
        )

    def test_manager_selects_companyos_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            token = Path(directory) / "token"
            token.write_text("secret", encoding="utf-8")
            provider = AIManager(settings=self.settings(token)).provider()
            self.assertIsInstance(provider, CompanyOSProvider)

    def test_provider_returns_structured_success(self):
        with tempfile.TemporaryDirectory() as directory:
            token = Path(directory) / "token"
            token.write_text("secret", encoding="utf-8")
            provider = CompanyOSProvider(self.settings(token))
            envelope = {"success": True, "task": "ocr_cleanup", "model": "archive-model", "result": {"cleaned_text": "Christmas"}, "warnings": [], "error": None}
            with patch.object(provider, "_request", return_value=(envelope, "")):
                response = provider.send_request(AIRequest(prompt="", metadata={"task": "ocr_cleanup", "input": {"raw_text": "Chnstmas"}}))
            self.assertTrue(response.success)
            self.assertEqual(json.loads(response.text)["cleaned_text"], "Christmas")

    def test_advisory_client_preserves_failure(self):
        class Manager:
            def send_request(self, request):
                from core.ai.ai_response import AIResponse
                return AIResponse.failure_response("offline", provider_name="CompanyOS", raw_response={"error": {"code": "PROVIDER_UNAVAILABLE", "message": "offline"}})

        result = ArchiveAdvisoryClient(Manager()).run("ocr_cleanup", {"raw_text": "text"})
        self.assertFalse(result.success)
        self.assertEqual(result.error["code"], "PROVIDER_UNAVAILABLE")

    def test_advisory_client_has_no_write_api(self):
        self.assertFalse(hasattr(ArchiveAdvisoryClient, "save"))
        self.assertFalse(hasattr(ArchiveAdvisoryClient, "apply"))


if __name__ == "__main__":
    unittest.main()
