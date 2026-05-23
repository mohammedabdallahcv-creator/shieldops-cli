"""Human-friendly Rich table output."""
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
import io

SEVERITY_COLORS = {
    "critical": "bold white on red",
    "high": "bold red",
    "medium": "yellow",
    "low": "dim",
    "info": "dim cyan",
}


def to_table(task: str, result: dict) -> str:
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=True)

    # ── Score hero ──
    stats = result.get("stats", result.get("report_contract", {}).get("stats", {}))
    score = (
        result.get("security_score")
        or result.get("security_score_percent")
        or result.get("report_contract", {}).get("security_score")
        or result.get("report_contract", {}).get("security_score_percent")
        or stats.get("security_score")
        or stats.get("score")
        or result.get("v2_scan", {}).get("stats", {}).get("score")
        or "N/A"
    )
    grade = (
        result.get("security_score_grade")
        or result.get("report_contract", {}).get("security_score_grade")
        or ""
    )

    console.print(Panel(
        f"[bold]{_task_label(task)}[/bold]\n"
        f"Score: [bold cyan]{score}[/bold cyan] {grade}\n"
        f"Engine: {result.get('engine', 'ShieldOps AI')}",
        title="ShieldOps AI",
        border_style="blue",
    ))

    # ── Findings table ──
    findings = (
        result.get("report_contract", {}).get("detailed_issues")
        or result.get("results")
        or result.get("findings")
        or []
    )
    if not findings:
        console.print("[green]\u2705 No issues found![/green]")
        return buf.getvalue()

    table = Table(title="Findings", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Severity", width=10)
    table.add_column("Category", width=14)
    table.add_column("Message", ratio=3)
    table.add_column("Fix", ratio=2)

    for i, f in enumerate(findings, 1):
        sev = str(f.get("severity", "info")).lower()
        style = SEVERITY_COLORS.get(sev, "")
        table.add_row(
            str(i),
            Text(sev.upper(), style=style),
            str(f.get("category", "")),
            str(f.get("message") or f.get("title", "")),
            str(f.get("fix", ""))[:120],
        )

    console.print(table)

    # ── Summary ──
    summary = result.get("summary")
    if isinstance(summary, str) and summary:
        console.print(f"\n[dim]{summary}[/dim]")

    return buf.getvalue()


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
