"""Ansible playbook execution commands.

Provides a wrapper around ansible-playbook for standardized execution.
"""

from __future__ import annotations

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


def _is_dry_run() -> bool:
    """Check if dry-run mode is enabled."""
    from ..main import state

    return state.dry_run


@app.command()
def run(
    name: Annotated[str, typer.Argument(help="Playbook name to execute.")],
    target: Annotated[str, typer.Argument(help="Target host or group.")],
    extra_vars: Annotated[
        str | None,
        typer.Option("--extra-vars", "-e", help="Extra variables (key=value format)."),
    ] = None,
    reason: Annotated[
        str | None,
        typer.Option("--reason", help="Audit reason or ticket ID."),
    ] = None,
) -> None:
    """Run an Ansible playbook.

    Executes a standardized playbook with Vault credential injection.
    Output is streamed to the console in real-time.

    Use --dry-run to preview the operation (ansible --check mode).

    Examples:
        dbtool playbook run os-patch mssql-01
        dbtool playbook run config-update db-cluster --extra-vars "version=1.2"
    """
    console = _get_console()
    dry_run = _is_dry_run()

    # Validate playbook exists
    available_playbooks = _get_available_playbooks()
    if name not in available_playbooks:
        console.print(f"[red]Playbook '{name}' not found.[/red]")
        console.print(f"Available playbooks: {', '.join(available_playbooks.keys())}")
        raise typer.Exit(code=ExitCode.RESOURCE_NOT_FOUND)

    playbook_info = available_playbooks[name]

    if not _is_quiet():
        console.print(f"\n[bold]Playbook:[/bold] {name}")
        console.print(f"[bold]Target:[/bold] {target}")
        console.print(f"[bold]Description:[/bold] {playbook_info['description']}")
        if extra_vars:
            console.print(f"[bold]Extra vars:[/bold] {extra_vars}")
        if reason:
            console.print(f"[dim]Audit reason: {reason}[/dim]")
        console.print()

    if dry_run:
        console.print("[bold][DRY RUN] Would execute playbook with --check flag[/bold]")
        console.print("[yellow]Dry run - no changes made.[/yellow]")
        return

    # Build ansible-playbook command
    # In real implementation, this would:
    # 1. Resolve playbook path from registry
    # 2. Set up inventory for target
    # 3. Inject Vault credentials via environment or vars file
    # 4. Stream output in real-time

    console.print("[yellow]Playbook execution not yet implemented.[/yellow]")
    console.print("[dim]Would execute: ansible-playbook ... [/dim]")

    # Example of what real execution would look like:
    # cmd = [
    #     "ansible-playbook",
    #     playbook_info["path"],
    #     "-i", f"{target},",
    #     "-l", target,
    # ]
    # if extra_vars:
    #     cmd.extend(["-e", extra_vars])
    # if dry_run:
    #     cmd.append("--check")
    #
    # process = subprocess.Popen(
    #     cmd,
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.STDOUT,
    #     text=True,
    # )
    # for line in process.stdout:
    #     console.print(line, end="")
    # process.wait()


@app.command(name="list")
def list_playbooks() -> None:
    """List available approved playbooks."""
    console = _get_console()

    playbooks = _get_available_playbooks()

    if _is_quiet():
        for name in playbooks:
            console.print(name)
        return

    table = Table(title="Available Playbooks")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Category")

    for name, info in playbooks.items():
        table.add_row(name, info["description"], info.get("category", "general"))

    console.print(table)


def _get_available_playbooks() -> dict:
    """Get list of available playbooks.

    In real implementation, this would read from a registry/config.
    """
    return {
        "os-patch": {
            "description": "Apply OS security patches",
            "category": "maintenance",
            "path": "/opt/ansible/playbooks/os-patch.yml",
        },
        "config-update": {
            "description": "Update database configuration",
            "category": "configuration",
            "path": "/opt/ansible/playbooks/config-update.yml",
        },
        "backup-setup": {
            "description": "Configure automated backups",
            "category": "backup",
            "path": "/opt/ansible/playbooks/backup-setup.yml",
        },
        "monitoring-agent": {
            "description": "Install/update monitoring agent",
            "category": "monitoring",
            "path": "/opt/ansible/playbooks/monitoring-agent.yml",
        },
    }
