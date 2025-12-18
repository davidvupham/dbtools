# Dev Container Functional & Architecture Spec

Status: Implemented (Red Hat UBI 9 base). Legacy cleanup/removals pending approval. See [Technical Architecture](devcontainer-architecture.md) for a visual model.

## Goals & Non‑Goals

- **Goals:**
  - Small image; keep system Python available but use a workspace venv for tooling.
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
- **Python Runtime:** workspace venv at `.venv/` provisioned during `postCreate` via `uv` (default Python `3.14`). System `/usr/bin/python3` remains available as a fallback.
- **Workspace Layout:** Parent directory bind-mounted to `/workspaces/devcontainer`, opening `/workspaces/devcontainer/dbtools`; sibling repos are accessible for editable installs.
- **System Tooling:** `unixODBC`/`unixODBC-devel`, `msodbcsql18`, `mssql-tools18` (`sqlcmd`), `powershell` (PS7), and core build tools.
- **Install Method:** `microdnf`/`dnf` for OS packages; Microsoft RHEL 9 RPM repo for SQL Server tooling.
- **Networking:** Ensure `devcontainer-network` exists (host initialize); container joins for name‑based connectivity to local services.
- **Ports & Forwarding:** VS Code forwards 5432, 1433, 27017, 3000, 5000, 8000, 8888 (Jupyter). Labels defined for discoverability.
- **Container Env Flags:** `PIP_DISABLE_PIP_VERSION_CHECK=1` (faster pip); `ENABLE_JUPYTERLAB=0` by default (opt-in install during postCreate).
- `initializeCommand`: create `devcontainer-network` on host.

## Detailed Components

- **Container Image Build:**
  - Single consolidated `microdnf`/`dnf` `RUN` to install base tooling, add Microsoft RHEL 9 repo, and install SQL Server packages and PowerShell.
  - Clean package caches to keep the image small.
  - Symlink `sqlcmd` into PATH for convenience.
  - **Python Environment:**
    - `postCreate`: installs `uv`, installs Python `3.14` via `uv`, creates/updates `.venv/`, installs dev tools + editable local packages into the venv, and registers the `gds` kernelspec pointing at the venv.
    - VS Code setting `python.defaultInterpreterPath` points to `/workspaces/devcontainer/dbtools/.venv/bin/python`.
    - Override: set `DEVCONTAINER_PYTHON_VERSION` to change the version `uv` installs.
  - **Multi‑Repo Workflow:**
    - `workspaceMount: source=${localWorkspaceFolder}/..,target=/workspaces/devcontainer,type=bind`.
  - Optional script to clone additional repos: see [.devcontainer/scripts/clone-additional-repos.sh](../../.devcontainer/scripts/clone-additional-repos.sh) using [.devcontainer/additional-repos.json](../../.devcontainer/additional-repos.json).
  - **Lifecycle:**
    - `initializeCommand`: create `devcontainer-network` on host.
    - `postCreate`: installs `uv`, provisions Python, creates/updates `.venv/`, installs tooling from `pyproject.toml` optional dependencies (`.[devcontainer]`), installs local packages in editable mode, registers kernel; optional JupyterLab if enabled.
    - `postStart`: not used (kept empty).
- **Security & Compliance:**
  - Least privilege (non‑root), minimal mounts (SSH RO; Docker socket only), no embedded secrets.
  - Use environment variables or VS Code tasks to prompt for sensitive values; avoid baking secrets in image.
- **Image Optimization:**
  - Consolidated dnf/microdnf operations; minimal package set; defer heavy Python deps to `postCreate` to avoid increasing build layers.

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

1. Run verification tasks:

- Dev: Verify Dev Container
- Dev: Verify pyodbc
- Dev: Verify SQL Server (sqlcmd + pyodbc)

CLI alternative:

```bash
make verify-devcontainer
```

## Migration Plan (legacy → venv)

- **Phase 1 (Planning):** Adopt venv‑based devcontainer without removing existing files; draft removal plan.
- **Phase 2 (Execution after approval):** Enable venv devcontainer; remove legacy variant and unused troubleshooting/variant sync artifacts.
- **Phase 3 (Post‑migration):** Update docs and ensure tasks/scripts no longer assume legacy activation.

## `postCreate.sh` Behavior (Extracted Summary)

File: [.devcontainer/postCreate.sh](../../.devcontainer/postCreate.sh)

- **Environment checks:** Logs Python/pip versions; verifies Docker daemon reachability.
- **Venv lifecycle:** Creates/uses `.venv/` (default Python `3.14`) via `uv`; falls back to system Python if provisioning fails.
- **Prompt:** Appends a git-branch-aware prompt directly into `~/.bashrc` (no `~/.set_prompt` dependency; `$` on its own line).
- **Jupyter kernel:** Registers kernelspec `gds` ("Python (gds)") pointing at the venv interpreter.
- **Editable installs:** Installs local packages in editable mode (prefers `[dev]` extras) for: `gds_database`, `gds_postgres`, `gds_mssql`, `gds_mongodb`, `gds_liquibase`, `gds_vault`, `gds_snowflake`, `gds_snmp_receiver`.
- **pre-commit hooks:** If `.pre-commit-config.yaml` exists and `pre-commit` is available, installs hooks.
- **pyodbc verification:** Pure import/driver check; prints version and drivers. No OS package installs or other fallbacks.

## Legacy Cleanup (Completed)

Removed legacy or unused items tied to prior variants and troubleshooting artifacts:

- Ubuntu legacy variant: `.devcontainer/ubuntu/` (Dockerfile and `devcontainer.json`)
- Red Hat variant directory: `.devcontainer/redhat/`
- Variant management scripts: `.devcontainer/switch-variant.sh`, `.devcontainer/scripts/sync_devcontainers.py`, `.devcontainer/scripts/sync-devcontainers.sh`
- Troubleshooting artifacts: `.devcontainer/troubleshooting/`

Items retained:

- Active devcontainer files: `.devcontainer/devcontainer.json`, `.devcontainer/Dockerfile`
- Repo cloning: `.devcontainer/additional-repos.json` (optional), `.devcontainer/scripts/clone-additional-repos.sh`
- postCreate lifecycle: `.devcontainer/postCreate.sh` — provisions `.venv/` via `uv` and installs tooling from `pyproject.toml` optional dependencies (`.[devcontainer]`).

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
