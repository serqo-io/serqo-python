"""Small, dependency-free HTTP client for the public Serqo API."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class SerqoError(Exception):
    """API error with HTTP status and structured Serqo error fields."""

    def __init__(self, status: int, body: dict[str, Any], request_id: str | None = None):
        self.status = status
        self.code = str(body.get("code", "UNKNOWN_ERROR"))
        self.request_id = request_id
        self.retryable = bool(body.get("retryable", False))
        self.retry_after_ms = body.get("retryAfterMs")
        self.details = body.get("details")
        super().__init__(str(body.get("message") or f"Serqo API request failed with HTTP {status}"))


class Serqo:
    """Client for Serqo search and account endpoints.

    Args:
        api_key: Secret API key. Keep it on a trusted server.
        base_url: API origin, defaulting to ``https://api.serqo.io``.
        timeout: Per-request timeout in seconds (default 60).

    Search calls are not retried automatically because successful searches may
    consume credits. Use an idempotency key when retrying identical parameters.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.serqo.io", timeout: float = 60):
        if not api_key.strip():
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def search(self, query: dict[str, Any], *, idempotency_key: str | None = None) -> dict[str, Any]:
        """Run one search with a JSON body and return the full API envelope."""
        headers = {"x-api-key": self._api_key}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return self._request("POST", "/v1/search", body=query, headers=headers)

    def engines(self) -> dict[str, Any]:
        """Return the current engines and supported search types."""
        return self._request("GET", "/v1/engines")

    def me(self) -> dict[str, Any]:
        """Return account and API key identifiers associated with this key."""
        return self._request("GET", "/v1/me")

    def health(self) -> dict[str, Any]:
        """Check whether the product API responds; no API key is sent."""
        return self._request("GET", "/v1/health", authenticated=False)

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        request_headers = {"Accept": "application/json", **(headers or {})}
        if authenticated:
            request_headers["x-api-key"] = self._api_key
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        request = Request(f"{self._base_url}{path}", data=data, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict) or payload.get("success") is not True:
                    raise SerqoError(response.status, {"code": "INVALID_RESPONSE", "message": "Serqo API returned an invalid response"}, response.headers.get("x-request-id"))
                return payload
        except HTTPError as error:
            try:
                payload = json.loads(error.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = {}
            body_error = payload.get("error", {}) if isinstance(payload, dict) else {}
            request_id = payload.get("requestId", error.headers.get("x-request-id")) if isinstance(payload, dict) else error.headers.get("x-request-id")
            raise SerqoError(error.code, body_error if isinstance(body_error, dict) else {}, request_id) from error
        except URLError as error:
            raise ConnectionError(f"Could not reach Serqo API: {error.reason}") from error
