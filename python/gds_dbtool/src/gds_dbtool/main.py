"""Main entry point for dbtool CLI.

Provides the root application with global options and subcommand routing.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler

from . import __version__
from .config import GlobalConfig, load_config
from .constants import ExitCode
from .logging import setup_file_logging


# Global state shared across commands
class AppState:
    """Global application state."""

    def __init__(self) -> None:
        self.config: GlobalConfig | None = None
        self.console: Console | None = None
        self.debug: bool = False
        self.quiet: bool = False
        self.dry_run: bool = False


state = AppState()


def _parse_bool_env(name: str) -> bool:
    """Parse boolean environment variable."""
    value = os.getenv(name, "").lower()
    return value in ("1", "true", "yes")


def _get_console(no_color: bool) -> Console:
    """Create console with appropriate color settings."""
    # Check NO_COLOR env var (standard) or DBTOOL_NO_COLOR
    env_no_color = os.getenv("NO_COLOR") is not None or _parse_bool_env("DBTOOL_NO_COLOR")
    return Console(no_color=no_color or env_no_color, stderr=False)


def _setup_logging(debug: bool) -> None:
    """Configure logging based on debug flag."""
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=debug)],
    )


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console = Console()
        console.print(f"dbtool version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="dbtool",
    help="Unified Database CLI tool.",
    no_args_is_help=True,
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def main(
    ctx: typer.Context,  # noqa: ARG001
    version: Annotated[  # noqa: ARG001
        bool | None,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Print version information and exit.",
        ),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            envvar="DBTOOL_DEBUG",
            help="Enable verbose logging to stderr.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Suppress non-essential output (errors only).",
        ),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option(
            "--no-color",
            help="Disable colored output. Also respects NO_COLOR env var.",
        ),
    ] = False,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            "-p",
            envvar="DBTOOL_PROFILE",
            help="Use a specific configuration profile (overrides default).",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Preview changes without executing (destructive commands only).",
        ),
    ] = False,
) -> None:
    """dbtool - The operational Swiss Army Knife for database operations.

    A unified CLI tool for database troubleshooting, maintenance, and operations
    across Snowflake, SQL Server, MongoDB, and PostgreSQL.
    """
    # Initialize console
    state.console = _get_console(no_color)
    state.debug = debug or _parse_bool_env("DBTOOL_DEBUG")
    state.quiet = quiet
    state.dry_run = dry_run

    # Setup logging
    _setup_logging(state.debug)
    setup_file_logging(state.debug)

    # Load configuration
    state.config = load_config()

    # Override profile if specified
    if profile:
        state.config.current_profile = profile

    # Apply environment variable overrides to config
    if vault_url := os.getenv("DBTOOL_VAULT_URL"):
        state.config.active_profile.vault.url = vault_url
    if vault_ns := os.getenv("DBTOOL_VAULT_NAMESPACE"):
        state.config.active_profile.vault.namespace = vault_ns

    if state.debug and not state.quiet:
        state.console.print(
            f"[dim]Debug mode enabled. Profile: {state.config.current_profile}[/dim]",
            style="yellow",
        )


# Import and register subcommand modules
from .commands import alert, check, inventory, liquibase, maint, playbook, shell, sql, terraform, vault  # noqa: E402
from .commands import config as config_cmd  # noqa: E402

app.add_typer(vault.app, name="vault", help="Vault secret management.")
app.add_typer(config_cmd.app, name="config", help="Configuration management.")
app.add_typer(check.app, name="health", help="Health checks and diagnostics.")
app.add_typer(alert.app, name="alert", help="Alert triage and analysis.")
app.add_typer(sql.app, name="sql", help="Execute SQL queries.")
app.add_typer(shell.app, name="shell", help="Interactive database shells.")
app.add_typer(maint.app, name="maint", help="Maintenance operations.")
app.add_typer(playbook.app, name="playbook", help="Ansible playbook execution.")
app.add_typer(terraform.app, name="tf", help="Terraform operations.")
app.add_typer(liquibase.app, name="lb", help="Liquibase migrations.")
app.add_typer(inventory.app, name="inventory", help="Database target inventory.")

# Register command aliases
app.add_typer(vault.app, name="vt", help="Alias for vault.", hidden=True)
app.add_typer(config_cmd.app, name="cfg", help="Alias for config.", hidden=True)
app.add_typer(check.app, name="ck", help="Alias for health.", hidden=True)
app.add_typer(shell.app, name="sh", help="Alias for shell.", hidden=True)
app.add_typer(playbook.app, name="pb", help="Alias for playbook.", hidden=True)
app.add_typer(inventory.app, name="inv", help="Alias for inventory.", hidden=True)


def cli() -> None:
    """CLI entry point with error handling."""
    try:
        app()
    except KeyboardInterrupt:
        if state.console:
            state.console.print("\n[yellow]Operation cancelled.[/yellow]")
        sys.exit(ExitCode.GENERAL_ERROR)
    except Exception as e:
        if state.debug:
            raise
        if state.console:
            state.console.print(f"[red]Error: {e}[/red]")
        sys.exit(ExitCode.GENERAL_ERROR)


if __name__ == "__main__":
    cli()
