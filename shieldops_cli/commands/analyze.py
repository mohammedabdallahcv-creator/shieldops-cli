"""shieldops analyze — Dockerfile analysis."""
import sys
import click
from pathlib import Path
from rich.console import Console

from shieldops_cli.api_client import ShieldOpsClient, ApiError
from shieldops_cli.formatters import format_result

console = Console()

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "sarif", "summary"]),
              default=None, help="Output format. Default: from config or 'table'.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write output to file instead of stdout.")
@click.option("--open-report", is_flag=True, default=False,
              help="Open the full report in browser after scan.")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low", "none"]),
              default="none", help="Exit with code 1 if issues >= severity (for CI/CD).")
def analyze(file, fmt, output, open_report, fail_on):
    """Analyze a Dockerfile for security and best-practice issues.

    \b
    Examples:
      shieldops analyze Dockerfile
      shieldops analyze Dockerfile --format json --output report.json
      shieldops analyze Dockerfile --fail-on high    # CI/CD gate
      shieldops analyze Dockerfile --open-report
    """
    path = Path(file)
    content = path.read_text(encoding="utf-8")
    filename = path.name

    client = ShieldOpsClient()

    with console.status("[bold blue]Analyzing...", spinner="dots"):
        try:
            payload = client.run_task("analyze", content, filename)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(2)

    result = payload.get("result", {})

    # ── Format output ──
    formatted = format_result("analyze", result, fmt=fmt or "table")

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 Report saved to {output}[/green]")
    else:
        console.print(formatted)

    # ── Report URL ──
    report_url = result.get("report_url")
    if report_url:
        base = client.api_url
        full_url = report_url if report_url.startswith("http") else f"{base}{report_url}"
        console.print(f"\n[dim]Full report: {full_url}[/dim]")

    if open_report and report_url:
        import webbrowser
        full_url = report_url if report_url.startswith("http") else f"{client.api_url}{report_url}"
        webbrowser.open(full_url)

    # ── CI/CD exit code ──
    if fail_on != "none":
        if check_severity_gate(result, fail_on):
            console.print(f"\n[red]\u274c Issues found at {fail_on.upper()} or above. Failing.[/red]")
            sys.exit(1)


def check_severity_gate(result: dict, threshold: str) -> bool:
    """Return True if any finding meets or exceeds threshold severity."""
    threshold_level = SEVERITY_ORDER.get(threshold, 3)

    # Try report_contract first
    contract = result.get("report_contract", {})
    if contract:
        for sev in SEVERITY_ORDER:
            if SEVERITY_ORDER[sev] <= threshold_level:
                count = int(contract.get(f"{sev}_count", 0) or 0)
                if count > 0:
                    return True
        return False

    # Fallback: check raw findings
    findings = result.get("findings", result.get("results", []))
    for f in findings:
        sev = str(f.get("severity", "")).lower()
        if SEVERITY_ORDER.get(sev, 99) <= threshold_level:
            return True
    return False
