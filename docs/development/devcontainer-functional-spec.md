# Dev Container Functional & Architecture Spec

Status: Implemented (Red Hat UBI 9 base). Legacy cleanup/removals pending approval. See [Technical Architecture](devcontainer-architecture.md) for a visual model.

## Goals & Non‑Goals

- **Goals:**
  - Small image (no Miniconda); use Python `venv`.
  - Support multi‑repo development via parent folder mount.
  - Provide reliable SQL Server tooling (`msodbcsql18`, `sqlcmd`) and `pyodbc`.
  - Docker access via host socket; shared network for local services.
  - Clear lifecycle (`postCreate`, `postStart`), consistent VS Code settings.
  - Security: non‑root user, minimal mounts, no secrets baked in image.
- **Non‑Goals:**
  - Cloud deployment tooling or runtime provisioning.
  - Language runtimes beyond Python.

## Architecture Overview

- **Base Image:** `registry.access.redhat.com/ubi9/ubi` (corporate-aligned Red Hat UBI 9).
- **Python Runtime:** System `python3` with `python3-venv`; workspace `.venv` created on `postCreate`.
- **Workspace Layout:** Parent directory bind‑mounted to `/workspaces`, opening `/workspaces/dbtools`; sibling repos are accessible for editable installs.
- **System Tooling:** `unixODBC`/`unixODBC-devel`, `msodbcsql18`, `mssql-tools18` (`sqlcmd`), `powershell` (PS7), and core build tools.
- **Install Method:** `microdnf`/`dnf` for OS packages; Microsoft RHEL 9 RPM repo for SQL Server tooling.
- **Docker Access:** Mount `/var/run/docker.sock` (Docker Outside‑of‑Docker); no daemon inside container.
 **Networking:** Ensure `devcontainer-network` exists (host initialize); container joins for name‑based connectivity to local services.
 **User & Permissions:** Non‑root user aligned to host via build args; host SSH keys mounted read‑only for Git.
 **Ports & Forwarding:** VS Code forwards 5432, 1433, 27017, 3000, 5000, 8000, 8888 (Jupyter). Labels defined for discoverability.
 **Python Runtime:** System `python3` with `python3-venv`; workspace `.venv` created on `postCreate`. Optional guarded pyenv path to install Python 3.14 via build args (`USE_PYENV=1`, `PYENV_PYTHON_VERSION=3.14.0`).
- **Container Env Flags:** `PIP_DISABLE_PIP_VERSION_CHECK=1` (faster pip); `ENABLE_JUPYTERLAB=0` by default (opt-in install during postCreate).
  - `initializeCommand`: create `devcontainer-network` on host.

## Detailed Components

- **Container Image Build:**
  - Single consolidated `microdnf`/`dnf` `RUN` to install base tooling, add Microsoft RHEL 9 repo, and install SQL Server packages and PowerShell.
  - Clean package caches to keep the image small.
  - Symlink `sqlcmd` into PATH for convenience.
- **Python Environment:**
  - `postCreate`: `python3 -m venv .venv`, upgrade `pip`, install base dev tools (e.g., `ruff`, `pytest`, `pytest-cov`, `pyright`, `pyodbc`).
  - VS Code setting `python.defaultInterpreterPath` points to `/workspaces/dbtools/.venv/bin/python`.
  - Jupyter support: installs `ipykernel` and registers kernelspec `gds` ("Python (gds)"). If `ENABLE_JUPYTERLAB=1`, installs JupyterLab during `postCreate`.
- **Multi‑Repo Workflow:**
  - `workspaceMount: source=${localWorkspaceFolder}/..,target=/workspaces,type=bind`.
  - Optional script to clone additional repos: see [.devcontainer/scripts/clone-additional-repos.sh](../../.devcontainer/scripts/clone-additional-repos.sh) using [.devcontainer/additional-repos.json](../../.devcontainer/additional-repos.json).
- **Lifecycle:**
  - `initializeCommand`: create `devcontainer-network` on host.
  - `postCreate`: bootstrap venv and base packages; installs `ipykernel` and registers kernel; optional JupyterLab if enabled.
  - `postStart`: optional editable installs across sibling repos; VS Code server directory sanity (kept minimal).
- **Security & Compliance:**
  - Least privilege (non‑root), minimal mounts (SSH RO; Docker socket only), no embedded secrets.
  - Use environment variables or VS Code tasks to prompt for sensitive values; avoid baking secrets in image.
- **Image Optimization:**
  - Consolidated apt operations; minimal package set; defer heavy Python deps to `postCreate` to avoid increasing build layers.

## Verification & Tasks

- **Built‑in tasks:** "MSSQL: Health Check", "Dev: Verify SQL Server (sqlcmd + pyodbc)", "Dev: Verify pyodbc" (see workspace tasks).
- **Manual checks:**
  - `sqlcmd -S localhost -U SA -P "$MSSQL_SA_PASSWORD" -Q "SELECT @@VERSION"`
  - `python -c "import pyodbc; print(pyodbc.drivers())"`

Additional utility task:

- "Docs: Markdown Lint (Docker)" for validating docs formatting under `docs/`.

## Rebuild & Verify

Apply changes and run the verification suite:

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

## Migration Plan (Conda → venv)

- **Phase 1 (Planning):** Adopt venv‑based devcontainer without removing existing files; draft removal plan.
- **Phase 2 (Execution after approval):** Enable venv devcontainer; remove legacy Conda variant and unused troubleshooting/variant sync artifacts.
- **Phase 3 (Post‑migration):** Update docs and ensure tasks/scripts no longer assume Conda activation.

## `postCreate.sh` Behavior (Extracted Summary)

File: [.devcontainer/postCreate.sh](../../.devcontainer/postCreate.sh)

- **Environment checks:** Logs Python and pip versions; verifies Docker daemon reachability.
- **Jupyter kernel:** Registers kernelspec `gds` ("Python (gds)") after installing `ipykernel` during `postCreate`.
- **Editable installs:** Installs local packages in editable mode (tries `[dev]` extras first) for: `gds_database`, `gds_postgres`, `gds_snowflake`, `gds_vault`, `gds_mongodb`, `gds_mssql`, `gds_notification`, `gds_snmp_receiver`.
- **pre‑commit hooks:** If `.pre-commit-config.yaml` exists and `pre-commit` is available, installs hooks.
- **pyodbc verification:**
  - Checks if `pyodbc` imports; if not, ensures Microsoft repo and installs `msodbcsql18`, `unixodbc-dev` as needed.
  - Upgrades `pip`/`setuptools`/`wheel`, attempts `pyodbc` install (site, falls back to `--user`).
  - Prints `pyodbc` version and filtered ODBC drivers.
- **Conda auto‑activation (legacy):** If Conda exists and `gds` env present, tries installing `pyodbc` there and appends Conda activation to `~/.bashrc`.
- **Base interpreter fallback:** If `/opt/conda/bin/python` exists, attempts `pyodbc` install there as well.

Observation: Much of the script is Conda‑specific fallback logic; in the venv design, we keep editable installs and `pyodbc` verification and will drop Conda activation/install paths.

## Legacy Cleanup (Completed)

Removed legacy or unused items tied to prior Conda-based variants and troubleshooting artifacts:

- Conda Ubuntu variant: `.devcontainer/ubuntu/` (Dockerfile and `devcontainer.json`)
- Red Hat variant directory: `.devcontainer/redhat/`
- Variant management scripts: `.devcontainer/switch-variant.sh`, `.devcontainer/scripts/sync_devcontainers.py`, `.devcontainer/scripts/sync-devcontainers.sh`
- Troubleshooting artifacts: `.devcontainer/troubleshooting/`

Items retained:

- Active devcontainer files: `.devcontainer/devcontainer.json`, `.devcontainer/Dockerfile`
- Repo cloning: `.devcontainer/additional-repos.json` (optional), `.devcontainer/scripts/clone-additional-repos.sh`
- postCreate lifecycle: `.devcontainer/postCreate.sh` — slated to remain venv‑only; Conda fallbacks removed in documentation and will be pruned as needed.

## Open Questions

- **PowerShell:** Retain by default or make optional to slim the image? (Currently retained by default.)
- **Jupyter:** Keep `ipykernel` by default; JupyterLab via opt-in flag `ENABLE_JUPYTERLAB=1` during `postCreate` (current behavior).
- **DB tooling:** Keep SQLTools PostgreSQL driver or trim to MSSQL‑only?
- **PostgreSQL client libs:** Any need for `libpq-dev`/`psql`?

## Next Steps

- Review and approve the spec and the removal plan.
- Once approved, I will:
  - Simplify `postCreate.sh` to venv‑only flows.
  - Remove the listed legacy `.devcontainer` files.
  - Rebuild the dev container and run verification tasks.
