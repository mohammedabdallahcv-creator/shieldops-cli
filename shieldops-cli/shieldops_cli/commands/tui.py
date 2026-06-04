"""TUI command — entry point for the interactive Terminal UI.

Thin Click wrapper that delegates to the shieldops_tui package.
"""
from __future__ import annotations

import click


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
    try:
        from shieldops_tui.app import run
    except ImportError as exc:
        raise click.ClickException(
            f"TUI dependencies missing: {exc}.\n\n"
            "Install with: pip install 'shieldops-cli[tui]'"
        )
    run(theme=theme)
