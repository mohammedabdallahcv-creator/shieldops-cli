"""shieldops config — manage CLI settings."""
import click
from rich.console import Console
from rich.table import Table
from shieldops_cli import config as cfg

console = Console()


@click.group("config")
def config_group():
    """View or change CLI configuration."""
    pass


@config_group.command("list")
def config_list():
    """Show all configuration values."""
    data = cfg.load()
    table = Table(title="ShieldOps CLI Configuration")
    table.add_column("Key", style="bold")
    table.add_column("Value")
    for k, v in sorted(data.items()):
        display = "***" if k == "api_key" and v else str(v)
        table.add_row(k, display)
    console.print(table)


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value. E.g.: shieldops config set default_format json"""
    cfg.set_key(key, value)
    console.print(f"[green]\u2705 {key} = {value}[/green]")


@config_group.command("get")
@click.argument("key")
def config_get(key):
    """Get a configuration value."""
    val = cfg.get(key)
    if val is None:
        console.print(f"[yellow]Key '{key}' not found.[/yellow]")
    else:
        console.print(str(val))
