"""Alert triage commands.

Provides commands for analyzing and triaging database alerts.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ..constants import ExitCode

app = typer.Typer(no_args_is_help=True)


def _get_console():
    """Get console from app state."""
    from ..main import state

    return state.console


@app.command()
def triage(
    alert_id: Annotated[
        str | None,
        typer.Argument(help="ID of the alert to triage."),
    ] = None,
    target: Annotated[
        str | None,
        typer.Option("--target", help="Target host or database."),
    ] = None,
    type: Annotated[  # noqa: ARG001
        str | None,
        typer.Option("--type", help="Type of alert (blocking, long-query, etc)."),
    ] = None,
) -> None:
    """Triage a database alert.

    Analyzes the alert context and runs relevant diagnostics.
    """
    console = _get_console()

    if not alert_id and not target:
        console.print("[red]Provide either an ALERT_ID or --target.[/red]")
        raise typer.Exit(code=ExitCode.INVALID_INPUT)

    with console.status("[bold green]Triaging alert..."):
        # TODO: Implement alert triage logic
        pass

    console.print(f"[green]Triage complete for {alert_id or target}[/green]")
