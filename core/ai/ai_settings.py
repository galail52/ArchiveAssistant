import os
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class AISettings:
    OLLAMA_ENDPOINT: ClassVar[str] = "http://localhost:11434"
    OPEN_WEBUI_ENDPOINT: ClassVar[str] = "http://localhost:3000"

    provider_type: str = "ollama"
    endpoint_url: str = OLLAMA_ENDPOINT
    default_model: str = ""
    enabled: bool = True

    def normalized_provider_type(self):
        return self.provider_type.strip().lower()

    @classmethod
    def from_environment(cls, environ=None):
        environ = environ or os.environ
        provider_type = environ.get(
            "ARCHIVEASSISTANT_AI_PROVIDER",
            "ollama",
        )
        endpoint_url = environ.get("ARCHIVEASSISTANT_AI_ENDPOINT", "")
        default_model = environ.get("ARCHIVEASSISTANT_AI_MODEL", "")
        enabled_value = environ.get("ARCHIVEASSISTANT_AI_ENABLED", "1")

        return cls(
            provider_type=provider_type,
            endpoint_url=endpoint_url or cls.default_endpoint(provider_type),
            default_model=default_model,
            enabled=cls.parse_enabled(enabled_value),
        )

    @classmethod
    def for_provider(
        cls,
        provider_type,
        endpoint_url="",
        default_model="",
        enabled=True,
    ):
        return cls(
            provider_type=provider_type,
            endpoint_url=endpoint_url or cls.default_endpoint(provider_type),
            default_model=default_model,
            enabled=enabled,
        )

    @classmethod
    def default_endpoint(cls, provider_type):
        normalized = str(provider_type or "").strip().lower()

        if normalized in ("open_webui", "open-webui", "open webui"):
            return cls.OPEN_WEBUI_ENDPOINT

        return cls.OLLAMA_ENDPOINT

    @staticmethod
    def parse_enabled(value):
        return str(value).strip().lower() not in {
            "0",
            "false",
            "no",
            "off",
            "disabled",
        }
