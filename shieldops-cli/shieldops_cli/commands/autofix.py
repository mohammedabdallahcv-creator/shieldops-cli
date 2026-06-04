"""shieldops autofix — AI-powered Dockerfile auto-fix."""
import sys
import click
from pathlib import Path
from rich.console import Console

from shieldops_cli.api_client import ShieldOpsClient, ApiError
from shieldops_cli.formatters import format_result

console = Console()


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "summary"]),
              default=None, help="Output format.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write output to file.")
@click.option("--apply", is_flag=True, default=False,
              help="Apply the fix directly to the original file (creates .bak backup).")
def autofix(file, fmt, output, apply):
    """Auto-fix a Dockerfile using AI.

    \b
    Examples:
      shieldops autofix Dockerfile
      shieldops autofix Dockerfile --format json -o fixed.json
      shieldops autofix Dockerfile --apply
    """
    path = Path(file)
    content = path.read_text(encoding="utf-8")

    client = ShieldOpsClient()

    with console.status("[bold blue]Generating fix...", spinner="dots"):
        try:
            payload = client.run_task("autofix", content, path.name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(2)

    result = payload.get("result", {})
    fixed_content = result.get("fixed_content", "")

    if apply and fixed_content:
        # Create backup
        backup = path.with_suffix(path.suffix + ".bak")
        backup.write_text(content, encoding="utf-8")
        path.write_text(fixed_content, encoding="utf-8")
        console.print(f"[green]\u2705 Fix applied to {path}. Backup at {backup}[/green]")
        return

    formatted = format_result("autofix", result, fmt=fmt or "table")

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 Report saved to {output}[/green]")
    else:
        console.print(formatted)

    report_url = result.get("report_url")
    if report_url:
        full_url = report_url if report_url.startswith("http") else f"{client.api_url}{report_url}"
        print(f"\nFull report: {full_url}")
