# Dev Container Setup

This repository includes a VS Code Dev Container to provide a reproducible Python development environment based on Red Hat UBI 9.

## What you get

- Base image: Red Hat UBI 9 (`registry.access.redhat.com/ubi9/ubi`)
- Python: `.venv/` provisioned during `postCreate` via `uv` (default Python `3.14`; system `/usr/bin/python3` remains available)
- Dynamic user: Container user matches your host user via `${localEnv:USER}`
- **PowerShell 7+** for database/automation scripts
- **SQL Server tools**: `msodbcsql18`, `mssql-tools18` (`sqlcmd`)
- **ODBC support**: `unixODBC` and development headers
- Python extensions preinstalled (Python, Pylance, Jupyter, Ruff, Docker)
- Python tools installed via `pyproject.toml` optional deps: `.[devcontainer]`
- Post-create command installs local editable packages: gds_database, gds_postgres, gds_mssql, gds_mongodb, gds_liquibase, gds_vault, gds_snowflake, gds_snmp_receiver
- Docker CLI access via host socket mount
- SSH key mounting for Git authentication (read-only)
- Multi-repo support: parent folder mounted at `/workspaces/devcontainer`

For detailed documentation, see:

- Developer guide: [docs/development/devcontainer.md](../devcontainer.md)
- Functional spec: [docs/development/devcontainer-functional-spec.md](../devcontainer-functional-spec.md)
- Technical architecture: [docs/development/devcontainer-architecture.md](../devcontainer-architecture.md)
- Beginner's walkthrough: [devcontainer-beginners-guide.md](devcontainer-beginners-guide.md)

## Open in Dev Container

1. Ensure you have the "Dev Containers" extension installed.
2. Open this folder in VS Code.
3. When prompted, "Reopen in Container".
   - Or run: Command Palette → Dev Containers: Rebuild and Reopen in Container

## Notes

- Default interpreter is `.venv/bin/python`

### Troubleshooting

If Python still shows the old version after a devcontainer rebuild, you likely have a stale `.venv/` directory from a previous setup. Delete it and rebuild the dev container so `postCreate` can reprovision it:

```bash
rm -rf .venv
```

- To verify Python setup:

  ```bash
  python -V
  which python
  ```

- To verify PowerShell setup:

  ```bash
  pwsh -version
  pwsh -NoProfile -Command "Get-Module -ListAvailable"
  ```

- To verify SQL Server tools:

  ```bash
  sqlcmd -?
  odbcinst -q -d
  ```

- To verify installed packages:

  ```bash
  python -c "import gds_database, gds_postgres, gds_mssql; print('Packages OK')"
  ```

- Update `.devcontainer/devcontainer.json` or `.devcontainer/postCreate.sh` if you want to customize the setup.

### Kerberos configuration (optional)

- A template is provided at `.devcontainer/krb5/krb5.conf`. Edit this file to set your REALM and KDC.
- **Note:** Kerberos is not currently configured in the devcontainer.json. To enable it, add the mount and environment variable as described in [devcontainer-beginners-guide.md](devcontainer-beginners-guide.md).
- To acquire a ticket (once configured):

  ```bash
  kinit user@EXAMPLE.COM
  klist
  ```
