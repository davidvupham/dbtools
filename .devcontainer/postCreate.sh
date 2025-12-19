#!/usr/bin/env bash

# postCreate script for the VS Code dev container.
#
# This runs automatically after the container is built and the workspace is
# mounted. It sets up the Python environment and developer tooling inside the
# container.
#
# What this script does:
# - Provisions Python via `uv` into a repo-local virtual environment (./.venv)
#   (falls back to the system Python if that fails)
# - Installs project tooling from pyproject.toml extras (ruff, pytest, pyright, etc.)
# - Optionally installs Jupyter extras when ENABLE_JUPYTERLAB=1
# - Registers a Jupyter kernel pointing at the workspace virtual environment
# - Installs local packages in editable mode (so edits take effect immediately)
# - Installs pre-commit hooks (if .pre-commit-config.yaml exists)
# - Performs a quick pyodbc import sanity check (no OS package changes here)
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

# Prefer a workspace virtual environment managed by uv, fall back to system Python.
# Default to Python 3.13 to maximize availability of prebuilt wheels
# (for example, snowflake-connector-python).
# Override with DEVCONTAINER_PYTHON_VERSION if desired.
DEVCONTAINER_PYTHON_VERSION="${DEVCONTAINER_PYTHON_VERSION:-3.13}"

# IMPORTANT: use the OS Python explicitly.
# In this repo, `python3` may resolve to the workspace virtual environment
# (e.g., via PATH or shell activation), which breaks `pip --user` installs.
SYSTEM_PYTHON=/usr/bin/python3

# Ensure user-local bin is on PATH for uv (installed via `pip --user`).
export PATH="$HOME/.local/bin:$PATH"

PYTHON="$SYSTEM_PYTHON"
PIP="$PYTHON -m pip"

setup_uv_venv() {
  local venv_dir=".venv"

  if ! "$SYSTEM_PYTHON" -m pip -V >/dev/null 2>&1; then
    LOG "pip not available; trying ensurepip..."
    "$SYSTEM_PYTHON" -m ensurepip --upgrade >/dev/null 2>&1 || true
  fi

  LOG "Installing uv (user site)..."
  if ! "$SYSTEM_PYTHON" -m pip install --user --no-cache-dir -q -U uv; then
    LOG "WARN: Failed to install uv; continuing with system Python"
    return 1
  fi

  if ! command -v uv >/dev/null 2>&1; then
    LOG "WARN: uv not on PATH after install; continuing with system Python"
    return 1
  fi

  LOG "Installing Python ${DEVCONTAINER_PYTHON_VERSION} via uv..."
  if ! uv python install "$DEVCONTAINER_PYTHON_VERSION"; then
    LOG "WARN: Failed to install Python ${DEVCONTAINER_PYTHON_VERSION}; continuing with system Python"
    return 1
  fi

  LOG "Creating/updating venv at ${venv_dir} (Python ${DEVCONTAINER_PYTHON_VERSION})..."
  # --clear avoids interactive prompts when .venv already exists.
  if ! uv venv --clear --python "$DEVCONTAINER_PYTHON_VERSION" "$venv_dir"; then
    LOG "WARN: Failed to create venv; continuing with system Python"
    return 1
  fi

  if [[ -x "${venv_dir}/bin/python" ]]; then
    PYTHON="${venv_dir}/bin/python"
    PIP="$PYTHON -m pip"
    return 0
  fi

  LOG "WARN: venv python not found; continuing with system Python"
  return 1
}

if setup_uv_venv; then
  LOG "Using venv interpreter: $PYTHON"
else
  LOG "Using system interpreter: $PYTHON"
fi

if ! $PIP -V >/dev/null 2>&1; then
  LOG "pip not available; trying ensurepip..."
  $PYTHON -m ensurepip --upgrade >/dev/null 2>&1 || true
fi

LOG "Python: $($PYTHON -V)"
LOG "Pip: $($PIP -V)"

# Install dev tools (single source of truth: pyproject.toml optional deps)
LOG "Installing dev tools (.[devcontainer])..."
$PIP install --no-cache-dir -q -U pip setuptools wheel || true
if ! $PIP install --no-cache-dir -q -e ".[devcontainer]"; then
  LOG "WARN: Failed to install devcontainer tooling extras (continuing anyway)"
fi

# Optional Jupyter stack (kept behind the existing flag).
# Note: This installs the *Python* Jupyter packages. The VS Code Jupyter extension
# is installed via devcontainer.json.
if [[ "${ENABLE_JUPYTERLAB:-0}" == "1" ]]; then
  LOG "ENABLE_JUPYTERLAB=1: Installing optional Jupyter tooling (.[devcontainer-jupyter])..."
  if ! $PIP install --no-cache-dir -q -e ".[devcontainer-jupyter]"; then
    LOG "WARN: Failed to install devcontainer-jupyter extras (continuing anyway)"
  fi
fi

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

install_editable() {
  local pkg_dir="$1"
  if [[ -d "$pkg_dir" ]] && [[ -f "$pkg_dir/pyproject.toml" || -f "$pkg_dir/setup.py" ]]; then
    LOG "Installing $pkg_dir in editable mode..."
    if $PYTHON -m pip install -q -e "$pkg_dir[dev]" 2>/dev/null; then
      LOG "OK: Installed $pkg_dir[dev]"
    elif $PYTHON -m pip install -q -e "$pkg_dir" 2>/dev/null; then
      LOG "OK: Installed $pkg_dir"
    else
      LOG "WARN: Failed to install $pkg_dir (continuing anyway)"
    fi
  else
    LOG "Skipping $pkg_dir (no project files)."
  fi
}

# Install local packages
LOG "Installing local packages..."
for pkg in gds_database gds_postgres gds_mssql gds_mongodb gds_liquibase gds_vault gds_snowflake gds_snmp_receiver; do
  install_editable "$pkg"
done

# Install pre-commit hooks if .pre-commit-config.yaml exists
if [[ -f .pre-commit-config.yaml ]]; then
  LOG "Installing pre-commit hooks..."
  if $PYTHON -c "import pre_commit" >/dev/null 2>&1; then
    $PYTHON -m pre_commit install || LOG "⚠ Failed to install pre-commit hooks"
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

# --- Verify pyodbc import (no OS package changes here) ---
LOG "Verifying pyodbc..."
$PYTHON - <<'PY' || true
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
