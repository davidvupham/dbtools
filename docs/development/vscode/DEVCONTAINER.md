# Dev Container Setup

This repository includes a VS Code Dev Container to provide a reproducible Miniconda-based Python environment.

## What you get

- Base image: Microsoft Dev Containers Miniconda (`mcr.microsoft.com/devcontainers/miniconda:latest`)
- Conda environment: `gds` with Python 3.13
- Auto-activation of `gds` for interactive shells
- **PowerShell 7+** with database administration modules (dbatools, Pester, PSFramework)
- Python extensions preinstalled (Python, Pylance, Jupyter, Ruff, Docker)
- Python tools: ruff, pytest, pytest-cov, wheel, build, pyodbc
- Post-create command installs local editable packages: gds_database, gds_postgres, gds_snowflake, gds_vault, gds_mongodb, gds_mssql, gds_notification, gds_snmp_receiver
- Docker-in-Docker support for container operations
- SSH key mounting for Git authentication
- Pre-commit hooks setup (if configured)
- ODBC support: unixODBC and development libraries

For a step-by-step beginner's walkthrough (what Docker is, how the Dockerfile and devcontainer.json work, and how to build/run), see:
- `devcontainer-beginners-guide.md`

## Open in Dev Container

1. Ensure you have the "Dev Containers" extension installed.
2. Open this folder in VS Code.
3. When prompted, "Reopen in Container".
   - Or run: Command Palette → Dev Containers: Rebuild and Reopen in Container

## Notes

- Default interpreter is `/opt/conda/envs/gds/bin/python`
- To verify Python setup:
  ```bash
  python -V
  which python
  conda env list
  ```
- To verify PowerShell setup:
  ```bash
  pwsh -version
  pwsh -NoProfile -Command "Get-Module -ListAvailable dbatools,Pester,PSFramework"
  ```
- To verify installed packages:
  ```bash
  python -c "import gds_database, gds_postgres, gds_snowflake, gds_vault, gds_mongodb, gds_mssql, gds_notification, gds_snmp_receiver; print('All packages OK')"
  ```
- Update the `postCreateCommand` in `.devcontainer/devcontainer.json` if you want to customize package installs.

### Kerberos configuration (optional)

- A template is provided at `.devcontainer/krb5/krb5.conf`. Edit this file to set your REALM and KDC.
- **Note:** Kerberos is not currently configured in the devcontainer.json. To enable it, add the mount and environment variable as described in `devcontainer-beginners-guide.md`.
- To acquire a ticket (once configured):
  ```bash
  kinit user@EXAMPLE.COM
  klist
  ```
  Replace realm and KDC to match your environment.
