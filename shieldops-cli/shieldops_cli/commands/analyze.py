"""shieldops analyze — Dockerfile analysis (local or cloud)."""
import sys
import click
from pathlib import Path
from rich.console import Console

from shieldops_cli import config as cfg
from shieldops_cli.api_client import ShieldOpsClient, ApiError
from shieldops_cli.formatters import format_result
from shieldops_cli.local_analyzer import analyze_dockerfile as local_analyze

console = Console()

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "sarif", "summary"]),
              default=None, help="Output format. Default: from config or 'table'.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write output to file instead of stdout.")
@click.option("--open-report", is_flag=True, default=False,
              help="Open the full report in browser after scan (cloud only).")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low", "none"]),
              default="none", help="Exit with code 1 if issues >= severity (for CI/CD).")
@click.option("--api", "force_api", is_flag=True, default=False,
              help="Force cloud analysis (requires login).")
def analyze(file, fmt, output, open_report, fail_on, force_api):
    """Analyze a Dockerfile for security and best-practice issues.

    Runs locally by default (no API key needed). Use --api for cloud analysis.

    \b
    Examples:
      shieldops analyze Dockerfile
      shieldops analyze Dockerfile --api          # cloud (requires login)
      shieldops analyze Dockerfile --format json --output report.json
      shieldops analyze Dockerfile --fail-on high  # CI/CD gate
    """
    path = Path(file)
    content = path.read_text(encoding="utf-8")
    filename = path.name

    api_key = cfg.get_api_key()

    if api_key or force_api:
        if not api_key:
            console.print("[red]Cloud analysis requires login. Run: shieldops login --key <YOUR_KEY>[/red]")
            sys.exit(2)
        _run_cloud_analysis(content, filename, fmt, output, open_report, fail_on)
    else:
        _run_local_analysis(content, filename, fmt, output, fail_on)


def _run_local_analysis(content: str, filename: str, fmt, output, fail_on):
    result = local_analyze(content, filename)
    formatted = format_result("analyze", result, fmt=fmt or "table")

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 Report saved to {output}[/green]")
    else:
        console.print(formatted)

    console.print("\n[dim][Local analysis - 10 rules] Sign up for cloud analysis with AI:[/dim]")
    console.print(f"[dim]  {cfg.get_api_url()}/api-keys[/dim]")

    if fail_on != "none":
        if check_severity_gate(result, fail_on):
            console.print(f"\n[red]\u274c Issues found at {fail_on.upper()} or above. Failing.[/red]")
            sys.exit(1)


def _run_cloud_analysis(content: str, filename: str, fmt, output, open_report, fail_on):
    client = ShieldOpsClient()

    with console.status("[bold blue]Analyzing...", spinner="dots"):
        try:
            payload = client.run_task("analyze", content, filename)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(2)

    result = payload.get("result", {})

    formatted = format_result("analyze", result, fmt=fmt or "table")

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 Report saved to {output}[/green]")
    else:
        console.print(formatted)

    report_url = (
        result.get("report_url")
        or payload.get("route")
    )
    if not report_url:
        scan_id = result.get("scan_id") or payload.get("scan_id") or ""
        if scan_id:
            report_url = f"/analyze/report_view?scan_id={scan_id}&origin=extension"

    if report_url:
        base = client.api_url
        full_url = report_url if report_url.startswith("http") else f"{base}{report_url}"
        print(f"\nFull report: {full_url}")
        if open_report:
            import webbrowser
            webbrowser.open(full_url)
    else:
        print("\nNo report URL returned for this scan.")

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
