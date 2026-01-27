"""Configuration management commands.

Provides commands for managing dbtool configuration files and profiles.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

from ..config import get_config_path, load_config
from ..constants import ExitCode
from ._helpers import get_console, is_quiet

app = typer.Typer(no_args_is_help=True)


@app.command(name="list")
def list_config() -> None:
    """List all configuration values."""
    console = get_console()
    config = load_config()

    if is_quiet():
        console.print(f"profile={config.current_profile}")
        console.print(f"vault_url={config.active_profile.vault.url}")
        console.print(f"vault_namespace={config.active_profile.vault.namespace or ''}")
        console.print(f"output_format={config.defaults.output_format}")
        return

    table = Table(title="Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("config_path", str(get_config_path()))
    table.add_row("current_profile", config.current_profile)
    table.add_row("vault_url", config.active_profile.vault.url)
    table.add_row("vault_namespace", config.active_profile.vault.namespace or "(not set)")
    table.add_row("vault_base_path", config.active_profile.vault.base_path)
    table.add_row("output_format", config.defaults.output_format)
    table.add_row("ad_domain", config.auth.ad_domain or "(not set)")

    console.print(table)

    # Show aliases if any
    aliases = config.active_profile.aliases
    if aliases:
        console.print()
        alias_table = Table(title="Vault Aliases")
        alias_table.add_column("Alias", style="cyan")
        alias_table.add_column("Path", style="green")
        for alias, path in aliases.items():
            alias_table.add_row(alias, path)
        console.print(alias_table)


@app.command(name="get")
def get_config(
    key: Annotated[str, typer.Argument(help="Configuration key (e.g., 'vault_url', 'profile').")],
) -> None:
    """Get a specific configuration value."""
    console = get_console()
    config = load_config()

    key_map = {
        "profile": config.current_profile,
        "current_profile": config.current_profile,
        "vault_url": config.active_profile.vault.url,
        "vault_namespace": config.active_profile.vault.namespace or "",
        "vault_base_path": config.active_profile.vault.base_path,
        "output_format": config.defaults.output_format,
        "ad_domain": config.auth.ad_domain,
        "config_path": str(get_config_path()),
    }

    if key in key_map:
        console.print(key_map[key])
    else:
        console.print(f"[red]Unknown configuration key: {key}[/red]")
        console.print(f"Available keys: {', '.join(key_map.keys())}")
        raise typer.Exit(code=ExitCode.INVALID_INPUT)


@app.command(name="set")
def set_config(
    key: Annotated[str, typer.Argument(help="Configuration key to set.")],
    value: Annotated[str, typer.Argument(help="Value to set.")],
) -> None:
    """Set a configuration value.

    Note: This modifies the configuration file. Changes take effect immediately.
    """
    console = get_console()

    # For now, we inform user to edit config manually
    # Full implementation would use save_config()
    config_path = get_config_path()

    console.print(f"[yellow]To set '{key}={value}', edit your config file:[/yellow]")
    console.print(f"  {config_path}")
    console.print()
    console.print("[dim]Example config.toml:[/dim]")
    console.print("""
[auth]
vault_url = "https://vault.example.com"
vault_namespace = "db-ops"

[defaults]
output_format = "table"

[profile.default]
vault_url = "https://vault.example.com"
vault_namespace = "db-ops"

[vault.aliases]
logins = "secret/data/teams/gds/common/logins"
""")


@app.command()
def profiles() -> None:
    """List available configuration profiles."""
    console = get_console()
    config = load_config()

    if is_quiet():
        for name in config.profile:
            marker = "*" if name == config.current_profile else ""
            console.print(f"{marker}{name}")
        return

    table = Table(title="Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Vault URL", style="green")
    table.add_column("Namespace")
    table.add_column("Active", style="yellow")

    for name, profile in config.profile.items():
        active = "* (active)" if name == config.current_profile else ""
        table.add_row(name, profile.vault_url, profile.vault_namespace or "(default)", active)

    console.print(table)


@app.command()
def use(
    profile: Annotated[str, typer.Argument(help="Profile name to activate.")],
) -> None:
    """Switch the active configuration profile.

    Changes apply to subsequent commands in the same session.
    To make permanent, set DBTOOL_PROFILE environment variable.
    """
    console = get_console()
    config = load_config()

    if profile not in config.profile:
        console.print(f"[red]Profile '{profile}' not found.[/red]")
        console.print(f"Available profiles: {', '.join(config.profile.keys())}")
        raise typer.Exit(code=ExitCode.RESOURCE_NOT_FOUND)

    # Update the global state
    from ..main import state

    state.config.current_profile = profile

    if not is_quiet():
        console.print(f"[green]Switched to profile: {profile}[/green]")
        console.print(f"  Vault URL: {config.profile[profile].vault_url}")
        console.print(f"  Namespace: {config.profile[profile].vault_namespace or '(default)'}")


@app.command()
def init() -> None:
    """Initialize configuration file with defaults.

    Creates a new config.toml if it doesn't exist.
    """
    console = get_console()
    config_path = get_config_path()

    if config_path.exists():
        console.print(f"[yellow]Configuration file already exists: {config_path}[/yellow]")
        console.print("Use 'dbtool config list' to view current settings.")
        return

    # Create parent directories
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write default config
    default_config = """# dbtool configuration
# See: docs/projects/dbtool-cli/architecture/technical-architecture.md

[auth]
ad_domain = ""
vault_url = "https://vault.example.com"
# vault_namespace = "db-ops"

[defaults]
output_format = "table"

[profile.default]
vault_url = "https://vault.example.com"
# vault_namespace = "db-ops"

[profile.prod]
vault_url = "https://vault.example.com"
vault_namespace = "db-ops-prod"

[vault.aliases]
# logins = "secret/data/teams/gds/common/logins"
# certs = "secret/data/teams/gds/common/certs"
"""

    config_path.write_text(default_config)

    if not is_quiet():
        console.print(f"[green]Created configuration file: {config_path}[/green]")
        console.print("\nEdit this file to configure your Vault connection and profiles.")
