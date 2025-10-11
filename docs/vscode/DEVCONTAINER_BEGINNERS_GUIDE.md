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

We’ve designed a comprehensive environment for data engineering and platform work. Key highlights:

- Python via Miniconda, default environment `gds`
- Popular Python libs: pandas, pyarrow, boto3, psycopg2, pymongo, hvac, snowflake-connector-python
- Infra tools: Terraform, tflint, tfsec, terragrunt, terraform-docs, Infracost
- Cloud CLIs: AWS CLI v2, Azure CLI
- SQL tooling: Microsoft ODBC Driver 18, sqlcmd (mssql-tools18), unixODBC
- Ansible & linting: ansible, ansible-lint, checkov (IaC security)
- Kerberos: client libraries + Python bindings, with a template krb5.conf
- Pre-commit installed (git hooks can run automatically)

VS Code extensions auto-install in the container:
- Python, Pylance, GitHub Copilot, MSSQL, Terraform, Ansible, AWS Toolkit, and more

## File-by-file: How this works

### 1) `.devcontainer/Dockerfile` (the environment recipe)

This file defines how to build the image. Major steps:

1. Base image: `continuumio/miniconda3:latest`
   - Provides Python via Conda; great for managing environments.
2. Create `gds` conda environment and make it default
   - Ensures all shells use the same Python environment.
3. Install Python packages in `gds` (data, DB, cloud, security)
   - pandas, pyarrow, boto3, psycopg2, pymongo, hvac, snowflake-connector-python, checkov, ansible, ansible-lint, requests-kerberos, python-gssapi, and more.
4. Install OS-level tools
   - SQL tools (ODBC, sqlcmd), Terraform + helpers (tflint/tfsec/terragrunt/terraform-docs), Infracost, AWS CLI v2, Azure CLI.
5. Shell conveniences
   - Custom colorful prompt, pre-commit preinstalled.
6. Kerberos libraries
   - Client and dev packages; works with a mounted krb5.conf.

You don’t need to edit this file unless you want to add/remove tools.

### 2) `.devcontainer/devcontainer.json` (VS Code instructions)

This file tells VS Code how to build and run the container and what to do afterward.

Key fields explained:
- `build.dockerfile`: Points to our Dockerfile.
- `features`: Adds common utils in the container.
- `remoteUser`: User inside the container (root by default for simplicity).
- `containerEnv`: Environment variables (e.g., unbuffered Python output).
- `mounts`: Binds the template Kerberos config into `/etc/krb5.conf`.
- `remoteEnv`: Sets `KRB5_CONFIG` so tools use the mounted config.
- `customizations.vscode.extensions`: List of VS Code extensions that auto-install inside the container.
- `customizations.vscode.settings`: VS Code settings (interpreter path, testing, etc.).
- `postCreateCommand`: Commands run after the container is built the first time. In this repo it calls `.devcontainer/postCreate.sh`, which:
  - Installs local packages in editable mode (prefers `[dev]` extras when available)
  - Installs and configures pre-commit hooks if `.pre-commit-config.yaml` exists
  - Is the right place to add any additional first-run setup steps
- `runArgs`: Extra Docker runtime flags; `--init` adds a tiny init to handle processes cleanly.

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
2. Run a container interactively mounting your code:
   ```bash
   docker run --rm -it \
     -v "$(pwd)":/workspaces/dbtools \
     -v "$(pwd)/.devcontainer/krb5/krb5.conf":/etc/krb5.conf:ro \
     -e KRB5_CONFIG=/etc/krb5.conf \
     -w /workspaces/dbtools \
     dbtools-dev:latest bash
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

- Python and libs
  ```bash
  python -V
  python -c "import pandas, pyarrow, boto3, psycopg2, pymongo, hvac, snowflake.connector; print('OK')"
  ```
- IaC toolchain
  ```bash
  terraform -version && tflint --version && tfsec --version && terragrunt --version
  terraform-docs --version && infracost --version
  ```
- Cloud CLIs
  ```bash
  aws --version
  az version
  ```
- SQL tools
  ```bash
  sqlcmd -?
  odbcinst -j
  ```
- Kerberos
  ```bash
  krb5-config --version || true
  python -c "import requests_kerberos, gssapi; print('kerberos OK')"
  ```

## Kerberos configuration

A template config lives at `.devcontainer/krb5/krb5.conf`. It is bind-mounted into the container at `/etc/krb5.conf`, and `KRB5_CONFIG` is set accordingly.

- Edit REALM, KDC, and domain mappings to match your environment.
- Acquire a ticket:
  ```bash
  kinit user@EXAMPLE.COM
  klist
  ```
- Optional: use keytabs (ask us to add a mount and helper if you need this).

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

## Where to go next

- Explore the docs in `docs/vscode/DEVCONTAINER_SQLTOOLS.md` for tool-specific verification and usage.
- Tell us if you need additional tooling (e.g., SAM CLI, CDK, Molecule) and we’ll add it.

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

Helper scripts in `scripts/devcontainer/` mirror these tasks (useful on systems without `make`):
- `build.sh` / `rebuild.sh`
- `run.sh`
- `clean.sh`
- `verify.sh`

Example:
```bash
bash scripts/devcontainer/build.sh
bash scripts/devcontainer/run.sh
bash scripts/devcontainer/verify.sh
```
