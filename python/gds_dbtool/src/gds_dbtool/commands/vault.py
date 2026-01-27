"""Vault interaction commands.

Provides a safe, simplified wrapper around HashiCorp Vault for secret management.
"""

from __future__ import annotations

from typing import Annotated

import hvac
import requests
import typer
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..config import GlobalConfig, load_config, resolve_vault_path
from ..constants import ExitCode
from ..token_store import delete_token, get_token_location, load_token, save_token

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


def _get_vault_client(config: GlobalConfig) -> hvac.Client:
    """Get authenticated Vault client.

    Args:
        config: Global configuration.

    Returns:
        Authenticated hvac.Client.

    Raises:
        typer.Exit: If authentication fails.
    """
    console = _get_console()
    vault_url = config.active_profile.vault.url
    namespace = config.active_profile.vault.namespace

    # Load token from secure storage
    token = load_token()

    client = hvac.Client(url=vault_url, token=token, namespace=namespace)

    if token and not client.is_authenticated():
        if not _is_quiet():
            console.print("[yellow]Stored token is invalid or expired. Please run 'dbtool vault login'.[/yellow]")
        raise typer.Exit(code=ExitCode.AUTH_ERROR)

    if not token:
        if not _is_quiet():
            console.print("[yellow]No token found. Please run 'dbtool vault login'.[/yellow]")
        raise typer.Exit(code=ExitCode.AUTH_ERROR)

    return client


def _parse_mount_and_path(full_path: str) -> tuple[str, str]:
    """Split full path into mount point and sub-path.

    Assumes first component is mount point (e.g. 'secret/foo' -> 'secret', 'foo').

    Args:
        full_path: Full Vault path.

    Returns:
        Tuple of (mount_point, sub_path).
    """
    parts = full_path.split("/", 1)
    if len(parts) < 2:
        return "secret", parts[0]
    return parts[0], parts[1]


@app.command()
def login(
    method: Annotated[
        str,
        typer.Option("--method", "-m", help="Authentication method (saml, ldap, userpass)."),
    ] = "ldap",
    mount_point: Annotated[
        str | None,
        typer.Option("--mount", help="Auth method mount point."),
    ] = None,
    role: Annotated[
        str | None,
        typer.Option("--role", "-r", help="Role name (for saml/approle)."),
    ] = None,
) -> None:
    """Authenticate with Vault.

    Stores the resulting token securely in the system keyring.
    """
    console = _get_console()
    config = load_config()
    vault_url = config.active_profile.vault.url
    namespace = config.active_profile.vault.namespace

    if mount_point is None:
        mount_point = method

    client = hvac.Client(url=vault_url, namespace=namespace)

    if not _is_quiet():
        console.print(f"Authenticating to [bold]{vault_url}[/bold] using [cyan]{method}[/cyan]...")

    try:
        if method == "saml":
            # SAML flow: User must complete authentication in browser
            login_url = f"{vault_url}/ui/vault/auth/{mount_point}/login"
            if role:
                login_url += f"?role={role}"

            console.print("\n[bold]SAML Authentication[/bold]")
            console.print(f"1. Open this URL in your browser: [underline]{login_url}[/underline]")
            console.print("2. Complete authentication")
            console.print("3. Copy the token from the Vault UI")

            token = Prompt.ask("\nEnter the token from your browser")
            client.token = token

        elif method in ("ldap", "userpass"):
            username = Prompt.ask("Username")
            password = Prompt.ask("Password", password=True)

            with console.status(f"[bold green]Authenticating as {username}..."):
                if method == "ldap":
                    client.auth.ldap.login(username=username, password=password, mount_point=mount_point)
                else:
                    client.auth.userpass.login(username=username, password=password, mount_point=mount_point)

        else:
            console.print(f"[red]Authentication method '{method}' not supported.[/red]")
            console.print("Supported methods: saml, ldap, userpass")
            raise typer.Exit(code=ExitCode.INVALID_INPUT)

        if client.is_authenticated():
            save_token(client.token)
            if not _is_quiet():
                console.print(f"[green]Success![/green] Token saved to {get_token_location()}")
        else:
            console.print("[red]Authentication failed.[/red]")
            raise typer.Exit(code=ExitCode.AUTH_ERROR)

    except hvac.exceptions.InvalidRequest as e:
        console.print(f"[red]Authentication failed: {e}[/red]")
        raise typer.Exit(code=ExitCode.AUTH_ERROR) from None
    except requests.exceptions.ConnectionError:
        console.print(f"[red]Connection failed: Unable to reach {vault_url}[/red]")
        raise typer.Exit(code=ExitCode.CONNECTION_ERROR) from None


@app.command()
def logout() -> None:
    """Clear stored Vault token."""
    console = _get_console()
    delete_token()
    if not _is_quiet():
        console.print("[green]Logged out. Token cleared.[/green]")


@app.command(name="list")
def list_secrets(
    path: Annotated[
        str | None,
        typer.Argument(help="Path or alias to list (default: base_path)."),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (table, json)."),
    ] = "table",
) -> None:
    """List secrets at a path."""
    console = _get_console()
    config = load_config()
    client = _get_vault_client(config)

    target_path = resolve_vault_path(config, path)
    mount_point, sub_path = _parse_mount_and_path(target_path)
    display_path = target_path.rstrip("/")

    try:
        with console.status(f"[bold green]Listing secrets at {display_path}..."):
            response = client.secrets.kv.v2.list_secrets(path=sub_path, mount_point=mount_point)
            keys = response.get("data", {}).get("keys", [])

        if output_format == "json":
            console.print_json(data=keys)
        elif _is_quiet():
            for key in keys:
                console.print(key)
        else:
            table = Table(title=f"Secrets in {display_path}")
            table.add_column("Key", style="cyan")
            for key in keys:
                table.add_row(key)
            console.print(table)

    except hvac.exceptions.InvalidPath:
        console.print(f"[yellow]Path not found or empty: {display_path}[/yellow]")
        raise typer.Exit(code=ExitCode.RESOURCE_NOT_FOUND) from None
    except hvac.exceptions.Forbidden:
        console.print(f"[red]Permission denied: {display_path}[/red]")
        raise typer.Exit(code=ExitCode.PERMISSION_DENIED) from None


@app.command(name="get")
def get_secret(
    path: Annotated[str, typer.Argument(help="Path or alias to secret.")],
    key: Annotated[
        str | None,
        typer.Argument(help="Specific key to retrieve (returns raw value)."),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (json, table)."),
    ] = "json",
) -> None:
    """Read a secret.

    If a specific key is provided, outputs only that value (raw string).
    Otherwise, outputs all key-value pairs.
    """
    console = _get_console()
    config = load_config()
    client = _get_vault_client(config)

    full_path = resolve_vault_path(config, path)
    mount_point, sub_path = _parse_mount_and_path(full_path)

    try:
        with console.status("[bold green]Reading secret..."):
            response = client.secrets.kv.v2.read_secret_version(path=sub_path, mount_point=mount_point, raise_on_deleted_version=True)
            data = response.get("data", {}).get("data", {})

        if key:
            if key in data:
                # Output raw value for scripting
                console.print(data[key])
            else:
                console.print(f"[red]Key '{key}' not found in secret.[/red]")
                raise typer.Exit(code=ExitCode.RESOURCE_NOT_FOUND)
        elif output_format == "table":
            table = Table(title=f"Secret: {full_path}")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            for k, v in data.items():
                table.add_row(k, str(v))
            console.print(table)
        else:
            console.print_json(data=data)

    except hvac.exceptions.InvalidPath:
        console.print(f"[red]Secret not found: {full_path}[/red]")
        raise typer.Exit(code=ExitCode.RESOURCE_NOT_FOUND) from None
    except hvac.exceptions.Forbidden:
        console.print(f"[red]Permission denied: {full_path}[/red]")
        raise typer.Exit(code=ExitCode.PERMISSION_DENIED) from None


@app.command()
def put(
    path: Annotated[str, typer.Argument(help="Path or alias to secret.")],
    pairs: Annotated[list[str], typer.Argument(help="Key=Value pairs to write.")],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt."),
    ] = False,
) -> None:
    """Write a secret.

    Creates a new secret or updates an existing one.
    Use --dry-run to preview changes without executing.
    """
    console = _get_console()
    config = load_config()
    dry_run = _is_dry_run()

    full_path = resolve_vault_path(config, path)
    mount_point, sub_path = _parse_mount_and_path(full_path)

    # Parse K=V pairs
    secret_data = {}
    for pair in pairs:
        if "=" not in pair:
            console.print(f"[red]Invalid format '{pair}'. Expected Key=Value.[/red]")
            raise typer.Exit(code=ExitCode.INVALID_INPUT)
        k, v = pair.split("=", 1)
        secret_data[k] = v

    # Show what will be written
    if dry_run or not _is_quiet():
        console.print(f"\n[bold]{'[DRY RUN] ' if dry_run else ''}Writing to {full_path}:[/bold]")
        for k, _v in secret_data.items():
            console.print(f"  {k} = ****")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        return

    client = _get_vault_client(config)

    try:
        # Check if secret exists
        exists = False
        try:
            client.secrets.kv.v2.read_secret_version(path=sub_path, mount_point=mount_point, raise_on_deleted_version=True)
            exists = True
        except hvac.exceptions.InvalidPath:
            pass

        if exists and not force:
            if not Confirm.ask(f"Secret [bold]{full_path}[/bold] exists. Overwrite/Update?"):
                raise typer.Abort()

        with console.status("[bold green]Writing secret..."):
            client.secrets.kv.v2.create_or_update_secret(
                path=sub_path,
                secret=secret_data,
                mount_point=mount_point,
            )

        if not _is_quiet():
            console.print(f"[green]Successfully wrote to {full_path}[/green]")

    except hvac.exceptions.Forbidden:
        console.print(f"[red]Permission denied: {full_path}[/red]")
        raise typer.Exit(code=ExitCode.PERMISSION_DENIED) from None


@app.command(name="delete")
def delete_secret(
    path: Annotated[str, typer.Argument(help="Path or alias to delete.")],
    hard: Annotated[
        bool,
        typer.Option("--hard", help="Permanently destroy (cannot be recovered)."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt."),
    ] = False,
) -> None:
    """Delete a secret.

    By default performs a soft delete (can be recovered).
    Use --hard to permanently destroy the secret and all versions.
    Use --dry-run to preview the operation without executing.
    """
    console = _get_console()
    config = load_config()
    dry_run = _is_dry_run()

    full_path = resolve_vault_path(config, path)
    mount_point, sub_path = _parse_mount_and_path(full_path)

    action = "PERMANENTLY DESTROY" if hard else "delete"

    # Show what will be deleted
    if dry_run:
        console.print(f"\n[bold][DRY RUN] Would {action}:[/bold] {full_path}")
        if hard:
            console.print("[red]This would permanently destroy the secret and all versions.[/red]")
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        return

    if not force:
        if hard:
            console.print("\n[bold red]WARNING: This will PERMANENTLY DESTROY the secret![/bold red]")
            console.print(f"Path: {full_path}")
            console.print("This action cannot be undone.\n")

        if not Confirm.ask(f"Are you sure you want to [bold red]{action}[/bold red] [bold]{full_path}[/bold]?"):
            raise typer.Abort()

    client = _get_vault_client(config)

    try:
        with console.status(f"[bold green]{'Destroying' if hard else 'Deleting'} secret..."):
            if hard:
                client.secrets.kv.v2.delete_metadata_and_all_versions(path=sub_path, mount_point=mount_point)
            else:
                client.secrets.kv.v2.delete_latest_version_of_secret(path=sub_path, mount_point=mount_point)

        if not _is_quiet():
            if hard:
                console.print(f"[green]Permanently destroyed {full_path}[/green]")
            else:
                console.print(f"[green]Deleted {full_path} (can be recovered)[/green]")

    except hvac.exceptions.InvalidPath:
        console.print(f"[red]Secret not found: {full_path}[/red]")
        raise typer.Exit(code=ExitCode.RESOURCE_NOT_FOUND) from None
    except hvac.exceptions.Forbidden:
        console.print(f"[red]Permission denied: {full_path}[/red]")
        raise typer.Exit(code=ExitCode.PERMISSION_DENIED) from None


# Hidden aliases for commands
@app.command(name="ls", hidden=True)
def ls(
    path: Annotated[str | None, typer.Argument()] = None,
    output_format: Annotated[str, typer.Option("--format", "-f")] = "table",
) -> None:
    """Alias for 'list'."""
    list_secrets(path=path, output_format=output_format)


@app.command(name="rm", hidden=True)
def rm(
    path: Annotated[str, typer.Argument()],
    hard: Annotated[bool, typer.Option("--hard")] = False,
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
) -> None:
    """Alias for 'delete'."""
    delete_secret(path=path, hard=hard, force=force)
