from core.ai.ai_provider import AIProvider
from core.ai.ai_response import AIResponse


class OllamaProvider(AIProvider):
    provider_name = "Ollama"

    def is_available(self):
        _models, error = self.list_models_result()
        return error == ""

    def list_models(self):
        models, _error = self.list_models_result()
        return models

    def list_models_result(self):
        payload, error = self.get_json("/api/tags")

        if error:
            return [], error

        if not isinstance(payload, dict):
            return [], "Malformed Ollama model response."

        raw_models = payload.get("models", [])

        if not isinstance(raw_models, list):
            return [], "Malformed Ollama model response."

        models = [
            model.get("name", "")
            for model in raw_models
            if isinstance(model, dict) and model.get("name")
        ]
        return models, ""

    def send_request(self, request):
        model_name = request.model_name or self.settings.default_model

        if not model_name:
            return AIResponse.failure_response(
                "No model selected.",
                provider_name=self.provider_name,
            )

        prompt = request.prompt

        if request.system_text:
            prompt = f"{request.system_text}\n\n{prompt}"

        request_payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
        }

        if request.images:
            request_payload["images"] = list(request.images)

        payload, error = self.post_json(
            "/api/generate",
            request_payload,
        )

        if error:
            return AIResponse.failure_response(
                error,
                provider_name=self.provider_name,
                model_name=model_name,
            )

        if not isinstance(payload, dict):
            return AIResponse.failure_response(
                "Malformed Ollama generation response.",
                provider_name=self.provider_name,
                model_name=model_name,
                raw_response={"response": payload},
            )

        text = payload.get("response")

        if not isinstance(text, str):
            return AIResponse.failure_response(
                "Malformed Ollama generation response.",
                provider_name=self.provider_name,
                model_name=model_name,
                raw_response=payload,
            )

        return AIResponse.success_response(
            text=text,
            provider_name=self.provider_name,
            model_name=model_name,
            raw_response=payload,
        )
