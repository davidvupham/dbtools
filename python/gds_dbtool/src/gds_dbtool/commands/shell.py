"""Interactive shell commands.

Provides commands for opening interactive database shells with auto-injected credentials.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ..constants import ExitCode
from ._helpers import get_console, is_quiet

app = typer.Typer(no_args_is_help=True)


@app.callback(invoke_without_command=True)
def shell(
    ctx: typer.Context,
    target: Annotated[str, typer.Argument(help="Target database to connect to.")],
) -> None:
    """Open an interactive database shell.

    Drops you into the native shell (psql, sqlcmd, mongosh) with
    credentials automatically injected from Vault.

    Examples:
        dbtool shell prod-postgres
        dbtool shell dev-mssql
        dbtool shell staging-mongo
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    with console.status(f"[bold green]Connecting to {target}..."):
        # TODO: Implement actual shell connection
        # 1. Resolve target to connection info (host, port, type)
        # 2. Get credentials from Vault
        # 3. Build shell command with credentials
        # 4. Execute shell

        # Placeholder - detect database type and build command
        db_type = "postgres"  # Would come from inventory lookup

    if not is_quiet():
        console.print(f"[green]Connected to {target}[/green]")
        console.print("[dim]Type \\q or exit to disconnect.[/dim]\n")

    # Build shell command based on database type
    if db_type == "postgres":
        # Would include: host, port, user, and PGPASSWORD env var
        shell_cmd = ["psql", "-h", "localhost", "-U", "postgres", "-d", "postgres"]
    elif db_type == "mssql":
        shell_cmd = ["sqlcmd", "-S", "localhost", "-U", "sa"]
    elif db_type == "mongo":
        shell_cmd = ["mongosh", "mongodb://localhost:27017"]
    else:
        console.print(f"[red]Unsupported database type: {db_type}[/red]")
        raise typer.Exit(code=ExitCode.INVALID_INPUT)

    # Execute the shell (placeholder - actual implementation would set credentials)
    console.print(f"[yellow]Would execute: {' '.join(shell_cmd)}[/yellow]")
    console.print("[dim]Shell connection not yet implemented.[/dim]")

    # In actual implementation:
    # env = os.environ.copy()
    # env["PGPASSWORD"] = credentials.password  # For postgres
    # subprocess.run(shell_cmd, env=env)


@app.command()
def login() -> None:
    """Authenticate to Vault (Windows only).

    On Windows, prompts for AD credentials and stores Vault token.
    On Linux, uses Kerberos automatically.
    """
    console = get_console()

    # Redirect to vault login
    console.print("[yellow]Use 'dbtool vault login' instead.[/yellow]")
    raise typer.Exit(code=0)
