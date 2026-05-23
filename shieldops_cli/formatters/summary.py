"""One-line summary for scripts and CI logs."""


def to_summary(task: str, result: dict) -> str:
    contract = result.get("report_contract", {})
    findings = (
        contract.get("detailed_issues")
        or result.get("results")
        or result.get("findings")
        or []
    )
    total = len(findings)
    critical = int(contract.get("critical_count", 0) or 0)
    high = int(contract.get("high_count", 0) or 0)
    score = (
        result.get("security_score")
        or result.get("security_score_percent")
        or result.get("report_contract", {}).get("security_score")
        or contract.get("security_score_percent")
        or result.get("stats", {}).get("security_score")
        or result.get("stats", {}).get("score")
        or result.get("v2_scan", {}).get("stats", {}).get("score")
        or "N/A"
    )

    if total == 0:
        return f"\u2705 {task}: No issues found. Score: {score}"
    return f"\u26a0\ufe0f  {task}: {total} issues (C:{critical} H:{high}). Score: {score}"
