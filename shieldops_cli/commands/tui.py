"""TUI command — Wave 1 smoke test stub.

Will be replaced by full TUI dispatcher in Wave 2.
"""
from __future__ import annotations

import click
from rich.console import Console


@click.command("tui")
@click.option(
    "--theme",
    type=click.Choice(["dark", "light"], case_sensitive=False),
    default="dark",
    show_default=True,
    help="Color theme for the TUI.",
)
def tui(theme: str) -> None:
    """Launch the interactive TUI (Claude-Code-like experience)."""
    console = Console()
    console.print(
        f"[bold cyan][OK] TUI Smoke Test OK[/bold cyan] "
        f"[dim](theme={theme})[/dim]"
    )
    console.print(
        "[dim]Wave 1 complete. Full TUI arrives in Wave 2.[/dim]"
    )
