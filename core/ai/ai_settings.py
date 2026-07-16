import os
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class AISettings:
    OLLAMA_ENDPOINT: ClassVar[str] = "http://localhost:11434"
    OPEN_WEBUI_ENDPOINT: ClassVar[str] = "http://localhost:3000"
    COMPANYOS_ENDPOINT: ClassVar[str] = "http://localhost:8766"

    provider_type: str = "ollama"
    endpoint_url: str = OLLAMA_ENDPOINT
    default_model: str = ""
    enabled: bool = True
    token_file: str = ""

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
        token_file = environ.get("ARCHIVEASSISTANT_AI_TOKEN_FILE", "")

        return cls(
            provider_type=provider_type,
            endpoint_url=endpoint_url or cls.default_endpoint(provider_type),
            default_model=default_model,
            enabled=cls.parse_enabled(enabled_value),
            token_file=token_file,
        )

    @classmethod
    def for_provider(
        cls,
        provider_type,
        endpoint_url="",
        default_model="",
        enabled=True,
        token_file="",
    ):
        return cls(
            provider_type=provider_type,
            endpoint_url=endpoint_url or cls.default_endpoint(provider_type),
            default_model=default_model,
            enabled=enabled,
            token_file=token_file,
        )

    @classmethod
    def default_endpoint(cls, provider_type):
        normalized = str(provider_type or "").strip().lower()

        if normalized in ("open_webui", "open-webui", "open webui"):
            return cls.OPEN_WEBUI_ENDPOINT
        if normalized in ("companyos", "da-server", "daserver"):
            return cls.COMPANYOS_ENDPOINT

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
