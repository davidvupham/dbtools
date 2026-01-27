"""Main entry point for dbtool CLI."""
from __future__ import annotations

import typer
from rich.console import Console
from .config import load_config
from .commands import vault

app = typer.Typer(
    name="dbtool",
    help="Database Reliability Engineering CLI tool.",
    no_args_is_help=True,
    add_completion=False,
)

# Global console instance
console = Console()

@app.callback()
def main(
    debug: bool = typer.Option(
        False, "--debug", help="Enable verbose logging."
    ),
    profile: str | None = typer.Option(
        None, "--profile", help="Use a specific configuration profile."
    ),
):
    """
    dbtool - The operational Swiss Army Knife for DBREs.
    """
    # In a real app, we'd configure logging/config here
    # config = load_config()
    # if profile:
    #     config.current_profile = profile
    if debug:
        console.print("[yellow]Debug mode enabled[/yellow]", style="dim")

app.add_typer(vault.app, name="vault", help="Vault interaction wrapper.", aliases=["vt"])

if __name__ == "__main__":
    app()
