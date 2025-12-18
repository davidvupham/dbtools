#!/usr/bin/env bash

# postCreate script for the dev container
# - Provisions Python 3.14 via uv (fallback: system Python)
# - Creates/uses a repo-local .venv
# - Installs dev tools (ruff, pytest, pyright, etc.) into that venv
# - Registers a Jupyter kernel pinned to the venv
# - Installs local packages in editable mode
# - Sets up pre-commit hooks if configured
# - Verifies pyodbc import (no OS package changes here)

set -euo pipefail

LOG() { echo "[postCreate] $*"; }

LOG "Starting setup..."

# Ensure we're at the workspace root expected by devcontainer.json
WORKSPACE_ROOT=${WORKSPACE_ROOT:-/workspaces/dbtools}
cd "$WORKSPACE_ROOT" || {
  echo "[postCreate] Workspace folder $WORKSPACE_ROOT not found" >&2
  exit 1
}

# Prefer a workspace venv managed by uv, fall back to system Python.
# Override with DEVCONTAINER_PYTHON_VERSION if desired (e.g., 3.13).
DEVCONTAINER_PYTHON_VERSION="${DEVCONTAINER_PYTHON_VERSION:-3.14}"

SYSTEM_PYTHON=python3

# Ensure user-local bin is on PATH for uv (installed via pip --user)
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
    LOG "⚠ Failed to install uv; continuing with system Python"
    return 1
  fi

  if ! command -v uv >/dev/null 2>&1; then
    LOG "⚠ uv not on PATH after install; continuing with system Python"
    return 1
  fi

  LOG "Installing Python ${DEVCONTAINER_PYTHON_VERSION} via uv..."
  if ! uv python install "$DEVCONTAINER_PYTHON_VERSION"; then
    LOG "⚠ Failed to install Python ${DEVCONTAINER_PYTHON_VERSION}; continuing with system Python"
    return 1
  fi

  LOG "Creating/updating venv at ${venv_dir} (Python ${DEVCONTAINER_PYTHON_VERSION})..."
  # --clear avoids interactive prompts when .venv already exists.
  if ! uv venv --clear --python "$DEVCONTAINER_PYTHON_VERSION" "$venv_dir"; then
    LOG "⚠ Failed to create venv; continuing with system Python"
    return 1
  fi

  if [[ -x "${venv_dir}/bin/python" ]]; then
    PYTHON="${venv_dir}/bin/python"
    PIP="$PYTHON -m pip"
    return 0
  fi

  LOG "⚠ venv python not found; continuing with system Python"
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
  LOG "⚠ Failed to install devcontainer tooling extras (continuing anyway)"
fi

# Optional Jupyter stack (kept behind the existing flag)
if [[ "${ENABLE_JUPYTERLAB:-0}" == "1" ]]; then
  LOG "ENABLE_JUPYTERLAB=1: Installing optional Jupyter tooling (.[devcontainer-jupyter])..."
  if ! $PIP install --no-cache-dir -q -e ".[devcontainer-jupyter]"; then
    LOG "⚠ Failed to install devcontainer-jupyter extras (continuing anyway)"
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
  # Force update so the kernel always points at the current interpreter.
  if $PYTHON -m ipykernel install --user --name gds --display-name "Python (gds)" --force >/dev/null 2>&1; then
    LOG "✓ Registered Jupyter kernel 'Python (gds)'"
  else
    LOG "⚠ Failed to register Jupyter kernel (continuing anyway)"
  fi
else
  LOG "⚠ ipykernel not available; skipping kernel registration"
fi

# Ensure prompt customization is present directly in ~/.bashrc (no external file dependency)
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
# Uses WORKSPACE_ROOT (set by devcontainer.json) when available.
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
      LOG "✓ Installed $pkg_dir[dev]"
    elif $PYTHON -m pip install -q -e "$pkg_dir" 2>/dev/null; then
      LOG "✓ Installed $pkg_dir"
    else
      LOG "⚠ Failed to install $pkg_dir (continuing anyway)"
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
    LOG "⚠ pre-commit not installed, skipping hook installation"
  fi
fi

# Verify Docker CLI and socket access (informational only)
LOG "Docker CLI: $(docker --version 2>/dev/null || echo 'not available')"
if docker version >/dev/null 2>&1; then
  LOG "Docker daemon reachable"
else
  LOG "WARNING: Docker daemon not reachable. Check /var/run/docker.sock mount and permissions."
  ls -l /var/run/docker.sock 2>/dev/null || true
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
