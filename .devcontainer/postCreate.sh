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

echo "[postCreate] Upgrading pip and wheel..."
python -m pip install --upgrade pip wheel >/dev/null

install_editable() {
  local pkg_dir="$1"
  if [[ -d "$pkg_dir" ]] && [[ -f "$pkg_dir/pyproject.toml" || -f "$pkg_dir/setup.py" ]]; then
    echo "[postCreate] Installing $pkg_dir in editable mode (prefer [dev] extras if available)..."
    # Try with dev extras first; if it fails (e.g., extras not defined), fall back to base
    if ! python -m pip install -e "$pkg_dir[dev]" >/dev/null 2>&1; then
      python -m pip install -e "$pkg_dir" >/dev/null
    fi
  else
    echo "[postCreate] Skipping $pkg_dir (no project files)."
  fi
}

# Install local packages
for pkg in gds_database gds_postgres gds_snowflake gds_vault; do
  install_editable "$pkg"
done

# Setup pre-commit if configured
if [[ -f .pre-commit-config.yaml ]]; then
  echo "[postCreate] Installing and configuring pre-commit hooks..."
  python -m pip install --upgrade pre-commit >/dev/null
  pre-commit install || true
else
  echo "[postCreate] No .pre-commit-config.yaml found; skipping pre-commit setup."
fi

echo "[postCreate] Done."
