from dataclasses import dataclass


@dataclass(frozen=True)
class AISettings:
    provider_type: str = "ollama"
    endpoint_url: str = "http://localhost:11434"
    default_model: str = ""
    enabled: bool = True

    def normalized_provider_type(self):
        return self.provider_type.strip().lower()
