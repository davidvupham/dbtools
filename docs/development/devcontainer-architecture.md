# Dev Container Technical Architecture

This document explains how the dbtools dev container works, including lifecycle, components, and security. It complements the functional spec and the developer README.

## Overview

- Base image: `registry.access.redhat.com/ubi9/ubi`
- Python 3.13 is provisioned during `postCreate` via `uv` into a workspace venv at `.venv/` (system `/usr/bin/python3` remains available as fallback).
- System tooling: `msodbcsql18`, `mssql-tools18` (`sqlcmd`), `unixodbc` dev headers
- Multi-repo: parent folder mounted at `/workspaces/devcontainer`, workspace at `/workspaces/devcontainer/dbtools`
- Network: container connects to `devcontainer-network` (created if missing)
- Security: non-root host-aligned user (fallback: `vscode`); read-only SSH key mount; Docker socket mount

## Lifecycle (Sequence)

1. VS Code builds the image from `.devcontainer/Dockerfile`.
2. `initializeCommand` (host): ensure `devcontainer-network` exists.
3. Container starts with `runArgs` (joins shared network).
4. VS Code installs extensions listed in `customizations.vscode.extensions`.
5. `postCreateCommand`:

- Register kernelspec `gds`; tooling is installed from `pyproject.toml` optional dependencies (`.[devcontainer]`) into `.venv/`.
- Append custom prompt to `~/.bashrc`.
- If `ENABLE_JUPYTERLAB=1`, install optional Jupyter packages from `pyproject.toml` (`.[devcontainer-jupyter]`).

1. `postStartCommand`: none (not used).
2. VS Code forwards ports (5432, 1433, 27017, 3000, 5000, 8000, 8888) with labels.

## Diagram

```mermaid
flowchart TD
  subgraph Host
    VS[VS Code + Dev Containers Ext]
    DK[Docker Engine]
    NET[devcontainer-network]
  end

  subgraph Image
    IMG[Red Hat UBI 9 base\n+ ODBC + sqlcmd + PS7]
  end

  subgraph Container[/dbtools dev container/]
    WS[/ /workspaces/devcontainer/dbtools /]
    EXT[VS Code Server + Extensions]
    TOOLS[unixODBC, msodbcsql18, mssql-tools18]
  end

  VS -- build --> IMG
  IMG -- run --> DK
  DK -- create --> Container
  VS -- initializeCommand: create NET --> DK
  DK -- connect to --> NET
  Container -- mount parent --> WS
  VS -- postCreate: kernel registration, optional JupyterLab --> WS
  VS -- install --> EXT
  TOOLS --> Container

```

## Configuration Knobs

- `workspaceMount`: Mounts the parent folder at `/workspaces/devcontainer` for multi-repo workflows.
- `runArgs`: Joins `devcontainer-network` for shared dev DB services.

## Python Versions

The image includes the system Python `/usr/bin/python3`, but the devcontainer is designed to use a repo-local venv at `.venv/`.

- `postCreate` installs `uv`, installs Python `3.13` (default) via `uv`, and creates/updates `.venv/`.
- VS Code is configured to default to `.venv/bin/python`.
- `postCreate` registers the `gds` Jupyter kernel pointing at the active interpreter.
- Override Python version by setting `DEVCONTAINER_PYTHON_VERSION`.

- `containerEnv`:
  - `PIP_DISABLE_PIP_VERSION_CHECK=1` to speed up pip.
  - `ENABLE_JUPYTERLAB=0` (set to `1` to install JupyterLab during postCreate).
- `customizations.vscode.settings`: Sets interpreter path, testing, and linting options.
- `forwardPorts` and `portsAttributes`: Labels for discoverability (Jupyter at 8888).

## Security Considerations

- Non-root host-aligned user for daily operations.
- Minimal mounts: read-only SSH keys, Docker socket (necessary for local DB containers).
- No secrets baked into the image; use environment variables and VS Code tasks for secrets like `MSSQL_SA_PASSWORD`.
- Keep OS packages minimal and clean dnf caches to reduce surface area.

## Verification

- Tasks:
  - MSSQL: Health Check
  - Dev: Verify SQL Server (sqlcmd + pyodbc)
  - Dev: Verify pyodbc
  - Docs: Markdown Lint (Docker)
- Manual:
  - `sqlcmd -S localhost -U SA -P "$MSSQL_SA_PASSWORD" -Q "SELECT @@VERSION"`
  - `python -c "import pyodbc; print(pyodbc.drivers())"`

## Rebuild & Verify

To apply changes and validate the environment:

1. Rebuild the dev container:

```bash
Dev Containers: Rebuild and Reopen in Container
```

1. Run verification tasks:

- Dev: Verify Dev Container
- Dev: Verify pyodbc
- Dev: Verify SQL Server (sqlcmd + pyodbc)

CLI alternative:

```bash
make verify-devcontainer
```

## Related Documents

- Functional spec: [docs/development/devcontainer-functional-spec.md](devcontainer-functional-spec.md)
- Developer guide: [docs/development/devcontainer.md](devcontainer.md)
- Container config: [.devcontainer/devcontainer.json](../../.devcontainer/devcontainer.json)
- Dockerfile: [.devcontainer/Dockerfile](../../.devcontainer/Dockerfile)
