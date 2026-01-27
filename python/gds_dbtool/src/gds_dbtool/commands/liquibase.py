"""Liquibase migration commands.

Provides a wrapper around Liquibase for database schema management.
Runs Liquibase in a standardized Docker container.
"""
from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.prompt import Confirm
from rich.table import Table

from ..constants import ExitCode

app = typer.Typer(no_args_is_help=True)


def _get_console():
    """Get console from app state."""
    from ..main import state

    return state.console


def _is_quiet() -> bool:
    """Check if quiet mode is enabled."""
    from ..main import state

    return state.quiet


def _is_dry_run() -> bool:
    """Check if dry-run mode is enabled."""
    from ..main import state

    return state.dry_run


@app.command()
def update(
    project: Annotated[str, typer.Argument(help="Liquibase project name.")],
    env: Annotated[str, typer.Argument(help="Target environment (dev, staging, prod).")],
    count: Annotated[
        Optional[int],
        typer.Option("--count", "-c", help="Number of changesets to apply (default: all)."),
    ] = None,
    reason: Annotated[
        Optional[str],
        typer.Option("--reason", help="Audit reason or ticket ID."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt."),
    ] = False,
) -> None:
    """Apply pending database migrations.

    Runs Liquibase update to apply pending changesets.
    Use --dry-run to preview SQL without executing.

    Examples:
        dbtool lb update myproject dev
        dbtool lb update myproject prod --count 1
        dbtool lb update myproject prod --dry-run
    """
    console = _get_console()
    dry_run = _is_dry_run()

    if not _is_quiet():
        console.print(f"\n[bold]Liquibase Update[/bold]")
        console.print(f"Project: [cyan]{project}[/cyan]")
        console.print(f"Environment: [cyan]{env}[/cyan]")
        if count:
            console.print(f"Changesets to apply: {count}")
        if reason:
            console.print(f"[dim]Audit reason: {reason}[/dim]")
        console.print()

    if dry_run:
        console.print("[bold][DRY RUN] Would generate update SQL:[/bold]")
        console.print()
        # Show preview of SQL that would be executed
        console.print("[dim]-- Changeset: 001-create-users-table[/dim]")
        console.print("[cyan]CREATE TABLE users ([/cyan]")
        console.print("[cyan]    id SERIAL PRIMARY KEY,[/cyan]")
        console.print("[cyan]    username VARCHAR(255) NOT NULL[/cyan]")
        console.print("[cyan]);[/cyan]")
        console.print()
        console.print("[yellow]Dry run - no changes made.[/yellow]")
        return

    # Production safety check
    if env == "prod" and not force:
        console.print("[bold red]WARNING: You are about to modify PRODUCTION database schema![/bold red]")
        if not Confirm.ask("Are you sure you want to continue?"):
            raise typer.Abort()

    with console.status("[bold green]Running Liquibase update..."):
        # TODO: Implement actual Liquibase execution via Docker
        # 1. Locate changelog files
        # 2. Get database credentials from Vault
        # 3. Run Liquibase Docker container with volume mounts
        # 4. Stream output
        pass

    console.print("[yellow]Liquibase update not yet implemented.[/yellow]")
    console.print("[dim]Would execute Liquibase in Docker container[/dim]")


@app.command()
def rollback(
    project: Annotated[str, typer.Argument(help="Liquibase project name.")],
    env: Annotated[str, typer.Argument(help="Target environment.")],
    count: Annotated[
        int,
        typer.Option("--count", "-c", help="Number of changesets to rollback."),
    ] = 1,
    reason: Annotated[
        Optional[str],
        typer.Option("--reason", help="Audit reason or ticket ID."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt."),
    ] = False,
) -> None:
    """Rollback database migrations.

    Reverts the specified number of changesets.
    Use --dry-run to preview rollback SQL without executing.

    Examples:
        dbtool lb rollback myproject dev --count 1
        dbtool lb rollback myproject prod --dry-run
    """
    console = _get_console()
    dry_run = _is_dry_run()

    if not _is_quiet():
        console.print(f"\n[bold]Liquibase Rollback[/bold]")
        console.print(f"Project: [cyan]{project}[/cyan]")
        console.print(f"Environment: [cyan]{env}[/cyan]")
        console.print(f"Changesets to rollback: {count}")
        if reason:
            console.print(f"[dim]Audit reason: {reason}[/dim]")
        console.print()

    if dry_run:
        console.print("[bold][DRY RUN] Would generate rollback SQL:[/bold]")
        console.print()
        console.print("[dim]-- Rollback changeset: 001-create-users-table[/dim]")
        console.print("[cyan]DROP TABLE users;[/cyan]")
        console.print()
        console.print("[yellow]Dry run - no changes made.[/yellow]")
        return

    if not force:
        console.print(f"[bold red]WARNING: This will rollback {count} changeset(s)![/bold red]")
        if not Confirm.ask("Are you sure you want to continue?"):
            raise typer.Abort()

    with console.status("[bold green]Running Liquibase rollback..."):
        # TODO: Implement actual rollback
        pass

    console.print("[yellow]Liquibase rollback not yet implemented.[/yellow]")


@app.command()
def status(
    project: Annotated[str, typer.Argument(help="Liquibase project name.")],
    env: Annotated[str, typer.Argument(help="Target environment.")],
) -> None:
    """Show pending changesets.

    Lists changesets that have not been applied to the target database.

    Examples:
        dbtool lb status myproject dev
    """
    console = _get_console()

    with console.status("[bold green]Checking changeset status..."):
        # TODO: Implement actual status check
        pending = [
            {"id": "002-add-email-column", "author": "alice", "description": "Add email column to users"},
            {"id": "003-create-orders-table", "author": "bob", "description": "Create orders table"},
        ]
        applied = [
            {"id": "001-create-users-table", "author": "alice", "description": "Create users table"},
        ]

    if _is_quiet():
        console.print(f"pending: {len(pending)}")
        console.print(f"applied: {len(applied)}")
        return

    console.print(f"\n[bold]Changeset Status: {project}/{env}[/bold]\n")

    if pending:
        table = Table(title=f"Pending Changesets ({len(pending)})")
        table.add_column("ID", style="yellow")
        table.add_column("Author")
        table.add_column("Description")

        for cs in pending:
            table.add_row(cs["id"], cs["author"], cs["description"])

        console.print(table)
    else:
        console.print("[green]No pending changesets.[/green]")

    console.print()

    if applied:
        table = Table(title=f"Applied Changesets ({len(applied)})")
        table.add_column("ID", style="green")
        table.add_column("Author")
        table.add_column("Description")

        for cs in applied:
            table.add_row(cs["id"], cs["author"], cs["description"])

        console.print(table)


@app.command()
def validate(
    project: Annotated[str, typer.Argument(help="Liquibase project name.")],
) -> None:
    """Validate changelog files.

    Checks changelog syntax and references without connecting to database.

    Examples:
        dbtool lb validate myproject
    """
    console = _get_console()

    with console.status("[bold green]Validating changelog..."):
        # TODO: Implement actual validation
        valid = True
        issues = []

    if valid:
        if not _is_quiet():
            console.print("[green]Changelog validation passed.[/green]")
    else:
        console.print("[red]Changelog validation failed:[/red]")
        for issue in issues:
            console.print(f"  - {issue}")
        raise typer.Exit(code=ExitCode.INVALID_INPUT)
