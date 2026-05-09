"""shieldops sbom — Generate Software Bill of Materials."""
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
def sbom(file, fmt, output):
    """Generate SBOM (Software Bill of Materials) from a Dockerfile or dependency file.

    \b
    Examples:
      shieldops sbom Dockerfile
      shieldops sbom requirements.txt -f json -o sbom.json
    """
    path = Path(file)
    content = path.read_text(encoding="utf-8")

    client = ShieldOpsClient()

    with console.status("[bold blue]Generating SBOM...", spinner="dots"):
        try:
            payload = client.run_task("sbom", content, path.name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(2)

    result = payload.get("result", {})
    formatted = format_result("sbom", result, fmt=fmt or "table")

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 SBOM saved to {output}[/green]")
    else:
        console.print(formatted)
