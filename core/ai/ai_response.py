from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class AIResponse:
    text: str = ""
    provider_name: str = ""
    model_name: str | None = None
    success: bool = False
    error_message: str = ""
    raw_response: dict = field(default_factory=dict)

    @staticmethod
    def success_response(
        text,
        provider_name,
        model_name=None,
        raw_response=None,
    ):
        return AIResponse(
            text=text,
            provider_name=provider_name,
            model_name=model_name,
            success=True,
            error_message="",
            raw_response=raw_response or {},
        )

    @staticmethod
    def failure_response(
        error_message,
        provider_name="",
        model_name=None,
        raw_response=None,
    ):
        return AIResponse(
            text="",
            provider_name=provider_name,
            model_name=model_name,
            success=False,
            error_message=error_message,
            raw_response=raw_response or {},
        )
