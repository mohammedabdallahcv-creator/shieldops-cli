"""Authentication commands."""
import click
from rich.console import Console
from shieldops_cli import config as cfg
from shieldops_cli.api_client import ShieldOpsClient

console = Console()


@click.command()
@click.option("--key", prompt="API Key", hide_input=True,
              help="API key from https://shieldops-ai.dev/settings/api-keys")
@click.option("--url", default=None, help="Override API base URL.")
def login(key, url):
    """Authenticate with your ShieldOps API key."""
    cfg.set_key("api_key", key.strip())
    if url:
        cfg.set_key("api_url", url.strip().rstrip("/"))

    # Verify the key
    client = ShieldOpsClient(api_key=key.strip())
    info = client.whoami()
    if "error" in info:
        console.print("[yellow]\u26a0  Key saved but could not verify. Check it at:[/yellow]")
        console.print(f"   {cfg.get_api_url()}/settings/api-keys")
    else:
        plan = info.get("plan", "free").title()
        name = info.get("name", info.get("email", "User"))
        console.print(f"[green]\u2705 Authenticated as [bold]{name}[/bold] ({plan} plan)[/green]")


@click.command()
def logout():
    """Remove stored credentials."""
    cfg.set_key("api_key", "")
    console.print("[green]\u2705 Logged out. API key removed.[/green]")


@click.command()
def whoami():
    """Show current account info and plan."""
    api_key = cfg.get_api_key()
    if not api_key:
        console.print("[yellow]Not authenticated. Run: shieldops login[/yellow]")
        return

    client = ShieldOpsClient()
    info = client.whoami()
    if "error" in info:
        console.print("[red]Could not fetch account info. Check your API key.[/red]")
        return

    console.print(f"[bold]Name:[/bold]  {info.get('name', '\u2014')}")
    console.print(f"[bold]Email:[/bold] {info.get('email', '\u2014')}")
    console.print(f"[bold]Plan:[/bold]  {info.get('plan', 'free').title()}")

    caps = client.capabilities()
    limits = caps.get("limits", {})
    used = limits.get("daily_ai_used", 0)
    total = limits.get("daily_ai_requests")
    if total:
        console.print(f"[bold]Usage:[/bold] {used}/{total} requests today")
    else:
        console.print("[bold]Usage:[/bold] Unlimited")
