"""shieldops scan-image — Scan a Docker image for vulnerabilities (requires Trivy)."""
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

SEVERITY_COLORS = {
    "CRITICAL": "bold white on red",
    "HIGH": "bold red",
    "MEDIUM": "yellow",
    "LOW": "dim",
}


@click.command("scan-image")
@click.argument("image_name")
@click.option("--severity", "-s", default="HIGH,CRITICAL",
              help="Severity levels to report (e.g., HIGH,CRITICAL)")
@click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "summary"]),
              default="table", help="Output format.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write output to file.")
def scan_image(image_name, severity, fmt, output):
    """Scan a Docker image from a registry for vulnerabilities.

    Requires Trivy to be installed locally.

    \b
    Examples:
      shieldops scan-image nginx:latest
      shieldops scan-image python:3.11-slim --severity CRITICAL
      shieldops scan-image myapp:v1 -f json -o vulns.json
    """
    try:
        sys.path.insert(0, ".")
        from src.analysis.registry_scanner import RegistryScanner

        scanner = RegistryScanner()

        if not scanner.is_trivy_installed():
            console.print(f"[yellow]{scanner.get_installation_instructions()}[/yellow]")
            return

        with console.status(f"[bold blue]Scanning image: {image_name}...", spinner="dots"):
            result = scanner.scan_image(image_name, severity)

        if "error" in result:
            console.print(f"[red]\u274c Error: {result['error']}[/red]")
            if result.get("message"):
                console.print(result["message"])
            return

        total = result["total_vulnerabilities"]

        if fmt == "json":
            import json
            out = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            if output:
                from pathlib import Path
                Path(output).write_text(out, encoding="utf-8")
                console.print(f"[green]\u2705 Report saved to {output}[/green]")
            else:
                console.print(out)
            return

        if fmt == "summary":
            if total == 0:
                line = f"\u2705 scan-image: No {severity} vulnerabilities in {image_name}"
            else:
                line = f"\u26a0\ufe0f  scan-image: {total} vulnerabilities in {image_name}"
            if output:
                from pathlib import Path
                Path(output).write_text(line, encoding="utf-8")
            else:
                console.print(line)
            return

        # Table format
        if total == 0:
            console.print(f"[green bold]\u2705 No {severity} vulnerabilities found in {image_name}![/green bold]")
        else:
            console.print(f"[red bold]\u26a0\ufe0f  Found {total} vulnerabilities in {image_name}:[/red bold]")
            console.print(f"Image: {result['image']}")
            console.print(f"Scan Date: {result.get('scan_date', 'Unknown')}\n")

            table = Table(title="Vulnerabilities", show_lines=True)
            table.add_column("ID", width=18)
            table.add_column("Severity", width=10)
            table.add_column("Package", width=20)
            table.add_column("Installed", width=12)
            table.add_column("Fixed In", width=12)
            table.add_column("Title", ratio=2)

            for v in result["vulnerabilities"][:30]:
                sev = v["severity"]
                style = SEVERITY_COLORS.get(sev, "")
                table.add_row(
                    v["vulnerability_id"],
                    Text(sev, style=style),
                    v["package_name"],
                    v["installed_version"],
                    v["fixed_version"],
                    v["title"][:80],
                )

            console.print(table)

            if total > 30:
                console.print(f"\n[dim]... and {total - 30} more vulnerabilities[/dim]")

    except ImportError as e:
        console.print(f"[red]\u274c Error importing scanner: {e}[/red]")
        console.print("Make sure you're running from the project directory.")
    except Exception as e:
        console.print(f"[red]\u274c Unexpected error: {e}[/red]")
