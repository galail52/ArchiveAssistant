from __future__ import annotations

import json
from dataclasses import dataclass

from core.ai.ai_request import AIRequest


ARCHIVE_TASKS = {
    "ocr_cleanup",
    "back_interpretation",
    "metadata_suggestion",
    "description_draft",
    "keyword_suggestion",
    "consistency_check",
    "research_questions",
}


@dataclass(frozen=True)
class ArchiveSuggestionResult:
    success: bool
    task: str
    result: dict | None
    warnings: tuple
    error: dict | None
    provider: str
    model: str | None


class ArchiveAdvisoryClient:
    """Thin human-review client; it never writes ArchiveAssistant records."""

    def __init__(self, ai_manager):
        self.ai_manager = ai_manager

    def run(self, task, input_data):
        if task not in ARCHIVE_TASKS:
            raise ValueError(f"Unsupported archive advisory task: {task}")
        response = self.ai_manager.send_request(AIRequest(prompt="", metadata={"task": task, "input": dict(input_data)}))
        envelope = response.raw_response or {}
        if not response.success:
            return ArchiveSuggestionResult(False, task, None, tuple(envelope.get("warnings") or ()), envelope.get("error") or {"code": "PROVIDER_ERROR", "message": response.error_message}, response.provider_name, response.model_name)
        result = envelope.get("result")
        if not isinstance(result, dict):
            try:
                result = json.loads(response.text)
            except (TypeError, json.JSONDecodeError):
                return ArchiveSuggestionResult(False, task, None, (), {"code": "MALFORMED_RESPONSE", "message": "AI result was not a JSON object."}, response.provider_name, response.model_name)
        return ArchiveSuggestionResult(True, task, result, tuple(envelope.get("warnings") or ()), None, response.provider_name, response.model_name)
