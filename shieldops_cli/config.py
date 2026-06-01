"""Manage ~/.shieldops/config.json"""
from __future__ import annotations
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".shieldops"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "api_url": "https://shieldops-ai.dev",
    "api_key": "",
    "default_format": "table",
    "language": "en",
    "color": True,
}


def load() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            stored = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(stored)
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def save(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get(key: str, default=None):
    return load().get(key, default)


def set_key(key: str, value) -> None:
    cfg = load()
    cfg[key] = value
    save(cfg)


def get_api_key() -> str:
    """API key priority: env var > config file."""
    return os.environ.get("SHIELDOPS_API_KEY", "") or load().get("api_key", "")


def get_api_url() -> str:
    return os.environ.get("SHIELDOPS_API_URL", "") or load().get("api_url", DEFAULT_CONFIG["api_url"])
