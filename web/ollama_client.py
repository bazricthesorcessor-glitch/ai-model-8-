"""Local-first Ollama client for semantic extraction."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib import error as urllib_error
from urllib import request as urllib_request

from config import endpoint_of
from config.web import DEFAULT_EMBEDDING_MODEL, DEFAULT_OLLAMA_MODEL, WEB_CONFIG


class OllamaClient:
    """Thin client around the Ollama HTTP API with retry support."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        generate_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.base_url = base_url or endpoint_of("ollama")
        self.generate_url = generate_url or endpoint_of("ollama_generate")
        self.model = model or DEFAULT_OLLAMA_MODEL
        self.timeout = timeout or WEB_CONFIG["timeout"]
        self.max_retries = max_retries or WEB_CONFIG["max_retries"]

    def is_ollama_alive(self) -> bool:
        success, _, _ = self._request_json("GET", f"{self.base_url}/api/tags")
        return success

    def list_models(self) -> Dict[str, Any]:
        success, payload, error = self._request_json("GET", f"{self.base_url}/api/tags")
        return {
            "success": success,
            "result": payload,
            "error": error,
        }

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
        format_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": stream,
            "options": options or {},
        }
        if system:
            payload["system"] = system
        if format_schema:
            payload["format"] = format_schema

        success, response, error = self._request_json("POST", self.generate_url, payload)
        return {
            "success": success,
            "result": response,
            "error": error,
        }

    def embed(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "model": model or DEFAULT_EMBEDDING_MODEL,
            "input": text,
        }
        success, response, error = self._request_json("POST", f"{self.base_url}/api/embed", payload)
        return {
            "success": success,
            "result": response,
            "error": error,
        }

    def _request_json(
        self,
        method: str,
        url: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        body = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        last_error = None
        for _ in range(self.max_retries):
            try:
                request = urllib_request.Request(url, data=body, headers=headers, method=method)
                with urllib_request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read().decode("utf-8", errors="replace")
                    return True, json.loads(raw or "{}"), None
            except urllib_error.URLError as exc:
                last_error = f"Ollama request failed: {exc.reason}"
            except Exception as exc:
                last_error = f"Ollama request failed: {exc}"
        return False, None, last_error

