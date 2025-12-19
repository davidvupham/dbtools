# Developer Onboarding: Personal Linux Environment (WSL2 or Red Hat)

This guide helps new team members set up a **personal Linux development environment** for this repo.

**Recommended approach:** use the repo’s **VS Code Dev Container** for a consistent toolchain (Python, PowerShell, ODBC/sqlcmd, linters, test tools).

## Table of Contents

- [What you’ll end up with](#what-youll-end-up-with)
- [Choose your platform](#choose-your-platform)
- [Step 1 — Set up VS Code (recommended)](#step-1--set-up-vs-code-recommended)
- [Step 2 — Set up the `uv` Python environment](#step-2--set-up-the-uv-python-environment)
- [Step 3 — Common setup (WSL2 or RHEL)](#step-3--common-setup-wsl2-or-rhel)
- [Step 4 — Open dbtools in the Dev Container (recommended)](#step-4--open-dbtools-in-the-dev-container-recommended)
- [Step 5 — Verify your environment](#step-5--verify-your-environment)
- [Troubleshooting](#troubleshooting)
- [What’s next](#whats-next)

## What you’ll end up with

- A working Linux shell environment (WSL2 or RHEL)
- Git + GitHub access (SSH or HTTPS)
- Docker available for dev containers
- VS Code configured to open this repo in the dev container
- A verified dev setup using the repo’s built-in verification scripts/tasks

## Choose your platform

- **WSL2 (Windows Subsystem for Linux):** personal Linux environment on a Windows laptop
- **Red Hat Enterprise Linux (or compatible):** shared Linux server environment

If you’re unsure: pick **WSL2 + Ubuntu**.

### Shared RHEL server checklist

If you are developing on a **shared Red Hat Linux server**, verify these basics before proceeding:

- **Access**: You can SSH to the server and have a home directory (`$HOME`) with enough space.
- **GitHub auth**: SSH keys are set up and you can `git clone` from GitHub.
  - If your environment uses bastions/jump hosts, confirm your SSH config works.
- **Editor workflow**: Decide whether you will use:
  - VS Code Remote SSH (recommended for a shared server), or
  - CLI-only editing (vim/emacs) if you prefer.
- **Docker/dev containers**: Confirm whether Docker is available to you on the shared server.
  - Many shared servers do not allow Docker for non-admin users; if Docker is not available, skip dev container steps and use host-side `uv` (Step 2).
- **Install policy**: Know what you can install.
  - If you cannot install system packages, prefer user-scoped tooling (for example, UV-managed Python under your home directory).

---

## Step 1 — Set up VS Code (recommended)

Use the repo’s existing VS Code + dev container documentation:

- [docs/development/vscode/README.md](vscode/README.md)
- [docs/development/vscode/platform-specific.md](vscode/platform-specific.md)

If you are using WSL2, follow the dedicated WSL2 setup guide:

- [docs/how-to/setup-wsl2.md](../how-to/setup-wsl2.md)

**Note (managed Windows laptops):** If you do not have admin rights, you may need to submit a ServiceNow request to have IT enable WSL2 and install Docker Desktop.
The WSL2 setup guide includes a checklist of what to request.

Once VS Code is installed and configured for your platform, proceed to Step 2.

---

## Step 2 — Set up the `uv` Python environment

This repo uses **UV** as the primary Python package manager.

- UV how-to index (start here): [docs/how-to/python/uv/README.md](../how-to/python/uv/README.md)

**Important:** If you will use the VS Code dev container (recommended), you usually do **not** need to set up UV on your host OS.
Open the repo in the dev container (Step 4), then verify the environment (Step 5).

#### If you are using the VS Code dev container

The dev container provisions the repo’s `.venv/` during `postCreate` using UV.

You typically do not need to run UV manually on the host.

#### If you are NOT using the dev container

1. Install UV (see the “Getting Started” links in the UV how-to index):

2. From the repo root, create/sync the workspace environment:

```bash
cd ~/dbtools

# Install tools for typical local development
uv sync --group dev

# If you want the fuller toolchain used by the dev container (ODBC tooling, etc.)
uv sync --group devcontainer
```

If you’re migrating from pip/Poetry, follow:

- [docs/how-to/python/uv/uv-migrate-from-pip.md](../how-to/python/uv/uv-migrate-from-pip.md)

---

## Step 3 — Common setup (WSL2 or RHEL)

These steps apply whether you develop on **WSL2** or on a **shared RHEL server**.

### 3.1) Install Git and basic tooling

Make sure you have:

- `git`
- `curl`
- `make`

### 3.2) Configure Git identity

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3.3) Set up SSH keys for GitHub

GitHub access is a shared prerequisite for both WSL2 and shared RHEL environments.

1. Check for an existing key:

```bash
ls -la ~/.ssh
```

1. If you don’t have one, create an Ed25519 key:

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

1. Start an agent and add the key:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

1. Add the public key to GitHub:

```bash
cat ~/.ssh/id_ed25519.pub
```

### 3.4) Clone the repository

```bash
cd ~
git clone https://github.com/davidvupham/dbtools.git
cd dbtools
```

If your team uses SSH cloning instead of HTTPS, use the SSH URL instead.

### 3.5) Corporate Docker registry (if applicable)

If your network requires pulling images through a corporate registry, follow:

- [docs/how-to/configure-corporate-docker-registry.md](../how-to/configure-corporate-docker-registry.md)

---

## Step 4 — Open dbtools in the Dev Container (recommended)

This repo ships a dev container based on **Red Hat UBI 9**, with Python provisioned via `uv`.

Reference docs:

- [docs/development/vscode/DEVCONTAINER.md](vscode/DEVCONTAINER.md)
- [docs/development/vscode/devcontainer-beginners-guide.md](vscode/devcontainer-beginners-guide.md)

### Steps

1. Open the repo in VS Code.
2. Use the Command Palette:
   - `Dev Containers: Rebuild and Reopen in Container`
3. Wait for the container build to finish.

---

## Step 5 — Verify your environment

### Option 1 (recommended): Run the VS Code task

Run the default task:

- `Dev: Verify Dev Container`

This runs the repo’s verification script and checks Python, Jupyter kernel registration, ODBC tooling, `sqlcmd`, and optional SQL Server checks.

### Option 2: Run verification from a terminal inside the container

From the repo root:

```bash
bash scripts/verify_devcontainer.sh
```

### Optional: SQL Server verification

If you are using the local SQL Server container in this repo, set `MSSQL_SA_PASSWORD` and run:

- `Dev: Verify SQL Server (sqlcmd + pyodbc)`

---

## Troubleshooting

### Slow performance on WSL2

You are probably working under `/mnt/c/`. Move the repo to your WSL home directory.

See the WSL2 guidance in:

- [docs/development/vscode/platform-specific.md](vscode/platform-specific.md)

### Dev container builds, but Python packages look wrong

The container provisions `.venv/` during `postCreate`. If you previously had a stale `.venv/`, remove it and rebuild the container:

```bash
rm -rf .venv
```

---

## What’s next

- Read the team’s development entrypoints:
  - [docs/development/README.md](README.md)
  - [docs/development/vscode/README.md](vscode/README.md)
- Follow coding standards:
  - [docs/development/coding-standards/README.md](coding-standards/README.md)
