import json
import socket
from abc import ABC
from abc import abstractmethod
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen

from core.ai.ai_response import AIResponse


class AIProvider(ABC):
    provider_name = "AI Provider"

    def __init__(self, settings, timeout_seconds=3):
        self.settings = settings
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    def is_available(self):
        raise NotImplementedError

    @abstractmethod
    def list_models(self):
        raise NotImplementedError

    @abstractmethod
    def send_request(self, request):
        raise NotImplementedError

    def endpoint(self, path):
        base = self.settings.endpoint_url.rstrip("/")
        return f"{base}/{path.lstrip('/')}"

    def get_json(self, path):
        return self.request_json("GET", path)

    def post_json(self, path, payload):
        return self.request_json("POST", path, payload)

    def request_json(self, method, path, payload=None):
        data = None
        headers = {"Accept": "application/json"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(
            self.endpoint(path),
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as error:
            return None, f"HTTP {error.code}: {error.reason}"
        except URLError as error:
            return None, str(error.reason)
        except (TimeoutError, socket.timeout):
            return None, "Connection timed out."
        except OSError as error:
            return None, str(error)

        if not body.strip():
            return {}, ""

        try:
            return json.loads(body), ""
        except json.JSONDecodeError as error:
            return None, f"Invalid JSON response: {error}"
        except UnicodeDecodeError as error:
            return None, f"Invalid text response: {error}"

    def unavailable_response(self, message):
        return AIResponse.failure_response(
            message,
            provider_name=self.provider_name,
        )
