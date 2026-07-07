from core.ai.ai_provider import AIProvider
from core.ai.ai_response import AIResponse


class OpenWebUIProvider(AIProvider):
    provider_name = "Open WebUI"

    def is_available(self):
        _models, error = self.list_models_result()
        return error == ""

    def list_models(self):
        models, _error = self.list_models_result()
        return models

    def list_models_result(self):
        payload, error = self.get_json("/api/models")

        if error:
            return [], error

        if isinstance(payload, list):
            raw_models = payload
        else:
            raw_models = payload.get("data", [])
        models = []

        for model in raw_models:
            if isinstance(model, str):
                models.append(model)
            elif isinstance(model, dict):
                name = model.get("id") or model.get("name")

                if name:
                    models.append(name)

        return models, ""

    def send_request(self, request):
        model_name = request.model_name or self.settings.default_model

        if not model_name:
            return AIResponse.failure_response(
                "No model selected.",
                provider_name=self.provider_name,
            )

        messages = []

        if request.system_text:
            messages.append({
                "role": "system",
                "content": request.system_text,
            })

        messages.append({
            "role": "user",
            "content": request.prompt,
        })

        payload, error = self.post_json(
            "/api/chat/completions",
            {
                "model": model_name,
                "messages": messages,
                "stream": False,
            },
        )

        if error:
            return AIResponse.failure_response(
                error,
                provider_name=self.provider_name,
                model_name=model_name,
            )

        text = self.response_text(payload)
        return AIResponse.success_response(
            text=text,
            provider_name=self.provider_name,
            model_name=model_name,
            raw_response=payload,
        )

    def response_text(self, payload):
        choices = payload.get("choices", [])

        if not choices:
            return ""

        message = choices[0].get("message", {})
        return message.get("content", "")
