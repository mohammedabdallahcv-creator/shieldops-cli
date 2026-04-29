"""HTTP client for ShieldOps external API.

This module is intentionally thin:
- no CLI output
- no business logic
- no formatting
- no command-specific behavior
"""
from __future__ import annotations

from typing import Any

import requests

from shieldops_cli import config


_TIMEOUT_SECONDS = 300
API_KEY_HEADER = "X-ShieldOps-Extension-Key"


class ApiError(Exception):
    """Normalized API error raised by ShieldOpsClient."""

    def __init__(self, status: int, code: str, message: str = "") -> None:
        self.status = status
        self.code = code
        self.message = message
        super().__init__(f"[{status}] {code}: {message}")


class ShieldOpsClient:
    """Small wrapper around ShieldOps external API."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        self.api_url = (api_url or config.get_api_url()).rstrip("/")
        self.api_key = api_key if api_key is not None else config.get_api_key()

    @property
    def headers(self) -> dict[str, str]:
        """Return request headers for JSON API calls."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.api_key:
            headers[API_KEY_HEADER] = self.api_key

        return headers

    def run_task(
        self,
        task: str,
        content: str,
        filename: str = "untitled",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run an analysis task through POST /api/ext/run."""
        body: dict[str, Any] = {
            "task": task,
            "content": content,
            "filename": filename,
        }

        if options:
            body["options"] = options

        try:
            response = requests.post(
                f"{self.api_url}/api/ext/run",
                json=body,
                headers=self.headers,
                timeout=_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            raise ApiError(
                0,
                "network_error",
                f"Could not connect to ShieldOps API: {exc}",
            ) from exc

        data = self._safe_json(response)
        self._raise_for_error(response, data)
        return data

    def capabilities(self) -> dict[str, Any]:
        """Return current API capabilities and plan limits."""
        try:
            response = requests.get(
                f"{self.api_url}/api/ext/capabilities",
                headers=self.headers,
                timeout=30,
            )
        except requests.RequestException:
            return {}

        if response.status_code != 200:
            return {}

        return self._safe_json(response)

    def whoami(self) -> dict[str, Any]:
        """Return current authenticated account information."""
        try:
            response = requests.get(
                f"{self.api_url}/api/ext/account",
                headers=self.headers,
                timeout=60,
            )
        except requests.RequestException:
            return {"error": "network_error"}

        if response.status_code != 200:
            data = self._safe_json(response)
            return {"error": data.get("error", "not_authenticated")}

        return self._safe_json(response)

    def ping(self) -> bool:
        """Return True when the ShieldOps external API is reachable."""
        try:
            response = requests.get(
                f"{self.api_url}/api/ext/health",
                timeout=5,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    @staticmethod
    def _safe_json(response: requests.Response) -> dict[str, Any]:
        """Safely parse a JSON response."""
        try:
            data = response.json()
        except ValueError:
            return {}

        return data if isinstance(data, dict) else {}

    @staticmethod
    def _raise_for_error(
        response: requests.Response,
        data: dict[str, Any],
    ) -> None:
        """Normalize HTTP errors into ApiError."""
        if response.status_code < 400:
            return

        if response.status_code == 403:
            raise ApiError(
                403,
                data.get("error", "access_denied"),
                "Invalid or missing API key. Run: shieldops login --key <YOUR_KEY>",
            )

        if response.status_code == 429:
            raise ApiError(
                429,
                "rate_limit",
                "Daily limit reached. Upgrade your ShieldOps plan.",
            )

        if response.status_code == 413:
            raise ApiError(
                413,
                "content_too_large",
                "File too large for analysis.",
            )

        raise ApiError(
            response.status_code,
            data.get("error", "unknown_error"),
            data.get("details") or data.get("message") or response.text[:200],
        )
