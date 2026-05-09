"""Tests for auth commands."""
import json
import pytest
from unittest.mock import patch, MagicMock
from shieldops_cli.main import cli


def test_login_saves_key(runner, mock_config):
    """Login should save the API key to config."""
    with patch("shieldops_cli.auth.ShieldOpsClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.whoami.return_value = {"name": "Test", "email": "test@test.com", "plan": "pro"}
        mock_client_cls.return_value = mock_client

        result = runner.invoke(cli, ["login", "--key", "test-key-123"])
        assert result.exit_code == 0

        config_file = mock_config / "config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["api_key"] == "test-key-123"


def test_login_warns_on_invalid_key(runner, mock_config):
    """Login should warn if key verification fails."""
    with patch("shieldops_cli.auth.ShieldOpsClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.whoami.return_value = {"error": "not_authenticated"}
        mock_client_cls.return_value = mock_client

        result = runner.invoke(cli, ["login", "--key", "bad-key"])
        assert result.exit_code == 0
        assert "could not verify" in result.output.lower() or "Key saved" in result.output


def test_logout(runner, mock_config):
    """Logout should clear the API key."""
    # First set a key
    from shieldops_cli import config as cfg
    cfg.set_key("api_key", "some-key")

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0

    data = json.loads((mock_config / "config.json").read_text())
    assert data["api_key"] == ""


def test_whoami_not_authenticated(runner, mock_config):
    """Whoami should say not authenticated if no key."""
    result = runner.invoke(cli, ["whoami"])
    assert result.exit_code == 0
    assert "Not authenticated" in result.output or "not authenticated" in result.output.lower()


def test_whoami_shows_info(runner, mock_config):
    """Whoami should display user info when authenticated."""
    from shieldops_cli import config as cfg
    cfg.set_key("api_key", "valid-key")

    with patch("shieldops_cli.auth.ShieldOpsClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.whoami.return_value = {"name": "Mohammed", "email": "m@test.com", "plan": "pro"}
        mock_client.capabilities.return_value = {"limits": {"daily_ai_used": 5, "daily_ai_requests": 50}}
        mock_client_cls.return_value = mock_client

        result = runner.invoke(cli, ["whoami"])
        assert result.exit_code == 0
        assert "Mohammed" in result.output
        assert "Pro" in result.output
