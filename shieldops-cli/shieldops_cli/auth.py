"""Authentication commands — supports free mode (no key) and paid plans."""
import click
from rich.console import Console
from shieldops_cli import config as cfg
from shieldops_cli.api_client import ShieldOpsClient

console = Console()


@click.command()
@click.option("--key", default="", help="API key from https://shieldops-ai.dev/settings/api-keys")
@click.option("--url", default=None, help="Override API base URL.")
def login(key, url):
    """Authenticate with your ShieldOps API key (or run in free mode)."""
    api_key = (key or "").strip()
    cfg.set_key("api_key", api_key)
    if url:
        cfg.set_key("api_url", url.strip().rstrip("/"))

    # Free mode: no key provided — verify server reachable
    if not api_key:
        client = ShieldOpsClient(api_key="")
        if not client.ping():
            console.print("[red]Could not reach ShieldOps API at:[/red]")
            console.print(f"   {cfg.get_api_url()}")
            console.print("   Check your network or set --url.")
            return
        caps = client.capabilities()
        if not caps:
            console.print("[yellow]Could not fetch capabilities. Check it at:[/yellow]")
            console.print(f"   {cfg.get_api_url()}")
            return
        console.print("[green]Running in [bold]FREE mode[/bold] (no API key)[/green]")
        console.print("   Dockerfile analysis: [green]local[/green] (no cloud credits)")
        console.print("   Other features: require Team or Enterprise plan")
        console.print(f"   Get a key at: {cfg.get_api_url()}/settings/api-keys")
        return

    # Verify the key
    client = ShieldOpsClient(api_key=api_key)
    info = client.whoami()
    if "error" in info:
        console.print("[yellow]Key saved but could not verify.[/yellow]")
        console.print(f"   Check the key at: {cfg.get_api_url()}/settings/api-keys")
        console.print(f"   Server said: {info.get('error', 'unknown')}")
        console.print("   You can still try CLI commands — free features work locally.")
    else:
        plan = info.get("plan", "free").title()
        name = info.get("name", info.get("email", "User"))
        console.print(f"[green]Authenticated as [bold]{name}[/bold] ({plan} plan)[/green]")


@click.command()
def logout():
    """Remove stored credentials."""
    cfg.set_key("api_key", "")
    console.print("[green]Logged out. API key removed.[/green]")


@click.command()
def whoami():
    """Show current account info and plan."""
    api_key = cfg.get_api_key()
    if not api_key:
        console.print("[yellow]Running in FREE mode (no API key). Run: shieldops login --key <KEY> for cloud features.[/yellow]")
        return

    client = ShieldOpsClient()
    info = client.whoami()
    if "error" in info:
        console.print("[red]Could not fetch account info. Check your API key.[/red]")
        return

    console.print(f"[bold]Name:[/bold]  {info.get('name', '—')}")
    console.print(f"[bold]Email:[/bold] {info.get('email', '—')}")
    console.print(f"[bold]Plan:[/bold]  {info.get('plan', 'free').title()}")

    caps = client.capabilities()
    limits = caps.get("limits", {})
    used = limits.get("daily_ai_used", 0)
    total = limits.get("daily_ai_requests")
    if total:
        console.print(f"[bold]Usage:[/bold] {used}/{total} requests today")
    else:
        console.print("[bold]Usage:[/bold] Unlimited")
