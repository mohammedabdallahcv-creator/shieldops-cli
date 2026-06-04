"""One-line summary for scripts and CI logs."""
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _first_present(*values):
    """Return first non-None non-empty value (preserves 0 as valid)."""
    for v in values:
        if v is not None and v != "":
            return v
    return None


def _safe_score(result: dict) -> str:
    contract = result.get("report_contract", {})
    stats = result.get("stats", {})
    score = _first_present(
        result.get("security_score"),
        result.get("security_score_percent"),
        contract.get("security_score"),
        contract.get("security_score_percent"),
        contract.get("score"),
        stats.get("security_score"),
        stats.get("score"),
        stats.get("security_score_percent"),
        result.get("score"),
        result.get("overall_score"),
    )
    return str(score) if score is not None else "N/A"


def to_summary(task: str, result: dict) -> str:
    contract = result.get("report_contract", {})
    findings = (
        contract.get("detailed_issues")
        or result.get("results")
        or result.get("findings")
        or result.get("issues")
        or []
    )
    summary = result.get("summary", {})
    total = len(findings)
    critical = int(
        contract.get("critical_count", 0)
        or result.get("critical_count", 0)
        or summary.get("critical", 0)
        or 0
    )
    high = int(
        contract.get("high_count", 0)
        or result.get("high_count", 0)
        or summary.get("high", 0)
        or 0
    )
    score = _safe_score(result)

    if total == 0:
        return f"\u2705 {task}: No issues found. Score: {score}"
    return f"\u26a0\ufe0f  {task}: {total} issues (C:{critical} H:{high}). Score: {score}"
