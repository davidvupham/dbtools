# Dev Container (Red Hat UBI 9, Python venv, Multi-Repo)

This workspace ships a simplified dev container based on Red Hat UBI 9, designed for Python venv (no Conda), Docker access, and multi-repo development.

Related docs: [Technical Architecture](devcontainer-architecture.md) · [Functional Spec](devcontainer-functional-spec.md)

## Highlights

- Python via `venv`: created in `.venv` at the repo root.
- Docker access: uses the host Docker daemon via socket mount.
- Multi-repo: mounts the parent folder so sibling repos under `/workspaces` are available.

## Additional Repos (Optional)

You can auto-clone extra repos into `/workspaces` using a per-developer config:

1. Create `.devcontainer/additional-repos.json` in your workspace with:

```
{
    "repos": [
        "git@github.com:your-org/sqlserver.git",
        { "url": "git@github.com:your-org/linux-dev-setup.git", "directory": "linux-dev-setup" }
    ]
}
```

2. From inside the devcontainer, run:

```
bash .devcontainer/scripts/clone-additional-repos.sh
```

- The file is git-ignored; each developer can maintain their own list.
- Existing clones under `/workspaces` are detected and skipped.
- SQL Server tools: `msodbcsql18` and `sqlcmd` preinstalled for `pyodbc` and diagnostics (installed via the Microsoft RHEL 9 repo).
- PowerShell 7 installed for database/automation scripts.
- No JupyterLab baked in by default; use VS Code notebooks via the Jupyter extension, or enable an optional flag to install JupyterLab.
- Docker-level healthcheck: verifies `python3`, `pwsh`, and `sqlcmd` are available on PATH.

## Rebuild & Start

1. Open the folder in VS Code.
2. Run “Dev Containers: Rebuild and Reopen in Container”.
3. Wait for `postCreate` to finish (venv + base tools).

## Verify

- Full suite: run the default task “Dev: Verify Dev Container”.
- PyODBC: run the task “Dev: Verify pyodbc”.
- SQL Server: run the task “MSSQL: Health Check” or “Dev: Verify SQL Server (sqlcmd + pyodbc)”.
- Docs formatting: run the task “Docs: Markdown Lint (Docker)”.

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

The container mounts your parent folder to `/workspaces`. Your current repo is at `/workspaces/dbtools`; sibling repos under the same parent are accessible, e.g. `/workspaces/other-repo`. You can `pip install -e` any local package as needed.

## Local Packages

If present, the container attempts to install local packages in editable mode on start. Adjust `postStartCommand` in `.devcontainer/devcontainer.json` or remove it if you prefer manual installs.

## Notes

- The previous Conda-based configuration is superseded. This setup uses `python3 -m venv .venv` for simplicity and portability.
- If you need additional system libraries (e.g., database clients), add them in `.devcontainer/Dockerfile` and rebuild.
- Prefer VS Code notebooks with `ipykernel` over embedding JupyterLab to keep the image small.
- The container joins the shared Docker network `devcontainer-network` (created via `initializeCommand`).
- Environment flags: `PIP_DISABLE_PIP_VERSION_CHECK=1` (speed up pip) and `ENABLE_JUPYTERLAB=0` (opt-in JupyterLab during postCreate).
- OS packages are installed via `microdnf`/`dnf` (UBI 9); Python packages via `pip` into `.venv`.

## Shell Prompt Customization

- The devcontainer uses `bash` by default; the prompt (`PS1`) comes from UBI 9 and your `~/.bashrc`.
- A post-start hook sources `~/.set_prompt` if present, so you can customize your prompt per-user.
- On first create, a default `~/.set_prompt` is generated with a venv-aware, colored prompt and optional git branch display.

To customize:

```bash
cat > ~/.set_prompt <<'EOF'
# Example: venv name + user@host:path + git branch
venv_prefix=''
[ -n "$VIRTUAL_ENV" ] && venv_prefix="($(basename "$VIRTUAL_ENV")) "
GREEN='\[\e[32m\]'; BLUE='\[\e[34m\]'; CYAN='\[\e[36m\]'; RESET='\[\e[0m\]'
export PS1="${venv_prefix}${GREEN}\u@\h${RESET}:${BLUE}\w${RESET}\$(type __git_ps1 >/dev/null 2>&1 && __git_ps1 ' (%s)') ${CYAN}\$${RESET} "
EOF
source ~/.set_prompt
```

The hook is idempotent and only appends sourcing logic to `~/.bashrc` if missing.

## Jupyter Support

- VS Code Jupyter and Python extensions provide Notebook support.
- `ipykernel` is installed in `.venv` and registered as `Python (gds)`.
- Port 8888 is forwarded and labeled "Jupyter".

### JupyterLab (Optional)

JupyterLab is not installed by default. You can opt-in by setting `ENABLE_JUPYTERLAB=1`, which triggers installation during `postCreate`:

Example `devcontainer.local.json` override:

```
{
 "name": "dbtools (venv, local)",
 "containerEnv": {
  "ENABLE_JUPYTERLAB": "1"
 }
}
```

After rebuild/reopen in container, you can launch JupyterLab if desired:

```
source .venv/bin/activate
jupyter lab --no-browser --ip=0.0.0.0 --port=8888

## Python 3.14 via Pyenv (Optional)

The base image (UBI 9) uses system `python3`. To use Python 3.14 without changing the base image, enable the guarded pyenv path:

- In `.devcontainer/devcontainer.json` under `build.args`, set:

```

"USE_PYENV": "1",
"PYENV_PYTHON_VERSION": "3.14.0"

```

- Rebuild the container (Dev Containers: Rebuild and Reopen in Container).
- Verify inside the container:

```bash
python --version
python3 --version
which python
which python3
```

When `USE_PYENV=1`, the Dockerfile installs pyenv and sets the global Python to `PYENV_PYTHON_VERSION`. The `postCreateCommand` will create `.venv` from this Python, keeping VS Code pointing at `/workspaces/dbtools/.venv/bin/python`.

```
