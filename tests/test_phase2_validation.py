"""Phase 2 validation: CLI consumers read canonical fields first, fall back safely."""
import json
import pytest
from shieldops_cli.formatters.summary import to_summary
from shieldops_cli.formatters.table import to_table


# ── Test Scenarios ──────────────────────────────────────────────────────────

SCENARIO_1_CANONICAL_ONLY = {
    "description": "Top-level canonical fields present, no legacy",
    "result": {
        "security_score": 85,
        "security_score_percent": 85,
        "security_score_grade": "A",
        "readiness_score": 78,
        "production_readiness_percent": 78,
        "production_readiness_grade": "B",
    },
    "expect_security_score": "85",
    "expect_readiness_score": "78",
    "expect_grade": "A",
}

SCENARIO_2_LEGACY_ONLY = {
    "description": "Canonical absent, legacy nested fields present",
    "result": {
        "report_contract": {
            "security_score_percent": 72,
            "security_score_grade": "B",
            "critical_count": 1,
            "high_count": 1,
            "medium_count": 1,
            "low_count": 0,
            "detailed_issues": [
                {"severity": "critical", "category": "Security",
                 "message": "Running as root", "fix": "Add USER", "rule_id": "SO001", "line": 1},
            ],
        },
    },
    "expect_security_score": "72",
    "expect_readiness_score": None,
    "expect_grade": "B",
}

SCENARIO_3_CANONICAL_WINS = {
    "description": "Canonical and nested present with DIFFERENT values — canonical must win",
    "result": {
        "security_score": 95,
        "security_score_percent": 95,
        "security_score_grade": "A+",
        "readiness_score": 88,
        "production_readiness_percent": 88,
        "production_readiness_grade": "A",
        "report_contract": {
            "security_score": 50,
            "security_score_percent": 50,
            "security_score_grade": "D",
            "production_readiness_percent": 40,
            "production_readiness_grade": "F",
        },
        "stats": {"security_score": 30, "readiness_score": 25, "score": 20},
        "v2_scan": {"stats": {"score": 10}},
    },
    "expect_security_score": "95",
    "expect_readiness_score": "88",
    "expect_grade": "A+",
}

SCENARIO_4_PARTIAL_READINESS = {
    "description": "Readiness fields partially missing",
    "result": {
        "security_score": 65,
        "security_score_percent": 65,
        "security_score_grade": "C",
        "readiness_score": 0,
        "report_contract": {
            "production_readiness_percent": 55,
            "production_readiness_grade": "C",
        },
    },
    "expect_security_score": "65",
    "expect_readiness_score": "0",
    "expect_grade": "C",
}

SCENARIO_5_EMPTY_RESULT = {
    "description": "Empty result with no scores at all",
    "result": {
        "findings": [],
    },
    "expect_security_score": "N/A",
    "expect_readiness_score": None,
    "expect_grade": "",
}


# ── Summary Formatter Tests ─────────────────────────────────────────────────

class TestSummaryPhase2:
    def test_scenario1_canonical_only(self):
        s = to_summary("analyze", SCENARIO_1_CANONICAL_ONLY["result"])
        # summary only displays score, not grade — verify score from canonical
        assert "85" in s

    def test_scenario2_legacy_only(self):
        s = to_summary("analyze", SCENARIO_2_LEGACY_ONLY["result"])
        assert SCENARIO_2_LEGACY_ONLY["expect_security_score"] in s

    def test_scenario3_canonical_wins(self):
        s = to_summary("analyze", SCENARIO_3_CANONICAL_WINS["result"])
        # Should show 95 (canonical) NOT 50 (report_contract)
        assert "95" in s
        assert "50" not in s

    def test_scenario4_partial_readiness(self):
        s = to_summary("analyze", SCENARIO_4_PARTIAL_READINESS["result"])
        assert SCENARIO_4_PARTIAL_READINESS["expect_security_score"] in s

    def test_scenario5_empty_result(self):
        s = to_summary("analyze", SCENARIO_5_EMPTY_RESULT["result"])
        assert SCENARIO_5_EMPTY_RESULT["expect_security_score"] in s


# ── Table Formatter Tests ───────────────────────────────────────────────────

class TestTablePhase2:
    def test_scenario1_canonical_only(self):
        s = to_table("analyze", SCENARIO_1_CANONICAL_ONLY["result"])
        assert "85" in s
        assert "A" in s  # grade from canonical

    def test_scenario2_legacy_only(self):
        s = to_table("analyze", SCENARIO_2_LEGACY_ONLY["result"])
        assert "72" in s
        assert "B" in s  # grade from legacy

    def test_scenario3_canonical_wins(self):
        s = to_table("analyze", SCENARIO_3_CANONICAL_WINS["result"])
        assert "95" in s
        # Rich output contains "Score: 95 A+" — canonical grade displayed
        assert "95" in s and "A+" in s
        # Legacy nested score 50 must NOT be the displayed score
        assert "Score: 50" not in s

    def test_scenario4_partial_readiness(self):
        s = to_table("analyze", SCENARIO_4_PARTIAL_READINESS["result"])
        assert "65" in s
        assert "C" in s  # grade from canonical

    def test_scenario5_empty_result(self):
        s = to_table("analyze", SCENARIO_5_EMPTY_RESULT["result"])
        assert "N/A" in s


# ── Scenario 3 Deep Verification ────────────────────────────────────────────

def test_scenario3_canonical_wins_deep():
    """Verify that canonical 95 wins over legacy 50 in both formatters."""
    result = SCENARIO_3_CANONICAL_WINS["result"]

    # Summary
    s = to_summary("analyze", result)
    assert "95" in s, f"Summary should show canonical 95, got: {s}"

    # Table — use stripped plain text to avoid Rich ANSI artifacts
    import re
    t = to_table("analyze", result)
    t_plain = re.sub(r'\x1b\[[0-9;]*m', '', t)
    t_plain = t_plain.replace('\u2502', '|').replace('\u250c', ',').replace('\u2510', ',').replace('\u2514', '`').replace('\u2518', "'").replace('\u2500', '-')
    assert "95" in t_plain, f"Table should show canonical 95, got: {t_plain}"
    assert "A+" in t_plain, f"Table should show canonical grade A+, got: {t_plain}"
    assert "Score: 50" not in t_plain, f"Table should NOT show legacy 50, got: {t_plain}"
