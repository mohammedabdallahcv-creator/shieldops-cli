"""Thin wrapper around /api/ext/run and other endpoints."""
from __future__ import annotations
import requests
from shieldops_cli import config

_TIMEOUT = 120  # seconds


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str = ""):
        self.status = status
        self.code = code
        self.message = message
        super().__init__(f"[{status}] {code}: {message}")


class ShieldOpsClient:
    def __init__(self, api_url: str | None = None, api_key: str | None = None):
        self.api_url = (api_url or config.get_api_url()).rstrip("/")
        self.api_key = api_key or config.get_api_key()

    @property
    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["X-ShieldOps-Extension-Key"] = self.api_key
        return h

    # ── Core: run task ──────────────────────────────────
    def run_task(
        self,
        task: str,
        content: str,
        filename: str = "untitled",
        options: dict | None = None,
    ) -> dict:
        """POST /api/ext/run — runs any supported task."""
        body = {
            "task": task,
            "content": content,
            "filename": filename,
        }
        if options:
            body["options"] = options

        resp = requests.post(
            f"{self.api_url}/api/ext/run",
            json=body,
            headers=self._headers,
            timeout=_TIMEOUT,
        )
        is_json = resp.headers.get("content-type", "").startswith("application/json")
        data = resp.json() if is_json else {}

        if resp.status_code == 403:
            raise ApiError(403, data.get("error", "access_denied"),
                           "Invalid or missing API key. Run: shieldops login --key <YOUR_KEY>")
        if resp.status_code == 429:
            raise ApiError(429, "rate_limit",
                           f"Daily limit reached. Upgrade at {self.api_url}/pricing")
        if resp.status_code == 413:
            raise ApiError(413, "content_too_large", "File too large (max 250KB).")
        if resp.status_code >= 400:
            if not is_json:
                raise ApiError(resp.status_code, "server_error",
                               f"Server error ({resp.status_code}) while generating report.")
            raise ApiError(resp.status_code,
                           data.get("error", "unknown"),
                           data.get("details", resp.text[:200]))
        return data

    # ── Capabilities ────────────────────────────────────
    def capabilities(self) -> dict:
        """GET /api/ext/capabilities — returns plan features and limits."""
        resp = requests.get(
            f"{self.api_url}/api/ext/capabilities",
            headers=self._headers,
            timeout=30,
        )
        if resp.status_code != 200:
            return {}
        return resp.json()

    # ── Account info ────────────────────────────────────
    def whoami(self) -> dict:
        """GET /api/ext/account — returns current user info."""
        resp = requests.get(
            f"{self.api_url}/api/ext/account",
            headers=self._headers,
            timeout=15,
        )
        if resp.status_code != 200:
            return {"error": "not_authenticated"}
        return resp.json()

    # ── Health check ────────────────────────────────────
    def ping(self) -> bool:
        try:
            resp = requests.get(f"{self.api_url}/api/ext/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
