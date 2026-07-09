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
        elif isinstance(payload, dict):
            raw_models = payload.get("data", [])
        else:
            return [], "Malformed Open WebUI model response."

        if not isinstance(raw_models, list):
            return [], "Malformed Open WebUI model response."

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

        text, response_error = self.response_text_result(payload)

        if response_error:
            return AIResponse.failure_response(
                response_error,
                provider_name=self.provider_name,
                model_name=model_name,
                raw_response=payload if isinstance(payload, dict) else {
                    "response": payload,
                },
            )

        return AIResponse.success_response(
            text=text,
            provider_name=self.provider_name,
            model_name=model_name,
            raw_response=payload,
        )

    def response_text(self, payload):
        text, _error = self.response_text_result(payload)
        return text

    def response_text_result(self, payload):
        if not isinstance(payload, dict):
            return "", "Malformed Open WebUI chat response."

        choices = payload.get("choices", [])

        if not isinstance(choices, list) or not choices:
            return "", "Malformed Open WebUI chat response."

        if not isinstance(choices[0], dict):
            return "", "Malformed Open WebUI chat response."

        message = choices[0].get("message", {})

        if not isinstance(message, dict):
            return "", "Malformed Open WebUI chat response."

        text = message.get("content")

        if not isinstance(text, str):
            return "", "Malformed Open WebUI chat response."

        return text, ""
