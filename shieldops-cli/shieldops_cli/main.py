"""shieldops — CLI entry point."""
import click
from shieldops_cli import __version__


@click.group()
@click.version_option(__version__, prog_name="shieldops")
def cli():
    """ShieldOps AI — Security scanner for Docker, Kubernetes, Compose, SBOM, and more."""
    pass


# ── Import and register commands ──
from shieldops_cli.auth import login, logout, whoami
from shieldops_cli.commands.analyze import analyze
from shieldops_cli.commands.autofix import autofix
from shieldops_cli.commands.sbom import sbom
from shieldops_cli.commands.compose_scan import compose_scan
from shieldops_cli.commands.k8s_scan import k8s_scan
from shieldops_cli.commands.compose_gen import compose_generate
from shieldops_cli.commands.scan_image import scan_image
from shieldops_cli.commands.config_cmd import config_group

cli.add_command(login)
cli.add_command(logout)
cli.add_command(whoami)
cli.add_command(analyze)
cli.add_command(autofix)
cli.add_command(sbom)
cli.add_command(compose_scan, "compose-scan")
cli.add_command(k8s_scan, "k8s-scan")
cli.add_command(compose_generate, "compose-generate")
cli.add_command(scan_image, "scan-image")
cli.add_command(config_group, "config")

# ── TUI command (optional, requires prompt_toolkit) ──
try:
    from shieldops_cli.commands.tui import tui
    cli.add_command(tui)
except ImportError:
    pass  # TUI extra not installed; CLI works without it


if __name__ == "__main__":
    cli()
