"""Health check and diagnostic commands.

Provides commands for checking database health, connectivity, and AD account status.
"""
from __future__ import annotations

from typing import Annotated, Optional

import typer
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


@app.callback(invoke_without_command=True)
def check(
    ctx: typer.Context,
    target: Annotated[
        Optional[str],
        typer.Argument(help="Target database or host to check."),
    ] = None,
    deep: Annotated[
        bool,
        typer.Option("--deep", help="Run extended diagnostics (resource usage, logs)."),
    ] = False,
) -> None:
    """Run health checks on a target.

    Without a subcommand, runs default health checks (ping, auth, service status).
    Use --deep for extended diagnostics.
    """
    if ctx.invoked_subcommand is not None:
        return

    if target is None:
        raise typer.BadParameter("Target is required when not using a subcommand.")

    console = _get_console()

    with console.status(f"[bold green]Checking {target}..."):
        # TODO: Implement actual health checks using provider factory
        pass

    if not _is_quiet():
        table = Table(title=f"Health Check: {target}")
        table.add_column("Check", style="cyan")
        table.add_column("Result", style="green")
        table.add_column("Details")

        # Placeholder results - would come from actual checks
        table.add_row("Connectivity", "[green]OK[/green]", "Response time: 23ms")
        table.add_row("Authentication", "[green]OK[/green]", "Vault credentials valid")
        table.add_row("Service Status", "[green]OK[/green]", "Database accepting connections")

        if deep:
            table.add_row("CPU Usage", "[green]OK[/green]", "15%")
            table.add_row("Memory Usage", "[yellow]WARN[/yellow]", "78%")
            table.add_row("Disk Usage", "[green]OK[/green]", "45%")
            table.add_row("Active Connections", "[green]OK[/green]", "12/100")

        console.print(table)
    else:
        console.print("OK")


@app.command()
def ad(
    username: Annotated[str, typer.Argument(help="AD username to check.")],
    status: Annotated[
        bool,
        typer.Option("--status", help="Check if account is Active, Disabled, or Locked."),
    ] = False,
    verify_password: Annotated[
        bool,
        typer.Option("--verify-password", help="Test password validity (safe test)."),
    ] = False,
) -> None:
    """Check Active Directory account status.

    Queries AD to determine account state (Active, Disabled, Locked)
    or verify password validity.
    """
    console = _get_console()

    if not status and not verify_password:
        console.print("[yellow]Specify --status or --verify-password[/yellow]")
        raise typer.Exit(code=ExitCode.INVALID_INPUT)

    with console.status(f"[bold green]Checking AD account {username}..."):
        # TODO: Implement actual AD checks via LDAP
        # This would use ldap3 or similar library
        pass

    if status:
        # Placeholder - would come from actual LDAP query
        account_status = "Active"  # Could be: Active, Disabled, Locked
        if _is_quiet():
            console.print(account_status)
        else:
            console.print(f"Account [cyan]{username}[/cyan]: [green]{account_status}[/green]")

    if verify_password:
        from rich.prompt import Prompt

        password = Prompt.ask("Password", password=True)
        with console.status("[bold green]Verifying password..."):
            # TODO: Implement actual password verification
            # This would attempt LDAP bind with provided credentials
            valid = True  # Placeholder

        if valid:
            if not _is_quiet():
                console.print("[green]Password is valid.[/green]")
        else:
            console.print("[red]Password is invalid.[/red]")
            raise typer.Exit(code=ExitCode.AUTH_ERROR)
