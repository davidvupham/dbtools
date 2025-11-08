#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PYTHON_SCRIPT="${SCRIPT_DIR}/sync_devcontainers.py"

if [[ ! -x "${PYTHON_SCRIPT}" ]]; then
  echo "[sync-devcontainers] Python helper not found or not executable: ${PYTHON_SCRIPT}" >&2
  exit 1
fi

python3 "${PYTHON_SCRIPT}" "$@"
