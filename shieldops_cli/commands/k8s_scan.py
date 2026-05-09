"""shieldops k8s-scan — Kubernetes manifest scanner."""
import sys
import click
from pathlib import Path
from rich.console import Console

from shieldops_cli.api_client import ShieldOpsClient, ApiError
from shieldops_cli.formatters import format_result

console = Console()


@click.command("k8s-scan")
@click.argument("file", type=click.Path(exists=True))
@click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "sarif", "summary"]),
              default=None, help="Output format.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write output to file.")
@click.option("--open-report", is_flag=True, default=False,
              help="Open the full report in browser.")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low", "none"]),
              default="none", help="Exit with code 1 if issues >= severity.")
def k8s_scan(file, fmt, output, open_report, fail_on):
    """Scan a Kubernetes manifest (YAML) for misconfigurations.

    \b
    Examples:
      shieldops k8s-scan deployment.yaml
      shieldops k8s-scan k8s/ --format sarif --output k8s-report.sarif
      shieldops k8s-scan pod.yaml --fail-on high
    """
    path = Path(file)
    content = path.read_text(encoding="utf-8")

    client = ShieldOpsClient()

    with console.status("[bold blue]Scanning Kubernetes manifest...", spinner="dots"):
        try:
            payload = client.run_task("k8s", content, path.name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(2)

    result = payload.get("result", {})
    formatted = format_result("k8s", result, fmt=fmt or "table")

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 Report saved to {output}[/green]")
    else:
        console.print(formatted)

    report_url = result.get("report_url")
    if report_url:
        base = client.api_url
        full_url = report_url if report_url.startswith("http") else f"{base}{report_url}"
        console.print(f"\n[dim]Full report: {full_url}[/dim]")

    if open_report and report_url:
        import webbrowser
        full_url = report_url if report_url.startswith("http") else f"{client.api_url}{report_url}"
        webbrowser.open(full_url)

    if fail_on != "none":
        from shieldops_cli.commands.analyze import check_severity_gate
        if check_severity_gate(result, fail_on):
            console.print(f"\n[red]\u274c Issues at {fail_on.upper()} or above. Failing.[/red]")
            sys.exit(1)
