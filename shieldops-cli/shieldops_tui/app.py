"""ShieldOps TUI — Main application with REPL loop."""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.styles import Style
from rich.console import Console

from shieldops_tui.completer import COMMAND_DESCRIPTIONS, ShieldOpsCompleter

console = Console()

HISTORY_FILE = Path.home() / ".shieldops" / "tui_history"

WELCOME = """
  _   _        _____ _     _____
 | | | |      /  ___| |   /  ___|
 | | | |_ __  \\ `--.| |__ \\ `--.
 | | | | '_ \\  `--. \\ '_ \\ `--. \\
 | |_| | | | /\\__/ / | | /\\__/ /
  \\___/|_| |_\\____/|_| |_\\____/   AI

"""

HELP_TEXT = """
Available commands:
  /analyze <file>          Analyze Dockerfile (local, free, no API key)
  /analyze-json <file>     Analyze Dockerfile, output as JSON
  /autofix <file>          AI auto-fix Dockerfile (requires API key)
  /sbom <file>             Generate SBOM (requires API key)
  /compose-scan <file>     Scan docker-compose.yml (requires API key)
  /compose-generate <file> Generate docker-compose.yml from Dockerfile (cloud)
  /k8s-scan <file>         Scan Kubernetes YAML (requires API key)
  /scan-image <name>       Scan Docker image (local, requires Trivy)
  /login --key <KEY>       Authenticate with API key
  /logout                  Remove stored credentials
  /whoami                  Show account info
  /config                  Show CLI configuration
  /save <file>             Save last report to file
  /help                    Show this help message
  /clear                   Clear the screen
  /exit                    Exit the TUI

Tips:
  - Tab to autocomplete commands
  - Up/Down arrows for command history
  - Free users: /analyze runs locally with 20 security rules
  - /save saves the last scan output to a file
"""

THEME_DARK = Style.from_dict({
    "prompt": "#8B5CF6 bold",
    "command": "#ffffff",
})

THEME_LIGHT = Style.from_dict({
    "prompt": "#7C3AED bold",
    "command": "#1f2937",
})


def run(theme: str = "dark") -> None:
    """Launch the interactive TUI."""
    style = THEME_DARK if theme == "dark" else THEME_LIGHT

    config_dir = Path.home() / ".shieldops"
    config_dir.mkdir(parents=True, exist_ok=True)

    history = FileHistory(str(HISTORY_FILE))
    completer = ShieldOpsCompleter()
    session = PromptSession(
        history=history,
        completer=completer,
        complete_while_typing=True,
        style=style,
    )

    clear()
    print(WELCOME)
    print(" Type /help for commands. Free tier: local analysis available.\n")

    last_output = ""
    running = True

    while running:
        try:
            user_input = session.prompt(
                HTML('<ansiblue bold>shieldops</ansiblue><ansigray>&gt; </ansigray>'),
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        cmd, output = process_command(user_input, last_output)
        if output:
            last_output = output

        if cmd == "exit":
            running = False

    print("Session closed.\n")


def process_command(user_input: str, last_output: str) -> tuple[str, str]:
    """Process a single command and return (cmd_name, output_text)."""
    parts = user_input.split(None, 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else None

    handlers = {
        "/analyze": cmd_analyze,
        "/analyze-json": cmd_analyze_json,
        "/autofix": cmd_autofix,
        "/sbom": cmd_sbom,
        "/compose-scan": cmd_compose_scan,
        "/compose-generate": cmd_compose_generate,
        "/k8s-scan": cmd_k8s_scan,
        "/scan-image": cmd_scan_image,
        "/login": cmd_login,
        "/logout": cmd_logout,
        "/whoami": cmd_whoami,
        "/config": cmd_config,
        "/save": cmd_save,
        "/help": cmd_help,
        "/clear": cmd_clear,
        "/exit": cmd_exit,
    }

    handler = handlers.get(cmd)
    if handler is None:
        console.print(f"[red]Unknown command: {cmd}. Type /help for available commands.[/red]")
        return cmd, ""

    try:
        output = handler(args, last_output)
        return cmd, output or ""
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return cmd, ""
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        return cmd, ""


def _read_file(file_path: str) -> str:
    """Read file contents, return empty string on failure."""
    p = Path(file_path)
    if not p.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except Exception as exc:
        console.print(f"[red]Error reading {file_path}: {exc}[/red]")
        return ""


def cmd_analyze(args: str | None, last_output: str) -> str:
    """Analyze a Dockerfile locally (free tier)."""
    if not args:
        console.print("[yellow]Usage: /analyze <path/to/Dockerfile>[/yellow]")
        return ""

    content = _read_file(args)
    if not content:
        return ""

    from shieldops_cli.formatters.table import render_table
    from shieldops_cli.local_analyzer import analyze_dockerfile_local

    with console.status("[bold blue]Analyzing Dockerfile...", spinner="dots"):
        time.sleep(0.3)
        result = analyze_dockerfile_local(content, filename=Path(args).name)

    console.print(render_table("analyze", result))

    console.print(f"\n[dim]Engine: {result['engine']} | Risk: {result['summary']['risk_score']}/100[/dim]")
    console.print("[dim]Sign up at https://shieldops-ai.dev for cloud AI analysis with autofix[/dim]")
    return f"Local analysis: {result['summary']['total_issues']} issues found"


def cmd_analyze_json(args: str | None, last_output: str) -> str:
    """Analyze a Dockerfile and output JSON."""
    if not args:
        console.print("[yellow]Usage: /analyze-json <path/to/Dockerfile>[/yellow]")
        return ""

    content = _read_file(args)
    if not content:
        return ""

    from shieldops_cli.formatters.json_fmt import to_json
    from shieldops_cli.local_analyzer import analyze_dockerfile_local

    with console.status("[bold blue]Analyzing...", spinner="dots"):
        time.sleep(0.3)
        result = analyze_dockerfile_local(content, filename=Path(args).name)

    console.print(to_json(result))
    return to_json(result)


def cmd_autofix(args: str | None, last_output: str) -> str:
    """Run cloud autofix (requires API key)."""
    if not args:
        console.print("[yellow]Usage: /autofix <path/to/Dockerfile>[/yellow]")
        return ""

    content = _read_file(args)
    if not content:
        return ""

    from shieldops_cli.api_client import ApiError, ShieldOpsClient
    from shieldops_cli.formatters.table import render_table

    client = ShieldOpsClient()
    if not client.api_key:
        console.print("[red]Autofix requires an API key. Run /login --key <YOUR_KEY>[/red]")
        return ""

    with console.status("[bold blue]Generating fix...", spinner="dots"):
        try:
            payload = client.run_task("autofix", content, Path(args).name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            return ""

    result = payload.get("result", {})
    fixed = result.get("fixed_content", "")

    if fixed:
        console.print(fixed)
        save_path = Path(args).with_suffix(".fixed" + Path(args).suffix)
        save_path.write_text(fixed, encoding="utf-8")
        console.print(f"\n[dim]Fixed version saved to {save_path}[/dim]")
        return fixed

    console.print(render_table("autofix", result))
    return ""


def cmd_sbom(args: str | None, last_output: str) -> str:
    """Generate SBOM (requires API key)."""
    if not args:
        console.print("[yellow]Usage: /sbom <path/to/file>[/yellow]")
        return ""

    content = _read_file(args)
    if not content:
        return ""

    from shieldops_cli.api_client import ApiError, ShieldOpsClient
    from shieldops_cli.formatters.table import render_table

    client = ShieldOpsClient()
    if not client.api_key:
        console.print("[red]SBOM requires an API key. Run /login --key <YOUR_KEY>[/red]")
        return ""

    with console.status("[bold blue]Generating SBOM...", spinner="dots"):
        try:
            payload = client.run_task("sbom", content, Path(args).name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            return ""

    result = payload.get("result", {})
    console.print(render_table("sbom", result))
    return ""


def cmd_compose_scan(args: str | None, last_output: str) -> str:
    """Scan docker-compose.yml (requires API key)."""
    if not args:
        console.print("[yellow]Usage: /compose-scan <path/to/docker-compose.yml>[/yellow]")
        return ""

    content = _read_file(args)
    if not content:
        return ""

    from shieldops_cli.api_client import ApiError, ShieldOpsClient
    from shieldops_cli.formatters.table import render_table

    client = ShieldOpsClient()
    if not client.api_key:
        console.print("[red]Compose scan requires an API key. Run /login --key <YOUR_KEY>[/red]")
        return ""

    with console.status("[bold blue]Scanning Compose file...", spinner="dots"):
        try:
            payload = client.run_task("compose", content, Path(args).name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            return ""

    result = payload.get("result", {})
    console.print(render_table("compose", result))
    return ""


def cmd_compose_generate(args: str | None, last_output: str) -> str:
    """Generate docker-compose.yml from Dockerfile (cloud)."""
    if not args:
        console.print("[yellow]Usage: /compose-generate <path/to/Dockerfile>[/yellow]")
        return ""

    content = _read_file(args)
    if not content:
        return ""

    from shieldops_cli.api_client import ApiError, ShieldOpsClient

    client = ShieldOpsClient()
    if not client.api_key:
        console.print("[red]Compose generation requires an API key. Run /login --key <YOUR_KEY>[/red]")
        return ""

    with console.status("[bold blue]Generating Compose file...", spinner="dots"):
        try:
            payload = client.run_task("compose_generator", content, Path(args).name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            return ""

    result = payload.get("result", {})
    generated = result.get("compose_content", "")

    if generated:
        console.print(generated)
    else:
        from shieldops_cli.formatters.table import render_table
        console.print(render_table("compose_generator", result))
    return ""


def cmd_k8s_scan(args: str | None, last_output: str) -> str:
    """Scan Kubernetes manifest (requires API key)."""
    if not args:
        console.print("[yellow]Usage: /k8s-scan <path/to/k8s.yaml>[/yellow]")
        return ""

    content = _read_file(args)
    if not content:
        return ""

    from shieldops_cli.api_client import ApiError, ShieldOpsClient
    from shieldops_cli.formatters.table import render_table

    client = ShieldOpsClient()
    if not client.api_key:
        console.print("[red]K8s scan requires an API key. Run /login --key <YOUR_KEY>[/red]")
        return ""

    with console.status("[bold blue]Scanning Kubernetes manifest...", spinner="dots"):
        try:
            payload = client.run_task("k8s", content, Path(args).name)
        except ApiError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            return ""

    result = payload.get("result", {})
    console.print(render_table("k8s", result))
    return ""


def cmd_scan_image(args: str | None, last_output: str) -> str:
    """Scan a Docker image locally using Trivy."""
    if not args:
        console.print("[yellow]Usage: /scan-image <image_name>[/yellow]")
        return ""

    image_name = args.strip()

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from src.analysis.registry_scanner import RegistryScanner

        scanner = RegistryScanner()
        if not scanner.is_trivy_installed():
            console.print("[yellow]Trivy not installed. Install Trivy first.[/yellow]")
            return ""

        from rich.text import Text

        severity_colors = {
            "CRITICAL": "bold white on red",
            "HIGH": "bold red",
            "MEDIUM": "yellow",
            "LOW": "dim",
        }

        with console.status(f"[bold blue]Scanning image: {image_name}...", spinner="dots"):
            result = scanner.scan_image(image_name, "HIGH,CRITICAL")

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return ""

        total = result["total_vulnerabilities"]

        if total == 0:
            console.print(f"[green bold]No HIGH/CRITICAL vulnerabilities in {image_name}![/green bold]")
            return ""

        console.print(f"[red bold]Found {total} vulnerabilities in {image_name}:[/red bold]")
        console.print(f"Image: {result['image']}")

        table = console.render_str("[bold]Vulnerabilities[/bold]")
        from rich.table import Table
        tbl = Table(show_lines=True)
        tbl.add_column("ID", width=18)
        tbl.add_column("Severity", width=10)
        tbl.add_column("Package", width=20)
        tbl.add_column("Installed", width=12)
        tbl.add_column("Fixed In", width=12)
        tbl.add_column("Title", ratio=2)

        for v in result["vulnerabilities"][:30]:
            sev = v["severity"]
            tbl.add_row(
                v["vulnerability_id"],
                Text(sev, style=severity_colors.get(sev, "")),
                v["package_name"],
                v["installed_version"],
                v["fixed_version"],
                v["title"][:80],
            )

        console.print(tbl)
        if total > 30:
            console.print(f"\n[dim]... and {total - 30} more vulnerabilities[/dim]")

        return f"scan-image: {total} vulnerabilities"

    except ImportError:
        console.print("[red]Registry scanner not available. Make sure you're in the project directory.[/red]")
        return ""


def cmd_login(args: str | None, last_output: str) -> str:
    """Login with API key."""
    from shieldops_cli import config as cfg
    from shieldops_cli.api_client import ShieldOpsClient

    key = ""
    if args and "--key" in args:
        parts = args.split("--key", 1)
        if len(parts) > 1:
            key = parts[1].strip()

    if not key:
        console.print("[red]Usage: /login --key <YOUR_API_KEY>[/red]")
        return ""

    cfg.set_key("api_key", key)

    client = ShieldOpsClient(api_key=key)
    info = client.whoami()

    if "error" in info:
        console.print("[yellow]Key saved but could not verify immediately.[/yellow]")
        console.print(f"   Check at: {cfg.get_api_url()}/settings/api-keys")
        return ""

    plan = info.get("plan", "free").title()
    name = info.get("name", info.get("email", "User"))
    console.print(f"[green]Authenticated as {name} ({plan} plan)[/green]")
    return f"Logged in as {name}"


def cmd_logout(args: str | None, last_output: str) -> str:
    """Remove stored credentials."""
    from shieldops_cli import config as cfg

    cfg.set_key("api_key", "")
    console.print("[green]Logged out. API key removed.[/green]")
    return "Logged out"


def cmd_whoami(args: str | None, last_output: str) -> str:
    """Show current account info."""
    from rich.table import Table
    from shieldops_cli import config as cfg
    from shieldops_cli.api_client import ShieldOpsClient

    api_key = cfg.get_api_key()

    if not api_key:
        console.print("[yellow]Running in FREE mode (no API key)[/yellow]")
        console.print("Run /login --key <KEY> for cloud features")
        return "Free mode"

    client = ShieldOpsClient()
    info = client.whoami()

    if "error" in info:
        console.print("[red]Could not fetch account info. Check your API key.[/red]")
        return ""

    table = Table(title="Account Info")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Name", info.get("name", "-"))
    table.add_row("Email", info.get("email", "-"))
    table.add_row("Plan", info.get("plan", "free").title())

    caps = client.capabilities()
    limits = caps.get("limits", {})
    used = limits.get("daily_ai_used", 0)
    total = limits.get("daily_ai_requests")
    usage_str = f"{used}/{total}" if total else "Unlimited"
    table.add_row("Daily Usage", usage_str)

    console.print(table)
    return ""


def cmd_config(args: str | None, last_output: str) -> str:
    """Show CLI configuration."""
    from rich.table import Table
    from shieldops_cli import config as cfg

    data = cfg.load()

    table = Table(title="ShieldOps CLI Configuration")
    table.add_column("Key", style="bold")
    table.add_column("Value")

    for k, v in sorted(data.items()):
        display = "***" if k == "api_key" and v else str(v)
        table.add_row(k, display)

    console.print(table)
    return ""


def cmd_save(args: str | None, last_output: str) -> str:
    """Save last report to file."""
    if not last_output:
        console.print("[yellow]No report to save. Run a scan first, then /save.[/yellow]")
        return ""

    if args:
        save_path = Path(args)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = Path(f"shieldops_report_{timestamp}.txt")

    try:
        save_path.write_text(last_output, encoding="utf-8")
        console.print(f"[green]Report saved to {save_path}[/green]")
        return f"Saved: {save_path}"
    except Exception as exc:
        console.print(f"[red]Error saving report: {exc}[/red]")
        return ""


def cmd_help(args: str | None, last_output: str) -> str:
    """Show help text."""
    print(HELP_TEXT)
    return "help"


def cmd_clear(args: str | None, last_output: str) -> str:
    """Clear the screen."""
    clear()
    print(WELCOME)
    return ""


def cmd_exit(args: str | None, last_output: str) -> str:
    """Exit the TUI."""
    print("Session closed.")
    return "exit"
