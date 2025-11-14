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

# Install pre-commit hooks if .pre-commit-config.yaml exists
if [[ -f .pre-commit-config.yaml ]]; then
  echo "[postCreate] Installing pre-commit hooks..."
  if command -v pre-commit &> /dev/null; then
    pre-commit install || echo "[postCreate] ⚠ Failed to install pre-commit hooks"
  else
    echo "[postCreate] ⚠ pre-commit not installed, skipping hook installation"
  fi
fi

echo "[postCreate] Setup complete!"

# --- Optional: Ensure pyodbc is available for SQL Server tooling ---
# Installs Microsoft ODBC Driver 18 and attempts a pyodbc install only if import fails.
# Safe to re-run; skips work when already satisfied.
echo "[postCreate] Verifying pyodbc and ODBC driver..."

has_pyodbc() {
  python - <<'PY' >/dev/null 2>&1 || return 1
import sys
try:
    import pyodbc  # noqa: F401
except Exception:
    raise SystemExit(1)
PY
}

print_pyodbc_info() {
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
}

if has_pyodbc; then
  echo "[postCreate] pyodbc already available. Skipping installation."
  print_pyodbc_info
else
  echo "[postCreate] pyodbc not found. Installing prerequisites..."

  # Install Microsoft repo + ODBC Driver 18 if not present
  if ! command -v odbcinst >/dev/null 2>&1 || ! odbcinst -q -d 2>/dev/null | grep -q "ODBC Driver 18 for SQL Server"; then
    echo "[postCreate] Adding Microsoft APT repo (if needed) and installing msodbcsql18..."
    if [[ -f /etc/os-release ]]; then
      # shellcheck disable=SC1091
      source /etc/os-release
      if [[ "${ID:-}" = "debian" || "${ID_LIKE:-}" =~ debian ]]; then
        sudo mkdir -p /usr/share/keyrings
        if [[ ! -f /usr/share/keyrings/microsoft-archive-keyring.gpg ]]; then
          curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg || true
        fi
        if [[ ! -f /etc/apt/sources.list.d/microsoft-prod.list ]]; then
          echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/${VERSION_ID}/prod ${VERSION_CODENAME} main" | sudo tee /etc/apt/sources.list.d/microsoft-prod.list >/dev/null
        fi
        sudo DEBIAN_FRONTEND=noninteractive apt-get update -y || true
        sudo ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt-get install -y msodbcsql18 unixodbc-dev || true
      fi
    fi
  else
    echo "[postCreate] Found existing 'ODBC Driver 18 for SQL Server'."
  fi

  echo "[postCreate] Installing pyodbc via pip..."
  # Try system/site install first; fall back to user site if needed
  python -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1 || true
  if python -m pip install pyodbc >/dev/null 2>&1; then
    echo "[postCreate] ✓ Installed pyodbc (site)."
  elif python -m pip install --user pyodbc >/dev/null 2>&1; then
    echo "[postCreate] ✓ Installed pyodbc (user)."
  else
    echo "[postCreate] ⚠ Failed to install pyodbc via pip."
  fi

  if has_pyodbc; then
    echo "[postCreate] pyodbc installation verified."
    print_pyodbc_info
  else
    echo "[postCreate] ⚠ pyodbc still not importable; check ODBC headers/driver and Python environment permissions."
  fi
fi

# --- Ensure interactive shells auto-activate the 'gds' conda environment ---
if command -v conda >/dev/null 2>&1; then
  if conda env list 2>/dev/null | awk '{print $1}' | grep -qx "gds"; then
    # Validate pyodbc inside gds; install there if missing (with safe fallbacks)
    echo "[postCreate] Validating pyodbc inside 'gds' environment..."
    if conda run -n gds python - <<'PY' >/dev/null 2>&1
import sys
import pyodbc  # noqa: F401
print('OK')
PY
      then
      echo "[postCreate] pyodbc import OK inside 'gds'."
    else
      echo "[postCreate] pyodbc missing in 'gds'. Attempting conda install..."
      if conda install -n gds -y pyodbc >/dev/null 2>&1; then
        echo "[postCreate] ✓ Installed pyodbc into 'gds' via conda."
      else
        echo "[postCreate] conda install failed; attempting pip user install within 'gds'..."
        if conda run -n gds python -m pip install --user pyodbc >/dev/null 2>&1; then
          echo "[postCreate] ✓ Installed pyodbc into 'gds' user site via pip."
        else
          echo "[postCreate] ⚠ Failed to install pyodbc into 'gds'."
        fi
      fi
    fi

    if ! grep -q "conda activate gds" "$HOME/.bashrc" 2>/dev/null; then
      echo "[postCreate] Enabling auto-activation of 'gds' conda env for interactive shells..."
      {
        echo ''
        echo '# Auto-activate conda env: gds'
        echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then'
        echo '  . /opt/conda/etc/profile.d/conda.sh'
        echo '  conda activate gds >/dev/null 2>&1 || true'
        echo '  # Refresh command hash so python resolves to env bin'
        echo '  hash -r'
        echo 'fi'
      } >> "$HOME/.bashrc"
    else
      # Ensure hash refresh exists even if activation was previously added
      if ! grep -q "hash -r" "$HOME/.bashrc" 2>/dev/null; then
        echo "[postCreate] Adding hash refresh after gds activation in ~/.bashrc."
        printf "\n# Ensure command hash is refreshed after conda activation\nhash -r\n" >> "$HOME/.bashrc"
      fi
      echo "[postCreate] Auto-activation for 'gds' already configured in ~/.bashrc."
    fi
  else
    echo "[postCreate] Conda env 'gds' not found; skipping auto-activation setup."
  fi
else
  echo "[postCreate] conda not available; skipping auto-activation setup."
fi

# --- Ensure base interpreter also has pyodbc (fallback for path mismatches) ---
if [[ -x "/opt/conda/bin/python" ]]; then
  echo "[postCreate] Checking pyodbc in base interpreter: /opt/conda/bin/python"
  if /opt/conda/bin/python - <<'PY' >/dev/null 2>&1
import pyodbc  # noqa: F401
PY
    then
    echo "[postCreate] pyodbc already present in base interpreter."
  else
    echo "[postCreate] Installing pyodbc into base interpreter..."
    /opt/conda/bin/python -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1 || true
    if /opt/conda/bin/python -m pip install pyodbc >/dev/null 2>&1; then
      echo "[postCreate] ✓ Installed pyodbc in base interpreter."
    else
      echo "[postCreate] ⚠ Failed to install pyodbc in base interpreter."
    fi
  fi
fi
