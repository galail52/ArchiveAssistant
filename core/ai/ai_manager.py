from core.ai.ai_request import AIRequest
from core.ai.ai_response import AIResponse
from core.ai.ai_settings import AISettings
from core.ai.providers import OllamaProvider
from core.ai.providers import OpenWebUIProvider
from core.ai.providers import CompanyOSProvider


class AIManager:
    def __init__(self, settings=None, providers=None):
        self.settings = settings or AISettings.from_environment()
        self.providers = providers or {}
        self._last_response = None

    def provider(self):
        provider_type = self.settings.normalized_provider_type()

        if provider_type in self.providers:
            return self.providers[provider_type]

        if provider_type == "ollama":
            return OllamaProvider(self.settings)

        if provider_type in ("open_webui", "open-webui", "open webui"):
            return OpenWebUIProvider(self.settings)
        if provider_type in ("companyos", "da-server", "daserver"):
            return CompanyOSProvider(self.settings)

        return None

    def status(self):
        provider = self.provider()

        if provider is None:
            return {
                "enabled": self.settings.enabled,
                "provider_type": self.settings.provider_type,
                "provider_name": "Unknown",
                "endpoint_url": self.settings.endpoint_url,
                "default_model": self.settings.default_model,
                "available": False,
                "models": [],
                "error_message": "Unknown AI provider.",
            }

        if not self.settings.enabled:
            return {
                "enabled": False,
                "provider_type": self.settings.provider_type,
                "provider_name": provider.provider_name,
                "endpoint_url": self.settings.endpoint_url,
                "default_model": self.settings.default_model,
                "available": False,
                "models": [],
                "error_message": "AI provider is disabled.",
            }

        models, error = self.list_models_result(provider)

        return {
            "enabled": True,
            "provider_type": self.settings.provider_type,
            "provider_name": provider.provider_name,
            "endpoint_url": self.settings.endpoint_url,
            "default_model": self.settings.default_model,
            "available": error == "",
            "models": models,
            "error_message": error,
        }

    def test_connection(self):
        status = self.status()

        if status["available"]:
            return AIResponse.success_response(
                text="AI provider is available.",
                provider_name=status["provider_name"],
                model_name=status["default_model"] or None,
                raw_response={"models": status["models"]},
            )

        return AIResponse.failure_response(
            status["error_message"] or "AI provider is unavailable.",
            provider_name=status["provider_name"],
            model_name=status["default_model"] or None,
            raw_response={"models": status["models"]},
        )

    def list_models(self):
        models, _error = self.list_models_result()
        return models

    def list_models_result(self, provider=None):
        provider = provider or self.provider()

        if provider is None:
            return [], "Unknown AI provider."

        if hasattr(provider, "list_models_result"):
            return provider.list_models_result()

        try:
            return provider.list_models(), ""
        except Exception as error:
            return [], str(error)

    def send_request(self, request):
        provider = self.provider()

        if provider is None:
            response = AIResponse.failure_response("Unknown AI provider.")
            self._last_response = response
            return response

        if not self.settings.enabled:
            response = AIResponse.failure_response(
                "AI provider is disabled.",
                provider_name=provider.provider_name,
            )
            self._last_response = response
            return response

        try:
            response = provider.send_request(request)
        except Exception as error:
            response = AIResponse.failure_response(
                str(error),
                provider_name=provider.provider_name,
                model_name=request.model_name,
            )

        self._last_response = response
        return response

    def send_test_prompt(self):
        return self.send_request(
            AIRequest(
                prompt="Reply with a short ArchiveAssistant connection test.",
                model_name=self.settings.default_model or None,
            )
        )

    def last_response(self):
        return self._last_response
