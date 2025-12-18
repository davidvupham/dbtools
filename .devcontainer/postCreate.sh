#!/usr/bin/env bash

# postCreate script for the dev container (system Python)
# - Installs dev tools (ruff, pytest, pyright, etc.)
# - Registers a Jupyter kernel
# - Installs local packages in editable mode (user site)
# - Sets up pre-commit hooks if configured
# - Verifies pyodbc import (no OS package changes here)

set -euo pipefail

echo "[postCreate] Starting setup (system Python)..."

# Ensure we're at the workspace root expected by devcontainer.json
WORKSPACE_ROOT=${WORKSPACE_ROOT:-/workspaces/dbtools}
cd "$WORKSPACE_ROOT" || {
  echo "[postCreate] Workspace folder $WORKSPACE_ROOT not found" >&2
  exit 1
}

# Use OS-provided Python
PYTHON=python3
PIP="$PYTHON -m pip"

if ! $PIP -V >/dev/null 2>&1; then
  echo "[postCreate] pip not available; trying ensurepip..."
  $PYTHON -m ensurepip --upgrade >/dev/null 2>&1 || true
fi

echo "[postCreate] Python: $($PYTHON -V)"
echo "[postCreate] Pip: $($PIP -V)"

# Install dev tools with feature-provided Python
echo "[postCreate] Installing dev tools..."
$PIP install --no-cache-dir ruff pytest pytest-cov pyright pyodbc ipykernel pre-commit || {
  echo "[postCreate] ⚠ Failed to install some dev tools (continuing anyway)"
}

# Clone additional repos if configured (optional)
if [[ -f .devcontainer/additional-repos.json ]]; then
  echo "[postCreate] Cloning additional repos..."
  bash .devcontainer/scripts/clone-additional-repos.sh || echo "[postCreate] ⚠ Failed to clone additional repos"
fi

# Register Jupyter kernel for this venv (idempotent)
echo "[postCreate] Registering Jupyter kernel..."
if $PYTHON -c "import ipykernel" >/dev/null 2>&1; then
  KERNEL_DIR="$HOME/.local/share/jupyter/kernels/gds"
  if [[ ! -d "$KERNEL_DIR" ]]; then
    if $PYTHON -m ipykernel install --user --name gds --display-name "Python (gds)" >/dev/null 2>&1; then
      echo "[postCreate] ✓ Registered Jupyter kernel 'Python (gds)'"
    else
      echo "[postCreate] ⚠ Failed to register Jupyter kernel (continuing anyway)"
    fi
  else
    echo "[postCreate] Jupyter kernel 'Python (gds)' already registered"
  fi
else
  echo "[postCreate] ⚠ ipykernel not available; skipping kernel registration"
fi

# Ensure prompt customization is present directly in ~/.bashrc (no external file dependency)
if [[ -f ~/.bashrc ]] && ! grep -q "dbtools devcontainer prompt" ~/.bashrc; then
  echo "[postCreate] Adding custom prompt to ~/.bashrc..."
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

# PS1 with user@host:path and optional git branch; place $ on the next line
export PS1="${GREEN}\u@\h${RESET}:${BLUE}\w${RESET}\$(type __git_ps1 >/dev/null 2>&1 && __git_ps1 ' (%s)')\n${CYAN}\$${RESET} "

EOP
fi

install_editable() {
  local pkg_dir="$1"
  if [[ -d "$pkg_dir" ]] && [[ -f "$pkg_dir/pyproject.toml" || -f "$pkg_dir/setup.py" ]]; then
    echo "[postCreate] Installing $pkg_dir in editable mode (user site)..."
    if $PYTHON -m pip install --user -q -e "$pkg_dir[dev]" 2>/dev/null; then
      echo "[postCreate] ✓ Installed $pkg_dir[dev]"
    elif $PYTHON -m pip install --user -q -e "$pkg_dir" 2>/dev/null; then
      echo "[postCreate] ✓ Installed $pkg_dir"
    else
      echo "[postCreate] ⚠ Failed to install $pkg_dir (continuing anyway)"
    fi
  else
    echo "[postCreate] Skipping $pkg_dir (no project files)."
  fi
}

# Install local packages
echo "[postCreate] Installing local packages..."
for pkg in gds_database gds_postgres gds_mssql gds_mongodb gds_liquibase gds_vault gds_snowflake gds_snmp_receiver; do
  install_editable "$pkg"
done

# Install pre-commit hooks if .pre-commit-config.yaml exists
if [[ -f .pre-commit-config.yaml ]]; then
  echo "[postCreate] Installing pre-commit hooks..."
  if command -v pre-commit &> /dev/null; then
    pre-commit install || echo "[postCreate] ⚠ Failed to install pre-commit hooks"
  else
    echo "[postCreate] ⚠ pre-commit not installed, skipping hook installation"
  fi
fi

# Verify Docker CLI and socket access (informational only)
echo "[postCreate] Docker CLI: $(docker --version 2>/dev/null || echo 'not available')"
if docker version >/dev/null 2>&1; then
  echo "[postCreate] Docker daemon reachable"
else
  echo "[postCreate] WARNING: Docker daemon not reachable. Check /var/run/docker.sock mount and permissions."
  ls -l /var/run/docker.sock 2>/dev/null || true
fi

echo "[postCreate] Setup complete!"

# --- Verify pyodbc import (no OS package changes here) ---
echo "[postCreate] Verifying pyodbc..."
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
