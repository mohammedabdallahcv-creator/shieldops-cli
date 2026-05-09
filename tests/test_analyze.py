"""Tests for analyze command."""
import json
import pytest
from unittest.mock import patch, MagicMock
from shieldops_cli.main import cli
from shieldops_cli.commands.analyze import check_severity_gate


MOCK_ANALYZE_RESPONSE = {
    "result": {
        "report_contract": {
            "security_score_percent": 72,
            "security_score_grade": "B",
            "critical_count": 1,
            "high_count": 1,
            "medium_count": 1,
            "low_count": 1,
            "detailed_issues": [
                {"severity": "critical", "category": "Security", "message": "Running as root", "fix": "Add USER"},
                {"severity": "high", "category": "Security", "message": "No HEALTHCHECK", "fix": "Add HEALTHCHECK"},
                {"severity": "medium", "category": "Efficiency", "message": "Multiple RUN", "fix": "Combine RUN"},
                {"severity": "low", "category": "Best Practice", "message": "No .dockerignore", "fix": "Create one"},
            ],
        },
        "engine": "ShieldOps AI",
    }
}


def test_analyze_table_output(runner, mock_config, sample_dockerfile):
    """Analyze should print a table report by default."""
    from shieldops_cli import config as cfg
    cfg.set_key("api_key", "test-key")

    with patch("shieldops_cli.commands.analyze.ShieldOpsClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.run_task.return_value = MOCK_ANALYZE_RESPONSE
        mock_client.api_url = "https://shieldops-ai.onrender.com"
        mock_cls.return_value = mock_client

        result = runner.invoke(cli, ["analyze", str(sample_dockerfile)])
        assert result.exit_code == 0


def test_analyze_json_output(runner, mock_config, sample_dockerfile):
    """Analyze with --format json should output valid JSON."""
    from shieldops_cli import config as cfg
    cfg.set_key("api_key", "test-key")

    with patch("shieldops_cli.commands.analyze.ShieldOpsClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.run_task.return_value = MOCK_ANALYZE_RESPONSE
        mock_client.api_url = "https://shieldops-ai.onrender.com"
        mock_cls.return_value = mock_client

        result = runner.invoke(cli, ["analyze", str(sample_dockerfile), "--format", "json"])
        assert result.exit_code == 0


def test_analyze_fail_on_high(runner, mock_config, sample_dockerfile):
    """Analyze with --fail-on high should exit 1 when high issues exist."""
    from shieldops_cli import config as cfg
    cfg.set_key("api_key", "test-key")

    with patch("shieldops_cli.commands.analyze.ShieldOpsClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.run_task.return_value = MOCK_ANALYZE_RESPONSE
        mock_client.api_url = "https://shieldops-ai.onrender.com"
        mock_cls.return_value = mock_client

        result = runner.invoke(cli, ["analyze", str(sample_dockerfile), "--fail-on", "high"])
        assert result.exit_code == 1


def test_analyze_save_to_file(runner, mock_config, sample_dockerfile, tmp_path):
    """Analyze with -o should save output to file."""
    from shieldops_cli import config as cfg
    cfg.set_key("api_key", "test-key")

    output_file = tmp_path / "report.json"

    with patch("shieldops_cli.commands.analyze.ShieldOpsClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.run_task.return_value = MOCK_ANALYZE_RESPONSE
        mock_client.api_url = "https://shieldops-ai.onrender.com"
        mock_cls.return_value = mock_client

        result = runner.invoke(cli, ["analyze", str(sample_dockerfile), "-f", "json", "-o", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()


# ── check_severity_gate unit tests ──

def test_severity_gate_critical():
    result = {"report_contract": {"critical_count": 1, "high_count": 0}}
    assert check_severity_gate(result, "critical") is True


def test_severity_gate_none():
    result = {"report_contract": {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}}
    assert check_severity_gate(result, "critical") is False


def test_severity_gate_high_threshold():
    result = {"report_contract": {"critical_count": 0, "high_count": 2, "medium_count": 1}}
    assert check_severity_gate(result, "high") is True
    assert check_severity_gate(result, "critical") is False
