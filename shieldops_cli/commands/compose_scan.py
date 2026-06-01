"""shieldops compose-scan — Docker Compose file scanner."""
import sys
import click
from pathlib import Path
from rich.console import Console

from shieldops_cli.api_client import ShieldOpsClient, ApiError
from shieldops_cli.formatters import format_result

console = Console()


@click.command("compose-scan")
@click.argument("file", type=click.Path(exists=True))
@click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "sarif", "summary"]),
              default=None, help="Output format.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write output to file.")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low", "none"]),
              default="none", help="Exit with code 1 if issues >= severity.")
def compose_scan(file, fmt, output, fail_on):
    """Scan a Docker Compose file for security and configuration issues.

    \b
    Examples:
      shieldops compose-scan docker-compose.yml
      shieldops compose-scan docker-compose.yml --format json
      shieldops compose-scan docker-compose.yml --fail-on high
    """
    path = Path(file)
    content = path.read_text(encoding="utf-8")

    client = ShieldOpsClient()

    with console.status("[bold blue]Scanning Compose file...", spinner="dots"):
        try:
            payload = client.run_task("compose", content, path.name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(2)

    result = payload.get("result", {})
    formatted = format_result("compose", result, fmt=fmt or "table")

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 Report saved to {output}[/green]")
    else:
        console.print(formatted)

    if fail_on != "none":
        from shieldops_cli.commands.analyze import check_severity_gate
        if check_severity_gate(result, fail_on):
            console.print(f"\n[red]\u274c Issues at {fail_on.upper()} or above. Failing.[/red]")
            sys.exit(1)
