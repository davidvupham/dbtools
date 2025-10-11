# Dev Containers and Docker: A Beginner-Friendly Guide

This guide walks you through what a dev container is, what’s inside this project’s container, and exactly how to build and use it with VS Code—even if you’ve never used Docker before.

## What is a Dev Container?

A dev container is a pre-configured development environment packaged in a Docker image. It ensures everyone on the team has the same tools, dependencies, and settings—no more “works on my machine.”

- Docker image: A blueprint of an environment (OS + tools + libraries).
- Docker container: A running instance of an image.
- Dev container (VS Code feature): Open your repo inside a container, with VS Code attaching to it seamlessly.

This repo includes a `.devcontainer` folder that defines the container and a `Dockerfile` that builds the image.

## Prerequisites

- Install Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Install VS Code
- Install the “Dev Containers” extension in VS Code

Optional but helpful:
- Git installed locally
- Basic terminal access

## What’s inside our container?

We've designed a streamlined environment focused on Python development with database connectivity. Key highlights:

- Python 3.13 via Miniconda, default environment `gds`
- Essential Python development tools: ruff (linter/formatter), pytest (testing), pytest-cov (coverage), wheel, build
- Database connectivity: pyodbc for ODBC connections, unixODBC development libraries
- VS Code extensions auto-install in the container: Python, Pylance, Jupyter, Ruff, Docker, Windows AI Studio
- Docker-in-Docker support for container operations within the dev container
- SSH key mounting for Git authentication
- Pre-commit hooks setup (when configured)
- Local package installation in editable mode (gds_database, gds_postgres, gds_snowflake, gds_vault)

## File-by-file: How this works

### 1) `.devcontainer/Dockerfile` (the environment recipe)

This file defines how to build the image. Major steps:

1. Base image: `mcr.microsoft.com/devcontainers/miniconda:latest`
   - Provides Python via Conda from Microsoft Dev Containers; optimized for development environments.
2. Install system dependencies
   - `unixodbc-dev` and `ca-certificates` for database connectivity and SSL support.
3. Create `gds` conda environment with Python 3.13
   - Ensures consistent Python version across all environments.
4. Configure shell environment
   - Sets up conda activation in `.bashrc` files so all interactive shells use the `gds` environment.
   - Adds a custom colorful prompt for better UX.
5. Install Python development tools in the conda environment
   - `ruff`: Fast Python linter and code formatter
   - `pytest` and `pytest-cov`: Testing framework and coverage reporting
   - `wheel` and `build`: Package building tools
   - `pyodbc`: Python ODBC database connectivity
6. Set up VS Code server directories
   - Pre-creates directories with correct permissions to avoid issues when VS Code attaches.

You don't need to edit this file unless you want to add/remove tools or change the Python version.

### 2) `.devcontainer/devcontainer.json` (VS Code instructions)

This file tells VS Code how to build and run the container and what to do afterward.

Key fields explained:
- `name`: Display name for the dev container configuration
- `build`: Specifies the Dockerfile and build arguments (Python version 3.13, conda env name "gds")
- `remoteUser`: User inside the container (`vscode` for security and proper file permissions)
- `features`: Additional dev container features to include:
  - `ghcr.io/devcontainers/features/common-utils`: Basic utilities and user setup
  - `ghcr.io/devcontainers/features/git`: Git version control tools
  - `ghcr.io/devcontainers/features/docker-in-docker`: Docker CLI and daemon for container operations
- `customizations.vscode.extensions`: VS Code extensions that auto-install inside the container (Python, Pylance, Jupyter, Ruff, Docker, Windows AI Studio)
- `customizations.vscode.settings`: VS Code settings for the container (Python interpreter, testing, formatting)
- `workspaceFolder`: The working directory inside the container
- `runArgs`: Extra Docker runtime arguments (unbuffered Python output, VS Code server cache volume)
- `postCreateCommand`: Script run after container creation (installs local packages in editable mode)
- `postStartCommand`: Commands run each time the container starts (sets up VS Code server permissions)
- `containerEnv`: Environment variables (disables pip version checks)
- `mounts`: Bind mounts for SSH keys (for Git authentication)

## Using the Dev Container in VS Code

1. Open this repository in VS Code.
2. If prompted, click “Reopen in Container”. If not prompted:
   - Open Command Palette (Ctrl/Cmd+Shift+P)
   - Search for: “Dev Containers: Rebuild and Reopen in Container”
3. Wait for the image to build (first time can take several minutes).
4. When it opens, the integrated terminal is already inside the container.

That’s it! You’re developing inside a consistent, fully-loaded environment.

## Building and running with Docker directly (optional)

You usually don’t need this because VS Code handles it, but it’s useful to know:

1. Build the image (from the repo root):
   ```bash
   docker build -f .devcontainer/Dockerfile -t dbtools-dev:latest .
   ```
2. Run a container interactively mounting your code (and optionally Kerberos config):
   ```bash
   docker run --rm -it \
     -v "$(pwd)":/workspaces/dbtools \
     -w /workspaces/dbtools \
     dbtools-dev:latest bash
   ```
   For Kerberos support, also add:
   ```bash
   -v "$(pwd)/.devcontainer/krb5/krb5.conf":/etc/krb5.conf:ro \
   -e KRB5_CONFIG=/etc/krb5.conf \
   ```
3. Inside, the `gds` env is already active; verify tools:
   ```bash
   python -V
   terraform -version
   aws --version
   sqlcmd -?
   ```

## Verifying the environment

Run these in the container terminal:

- Python and conda environment
  ```bash
  python -V
  conda env list
  which python
  ```
- Python development tools
  ```bash
  python -c "import ruff, pytest, pyodbc; print('Development tools OK')"
  ruff --version
  pytest --version
  ```
- ODBC connectivity
  ```bash
  python -c "import pyodbc; print('pyodbc version:', pyodbc.version)"
  odbcinst -j
  ```
- Local packages (installed via postCreate)
  ```bash
  python -c "import gds_database, gds_postgres, gds_snowflake, gds_vault; print('Local packages OK')"
  ```
- Docker-in-Docker
  ```bash
  docker --version
  docker ps
  ```

## Kerberos configuration (optional)

A template Kerberos config exists at `.devcontainer/krb5/krb5.conf` for reference. **Note:** This is not currently mounted in the devcontainer.json configuration. If you need Kerberos authentication:

1. Edit the template file with your REALM and KDC details
2. Add the mount to `devcontainer.json` under `mounts`:
   ```json
   "mounts": [
     "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly",
     "source=${workspaceFolder}/.devcontainer/krb5/krb5.conf,target=/etc/krb5.conf,type=bind,consistency=cached,readonly"
   ]
   ```
3. Add the environment variable under `containerEnv`:
   ```json
   "containerEnv": {
     "PIP_DISABLE_PIP_VERSION_CHECK": "1",
     "KRB5_CONFIG": "/etc/krb5.conf"
   }
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

- First build is slow
  - Many tools are installed; subsequent rebuilds will be faster due to Docker layer caching.
- Network/timeouts
  - If behind a proxy, configure Docker and add proxy env vars in `devcontainer.json` if needed.
- Missing tools or versions
  - Open an issue or adjust the Dockerfile to pin versions.
- Permission issues (volume mounts)
  - On Linux, ensure your user can access the project directory. VS Code remoting usually handles this.
- Kerberos realm not found
  - Double-check `.devcontainer/krb5/krb5.conf` entries and DNS. Use `kinit` and check `klist` output.

### Docker basics: list, rebuild, remove

Use these commands from a terminal on your host (not inside the container) to inspect and clean up Docker resources.

Containers (running/stopped):
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View logs for a container
docker logs <container_id>

# Stop and remove a container
docker stop <container_id>
docker rm <container_id>
```

Images:
```bash
# List images
docker images
# Same as above
docker image ls

# Remove an image by ID or name:tag (must not be used by a container)
docker rmi <image_id_or_name>

# Find devcontainer images (handy to clean stale ones)
docker images | grep -E 'devcontainer|vsc-|dbtools-dev'
```

Volumes and networks:
```bash
# List volumes and networks
docker volume ls
docker network ls

# Remove unused (dangling) volumes and networks (careful!)
docker volume prune -f
docker network prune -f
```

General cleanup:
```bash
# Remove unused data (stopped containers, dangling images, networks, build cache)
docker system prune -f

# Also prune build cache aggressively
docker builder prune -af
```

Rebuilding images:
```bash
# Rebuild the project image manually (from repo root)
docker build -f .devcontainer/Dockerfile -t dbtools-dev:latest .
```

If an image is in use, remove the containers first (stop + rm), then remove the image.

### VS Code dev container tips

- Rebuild the container
  - Command Palette → "Dev Containers: Rebuild and Reopen in Container"
- Rebuild without cache (forces fresh installs)
  - Command Palette → "Dev Containers: Rebuild Container without Cache"
- Open a shell inside the running container
  - VS Code Terminal → New Terminal (it opens inside the container automatically)
- See container logs during build
  - View → Output → Dev Containers (select from dropdown)
- If rebuilds keep using a stale image
  - Run the manual Docker cleanup commands above to remove old images/containers
  - Then run Rebuild and Reopen in Container again

### Common issues and fixes

- Permission denied mounting files
  - Ensure your user has read permissions on the repo path; on Linux check folder ownership and permissions.
- Proxy/SSL interceptors block downloads
  - Configure Docker’s proxy and add `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` in `devcontainer.json` under `containerEnv` if needed.
- pip/conda timeouts
  - Rebuild without cache and ensure network is stable; optionally pin versions in the Dockerfile to reduce solver work.
- Port binding conflicts
  - If you add services later (databases, web servers), choose unused host ports or stop the conflicting service.

## Configuration File Reference

### devcontainer.json - Line by Line

```jsonc
{
  "name": "dbtools - Miniconda3 (Py3.13)",  // Display name shown in VS Code dev container selection
  "build": {
    "dockerfile": "Dockerfile",  // Path to the Dockerfile relative to .devcontainer/
    "context": "..",  // Build context (parent directory containing the repo)
    "args": {
      "PYTHON_VERSION": "3.13",  // Python version to install in conda environment
      "CONDA_ENV_NAME": "gds"  // Name of the conda environment to create
    }
  },
  "remoteUser": "vscode",  // User to run as inside container (non-root for security)
  "features": {
    "ghcr.io/devcontainers/features/common-utils:2": {  // Basic Linux utilities and user setup
      "installZsh": false,  // Don't install Zsh shell
      "username": "vscode",  // Username for the user
      "userUid": "1000",  // User ID
      "userGid": "1000"  // Group ID
    },
    "ghcr.io/devcontainers/features/git:1": {},  // Git version control
    "ghcr.io/devcontainers/features/docker-in-docker:2": {  // Docker CLI and daemon
      "version": "latest"  // Use latest Docker version
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [  // VS Code extensions to install automatically
        "ms-python.python",  // Python language support
        "ms-python.vscode-pylance",  // Fast Python language server
        "ms-toolsai.jupyter",  // Jupyter notebook support
        "charliermarsh.ruff",  // Ruff linter and formatter
        "ms-azuretools.vscode-docker",  // Docker extension
        "ms-windows-ai-studio.windows-ai-studio"  // Windows AI Studio
      ],
      "settings": {
        "python.defaultInterpreterPath": "/opt/conda/envs/gds/bin/python",  // Default Python interpreter
        "python.terminal.activateEnvironment": true,  // Auto-activate conda env in terminals
        "python.testing.pytestEnabled": true,  // Enable pytest
        "python.testing.unittestEnabled": false,  // Disable unittest
        "editor.formatOnSave": true,  // Format code on save
        "ruff.organizeImports": true,  // Organize imports with ruff
        "ruff.enable": true  // Enable ruff linting
      }
    }
  },
  "workspaceFolder": "/workspaces/dbtools",  // Workspace directory inside container
  "runArgs": [  // Additional Docker run arguments
    "--env", "PYTHONUNBUFFERED=1",  // Unbuffered Python output for better logging
    "--mount", "type=volume,source=vscode-server-cache,target=/home/vscode/.vscode-server,consistency=cached"  // Cache VS Code server extensions
  ],
  "postCreateCommand": "bash .devcontainer/postCreate.sh",  // Run after container creation
  "postStartCommand": "bash -lc 'mkdir -p ~/.vscode-server/extensions ~/.vscode-server/extensionsCache && chmod -R 775 ~/.vscode-server && chown -R vscode:vscode ~/.vscode-server || true'",  // Run on each container start
  "containerEnv": {
    "PIP_DISABLE_PIP_VERSION_CHECK": "1"  // Disable pip version check warnings
  },
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly"  // Mount SSH keys for Git auth
  ]
}
```

## Makefile and helper scripts (optional)

If you prefer simple commands over long docker invocations, use the Makefile targets or scripts provided.

When to use:
- You want repeatable local commands outside of VS Code
- You need to build, run, or verify quickly from the terminal

Why use them:
- Short, memorable commands (e.g., `make build`, `make shell`)
- Encapsulate best practices (mounts, env vars like KRB5_CONFIG)

How to use:
```bash
# Show available targets
make help

# Build image (cached)
make build

# Build without cache (fresh)
make build-no-cache

# Start the container in background and mount the repo
make run

# Open a shell inside the running container (or start one-off)
make shell

# Quick verification run
make verify

# List containers/images
make ps
make ps-all
make images

# Logs/stop/rm/rmi
make logs ID=<container_id>
make stop ID=<container_id>
make rm ID=<container_id>
make rmi IMG=<image_id_or_name>

# Cleanup
make prune
make builder-prune
make clean-all
```

### Dockerfile - Line by Line

```dockerfile
# syntax=docker/dockerfile:1.4  // Use advanced Dockerfile syntax features

ARG VARIANT="latest"  // Build argument for base image variant
FROM mcr.microsoft.com/devcontainers/miniconda:${VARIANT}  // Base image with Miniconda

// Build arguments for customization
ARG PYTHON_VERSION=3.13  // Python version to install
ARG CONDA_ENV_NAME=gds  // Conda environment name

// Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

// Install system packages for ODBC support
RUN apt-get update && apt-get install -y unixodbc-dev ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

// Update conda and create the gds environment with specified Python version
RUN conda update -n base -c defaults conda -y && \
    conda create -n ${CONDA_ENV_NAME} -c conda-forge python=${PYTHON_VERSION} -y && \
    conda clean -afy

// Configure shell to use bash with login shell for conda activation
SHELL ["/bin/bash", "-lc"]

// Add conda initialization and environment activation to shell profiles
RUN for f in /etc/skel/.bashrc /home/vscode/.bashrc /home/vscode/.profile; do \
            echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then . /opt/conda/etc/profile.d/conda.sh; fi' >> "$f"; \
            echo "conda activate ${CONDA_ENV_NAME}" >> "$f"; \
        done

// Set up a colorful prompt for the dev container
RUN <<'BASH'
set -euo pipefail
for f in /etc/skel/.bashrc /home/vscode/.bashrc /home/vscode/.profile; do
    cat >> "$f" <<'EOF'
# dbtools devcontainer prompt
if [[ $- == *i* ]]; then
export PS1="\[$(tput setaf 208)\]\d  \[$(tput setaf 226)\]\u\[$(tput setaf 220)\]@\[$(tput setaf 214)\]\h \[$(tput setaf 33)\]\w
\[$(tput sgr0)\]$ "
fi
EOF
done
BASH

// Install Python development tools in the conda environment
RUN conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    conda run -n ${CONDA_ENV_NAME} pip install ruff pytest pytest-cov wheel build pyodbc

// Add the conda environment's bin directory to PATH
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:$PATH

// Switch to vscode user for running the container
USER vscode
WORKDIR /workspaces/dbtools

// Pre-create VS Code server directories with correct ownership (run as root first)
USER root
RUN mkdir -p /home/vscode/.vscode-server/extensions /home/vscode/.vscode-server/extensionsCache \
    && chown -R vscode:vscode /home/vscode/.vscode-server
USER vscode  // Switch back to vscode user
```

### postCreate.sh - Line by Line

```bash
#!/usr/bin/env bash

# postCreate script for the dbtools dev container
# - Installs local packages in editable mode
# - Optionally installs dev extras when available
# - Sets up pre-commit hooks if configured

set -euo pipefail  // Exit on error, undefined vars, pipe failures

echo "[postCreate] Starting setup..."

// Ensure we're in the correct workspace directory
cd /workspaces/dbtools || {
  echo "[postCreate] Workspace folder /workspaces/dbtools not found" >&2
  exit 1
}

echo "[postCreate] Python: $(python -V)"
echo "[postCreate] Pip: $(python -m pip -V)"

// Upgrade pip and wheel to latest versions
echo "[postCreate] Upgrading pip and wheel..."
python -m pip install --upgrade pip wheel >/dev/null

// Function to install a package in editable mode
install_editable() {
  local pkg_dir="$1"
  if [[ -d "$pkg_dir" ]] && [[ -f "$pkg_dir/pyproject.toml" || -f "$pkg_dir/setup.py" ]]; then
    echo "[postCreate] Installing $pkg_dir in editable mode (prefer [dev] extras if available)..."
    // Try installing with dev extras first, fall back to base if not available
    if ! python -m pip install -e "$pkg_dir[dev]" >/dev/null 2>&1; then
      python -m pip install -e "$pkg_dir" >/dev/null
    fi
  else
    echo "[postCreate] Skipping $pkg_dir (no project files)."
  fi
}

// Install local packages in editable mode
for pkg in gds_database gds_postgres gds_snowflake gds_vault; do
  install_editable "$pkg"
done

// Setup pre-commit if configuration file exists
if [[ -f .pre-commit-config.yaml ]]; then
  echo "[postCreate] Installing and configuring pre-commit hooks..."
  python -m pip install --upgrade pre-commit >/dev/null
  pre-commit install || true
else
  echo "[postCreate] No .pre-commit-config.yaml found; skipping pre-commit setup."
fi

echo "[postCreate] Done."
```

## Where to go next

- Explore the docs in `docs/vscode/DEVCONTAINER_SQLTOOLS.md` for tool-specific verification and usage.
- Tell us if you need additional tooling and we'll consider adding it to the Dockerfile.
