import os
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.ai import AIManager
from core.ai import AIRequest
from core.ai import AIResponse
from core.ai import AISettings
from core.review_session import ReviewSession


class AvailableProvider:
    provider_name = "Fake AI"

    def __init__(self):
        self.requests = []

    def is_available(self):
        return True

    def list_models(self):
        return ["family-history"]

    def send_request(self, request):
        self.requests.append(request)
        return AIResponse.success_response(
            text="connection ok",
            provider_name=self.provider_name,
            model_name=request.model_name,
            raw_response={"ok": True},
        )


class UnavailableProvider:
    provider_name = "Offline AI"

    def is_available(self):
        return False

    def list_models(self):
        raise OSError("service offline")

    def send_request(self, _request):
        raise OSError("service offline")


class ProviderWithResult:
    provider_name = "Result AI"

    def list_models_result(self):
        return ["one", "two"], ""

    def send_request(self, request):
        return AIResponse.success_response(
            text="hello",
            provider_name=self.provider_name,
            model_name=request.model_name,
        )


class AIFoundationTests(unittest.TestCase):
    def make_session(self, temp_path):
        project_path = temp_path / "project"
        project_path.mkdir()
        (project_path / "001.jpg").touch()

        session = ReviewSession()
        session.open_project(project_path)
        return session

    def test_ai_request_creation_is_immutable(self):
        request = AIRequest(
            prompt="Describe this archive task.",
            model_name="local-model",
            system_text="Be concise.",
            metadata={"image_id": "001.jpg"},
        )

        self.assertEqual(request.prompt, "Describe this archive task.")
        self.assertEqual(request.model_name, "local-model")
        self.assertEqual(request.metadata["image_id"], "001.jpg")

        with self.assertRaises(FrozenInstanceError):
            request.prompt = "changed"

    def test_ai_response_success_and_failure(self):
        success = AIResponse.success_response(
            text="ready",
            provider_name="Fake AI",
            model_name="model",
        )
        failure = AIResponse.failure_response(
            "offline",
            provider_name="Fake AI",
        )

        self.assertTrue(success.success)
        self.assertEqual(success.text, "ready")
        self.assertFalse(failure.success)
        self.assertEqual(failure.error_message, "offline")

    def test_ai_settings_defaults(self):
        settings = AISettings()

        self.assertEqual(settings.provider_type, "ollama")
        self.assertEqual(settings.endpoint_url, "http://localhost:11434")
        self.assertTrue(settings.enabled)

    def test_manager_selects_configured_provider(self):
        provider = AvailableProvider()
        manager = AIManager(
            providers={"ollama": provider},
        )

        self.assertIs(manager.provider(), provider)
        self.assertEqual(manager.list_models(), ["family-history"])

    def test_unavailable_provider_failure_does_not_crash(self):
        manager = AIManager(
            providers={"ollama": UnavailableProvider()},
        )

        response = manager.test_connection()

        self.assertFalse(response.success)
        self.assertIn("service offline", response.error_message)

    def test_manager_lists_models_and_sends_prompt(self):
        manager = AIManager(
            settings=AISettings(default_model="one"),
            providers={"ollama": ProviderWithResult()},
        )

        self.assertEqual(manager.list_models(), ["one", "two"])

        response = manager.send_test_prompt()

        self.assertTrue(response.success)
        self.assertEqual(response.text, "hello")
        self.assertEqual(response.model_name, "one")

    def test_disabled_provider_returns_structured_failure(self):
        manager = AIManager(
            settings=AISettings(enabled=False),
            providers={"ollama": AvailableProvider()},
        )

        response = manager.send_test_prompt()

        self.assertFalse(response.success)
        self.assertEqual(response.error_message, "AI provider is disabled.")

    def test_review_session_ai_does_not_write_metadata(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)
                session.ai_manager = AIManager(
                    settings=AISettings(default_model="family-history"),
                    providers={"ollama": AvailableProvider()},
                )

                def fail_save_metadata(*_args):
                    raise AssertionError("AI should not write metadata")

                session.database.save_metadata = fail_save_metadata

                response = session.send_ai_test_prompt()

                self.assertTrue(response.success)
                self.assertEqual(session.metadata.people, "")
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
