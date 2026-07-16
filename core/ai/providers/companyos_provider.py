import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from core.ai.ai_provider import AIProvider
from core.ai.ai_response import AIResponse


class CompanyOSProvider(AIProvider):
    provider_name = "CompanyOS"

    def _token(self):
        path = Path(self.settings.token_file)
        if not path.is_file():
            return "", "CompanyOS token file is unavailable."
        token = path.read_text(encoding="utf-8").strip()
        return (token, "") if token else ("", "CompanyOS token file is empty.")

    def _request(self, method, path, payload=None):
        token, error = self._token()
        if error:
            return None, error
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            self.endpoint(path),
            data=data,
            method=method,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=max(self.timeout_seconds, 45)) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            return None, f"HTTP {exc.code}: {exc.reason}"
        except URLError as exc:
            return None, str(exc.reason)
        except OSError as exc:
            return None, str(exc)
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            return None, f"Invalid JSON response: {exc}"
        return parsed, ""

    def is_available(self):
        payload, error = self._request("GET", "/tools/archive/health")
        return not error and bool(payload and payload.get("success"))

    def list_models(self):
        models, _error = self.list_models_result()
        return models

    def list_models_result(self):
        payload, error = self._request("GET", "/tools/archive/models")
        if error:
            return [], error
        envelope = payload or {}
        result = envelope.get("result") or {}
        if not envelope.get("success"):
            detail = envelope.get("error") or {}
            return [], detail.get("message") or "CompanyOS model listing failed."
        return list(result.get("models") or []), ""

    def send_request(self, request):
        task = str(request.metadata.get("task") or "connection_test")
        input_data = request.metadata.get("input")
        if not isinstance(input_data, dict):
            input_data = {"text": request.prompt}
        payload, error = self._request("POST", "/tools/archive/task", {"task": task, "input": input_data})
        if error:
            return AIResponse.failure_response(error, provider_name=self.provider_name, model_name=request.model_name)
        if not payload or not payload.get("success"):
            detail = (payload or {}).get("error") or {}
            return AIResponse.failure_response(
                detail.get("message") or "CompanyOS archival task failed.",
                provider_name=self.provider_name,
                model_name=(payload or {}).get("model") or request.model_name,
                raw_response=payload or {},
            )
        result = payload.get("result") or {}
        return AIResponse.success_response(
            text=json.dumps(result, indent=2, sort_keys=True),
            provider_name=self.provider_name,
            model_name=payload.get("model") or request.model_name,
            raw_response=payload,
        )
