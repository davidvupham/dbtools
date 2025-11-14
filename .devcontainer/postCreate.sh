#!/usr/bin/env bash

# postCreate script for the dbtools dev container
# - Installs local packages in editable mode
# - Optionally installs dev extras when available
# - Sets up pre-commit hooks if configured

set -euo pipefail

echo "[postCreate] Starting setup..."

# Ensure we're at the workspace root expected by devcontainer.json
cd /workspaces/dbtools || {
  echo "[postCreate] Workspace folder /workspaces/dbtools not found" >&2
  exit 1
}

echo "[postCreate] Python: $(python -V)"
echo "[postCreate] Pip: $(python -m pip -V)"

# Verify Docker CLI and socket access
echo "[postCreate] Docker CLI version: $(docker --version 2>/dev/null || echo 'not available')"
if docker version >/dev/null 2>&1; then
  echo "[postCreate] Docker daemon reachable"
else
  echo "[postCreate] WARNING: Docker daemon not reachable. Check /var/run/docker.sock mount and permissions."
  ls -l /var/run/docker.sock 2>/dev/null || true
fi

install_editable() {
  local pkg_dir="$1"
  if [[ -d "$pkg_dir" ]] && [[ -f "$pkg_dir/pyproject.toml" || -f "$pkg_dir/setup.py" ]]; then
    echo "[postCreate] Installing $pkg_dir in editable mode..."
    # Try with dev extras first; if it fails (e.g., extras not defined), fall back to base
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
for pkg in gds_database gds_postgres gds_snowflake gds_vault gds_mongodb gds_mssql gds_notification gds_snmp_receiver; do
  install_editable "$pkg"
done
echo "[postCreate] Package installation complete."

# Setup pre-commit if configured
if [[ -f .pre-commit-config.yaml ]]; then
  echo "[postCreate] Installing and configuring pre-commit hooks..."
  if python -m pip install -q --upgrade pre-commit 2>/dev/null && pre-commit install 2>/dev/null; then
    echo "[postCreate] ✓ Pre-commit hooks configured"
  else
    echo "[postCreate] ⚠ Pre-commit setup failed (continuing anyway)"
  fi
else
  echo "[postCreate] No .pre-commit-config.yaml found; skipping pre-commit setup."
fi

echo "[postCreate] Setup complete!"
exit 0
