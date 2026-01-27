"""Inventory commands.

Provides commands for listing and inspecting known database targets.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table

app = typer.Typer(no_args_is_help=True)


def _get_console():
    """Get console from app state."""
    from ..main import state

    return state.console


def _is_quiet() -> bool:
    """Check if quiet mode is enabled."""
    from ..main import state

    return state.quiet


@app.command(name="list")
def list_targets(
    type: Annotated[
        str | None,
        typer.Option("--type", "-t", help="Filter by database type (postgres, mssql, mongo, snowflake)."),
    ] = None,
) -> None:
    """List all known database targets.

    Displays the inventory of managed database instances.
    Use --type to filter by database engine.

    Examples:
        dbtool inventory list
        dbtool inventory list --type postgres
    """
    console = _get_console()

    with console.status("[bold green]Fetching inventory..."):
        # TODO: Implement actual inventory lookup from config/registry
        targets = [
            {"name": "prod-postgres-01", "type": "postgres", "host": "pg01.example.com", "port": "5432"},
            {"name": "prod-mssql-01", "type": "mssql", "host": "sql01.example.com", "port": "1433"},
            {"name": "staging-mongo-01", "type": "mongo", "host": "mongo01.example.com", "port": "27017"},
            {"name": "analytics-sf", "type": "snowflake", "host": "acme.snowflakecomputing.com", "port": "443"},
        ]

    if type:
        targets = [t for t in targets if t["type"] == type]

    if _is_quiet():
        for t in targets:
            console.print(t["name"])
        return

    table = Table(title="Database Inventory")
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Host", style="green")
    table.add_column("Port")

    for t in targets:
        table.add_row(t["name"], t["type"], t["host"], t["port"])

    console.print(table)


@app.command()
def show(
    target: Annotated[str, typer.Argument(help="Target name to inspect.")],
) -> None:
    """Show details for a specific database target.

    Displays connection info, health status, and metadata for the target.

    Examples:
        dbtool inventory show prod-postgres-01
    """
    console = _get_console()

    with console.status(f"[bold green]Looking up {target}..."):
        # TODO: Implement actual target lookup
        target_info = {
            "name": target,
            "type": "postgres",
            "host": "pg01.example.com",
            "port": "5432",
            "version": "PostgreSQL 16.1",
            "environment": "production",
            "vault_path": "secret/data/databases/prod-postgres-01",
        }

    if _is_quiet():
        for k, v in target_info.items():
            console.print(f"{k}={v}")
        return

    table = Table(title=f"Target: {target}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for k, v in target_info.items():
        table.add_row(k, str(v))

    console.print(table)
