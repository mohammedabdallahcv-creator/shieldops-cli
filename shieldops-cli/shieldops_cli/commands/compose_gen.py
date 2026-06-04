"""shieldops compose-generate — Generate Docker Compose from Dockerfile."""
import sys
import click
from pathlib import Path
from rich.console import Console

from shieldops_cli.api_client import ShieldOpsClient, ApiError
from shieldops_cli.formatters import format_result

console = Console()


@click.command("compose-generate")
@click.argument("file", type=click.Path(exists=True))
@click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "summary"]),
              default=None, help="Output format.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write generated compose to file.")
def compose_generate(file, fmt, output):
    """Generate a Docker Compose file from a Dockerfile.

    \b
    Examples:
      shieldops compose-generate Dockerfile
      shieldops compose-generate Dockerfile -o docker-compose.yml
    """
    path = Path(file)
    content = path.read_text(encoding="utf-8")

    client = ShieldOpsClient()

    with console.status("[bold blue]Generating Compose file...", spinner="dots"):
        try:
            payload = client.run_task("compose_generator", content, path.name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(2)

    result = payload.get("result", {})
    generated = result.get("compose_content", "")

    if output and generated:
        Path(output).write_text(generated, encoding="utf-8")
        console.print(f"[green]\u2705 Compose file saved to {output}[/green]")
    elif output:
        formatted = format_result("compose_generator", result, fmt=fmt or "json")
        Path(output).write_text(formatted, encoding="utf-8")
        console.print(f"[green]\u2705 Output saved to {output}[/green]")
    else:
        if generated:
            console.print(generated)
        else:
            formatted = format_result("compose_generator", result, fmt=fmt or "table")
            console.print(formatted)
