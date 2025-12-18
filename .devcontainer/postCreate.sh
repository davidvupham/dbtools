#!/usr/bin/env bash

# postCreate script for the dbtools dev container (venv-only)
# - Activates project venv and installs local packages in editable mode
# - Registers a Jupyter kernel for this venv
# - Sets up pre-commit hooks if configured
# - Verifies pyodbc import (no OS package changes here)

set -euo pipefail

echo "[postCreate] Starting setup (venv)..."

# Ensure we're at the workspace root expected by devcontainer.json
cd /workspaces/dbtools || {
  echo "[postCreate] Workspace folder /workspaces/dbtools not found" >&2
  exit 1
}

VENVPATH="/workspaces/dbtools/.venv"

# Detect and repair broken venvs or bad python3 symlinks (e.g., miniconda leftovers)
if [[ -e "$VENVPATH/bin/python3" ]]; then
  # Resolve symlink target if present; empty if readlink fails
  SYMTARGET="$(readlink "$VENVPATH/bin/python3" 2>/dev/null || true)"
  if [[ -n "$SYMTARGET" ]]; then
    if [[ "$SYMTARGET" == *"/miniconda3/"* ]]; then
      echo "[postCreate] Detected python3 symlink pointing to miniconda ($SYMTARGET); recreating venv..."
      rm -rf "$VENVPATH"
    elif [[ ! -e "$SYMTARGET" ]]; then
      echo "[postCreate] Detected broken python3 symlink target ($SYMTARGET); recreating venv..."
      rm -rf "$VENVPATH"
    fi
  fi
fi

# Ensure venv exists (fresh) and activate it
if [[ ! -d "$VENVPATH" ]]; then
  echo "[postCreate] Creating Python venv..."
  /usr/bin/python3 -m venv "$VENVPATH"
fi

# Ensure python3 inside venv points to venv's python
ln -sf "$VENVPATH/bin/python" "$VENVPATH/bin/python3"

. "$VENVPATH/bin/activate"

echo "[postCreate] Python: $(python -V)"
echo "[postCreate] Pip: $(python -m pip -V)"

# Register Jupyter kernel for this venv (idempotent)
echo "[postCreate] Registering Jupyter kernel for venv..."
if python -c "import ipykernel" >/dev/null 2>&1; then
  KERNEL_DIR="$HOME/.local/share/jupyter/kernels/gds"
  if [[ ! -d "$KERNEL_DIR" ]]; then
    if python -m ipykernel install --user --name gds --display-name "Python (gds)" >/dev/null 2>&1; then
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

# Ensure interactive shells auto-activate the venv
if [[ -f ~/.bashrc ]] && ! grep -q "/workspaces/dbtools/.venv/bin/activate" ~/.bashrc; then
  echo "[postCreate] Enabling venv auto-activation for interactive shells..."
  echo "source /workspaces/dbtools/.venv/bin/activate" >> ~/.bashrc
fi

install_editable() {
  local pkg_dir="$1"
  if [[ -d "$pkg_dir" ]] && [[ -f "$pkg_dir/pyproject.toml" || -f "$pkg_dir/setup.py" ]]; then
    echo "[postCreate] Installing $pkg_dir in editable mode..."
    if python -m pip install -q -e "$pkg_dir[dev]" 2>/dev/null; then
      echo "[postCreate] ✓ Installed $pkg_dir[dev]"
    elif python -m pip install -q -e "$pkg_dir" 2>/dev/null; then
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
python - <<'PY' || true
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

# --- Create default ~/.set_prompt if missing (optional custom prompt) ---
if [[ ! -f "$HOME/.set_prompt" ]]; then
  echo "[postCreate] Creating default ~/.set_prompt..."
  cat > "$HOME/.set_prompt" <<'EOP'
# ~/.set_prompt - default bash prompt for dbtools devcontainer

# Try to load git prompt helpers if available
for p in \
  /usr/share/git-core/contrib/completion/git-prompt.sh \
  /usr/share/bash-completion/completions/git-prompt \
  /etc/bash_completion.d/git-prompt; do
  [ -f "$p" ] && . "$p" && break
done

# venv prefix
venv_prefix=''
[ -n "$VIRTUAL_ENV" ] && venv_prefix="($(basename \"$VIRTUAL_ENV\")) "

# colors
GREEN='\[\e[32m\]'
BLUE='\[\e[34m\]'
CYAN='\[\e[36m\]'
RESET='\[\e[0m\]'

# PS1 with user@host:path and optional git branch
export PS1="${venv_prefix}${GREEN}\u@\h${RESET}:${BLUE}\w${RESET}\$(type __git_ps1 >/dev/null 2>&1 && __git_ps1 ' (%s)')
${CYAN}\$${RESET} "
EOP
fi
