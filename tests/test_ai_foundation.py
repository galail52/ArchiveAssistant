import os
import sys
import unittest
from dataclasses import FrozenInstanceError
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.ai import AIManager
from core.ai import AIRequest
from core.ai import AIResponse
from core.ai import AISettings
from core.ai.providers import OllamaProvider
from core.ai.providers import OpenWebUIProvider
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


class FakeOllamaProvider(OllamaProvider):
    def __init__(self, settings, get_payload=None, post_payload=None, error=""):
        super().__init__(settings)
        self.get_payload = get_payload
        self.post_payload = post_payload
        self.error = error
        self.last_post_payload = None

    def get_json(self, _path):
        return self.get_payload, self.error

    def post_json(self, _path, _payload):
        self.last_post_payload = _payload
        return self.post_payload, self.error


class FakeOpenWebUIProvider(OpenWebUIProvider):
    def __init__(self, settings, get_payload=None, post_payload=None, error=""):
        super().__init__(settings)
        self.get_payload = get_payload
        self.post_payload = post_payload
        self.error = error

    def get_json(self, _path):
        return self.get_payload, self.error

    def post_json(self, _path, _payload):
        return self.post_payload, self.error


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

    def test_ai_settings_load_from_environment(self):
        with patch.dict(
            os.environ,
            {
                "ARCHIVEASSISTANT_AI_PROVIDER": "open_webui",
                "ARCHIVEASSISTANT_AI_ENDPOINT": "http://local-ai:3000",
                "ARCHIVEASSISTANT_AI_MODEL": "family-history",
                "ARCHIVEASSISTANT_AI_ENABLED": "false",
            },
        ):
            settings = AISettings.from_environment()

        self.assertEqual(settings.provider_type, "open_webui")
        self.assertEqual(settings.endpoint_url, "http://local-ai:3000")
        self.assertEqual(settings.default_model, "family-history")
        self.assertFalse(settings.enabled)

    def test_provider_defaults_match_local_adapters(self):
        open_webui = AISettings.for_provider("open_webui")

        self.assertEqual(open_webui.endpoint_url, "http://localhost:3000")

    def test_manager_selects_configured_provider(self):
        provider = AvailableProvider()
        manager = AIManager(
            providers={"ollama": provider},
        )

        self.assertIs(manager.provider(), provider)
        self.assertEqual(manager.list_models(), ["family-history"])

    def test_manager_selects_open_webui_provider(self):
        manager = AIManager(
            settings=AISettings.for_provider("open_webui"),
        )

        self.assertIsInstance(manager.provider(), OpenWebUIProvider)

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

    def test_ollama_provider_handles_malformed_model_response(self):
        provider = FakeOllamaProvider(
            AISettings(default_model="model"),
            get_payload={"models": "not-a-list"},
        )

        models, error = provider.list_models_result()

        self.assertEqual(models, [])
        self.assertIn("Malformed Ollama", error)

    def test_ollama_provider_handles_malformed_prompt_response(self):
        provider = FakeOllamaProvider(
            AISettings(default_model="model"),
            post_payload={"unexpected": "shape"},
        )

        response = provider.send_request(AIRequest(prompt="hello"))

        self.assertFalse(response.success)
        self.assertIn("Malformed Ollama", response.error_message)

    def test_ollama_provider_sends_images(self):
        provider = FakeOllamaProvider(
            AISettings.for_provider("ollama", default_model="vision-model"),
            post_payload={"response": "ok"},
        )

        response = provider.send_request(
            AIRequest(prompt="read image", images=("base64-image",))
        )

        self.assertTrue(response.success)
        self.assertEqual(provider.last_post_payload["images"], ["base64-image"])

    def test_open_webui_provider_handles_malformed_model_response(self):
        provider = FakeOpenWebUIProvider(
            AISettings.for_provider("open_webui", default_model="model"),
            get_payload={"data": "not-a-list"},
        )

        models, error = provider.list_models_result()

        self.assertEqual(models, [])
        self.assertIn("Malformed Open WebUI", error)

    def test_open_webui_provider_handles_malformed_prompt_response(self):
        provider = FakeOpenWebUIProvider(
            AISettings.for_provider("open_webui", default_model="model"),
            post_payload={"choices": []},
        )

        response = provider.send_request(AIRequest(prompt="hello"))

        self.assertFalse(response.success)
        self.assertIn("Malformed Open WebUI", response.error_message)

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

    def test_review_session_ai_does_not_mutate_image_file(self):
        original_cwd = Path.cwd()

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            session = None

            try:
                session = self.make_session(temp_path)
                image_path = session.current_file
                before = sha256(image_path.read_bytes()).hexdigest()
                session.ai_manager = AIManager(
                    settings=AISettings(default_model="family-history"),
                    providers={"ollama": AvailableProvider()},
                )

                session.test_ai_connection()
                session.list_ai_models()
                session.send_ai_test_prompt()

                after = sha256(image_path.read_bytes()).hexdigest()

                self.assertEqual(before, after)
                self.assertEqual(session.metadata.people, "")
            finally:
                if session is not None:
                    session.database.connection.close()

                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
