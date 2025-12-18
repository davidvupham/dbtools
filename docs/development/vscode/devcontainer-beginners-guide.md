# Dev Containers and Docker: A Beginner-Friendly Guide

This guide walks you through what a dev container is, what's inside this project's container, and exactly how to build and use it with VS Code—even if you've never used Docker before.

## What is a Dev Container?

A dev container is a pre-configured development environment packaged in a Docker image. It ensures everyone on the team has the same tools, dependencies, and settings—no more "works on my machine."

- Docker image: A blueprint of an environment (OS + tools + libraries).
- Docker container: A running instance of an image.
- Dev container (VS Code feature): Open your repo inside a container, with VS Code attaching to it seamlessly.

This repo includes a `.devcontainer` folder that defines the container and a `Dockerfile` that builds the image.

## Prerequisites

- Install Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Install VS Code
- Install the "Dev Containers" extension in VS Code

Optional but helpful:

- Git installed locally
- Basic terminal access

## What's inside our container?

We've designed a streamlined environment focused on Python and PowerShell development with database connectivity. Key highlights:

- **Red Hat UBI 9** base image for enterprise stability
- **Python 3.14** provisioned via `uv` into `.venv/` (system `/usr/bin/python3` remains available)
- **PowerShell 7+** for database and automation scripts
- **SQL Server tools**: `msodbcsql18`, `mssql-tools18` (`sqlcmd`)
- **ODBC support**: `unixODBC` and development headers for `pyodbc`
- Python development tools are installed from `pyproject.toml` optional deps: `.[devcontainer]`
- VS Code extensions auto-install in the container: Python, Pylance, Jupyter, Ruff, Docker, GitLens
- Docker CLI access via host socket mount
- SSH key mounting for Git authentication (read-only)
- Pre-commit hooks setup (when configured)
- Local package installation in editable mode (gds_database, gds_postgres, gds_mssql, gds_mongodb, gds_liquibase, gds_vault, gds_snowflake, gds_snmp_receiver)
- Multi-repo support: parent folder mounted at `/workspaces/devcontainer`

## File-by-file: How this works

### 1) `.devcontainer/Dockerfile` (the environment recipe)

This file defines how to build the image. Major steps:

1. **Base image**: `registry.access.redhat.com/ubi9/ubi`
   - Red Hat Universal Base Image 9, enterprise-grade and corporate-aligned.

2. **Package manager detection**: Dynamically uses `microdnf` or `dnf` based on availability
   - Includes retry logic for resilience against mirror issues.

3. **Install base packages**:
   - `curl-minimal`, `gnupg2`, `ca-certificates`, `git` – essential tools
   - `gcc`, `gcc-c++`, `make`, `python3-devel` – build dependencies
   - `unixODBC`, `unixODBC-devel` – ODBC connectivity for databases

4. **Install Microsoft tools**:
   - Add Microsoft RHEL 9 RPM repository
   - Install `msodbcsql18` (ODBC driver), `mssql-tools18` (`sqlcmd`), `powershell`

5. **Create non-root user**: Uses `${localEnv:USER}` to match your host username
   - Enables proper file ownership when editing on host

6. **Python runtime**:
   - System Python is installed in the image.
   - Project Python (3.14 by default) is provisioned during `postCreate` via `uv` into `.venv/`.

7. **Install Docker CLI**: Latest stable Docker CLI and Compose plugin

8. **Healthcheck**: Verifies `python3`, `pwsh`, and `sqlcmd` are available

### 2) `.devcontainer/devcontainer.json` (VS Code instructions)

This file tells VS Code how to build and run the container and what to do afterward.

Key fields explained:

- `name`: Display name for the dev container configuration
- `build`: Specifies the Dockerfile and build arguments
  - `DEVCONTAINER_USER`: Uses `${localEnv:USER}` to match host user
- `remoteUser`: User inside the container (matches host user for file permissions)
- `features`: Additional dev container features:
  - `ghcr.io/devcontainers/features/common-utils`: Basic utilities
  - `ghcr.io/devcontainers/features/git`: Git version control
- `customizations.vscode.extensions`: Extensions auto-installed (Python, Pylance, Jupyter, Ruff, Docker, GitLens, etc.)
- `customizations.vscode.settings`: VS Code settings (Python interpreter at `.venv/bin/python`, testing, formatting)
- `workspaceMount`: Mounts parent folder at `/workspaces/devcontainer` for multi-repo workflows
- `workspaceFolder`: Opens at `/workspaces/devcontainer/dbtools`
- `initializeCommand`: Creates shared `devcontainer-network` Docker network
- `runArgs`: Joins the shared network for database container connectivity
- `postCreateCommand`: Runs `.devcontainer/postCreate.sh`
- `containerEnv`: Environment variables (pip optimizations, workspace paths)
- `mounts`: SSH keys (read-only), Docker socket

### 3) `.devcontainer/postCreate.sh` (setup script)

This script runs once after the container is first created:

1. **Workspace validation**: Ensures workspace directory exists
2. **Additional repos**: Optionally clones extra repos from `.devcontainer/additional-repos.json`
3. **Jupyter kernel**: Registers `gds` kernel for notebooks
4. **Shell prompt**: Adds colorful git-aware prompt to `~/.bashrc`
5. **Editable installs**: Installs local packages into `.venv/` with `pip -e`
6. **Pre-commit**: Installs git hooks if `.pre-commit-config.yaml` exists
7. **Docker verification**: Checks Docker daemon reachability
8. **pyodbc verification**: Validates ODBC driver installation

## Using the Dev Container in VS Code

1. Open this repository in VS Code.
2. If prompted, click "Reopen in Container". If not prompted:
   - Open Command Palette (Ctrl/Cmd+Shift+P)
   - Search for: "Dev Containers: Rebuild and Reopen in Container"
3. Wait for the image to build (first time can take several minutes).
4. When it opens, the integrated terminal is already inside the container.

That's it! You're developing inside a consistent, fully-loaded environment.

## Building and running with Docker directly (optional)

You usually don't need this because VS Code handles it, but it's useful to know:

1. Build the image (from the repo root):

   ```bash
   docker build -f .devcontainer/Dockerfile -t dbtools-dev:latest .
   ```

2. Run a container interactively mounting your code:

   ```bash
   docker run --rm -it \
     -v "$(pwd)":/workspaces/dbtools \
     -w /workspaces/dbtools \
     dbtools-dev:latest bash
   ```

3. Inside, verify tools:

   ```bash
   python3 -V
   pwsh -version
   sqlcmd -?
   docker --version
   ```

## Verifying the environment

Run these in the container terminal:

### Python and interpreter

```bash
python -V
which python
# Expected: .../dbtools/.venv/bin/python
```

### Python development tools

```bash
python -c "import ruff, pytest, pyodbc; print('Development tools OK')"
ruff --version
pytest --version
```

### PowerShell

```bash
pwsh -version
pwsh -NoProfile -Command '$PSVersionTable'
```

### ODBC and SQL Server connectivity

```bash
python -c "import pyodbc; print('pyodbc version:', pyodbc.version)"
odbcinst -q -d
# Should show: [ODBC Driver 18 for SQL Server]
sqlcmd -?
```

### Local packages (installed via postCreate)

```bash
python -c "import gds_database, gds_postgres, gds_mssql; print('Local packages OK')"
```

### Docker CLI

```bash
docker --version
docker ps
```

## Kerberos configuration (optional)

A template Kerberos config exists at `.devcontainer/krb5/krb5.conf` for reference.

**Note:** This is not currently mounted in the devcontainer.json configuration. If you need Kerberos authentication:

1. Edit the template file with your REALM and KDC details
2. Add the mount to `devcontainer.json` under `mounts`:

   ```json
   "source=${localWorkspaceFolder}/.devcontainer/krb5/krb5.conf,target=/etc/krb5.conf,type=bind,consistency=cached,readonly"
   ```

3. Add the environment variable under `containerEnv`:

   ```json
   "KRB5_CONFIG": "/etc/krb5.conf"
   ```

Then you can acquire a ticket:

```bash
kinit user@EXAMPLE.COM
klist
```

## Pre-commit hooks

If a `.pre-commit-config.yaml` file exists in the repo root, the container will automatically run:

- `pre-commit install`

Then, on each `git commit`, hooks will run (formatters, linters, etc.). You can trigger manually:

```bash
pre-commit run --all-files
```

## Troubleshooting

### First build is slow

Many tools are installed; subsequent rebuilds will be faster due to Docker layer caching.

### Network/timeouts

If behind a proxy, configure Docker and add proxy env vars in `devcontainer.json` if needed.

### Missing tools or versions

Open an issue or adjust the Dockerfile to pin versions.

### Permission issues (volume mounts)

On Linux, ensure your user can access the project directory. The container user matches your host user by default.

### Docker daemon not reachable

Check that Docker Desktop is running and `/var/run/docker.sock` is mounted.

## Docker basics: list, rebuild, remove

Use these commands from a terminal on your host (not inside the container):

### Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop and remove a container
docker stop <container_id>
docker rm <container_id>
```

### Images

```bash
# List images
docker images

# Remove an image
docker rmi <image_id_or_name>

# Find devcontainer images
docker images | grep -E 'devcontainer|vsc-|dbtools-dev'
```

### Cleanup

```bash
# Remove unused data
docker system prune -f

# Prune build cache
docker builder prune -af
```

### Rebuilding

```bash
# Rebuild the project image manually
docker build -f .devcontainer/Dockerfile -t dbtools-dev:latest .
```

## VS Code dev container tips

- **Rebuild the container**: Command Palette → "Dev Containers: Rebuild and Reopen in Container"
- **Rebuild without cache**: Command Palette → "Dev Containers: Rebuild Container without Cache"
- **See container logs**: View → Output → Dev Containers

## Verification Task

Run the verification suite to ensure everything is working:

```bash
make verify-devcontainer
```

Or use the VS Code task: "Dev: Verify Dev Container"

## Where to go next

- [Developer guide](../devcontainer.md) – Quick reference for daily usage
- [Technical architecture](../devcontainer-architecture.md) – Visual diagrams and component overview
- [Functional spec](../devcontainer-functional-spec.md) – Detailed feature specification
- [SQLTools connectivity](devcontainer-sqltools.md) – Database connection examples
