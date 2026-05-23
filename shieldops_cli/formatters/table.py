"""Human-friendly Rich table output."""
from __future__ import annotations

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

SEVERITY_COLORS = {
    "critical": "bold white on red",
    "high": "bold red",
    "medium": "yellow",
    "low": "dim",
    "info": "dim cyan",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _first_present(*values):
    """Return first non-None non-empty value (preserves 0 as valid)."""
    for v in values:
        if v is not None and v != "":
            return v
    return None


def _safe_get_score(result: dict) -> tuple[object, str]:
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
    if score is None:
        score = "N/A"
    grade = _first_present(
        result.get("security_score_grade"),
        contract.get("security_score_grade"),
        contract.get("grade"),
        stats.get("grade"),
        result.get("grade"),
        result.get("risk_grade"),
    )
    if grade is None:
        grade = ""
    return score, str(grade).strip()


def _safe_severity_counts(result: dict) -> dict[str, int]:
    contract = result.get("report_contract", {})
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for severity in counts:
        counts[severity] = int(
            contract.get(f"{severity}_count", 0)
            or result.get(f"{severity}_count", 0)
            or 0
        )
    return counts


def to_table(task: str, result: dict, limit: int | None = None, **kwargs) -> str:
    """Render readable plain text for files, tests, and no-color terminals."""
    score, grade = _safe_get_score(result)
    score_text = "Unavailable" if score == "N/A" else str(score)
    if grade and score_text != "Unavailable":
        score_text = f"{score_text} {grade}"

    contract = result.get("report_contract", {})
    findings = _get_findings(result)
    counts = _safe_severity_counts(result)
    total = len(findings)

    lines = [
        "ShieldOps AI",
        _task_label(task),
        f"Score: {score_text}",
        f"Engine: {result.get('engine', 'ShieldOps AI')}",
        "",
        (
            f"Total: {total} issues "
            f"(C:{counts['critical']} H:{counts['high']} "
            f"M:{counts['medium']} L:{counts['low']})"
        ),
    ]

    if not findings:
        lines.append("")
        lines.append("OK No issues found!")
        return "\n".join(lines) + "\n"

    if limit is not None and limit <= 0:
        lines.append("")
        lines.append(f"Showing 0 of {total} findings. Use --full to see all.")
        return "\n".join(lines) + "\n"

    display = findings if limit is None else findings[:limit]
    remaining = total - len(display) if limit else 0

    lines.append("")
    lines.append(f"Findings ({len(display)} of {total})" if remaining else f"Findings ({total})")
    lines.append("")

    for index, finding in enumerate(display, 1):
        severity = _clean(finding.get("severity", "info")).upper()
        rule = _clean(finding.get("rule_id") or finding.get("id") or finding.get("line") or "-")
        category = _clean(finding.get("category", "-"))
        message = _clean(
            finding.get("message")
            or finding.get("title")
            or finding.get("description")
            or "-"
        )
        fix = _clean(finding.get("fix") or finding.get("recommendation") or "-")

        lines.extend(
            [
                f"{index}. {severity} - {rule}",
                f"   Category: {category}",
                f"   Finding: {message}",
                f"   Fix: {fix}",
                "",
            ]
        )

    if remaining > 0:
        lines.append(f"... and {remaining} more findings. Use --full to see all.")

    result_summary = result.get("summary")
    if isinstance(result_summary, str) and result_summary:
        lines.append("")
        lines.append(result_summary)

    return "\n".join(lines).rstrip() + "\n"


def render_table(task: str, result: dict, limit: int | None = None):
    """Return Rich renderables for direct terminal output."""
    score, grade = _safe_get_score(result)
    if score == "N/A":
        score_line = "Score: [bold dim]Unavailable[/bold dim]"
    elif grade:
        score_line = f"Score: [bold cyan]{score}[/bold cyan] {grade}"
    else:
        score_line = f"Score: [bold cyan]{score}[/bold cyan]"

    header = Panel(
        f"[bold]{_task_label(task)}[/bold]\n"
        f"{score_line}\n"
        f"Engine: {result.get('engine', 'ShieldOps AI')}",
        title="ShieldOps AI",
        border_style="blue",
        box=box.ASCII,
        expand=False,
    )

    findings = _get_findings(result)
    if not findings:
        return Group(header, Text("OK No issues found!", style="green"))

    counts = _safe_severity_counts(result)
    total = len(findings)
    summary = Text.assemble(
        ("Total: ", "bold"),
        str(total),
        "  ",
        (f" C:{counts['critical']} ", SEVERITY_COLORS["critical"]),
        "  ",
        (f"H:{counts['high']}", SEVERITY_COLORS["high"]),
        "  ",
        (f"M:{counts['medium']}", SEVERITY_COLORS["medium"]),
        "  ",
        (f"L:{counts['low']}", SEVERITY_COLORS["low"]),
    )

    if limit is not None and limit <= 0:
        return Group(
            header,
            summary,
            Text(f"Showing 0 of {total} findings. Use --full to see all.", style="dim"),
        )

    display = findings if limit is None else findings[:limit]
    remaining = total - len(display) if limit else 0

    table = Table(
        title=f"Findings ({len(display)} of {total})" if remaining else f"Findings ({total})",
        show_lines=True,
        box=box.ASCII,
        expand=False,
    )
    table.add_column("#", justify="right", width=3, no_wrap=True)
    table.add_column("Severity", width=10, no_wrap=True)
    table.add_column("Rule", width=12, overflow="fold")
    table.add_column("Category", width=16, overflow="fold")
    table.add_column("Finding", min_width=24, ratio=3, overflow="fold")
    table.add_column("Fix", min_width=24, ratio=2, overflow="fold")

    for index, finding in enumerate(display, 1):
        severity = str(finding.get("severity", "info")).lower()
        table.add_row(
            str(index),
            Text(severity.upper(), style=SEVERITY_COLORS.get(severity, "")),
            _clean(finding.get("rule_id") or finding.get("id") or finding.get("line") or "-"),
            _clean(finding.get("category", "-")),
            _clean(
                finding.get("message")
                or finding.get("title")
                or finding.get("description")
                or "-"
            ),
            _clean(finding.get("fix") or finding.get("recommendation") or "-"),
        )

    renderables = [header, summary, table]
    if remaining > 0:
        renderables.append(Text(f"... and {remaining} more findings. Use --full to see all.", style="dim"))

    result_summary = result.get("summary")
    if isinstance(result_summary, str) and result_summary:
        renderables.append(Text(f"\n{result_summary}", style="dim"))

    return Group(*renderables)


def _clean(value) -> str:
    text = str(value if value is not None else "-").strip()
    return text or "-"


def _get_findings(result: dict) -> list:
    contract = result.get("report_contract", {})
    return (
        contract.get("detailed_issues")
        or result.get("results")
        or result.get("findings")
        or []
    )


def _task_label(task: str) -> str:
    return {
        "analyze": "Dockerfile Analysis",
        "autofix": "AutoFix",
        "sbom": "SBOM",
        "compose": "Compose Scan",
        "k8s": "Kubernetes Scan",
        "cost": "Cloud Cost",
        "compose_generator": "Compose Generator",
    }.get(task, task.title())
