# Dev Container Technical Architecture

This document explains how the dbtools dev container works, including lifecycle, components, and security. It complements the functional spec and the developer README.

## Overview

- Base image: `registry.access.redhat.com/ubi9/ubi`
- Python via `venv` in `.venv`; VS Code uses `/workspaces/dbtools/.venv/bin/python`
- System tooling: `msodbcsql18`, `mssql-tools18` (`sqlcmd`), `unixodbc` dev headers, PowerShell 7
- Multi-repo: parent folder mounted at `/workspaces`, workspace at `/workspaces/dbtools`
- Network: container connects to `devcontainer-network` (created if missing)
- Security: non-root `vscode` user; read-only SSH key mount; Docker socket mount

## Lifecycle (Sequence)

1. VS Code builds the image from `.devcontainer/Dockerfile`.
2. `initializeCommand` (host): ensure `devcontainer-network` exists.
3. Container starts with `runArgs` (joins shared network).
4. VS Code installs extensions listed in `customizations.vscode.extensions`.
5. `postCreateCommand`:
   - Create `.venv`, upgrade pip, install dev tools and `pyodbc`.
   - Install `ipykernel`; register kernelspec `gds` (Python (gds)).
   - If `ENABLE_JUPYTERLAB=1`, install JupyterLab.
6. `postStartCommand` (each start): ensure VS Code server dirs; install local packages in editable mode.
7. VS Code forwards ports (5432, 1433, 27017, 3000, 5000, 8000, 8888) with labels.

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
    WS[/ /workspaces/dbtools /]
    VENV[.venv Python env]
    EXT[VS Code Server + Extensions]
    TOOLS[unixODBC, msodbcsql18, mssql-tools18]
    PWSH[PowerShell 7]
  end

  VS -- build --> IMG
  IMG -- run --> DK
  DK -- create --> Container
  VS -- initializeCommand: create NET --> DK
  DK -- connect to --> NET
  Container -- mount parent --> WS
  VS -- postCreate: venv, ipykernel, optional JupyterLab --> VENV
  VS -- install --> EXT
  TOOLS --> Container
  PWSH --> Container

```

## Configuration Knobs

- `workspaceMount`: Mounts the parent folder at `/workspaces` for multi-repo workflows.
- `runArgs`: Joins `devcontainer-network` for shared dev DB services.

## Python Versions (Pyenv Optional)

The base uses system `python3` on UBI 9. To use Python 3.14, the Dockerfile supports a guarded pyenv path controlled via build args:

- `USE_PYENV`: `0` (default) disables pyenv; `1` enables pyenv installation.
- `PYENV_PYTHON_VERSION`: desired version (e.g., `3.14.0`).

When enabled, pyenv installs the specified Python and sets it as global. The devcontainer `postCreateCommand` builds `.venv` from whichever `python3` is active (pyenv when enabled, system otherwise).

- `containerEnv`:
  - `PIP_DISABLE_PIP_VERSION_CHECK=1` to speed up pip.
  - `ENABLE_JUPYTERLAB=0` (set to `1` to install JupyterLab during postCreate).
- `customizations.vscode.settings`: Sets interpreter path, testing, and linting options.
- `forwardPorts` and `portsAttributes`: Labels for discoverability (Jupyter at 8888).

## Security Considerations

- Non-root host-aligned user for daily operations.
- Minimal mounts: read-only SSH keys, Docker socket (necessary for local DB containers).
- No secrets baked into the image; use environment variables and VS Code tasks for secrets like `MSSQL_SA_PASSWORD`.
- Keep apt packages minimal and clean cache to reduce surface area.

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

2. Run verification tasks:

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
