# backend/app/providers/ollama_provider.py
#
# Same TriageProvider interface, calls a local Ollama server instead of
# a hosted API. Useful when a teammate's Groq key is rate-limited or
# unavailable -- swap providers via the TRIAGE_PROVIDER env var, nothing
# else in the app needs to change.

import json
import os

import httpx
from pydantic import ValidationError

from app.providers.base import TriageError, TriageTimeoutError, TriageValidationError
from app.schemas import TriageResult
from app.providers.llm_provider import _SYSTEM_PROMPT  # reuse the same prompt


class OllamaProvider:
    name = "llm:ollama"

    def __init__(self, timeout_seconds: float = 15.0):
        self._base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self._model = os.environ.get("OLLAMA_MODEL", "llama3.1")
        self._timeout = timeout_seconds

    def triage(self, text: str, location: str) -> TriageResult:
        prompt = f"{_SYSTEM_PROMPT}\n\nComplaint: {text}\nLocation: {location}"

        try:
            resp = httpx.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                },
                timeout=self._timeout,
            )
            resp.raise_for_status()
        except httpx.TimeoutException as exc:
            raise TriageTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise TriageError(str(exc)) from exc

        try:
            body = resp.json()
            parsed = json.loads(body["response"])
        except (json.JSONDecodeError, KeyError) as exc:
            raise TriageValidationError(f"Ollama did not return valid JSON: {exc}") from exc

        try:
            return TriageResult(**parsed)
        except ValidationError as exc:
            raise TriageValidationError(f"Ollama output failed schema validation: {exc}") from exc