#!/usr/bin/env bash

# postCreate script for the VS Code dev container.
#
# This runs automatically after the container is built and the workspace is
# mounted. It sets up the Python environment and developer tooling inside the
# container.
#
# What this script does:
# - Provisions Python and dependencies via `uv` into a repo-local virtual
#   environment (./.venv) using the lock file for reproducibility
# - Installs all workspace packages (gds_*) in editable mode automatically
# - Optionally installs Jupyter extras when ENABLE_JUPYTERLAB=1
# - Registers a Jupyter kernel pointing at the workspace virtual environment
# - Installs pre-commit hooks (if .pre-commit-config.yaml exists)
# - Performs a quick pyodbc import sanity check
#
# Environment variables you can override:
# - WORKSPACE_ROOT: Absolute path to the repo root inside the container.
#   If unset, we derive it from this script's location.
# - DEVCONTAINER_PYTHON_VERSION: Python version for `uv python install`.
#   Default is 3.13 (chosen for broad wheel availability).
# - ENABLE_JUPYTERLAB: If set to 1, installs the optional Jupyter stack.

set -euo pipefail

LOG() { echo "[postCreate] $*"; }

LOG "Starting setup..."

ensure_docker_socket_access() {
  if [[ ! -S /var/run/docker.sock ]]; then
    LOG "Docker socket not mounted; skipping docker permission setup"
    return 0
  fi

  # If Docker is already usable, nothing to do.
  if docker version >/dev/null 2>&1; then
    LOG "Docker daemon reachable"
    return 0
  fi

  local sock_gid
  sock_gid="$(stat -c %g /var/run/docker.sock 2>/dev/null || true)"
  if [[ -z "$sock_gid" ]]; then
    LOG "WARN: Could not read docker.sock group id; skipping"
    return 0
  fi

  # We need root to create groups / adjust membership.
  if ! command -v sudo >/dev/null 2>&1; then
    LOG "WARN: sudo not available; cannot fix docker.sock permissions automatically"
    return 0
  fi

  LOG "Docker socket is owned by group id ${sock_gid}; aligning user group membership..."

  # Use an existing group name for this gid if present; otherwise create one.
  local group_name
  group_name="$(getent group "$sock_gid" | cut -d: -f1 || true)"
  if [[ -z "$group_name" ]]; then
    group_name="docker-host"
    if ! sudo -n groupadd -g "$sock_gid" "$group_name" 2>/dev/null; then
      # If a race or naming conflict happens, fall back to whatever group name exists now.
      group_name="$(getent group "$sock_gid" | cut -d: -f1 || true)"
    fi
  fi

  if [[ -n "$group_name" ]]; then
    if id -nG "$USER" | tr ' ' '\n' | grep -qx "$group_name"; then
      LOG "Docker group already present on user ($group_name)"
    else
      sudo -n usermod -aG "$group_name" "$USER" || true
      LOG "OK: Added $USER to group '$group_name' (reopen terminals to pick up new group)"
    fi
  else
    LOG "WARN: Could not determine/create a group for docker.sock gid=${sock_gid}"
  fi
}

ensure_docker_socket_access

# Ensure we're at the repo root.
# Prefer an explicit WORKSPACE_ROOT, otherwise derive it from this script's
# location (parent of the .devcontainer directory).
if [[ -z "${WORKSPACE_ROOT:-}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

cd "$WORKSPACE_ROOT" || {
  echo "[postCreate] Workspace folder $WORKSPACE_ROOT not found" >&2
  exit 1
}

LOG "Workspace root: $WORKSPACE_ROOT"

# Default to Python 3.13 to maximize availability of prebuilt wheels
# (for example, snowflake-connector-python).
# Override with DEVCONTAINER_PYTHON_VERSION if desired.
DEVCONTAINER_PYTHON_VERSION="${DEVCONTAINER_PYTHON_VERSION:-3.13}"

# Ensure user-local bin is on PATH for uv.
export PATH="$HOME/.local/bin:$PATH"

# =============================================================================
# UV Setup
# =============================================================================
# UV is the single tool for Python version management, virtual environments,
# and dependency installation. No pip required.

setup_uv() {
  # Check if uv is already available
  if command -v uv >/dev/null 2>&1; then
    LOG "UV already available: $(uv --version)"
    return 0
  fi

  # Install UV via the official installer
  LOG "Installing UV..."
  if curl -LsSf https://astral.sh/uv/install.sh | sh; then
    # Reload PATH to pick up uv
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv >/dev/null 2>&1; then
      LOG "UV installed: $(uv --version)"
      return 0
    fi
  fi

  LOG "ERROR: Failed to install UV"
  return 1
}

if ! setup_uv; then
  echo "[postCreate] FATAL: UV installation failed" >&2
  exit 1
fi

# =============================================================================
# Install Python and Sync Dependencies
# =============================================================================
# uv sync reads pyproject.toml and uv.lock, creates .venv, and installs:
# - All external dependencies from the lock file
# - All workspace packages (gds_*) in editable mode automatically

LOG "Installing Python ${DEVCONTAINER_PYTHON_VERSION} via UV..."
uv python install "$DEVCONTAINER_PYTHON_VERSION"

LOG "Syncing dependencies (this installs all gds_* packages automatically)..."
if ! uv sync --python "$DEVCONTAINER_PYTHON_VERSION" --group devcontainer; then
  LOG "ERROR: uv sync failed"
  exit 1
fi

# Set PYTHON to the venv interpreter for subsequent commands
PYTHON=".venv/bin/python"

# Optional Jupyter stack (install additional group)
if [[ "${ENABLE_JUPYTERLAB:-0}" == "1" ]]; then
  LOG "ENABLE_JUPYTERLAB=1: Installing Jupyter tooling..."
  uv sync --python "$DEVCONTAINER_PYTHON_VERSION" --group devcontainer --group jupyter || \
    LOG "WARN: Failed to install jupyter group (continuing anyway)"
fi

LOG "Python: $($PYTHON --version)"
LOG "UV: $(uv --version)"

# Clone additional repos if configured (optional)
if [[ -f .devcontainer/additional-repos.json ]]; then
  LOG "Cloning additional repos..."
  bash .devcontainer/scripts/clone-additional-repos.sh || echo "[postCreate] ⚠ Failed to clone additional repos"
fi

# Register Jupyter kernel for this venv (idempotent)
LOG "Registering Jupyter kernel..."
if $PYTHON -c "import ipykernel" >/dev/null 2>&1; then
  # Keep this idempotent: remove any existing kernelspec so the kernel always
  # points at the current interpreter.
  rm -rf "$HOME/.local/share/jupyter/kernels/gds" 2>/dev/null || true
  if $PYTHON -m ipykernel install --user --name gds --display-name "Python (gds)" >/dev/null 2>&1; then
    LOG "OK: Registered Jupyter kernel 'Python (gds)'"
  else
    LOG "WARN: Failed to register Jupyter kernel (continuing anyway)"
  fi
else
  LOG "WARN: ipykernel not available; skipping kernel registration"
fi

# Ensure prompt customization is present directly in ~/.bashrc (no external file dependency).
# This is only for interactive shells.
if [[ -f ~/.bashrc ]] && ! grep -q "dbtools devcontainer prompt" ~/.bashrc; then
  LOG "Adding custom prompt to ~/.bashrc..."
  cat <<'EOP' >> ~/.bashrc
# dbtools devcontainer prompt
# Try to load git prompt helpers if available
for p in \
  /usr/share/git-core/contrib/completion/git-prompt.sh \
  /usr/share/bash-completion/completions/git-prompt \
  /etc/bash_completion.d/git-prompt; do
  [ -f "$p" ] && . "$p" && break
done

# colors
GREEN='\[\e[32m\]'
BLUE='\[\e[34m\]'
CYAN='\[\e[36m\]'
RESET='\[\e[0m\]'

# Auto-activate workspace venv (if present) for interactive shells.
# Uses WORKSPACE_ROOT if exported in the environment; otherwise uses a safe
# default for this repository.
if [[ -n "${PS1:-}" ]] && [[ -z "${VIRTUAL_ENV:-}" ]]; then
  __ws_root="${WORKSPACE_ROOT:-/workspaces/devcontainer/dbtools}"
  if [[ -f "${__ws_root}/.venv/bin/activate" ]]; then
    case "${PWD:-}" in
      "${__ws_root}"|"${__ws_root}"/*)
        . "${__ws_root}/.venv/bin/activate"
        ;;
    esac
  fi
fi

# PS1 with user@host:path and optional git branch; place $ on the next line
export PS1="${GREEN}\u@\h${RESET}:${BLUE}\w${RESET}\$(type __git_ps1 >/dev/null 2>&1 && __git_ps1 ' (%s)')\n${CYAN}\$${RESET} "

EOP
fi

# Install pre-commit hooks if .pre-commit-config.yaml exists
if [[ -f .pre-commit-config.yaml ]]; then
  LOG "Installing pre-commit hooks..."
  if uv run python -c "import pre_commit" >/dev/null 2>&1; then
    uv run pre-commit install || LOG "⚠ Failed to install pre-commit hooks"
  else
    LOG "WARN: pre-commit not installed, skipping hook installation"
  fi
fi

# Verify Docker CLI and socket access (informational only)
LOG "Docker CLI: $(docker --version 2>/dev/null || echo 'not available')"
if docker version >/dev/null 2>&1; then
  LOG "Docker daemon reachable"
else
  LOG "WARNING: Docker daemon not reachable. Check the /var/run/docker.sock mount and permissions."
  ls -l /var/run/docker.sock 2>/dev/null || true
  LOG "NOTE: If group membership was changed above, reopen terminals and try again."
fi

LOG "Setup complete!"

# --- Verify pyodbc import ---
LOG "Verifying pyodbc..."
uv run python - <<'PY' || true
import sys
try:
    import pyodbc
    print(f"[postCreate] pyodbc version: {pyodbc.version}")
    try:
        drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    except Exception:
        drivers = []
    print(f"[postCreate] ODBC drivers (SQL Server filtered): {drivers}")
    print(f"[postCreate] Python executable: {sys.executable}")
except Exception as e:
    print("[postCreate] pyodbc not importable:", e)
PY

