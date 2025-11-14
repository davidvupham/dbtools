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

# Ensure Docker CLI is available (for DooD) and basic network tools for tests
if ! command -v docker >/dev/null 2>&1; then
  echo "[postCreate] Installing Docker CLI (docker.io)..."
  if command -v sudo >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y -qq docker.io >/dev/null
  else
    apt-get update -y
    apt-get install -y -qq docker.io >/dev/null
  fi
else
  echo "[postCreate] Docker CLI already present."
fi

# Install netcat for connectivity tests if missing
if ! command -v nc >/dev/null 2>&1; then
  echo "[postCreate] Installing netcat-openbsd..."
  if command -v sudo >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y -qq netcat-openbsd >/dev/null || sudo apt-get install -y -qq netcat >/dev/null || true
  else
    apt-get update -y
    apt-get install -y -qq netcat-openbsd >/dev/null || apt-get install -y -qq netcat >/dev/null || true
  fi
fi

# Print docker diagnostic info (non-fatal if socket not yet mounted)
echo "[postCreate] Docker CLI version: $(docker --version 2>/dev/null || echo 'not available')"
if docker version >/dev/null 2>&1; then
  echo "[postCreate] Docker daemon reachable"
else
  echo "[postCreate] WARNING: Docker daemon not reachable. Ensure /var/run/docker.sock is mounted and permissions allow access."
  ls -l /var/run/docker.sock 2>/dev/null || true
fi

#echo "[postCreate] Upgrading pip and wheel..."
#python -m pip install --upgrade pip wheel >/dev/null

install_editable() {
  local pkg_dir="$1"
  if [[ -d "$pkg_dir" ]] && [[ -f "$pkg_dir/pyproject.toml" || -f "$pkg_dir/setup.py" ]]; then
    echo "[postCreate] Installing $pkg_dir in editable mode (prefer [dev] extras if available)..."
    # Try with dev extras first; if it fails (e.g., extras not defined), fall back to base
    if ! python -m pip install -e "$pkg_dir[dev]" 2>&1 | grep -v "^Requirement already satisfied"; then
      python -m pip install -e "$pkg_dir" 2>&1 | grep -v "^Requirement already satisfied"
    fi
    echo "[postCreate] ✓ Installed $pkg_dir"
  else
    echo "[postCreate] Skipping $pkg_dir (no project files)."
  fi
}

# Install local packages
for pkg in gds_database gds_postgres gds_snowflake gds_vault gds_mongodb gds_mssql gds_notification gds_snmp_receiver; do
  install_editable "$pkg"
done

# Setup pre-commit if configured
if [[ -f .pre-commit-config.yaml ]]; then
  echo "[postCreate] Installing and configuring pre-commit hooks..."
  python -m pip install --upgrade pre-commit 2>&1 | grep -v "^Requirement already satisfied" || true
  pre-commit install || true
  echo "[postCreate] ✓ Pre-commit hooks configured"
else
  echo "[postCreate] No .pre-commit-config.yaml found; skipping pre-commit setup."
fi

echo "[postCreate] Done."
