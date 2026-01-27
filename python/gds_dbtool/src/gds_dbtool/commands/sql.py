"""SQL query execution commands.

Provides commands for executing ad-hoc SQL queries and scripts.
"""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 - needed at runtime for Typer annotation evaluation
from typing import Annotated

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


@app.callback()
def main() -> None:
    """SQL query execution engine."""
    pass


@app.command(name="exec")
def execute(
    target: Annotated[str, typer.Argument(help="Target database (name or connection string).")],
    query: Annotated[
        str | None,
        typer.Argument(help="SQL query to execute."),
    ] = None,
    file: Annotated[
        Path | None,
        typer.Option("--file", "-f", help="SQL script file to execute."),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", help="Output format (table, json, csv, yaml)."),
    ] = "table",
    reason: Annotated[
        str | None,
        typer.Option("--reason", help="Audit reason or ticket ID for this query."),
    ] = None,
) -> None:
    """Execute SQL queries against a database.

    Provide either a query string or a --file with SQL script.
    Authentication is handled automatically via Vault.

    Examples:
        dbtool sql exec prod-db "SELECT 1"
        dbtool sql exec prod-db -f script.sql --format json
        dbtool sql exec prod-db "SELECT * FROM users" --reason "TICKET-123"
    """
    console = _get_console()

    if not query and not file:
        console.print("[red]Provide either a query string or --file.[/red]")
        raise typer.Exit(code=ExitCode.INVALID_INPUT)

    if query and file:
        console.print("[red]Provide either a query string or --file, not both.[/red]")
        raise typer.Exit(code=ExitCode.INVALID_INPUT)

    # Load query from file if specified
    if file:
        if not file.exists():
            console.print(f"[red]File not found: {file}[/red]")
            raise typer.Exit(code=ExitCode.RESOURCE_NOT_FOUND)
        query = file.read_text()

    # Log audit reason if provided
    if reason and not _is_quiet():
        console.print(f"[dim]Audit reason: {reason}[/dim]")

    with console.status(f"[bold green]Executing query on {target}..."):
        # TODO: Implement actual query execution using provider factory
        # 1. Resolve target to connection info
        # 2. Get credentials from Vault
        # 3. Execute query
        # 4. Return results

        # Placeholder results
        columns = ["id", "name", "status"]
        rows = [
            (1, "Alice", "active"),
            (2, "Bob", "inactive"),
            (3, "Charlie", "active"),
        ]

    # Format output
    if format == "json":
        data = [dict(zip(columns, row)) for row in rows]
        console.print_json(data=data)

    elif format == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)
        console.print(output.getvalue())

    elif format == "yaml":
        import yaml

        data = [dict(zip(columns, row)) for row in rows]
        console.print(yaml.dump(data, sort_keys=False))

    elif _is_quiet():
        for row in rows:
            console.print("\t".join(str(v) for v in row))
    else:
        table = Table(title=f"Query Results ({len(rows)} rows)")
        for col in columns:
            table.add_column(col, style="cyan")
        for row in rows:
            table.add_row(*[str(v) for v in row])
        console.print(table)
