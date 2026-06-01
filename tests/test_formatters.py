"""Tests for output formatters."""
import json
import pytest
from shieldops_cli.formatters.json_fmt import to_json
from shieldops_cli.formatters.summary import to_summary
from shieldops_cli.formatters.sarif import to_sarif
from shieldops_cli.formatters.table import to_table


SAMPLE_RESULT = {
    "report_contract": {
        "security_score_percent": 72,
        "security_score_grade": "B",
        "critical_count": 1,
        "high_count": 1,
        "medium_count": 1,
        "low_count": 0,
        "detailed_issues": [
            {"severity": "critical", "category": "Security", "message": "Running as root",
             "fix": "Add USER", "rule_id": "SO001", "line": 1},
            {"severity": "high", "category": "Security", "message": "No HEALTHCHECK",
             "fix": "Add HEALTHCHECK", "rule_id": "SO002", "line": 5},
            {"severity": "medium", "category": "Efficiency", "message": "Multiple RUN",
             "fix": "Combine", "rule_id": "SO003", "line": 3},
        ],
    },
    "engine": "ShieldOps AI",
}

EMPTY_RESULT = {
    "report_contract": {
        "security_score_percent": 100,
        "security_score_grade": "A+",
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
        "detailed_issues": [],
    },
}


class TestJsonFormatter:
    def test_valid_json(self):
        output = to_json(SAMPLE_RESULT)
        parsed = json.loads(output)
        assert parsed["engine"] == "ShieldOps AI"

    def test_empty_result(self):
        output = to_json(EMPTY_RESULT)
        parsed = json.loads(output)
        assert parsed["report_contract"]["critical_count"] == 0


class TestSummaryFormatter:
    def test_with_issues(self):
        output = to_summary("analyze", SAMPLE_RESULT)
        assert "3 issues" in output
        assert "C:1" in output
        assert "H:1" in output

    def test_no_issues(self):
        output = to_summary("analyze", EMPTY_RESULT)
        assert "No issues found" in output


class TestSarifFormatter:
    def test_valid_sarif(self):
        output = to_sarif("analyze", SAMPLE_RESULT)
        parsed = json.loads(output)
        assert parsed["version"] == "2.1.0"
        assert len(parsed["runs"]) == 1
        assert parsed["runs"][0]["tool"]["driver"]["name"] == "ShieldOps AI"
        assert len(parsed["runs"][0]["results"]) == 3

    def test_severity_mapping(self):
        output = to_sarif("analyze", SAMPLE_RESULT)
        parsed = json.loads(output)
        results = parsed["runs"][0]["results"]
        # Critical -> error
        assert results[0]["level"] == "error"
        # High -> error
        assert results[1]["level"] == "error"
        # Medium -> warning
        assert results[2]["level"] == "warning"

    def test_empty_findings(self):
        output = to_sarif("analyze", EMPTY_RESULT)
        parsed = json.loads(output)
        assert len(parsed["runs"][0]["results"]) == 0


class TestTableFormatter:
    def test_renders_without_error(self):
        output = to_table("analyze", SAMPLE_RESULT)
        assert "ShieldOps AI" in output
        assert "72" in output

    def test_no_issues_message(self):
        output = to_table("analyze", EMPTY_RESULT)
        assert "No issues found" in output
