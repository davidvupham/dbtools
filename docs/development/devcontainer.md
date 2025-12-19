# Dev Container (Red Hat UBI 9, Python 3.13 via uv, Multi-Repo)

This workspace ships a simplified dev container based on Red Hat UBI 9. During `postCreate`, it provisions **Python 3.13** via `uv` and creates a repo-local virtual environment at `.venv/` (fallback: system `/usr/bin/python3`). It targets Docker access and multi-repo development.

Related docs: [Technical Architecture](devcontainer-architecture.md) · [Functional Spec](devcontainer-functional-spec.md)

## Highlights

- Python 3.13 provisioned via `uv` into `.venv/` during `postCreate` (system `/usr/bin/python3` remains available as a fallback).
- Docker access: uses the host Docker daemon via socket mount.
- Multi-repo: mounts the parent folder so sibling repos under `/workspaces/devcontainer` are available (workspace opens at `/workspaces/devcontainer/dbtools`).

## Additional Repos (Optional)

You can auto-clone extra repos into `/workspaces/devcontainer` using a per-developer config:

1. Create `.devcontainer/additional-repos.json` in your workspace with:

```json
{
    "repos": [
        "git@github.com:your-org/sqlserver.git",
        { "url": "git@github.com:your-org/linux-dev-setup.git", "directory": "linux-dev-setup" }
    ]
}
```

1. From inside the devcontainer, run:

```bash
bash .devcontainer/scripts/clone-additional-repos.sh
```

- The file is git-ignored; each developer can maintain their own list.
- Existing clones under `/workspaces` are detected and skipped.
- SQL Server tools: `msodbcsql18` and `sqlcmd` preinstalled for `pyodbc` and diagnostics (installed via the Microsoft RHEL 9 repo).
- PowerShell 7: Installed from the Microsoft RHEL 9 repository for database and automation scripts.
- No JupyterLab baked in by default; use VS Code notebooks via the Jupyter extension, or enable an optional flag to install JupyterLab.
- Docker-level healthcheck: verifies `python3` and `sqlcmd` are available on PATH.

## Rebuild & Start

1. Open the folder in VS Code.
2. Run “Dev Containers: Rebuild and Reopen in Container”.
3. Wait for `postCreate` to finish (kernel registration + editable installs).

If you already had a `.venv/` directory from an older setup, rebuild may not replace it. To force reprovisioning on the next `postCreate`, remove it first:

```bash
rm -rf .venv
```

## Verify

- Full suite: run the default task “Dev: Verify Dev Container”.
- PyODBC: run the task “Dev: Verify pyodbc”.
- SQL Server: run the task “MSSQL: Health Check” or “Dev: Verify SQL Server (sqlcmd + pyodbc)”.
- Docs formatting: run the task “Docs: Markdown Lint (Docker)” (requires Docker socket access inside the dev container).

Prerequisites for SQL Server checks:

- Ensure a SQL Server container is running (e.g., start [docker/mssql/docker-compose.yml](../../docker/mssql/docker-compose.yml)).
- Export `MSSQL_SA_PASSWORD` in your environment before running tasks.

Container health status (optional):

```bash
docker inspect --format '{{.State.Health.Status}}' <container_name>
```

CLI alternative:

```bash
make verify-devcontainer
```

## Multi-Repo Workflow

The container mounts your parent folder to `/workspaces/devcontainer`. Your current repo is at `/workspaces/devcontainer/dbtools`; sibling repos under the same parent are accessible, e.g. `/workspaces/devcontainer/other-repo`.

## Local Packages

All workspace packages are automatically installed in editable mode via `uv sync` during `postCreate`.

Devcontainer tooling (ruff/pytest/pyright/pyodbc/ipykernel/pre-commit, etc.) is installed from `pyproject.toml` dependency groups.

- VS Code uses `.venv/bin/python` as the interpreter.
- Run commands using `uv run <command>` (e.g., `uv run pytest`, `uv run python script.py`).

## Notes

- VS Code Python interpreter is set to `.venv/bin/python` (created during `postCreate`).
- If you need additional system libraries (e.g., database clients), add them in `.devcontainer/Dockerfile` and rebuild.
- Prefer VS Code notebooks with `ipykernel` over embedding JupyterLab to keep the image small.
- The container joins the shared Docker network `devcontainer-network` (created via `initializeCommand`).
- Optional installs via environment flags: `ENABLE_JUPYTERLAB=0`, `ENABLE_DBATOOLS=0`.
- OS packages are installed via `dnf` (UBI 9); Python tooling via `uv sync --group devcontainer`.

### Python version override

`postCreate` defaults to Python `3.13`. To override, set `DEVCONTAINER_PYTHON_VERSION` in your devcontainer override (e.g., `devcontainer.local.json`).

## Shell Prompt Customization

- The devcontainer uses `bash` by default. `postCreate` appends a colored prompt directly into `~/.bashrc` (with the `$` on its own line) and avoids any `~/.set_prompt` file dependency.
- The snippet includes optional git branch display via `__git_ps1`. To change it, edit the injected block in your `~/.bashrc` after the `# dbtools devcontainer prompt` marker and reopen the shell (or `source ~/.bashrc`).

## Jupyter Support

- VS Code Jupyter and Python extensions provide Notebook support.
- `ipykernel` is installed in `.venv/` and registered as `Python (gds)`.
- Port 8888 is forwarded and labeled "Jupyter".

### JupyterLab (Optional)

JupyterLab is not installed by default. You can opt-in by setting `ENABLE_JUPYTERLAB=1`, which triggers installation during `postCreate`:

Example `devcontainer.local.json` override:

```json
{
 "name": "dbtools (system Python, local)",
 "containerEnv": {
  "ENABLE_JUPYTERLAB": "1"
 }
}
```

After rebuild/reopen in container, you can launch JupyterLab if desired:

```bash
jupyter lab --no-browser --ip=0.0.0.0 --port=8888
```

## dbatools PowerShell Module (Optional)

The [dbatools](https://dbatools.io/) PowerShell module for SQL Server management is not installed by default. Opt-in by setting `ENABLE_DBATOOLS=1`:

Example `devcontainer.local.json` override:

```json
{
 "name": "dbtools (with dbatools)",
 "containerEnv": {
  "ENABLE_DBATOOLS": "1"
 }
}
```

After rebuild, verify installation:

```bash
pwsh -Command 'Get-Module -ListAvailable dbatools'
```
